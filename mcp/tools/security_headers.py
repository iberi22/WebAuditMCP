"""
Security headers analysis tool.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

def security_headers(url: str) -> dict[str, Any]:
    """
    Analyze security headers for the specified URL.

    Args:
        url: The URL to analyze

    Returns:
        Dict containing security header analysis
    """
    try:
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")

        # Get path to Node script
        node_script = Path(__file__).parent.parent.parent / "node-tools" / "security-headers.js"

        if not node_script.exists():
            raise FileNotFoundError(f"Node script not found: {node_script}")

        # Run security headers analysis via Node script
        cmd = ["node", str(node_script), url]

        logger.info(f"Running security headers analysis for {url}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            raise RuntimeError(f"Security headers analysis failed: {result.stderr}")

        # Parse JSON output
        raw_data = json.loads(result.stdout)

        # Extract security flags
        headers = raw_data.get('headers', {})

        security_analysis = {
            'csp': bool(headers.get('content-security-policy')),
            'hsts': bool(headers.get('strict-transport-security')),
            'xfo': bool(headers.get('x-frame-options')),
            'xcto': bool(headers.get('x-content-type-options')),
            'referrer': bool(headers.get('referrer-policy')),
            'permissions': bool(headers.get('permissions-policy') or headers.get('feature-policy'))
        }

        # Calculate security score (0-100)
        total_checks = len(security_analysis)
        passed_checks = sum(security_analysis.values())
        security_score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0

        return {
            'status': 'ok',
            'url': url,
            'securityScore': round(security_score, 1),
            'headers': security_analysis,
            'raw': raw_data
        }

    except subprocess.TimeoutExpired:
        return {
            'status': 'error',
            'error': 'Security headers analysis timed out after 30 seconds'
        }
    except json.JSONDecodeError as e:
        return {
            'status': 'error',
            'error': f'Failed to parse security headers output: {e}'
        }
    except Exception as e:
        logger.error(f"Security headers analysis failed: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }