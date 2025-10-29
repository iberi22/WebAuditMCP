"""
Security headers analysis tool.
"""

import json
import logging
import re
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
            error_info = _parse_error_output(result)

            # Handle common network errors gracefully
            error_message = error_info.get("error_message", "Security headers analysis failed")
            if _is_connection_refused(error_message):
                logger.warning(f"Security headers analysis connection refused for {url}")
                return {
                    'status': 'error',
                    'error': 'Connection refused - server not reachable',
                    'url': url,
                    'code': 'CONNECTION_REFUSED',
                    'suggestion': (
                        "Make sure your development server is running and reachable at the given URL. "
                        "If it runs on a different port, pass the correct URL."
                    ),
                    'details': error_info.get("details")
                }

            raise RuntimeError(f"Security headers analysis failed: {error_message}")

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


def _parse_error_output(result: subprocess.CompletedProcess) -> dict[str, Any]:
    """Parse stderr/stdout from the Node script into a structured error."""
    raw_stderr = (result.stderr or "").strip()
    raw_stdout = (result.stdout or "").strip()

    payload = raw_stderr or raw_stdout
    parsed: dict[str, Any] = {}

    if payload:
        try:
            parsed_json = json.loads(payload)
            if isinstance(parsed_json, dict):
                parsed = parsed_json
        except json.JSONDecodeError:
            # Some tools include ANSI codes; strip them for readability
            cleaned = _strip_ansi(payload)
            parsed = {"error": cleaned}

    error_message = parsed.get("error") if isinstance(parsed, dict) else None

    if not error_message and payload:
        error_message = _strip_ansi(payload)

    details: dict[str, Any] = {}
    if isinstance(parsed, dict):
        details = parsed

    return {
        "error_message": error_message or "Unknown error",
        "details": details or None
    }


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from error output."""
    ansi_escape = re.compile(r'\x1B\[[0-9;]*[mK]')
    return ansi_escape.sub('', text)


def _is_connection_refused(message: str | None) -> bool:
    """Detect connection refused errors in error messages."""
    if not message:
        return False

    patterns = [
        "ERR_CONNECTION_REFUSED",
        "ECONNREFUSED",
        "Connection refused",
        "net::ERR_CONNECTION_REFUSED"
    ]
    return any(pattern.lower() in message.lower() for pattern in patterns)
