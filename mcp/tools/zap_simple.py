"""
OWASP ZAP baseline security scanning tool - Simplified version.
"""

import logging
import subprocess
from typing import Any

logger = logging.getLogger(__name__)

def zap_baseline_simple(url: str, minutes: int = 5) -> dict[str, Any]:
    """
    Run OWASP ZAP baseline security scan - simplified version.

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

        # Convert localhost to host.docker.internal for Docker access
        scan_url = url.replace('localhost', 'host.docker.internal')

        # Run ZAP baseline scan - simplified approach
        cmd = [
            "docker", "run", "--rm",
            "--add-host=host.docker.internal:host-gateway",
            "ghcr.io/zaproxy/zaproxy:stable",
            "zap-baseline.py",
            "-t", scan_url,
            "-m", str(minutes),
            "-I"  # Ignore warnings
        ]

        logger.info(f"Running ZAP baseline scan for {url} (max {minutes} minutes)")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=minutes * 60 + 60)

        # Parse output from stdout (ZAP baseline outputs results to stdout)
        output = result.stdout or ""

        # Extract alerts from text output
        alerts = []
        lines = output.split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('WARN') or line.startswith('FAIL'):
                # Parse alert line: "WARN-NEW: Alert Name [ID] x N"
                parts = line.split(': ', 1)
                if len(parts) == 2:
                    risk_level = parts[0].replace('-NEW', '').replace('-', ' ')
                    alert_info = parts[1]

                    # Extract alert name and ID
                    if '[' in alert_info and ']' in alert_info:
                        name_part = alert_info.split('[')[0].strip()
                        id_part = alert_info.split('[')[1].split(']')[0]

                        alerts.append({
                            'risk': risk_level,
                            'name': name_part,
                            'id': id_part,
                            'confidence': 'Medium',  # Default
                            'description': f"Security issue detected: {name_part}",
                            'solution': 'Review and fix the identified security issue',
                            'instances': 1
                        })

        # Calculate security score based on risk levels
        risk_weights = {'WARN': 10, 'FAIL': 25}
        total_risk_score = sum(
            risk_weights.get(alert['risk'], 5)
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
            'summary': f"ZAP baseline scan completed. Found {len(alerts)} potential issues.",
            'raw_output': output[:1000]  # First 1000 chars of output
        }

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