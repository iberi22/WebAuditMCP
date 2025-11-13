"""
OWASP ZAP baseline security scanning tool.
"""

import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

def zap_baseline(url: str, minutes: int = 5) -> dict[str, Any]:
    """
    Run OWASP ZAP baseline security scan.

    Args:
        url: The URL to scan
        minutes: Maximum scan duration in minutes

    Returns:
        Dict containing security alerts and raw ZAP results
    """
    try:
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")

        # Validate minutes
        if minutes < 1 or minutes > 30:
            raise ValueError("Minutes must be between 1 and 30")

        # Check if Docker is available
        try:
            subprocess.run(["docker", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {
                'status': 'error',
                'error': 'Docker is not available. Please install Docker to use ZAP baseline scanning.'
            }

        # Create temporary file for ZAP output
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            # Convert localhost to host.docker.internal for Docker access
            scan_url = url.replace('localhost', 'host.docker.internal')

            # Run ZAP baseline scan with new image and correct JSON output
            output_filename = Path(tmp_path).name
            cmd = [
                "docker", "run", "--rm", "-t",
                "--add-host=host.docker.internal:host-gateway",
                "-v", f"{Path(tmp_path).parent}:/zap/wrk/:rw",
                "ghcr.io/zaproxy/zaproxy:stable",
                "zap-baseline.py",
                "-t", scan_url,
                "-m", str(minutes),
                "-J", f"/zap/wrk/{output_filename}",
                "-I",  # Ignore warnings
                "-r", f"/zap/wrk/zap_report_{output_filename}.html"  # Also generate HTML report
            ]

            logger.info(f"Running ZAP baseline scan for {url} (max {minutes} minutes)")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=minutes * 60 + 60)

            if result.returncode != 0:
                error_output = (result.stderr or result.stdout or "").strip()
                logger.error(f"ZAP baseline scan docker error: {error_output}")
                return {
                    'status': 'error',
                    'error': 'Docker execution failed while running OWASP ZAP baseline scan.',
                    'details': error_output
                }

            # ZAP may return non-zero exit codes even on successful scans
            # Check if output file was created
            if not Path(tmp_path).exists():
                raise RuntimeError(f"ZAP scan failed to produce output: {result.stderr}")

            # Read and parse results
            try:
                with open(tmp_path) as f:
                    content = f.read()
                    if not content.strip():
                        raise ValueError("ZAP output file is empty")
                    raw_data = json.loads(content)
            except (json.JSONDecodeError, ValueError) as exc:
                logger.error(f"Failed to parse ZAP output JSON: {exc}")
                # Try to read the file content for debugging
                try:
                    with open(tmp_path) as f:
                        file_content = f.read()[:500]  # First 500 chars
                except (IOError, OSError):
                    file_content = "Could not read file"

                return {
                    'status': 'error',
                    'error': 'ZAP scan completed but produced invalid JSON output',
                    'details': f"JSON error: {exc}",
                    'file_content': file_content,
                    'docker_stdout': result.stdout[:500] if result.stdout else "",
                    'docker_stderr': result.stderr[:500] if result.stderr else ""
                }

            # Extract alerts
            alerts = []
            site_data = raw_data.get('site', [])

            for site in site_data:
                for alert in site.get('alerts', []):
                    alerts.append({
                        'risk': alert.get('riskdesc'),
                        'confidence': alert.get('confidence'),
                        'name': alert.get('name'),
                        'description': alert.get('desc'),
                        'solution': alert.get('solution'),
                        'instances': len(alert.get('instances', []))
                    })

            # Calculate security score based on risk levels
            risk_weights = {'High': 25, 'Medium': 10, 'Low': 5, 'Informational': 1}
            total_risk_score = sum(
                risk_weights.get(alert['risk'].split()[0], 0)
                for alert in alerts
            )

            # Convert to 0-100 scale (lower is better for security)
            security_score = max(0, 100 - total_risk_score)

            return {
                'status': 'ok',
                'url': url,
                'scanDuration': minutes,
                'securityScore': round(security_score, 1),
                'alerts': alerts,
                'alertsCount': len(alerts),
                'raw': raw_data
            }

        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)

    except subprocess.TimeoutExpired:
        return {
            'status': 'error',
            'error': f'ZAP baseline scan timed out after {minutes * 60 + 60} seconds'
        }
    except Exception as e:
        logger.error(f"ZAP baseline scan failed: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }
