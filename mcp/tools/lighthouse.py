"""
Lighthouse audit tool for performance, SEO, accessibility, and best practices.
"""

import json
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Literal

logger = logging.getLogger(__name__)

def _check_lighthouse_available() -> dict[str, Any]:
    """Check if Lighthouse is available and provide installation instructions."""
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

    # Try to run lighthouse to check if it's accessible
    try:
        result = subprocess.run(
            ["npx", "-y", "lighthouse", "--version"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return {"available": True, "version": result.stdout.strip()}
    except Exception as e:
        logger.debug(f"Lighthouse check failed: {e}")

    return {
        "available": False,
        "error": "Lighthouse not available via npx",
        "install_instructions": {
            "quick_fix": "npx will auto-install lighthouse on first run (requires internet)",
            "manual_install": "npm install -g lighthouse",
            "note": "This tool uses 'npx -y lighthouse' which auto-downloads lighthouse if needed"
        }
    }

def audit_lighthouse(url: str, device: Literal["mobile", "desktop"] = "mobile") -> dict[str, Any]:
    """
    Run Lighthouse audit on the specified URL.

    Args:
        url: The URL to audit
        device: Device preset (mobile or desktop)

    Returns:
        Dict containing categoryScores, audits, and raw Lighthouse JSON
    """
    # Check dependencies first
    dependency_check = _check_lighthouse_available()
    if not dependency_check.get("available") and "npx not found" in dependency_check.get("error", ""):
        return {
            "status": "error",
            "error": dependency_check["error"],
            "install_instructions": dependency_check["install_instructions"],
            "tool": "lighthouse",
            "suggestion": "Please install Node.js to use Lighthouse audits"
        }

    try:
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")

        # For localhost URLs, add helpful message
        is_localhost = 'localhost' in url or '127.0.0.1' in url
        if is_localhost:
            logger.info(f"Auditing localhost URL: {url}")
            logger.info("Make sure your development server is running")

        # Set preset based on device
        preset = "mobile" if device == "mobile" else "desktop"

        # Create temporary file for output
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            # Chrome flags to avoid localhost warnings and interstitials
            chrome_flags = [
                "--headless",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-background-networking",
                "--disable-default-apps",
                "--disable-extensions",
                "--disable-sync",
                "--metrics-recording-only",
                "--disable-features=Translate",
                "--safebrowsing-disable-download-protection",
                "--safebrowsing-disable-extension-blacklist",
                "--ignore-certificate-errors",
                "--allow-insecure-localhost"
            ]

            # Run Lighthouse
            cmd = [
                "npx", "-y", "lighthouse", url,
                f"--preset={preset}",
                "--output=json",
                f"--output-path={tmp_path}",
                "--quiet",
                f"--chrome-flags={' '.join(chrome_flags)}"
            ]

            logger.info(f"Running Lighthouse audit for {url} with {device} preset")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode != 0:
                error_msg = result.stderr.strip()

                # Check for common issues
                if "ECONNREFUSED" in error_msg or "ERR_CONNECTION_REFUSED" in error_msg:
                    return {
                        "status": "error",
                        "error": "Connection refused - server not reachable",
                        "url": url,
                        "suggestion": "Make sure your development server is running. For localhost, start your app first.",
                        "details": error_msg
                    }
                elif "interstitial" in error_msg.lower():
                    return {
                        "status": "error",
                        "error": "Chrome interstitial detected (warning page)",
                        "url": url,
                        "suggestion": "This usually happens with localhost URLs. Try using a different URL or check Chrome flags.",
                        "details": error_msg,
                        "note": "The audit includes --ignore-certificate-errors and --allow-insecure-localhost flags to avoid this"
                    }

                raise RuntimeError(f"Lighthouse failed: {error_msg}")

            # Read and parse results
            with open(tmp_path) as f:
                raw_data = json.load(f)

            # Extract category scores
            categories = raw_data.get('categories', {})
            category_scores = {
                'performance': categories.get('performance', {}).get('score', 0) * 100 if categories.get('performance', {}).get('score') else 0,
                'accessibility': categories.get('accessibility', {}).get('score', 0) * 100 if categories.get('accessibility', {}).get('score') else 0,
                'seo': categories.get('seo', {}).get('score', 0) * 100 if categories.get('seo', {}).get('score') else 0,
                'bestPractices': categories.get('best-practices', {}).get('score', 0) * 100 if categories.get('best-practices', {}).get('score') else 0
            }

            # Extract key audits
            audits = raw_data.get('audits', {})
            key_audits = {
                'first-contentful-paint': audits.get('first-contentful-paint', {}),
                'largest-contentful-paint': audits.get('largest-contentful-paint', {}),
                'cumulative-layout-shift': audits.get('cumulative-layout-shift', {}),
                'total-blocking-time': audits.get('total-blocking-time', {}),
                'speed-index': audits.get('speed-index', {})
            }

            return {
                'status': 'ok',
                'url': url,
                'device': device,
                'categoryScores': category_scores,
                'audits': key_audits,
                'raw': raw_data
            }

        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)

    except subprocess.TimeoutExpired:
        return {
            'status': 'error',
            'error': 'Lighthouse audit timed out after 120 seconds',
            'suggestion': 'Try auditing a simpler page or increase timeout'
        }
    except FileNotFoundError as e:
        dependency_check = _check_lighthouse_available()
        return {
            'status': 'error',
            'error': 'Lighthouse command not found',
            'details': str(e),
            'install_instructions': dependency_check.get('install_instructions', {}),
            'suggestion': 'Lighthouse will be auto-downloaded by npx on first run if Node.js is installed'
        }
    except Exception as e:
        logger.error(f"Lighthouse audit failed: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'tool': 'lighthouse',
            'suggestion': 'Check that the URL is accessible and Node.js is installed'
        }