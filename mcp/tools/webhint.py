"""
Webhint scanning tool for web best practices.
"""

import json
import logging
import os
import shutil
import subprocess
from typing import Any

logger = logging.getLogger(__name__)

def _resolve_npx_command() -> str | None:
    """Return platform-appropriate npx executable path."""
    candidates = ["npx"]
    if os.name == "nt":
        candidates = ["npx.cmd", "npx"]

    for candidate in candidates:
        path = shutil.which(candidate)
        if path:
            return path
    return None


def _resolve_webhint_runner() -> tuple[list[str], bool] | None:
    """Resolve executable for running webhint."""
    hint_cmd = shutil.which("hint.cmd") if os.name == "nt" else shutil.which("hint")
    if hint_cmd:
        return ([hint_cmd], False)

    npx_cmd = _resolve_npx_command()
    if npx_cmd:
        return ([npx_cmd, "-y", "hint"], True)

    return None


def _check_webhint_available() -> dict[str, Any]:
    """Check if webhint is available and provide installation instructions."""
    runner = _resolve_webhint_runner()
    if not runner:
        return {
            "available": False,
            "error": "webhint executable not found. Node.js is required.",
            "install_instructions": {
                "windows": "Download from https://nodejs.org or run: winget install OpenJS.NodeJS",
                "linux": "sudo apt install nodejs npm (Ubuntu/Debian) or brew install node (macOS)",
                "documentation": "https://nodejs.org/en/download/"
            }
        }

    # Try to check if hint is accessible
    try:
        base_cmd, uses_npx = runner
        version_cmd = base_cmd + (["--", "--version"] if uses_npx else ["--version"])
        result = subprocess.run(
            version_cmd,
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
        "error": "Webhint CLI (hint) is not accessible from PATH",
        "install_instructions": {
            "quick_fix": "Install globally with: npm install -g hint",
            "manual_install": "npm install -g hint",
            "note": "Alternatively ensure npx is available to download hint on demand"
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
    if not dependency_check.get("available"):
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
        runner = _resolve_webhint_runner()
        if not runner:
            raise FileNotFoundError("webhint executable not found in PATH")

        base_cmd, uses_npx = runner
        cmd = base_cmd.copy()
        if uses_npx:
            cmd.append("--")

        cmd += [url, "--formatters", "json"]

        logger.info(f"Running webhint scan for {url}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)

        # Webhint may return non-zero exit code even on successful scans with issues
        if result.returncode != 0 and not result.stdout:
            raise RuntimeError(f"Webhint failed: {result.stderr}")

        # Parse JSON output
        try:
            raw_data = json.loads(result.stdout)
        except json.JSONDecodeError:
            # Attempt to extract JSON arrays from mixed CLI output
            extracted = _extract_webhint_results(result.stdout)
            if not extracted:
                return {
                    'status': 'error',
                    'error': 'Failed to parse webhint output',
                    'stderr': result.stderr,
                    'stdout': result.stdout
                }
            raw_data = extracted

        # Normalize hints
        hints = []
        if isinstance(raw_data, list) and len(raw_data) > 0:
            for item in raw_data:
                if not isinstance(item, dict):
                    continue
                if 'problems' in item:
                    for problem in item['problems']:
                        hints.append({
                            'hintId': problem.get('hintId'),
                            'severity': problem.get('severity'),
                            'message': problem.get('message'),
                            'resource': problem.get('resource'),
                            'location': problem.get('location')
                        })
                elif 'hintId' in item:
                    hints.append({
                        'hintId': item.get('hintId'),
                        'severity': item.get('severity'),
                        'message': item.get('message'),
                        'resource': item.get('resource'),
                        'location': item.get('location')
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


def _extract_webhint_results(stdout: str) -> list[dict[str, Any]] | None:
    """Extract JSON objects from the mixed stdout generated by webhint."""
    decoder = json.JSONDecoder()
    index = 0
    collected: list[dict[str, Any]] = []

    while True:
        start = stdout.find('[', index)
        if start == -1:
            break

        try:
            obj, offset = decoder.raw_decode(stdout[start:])
        except json.JSONDecodeError:
            index = start + 1
            continue

        index = start + offset

        if isinstance(obj, list):
            for entry in obj:
                if isinstance(entry, dict):
                    collected.append(entry)
        elif isinstance(obj, dict):
            collected.append(obj)

    return collected or None
