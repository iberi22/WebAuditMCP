"""
Webhint scanning tool for web best practices.
"""

import json
import logging
import shutil
import subprocess
from typing import Any

logger = logging.getLogger(__name__)

def _check_webhint_available() -> dict[str, Any]:
    """Check if webhint is available and provide installation instructions."""
    # Check if npx is available
    if not shutil.which("npx"):
        return {
            "available": False,
            "error": "npx not found. Node.js is required.",
            "install_instructions": {
                "windows": "Download from https://nodejs.org or run: winget install OpenJS.NodeJS",
                "linux": "sudo apt install nodejs npm (Ubuntu/Debian) or brew install node (macOS)",
                "documentation": "https://nodejs.org/en/download/"
            }
        }

    # Try to check if hint is accessible
    try:
        result = subprocess.run(
            ["npx", "-y", "hint", "--version"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return {"available": True, "version": result.stdout.strip()}
    except Exception as e:
        logger.debug(f"Webhint check failed: {e}")

    return {
        "available": False,
        "error": "Webhint (hint) not available via npx",
        "install_instructions": {
            "quick_fix": "npx will auto-install hint on first run (requires internet)",
            "manual_install": "npm install -g hint",
            "note": "This tool uses 'npx -y hint' which auto-downloads hint if needed"
        }
    }

def webhint_scan(url: str) -> dict[str, Any]:
    """
    Run webhint scan on the specified URL.

    Args:
        url: The URL to scan

    Returns:
        Dict containing hints and raw webhint results
    """
    # Check dependencies first
    dependency_check = _check_webhint_available()
    if not dependency_check.get("available") and "npx not found" in dependency_check.get("error", ""):
        return {
            "status": "error",
            "error": dependency_check["error"],
            "install_instructions": dependency_check["install_instructions"],
            "tool": "webhint",
            "suggestion": "Please install Node.js to use webhint scans"
        }

    try:
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")

        # Run webhint
        cmd = ["npx", "-y", "hint", url, "--format=json"]

        logger.info(f"Running webhint scan for {url}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)

        # Webhint may return non-zero exit code even on successful scans with issues
        if result.returncode != 0 and not result.stdout:
            raise RuntimeError(f"Webhint failed: {result.stderr}")

        # Parse JSON output
        try:
            raw_data = json.loads(result.stdout)
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract from stderr or return basic info
            return {
                'status': 'error',
                'error': 'Failed to parse webhint output',
                'stderr': result.stderr,
                'stdout': result.stdout
            }

        # Normalize hints
        hints = []
        if isinstance(raw_data, list) and len(raw_data) > 0:
            for item in raw_data:
                if 'problems' in item:
                    for problem in item['problems']:
                        hints.append({
                            'hintId': problem.get('hintId'),
                            'severity': problem.get('severity'),
                            'message': problem.get('message'),
                            'resource': problem.get('resource'),
                            'location': problem.get('location')
                        })

        return {
            'status': 'ok',
            'url': url,
            'hints': hints,
            'hintsCount': len(hints),
            'raw': raw_data
        }

    except subprocess.TimeoutExpired:
        return {
            'status': 'error',
            'error': 'Webhint scan timed out after 90 seconds',
            'suggestion': 'Try scanning a simpler page or increase timeout'
        }
    except FileNotFoundError as e:
        dependency_check = _check_webhint_available()
        return {
            'status': 'error',
            'error': 'Webhint command not found',
            'details': str(e),
            'install_instructions': dependency_check.get('install_instructions', {}),
            'suggestion': 'Webhint will be auto-downloaded by npx on first run if Node.js is installed'
        }
    except Exception as e:
        logger.error(f"Webhint scan failed: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'tool': 'webhint',
            'suggestion': 'Check that the URL is accessible and Node.js is installed'
        }