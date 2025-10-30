"""
Fast Lighthouse audit - optimized for development and quick feedback
"""

import json
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Literal

logger = logging.getLogger(__name__)

def lighthouse_fast(url: str, device: Literal["mobile", "desktop"] = "mobile") -> dict[str, Any]:
    """
    Run ultra-fast Lighthouse audit with minimal audits.

    Args:
        url: The URL to audit
        device: Device preset (mobile or desktop)

    Returns:
        Dict containing basic performance metrics only
    """
    try:
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")

        # Check for lighthouse command (prefer global installation)
        lighthouse_cmd = shutil.which("lighthouse.cmd") if os.name == "nt" else shutil.which("lighthouse")
        if lighthouse_cmd:
            use_direct = True
        else:
            # Fallback to npx
            npx_cmd = shutil.which("npx.cmd") if os.name == "nt" else shutil.which("npx")
            if not npx_cmd:
                return {
                    "status": "error",
                    "error": "Neither lighthouse nor npx found",
                    "suggestion": "Install lighthouse globally: npm install -g lighthouse"
                }
            use_direct = False

        is_localhost = 'localhost' in url or '127.0.0.1' in url

        # Create temporary file for output
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            # Ultra-minimal Chrome flags for maximum speed
            chrome_flags = [
                "--headless",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--disable-extensions",
                "--disable-sync",
                "--disable-default-apps",
                "--ignore-certificate-errors" if is_localhost else ""
            ]
            chrome_flags = [f for f in chrome_flags if f]  # Remove empty strings

            # Minimal Lighthouse command for speed
            if use_direct:
                cmd = [lighthouse_cmd, url]
            else:
                cmd = [npx_cmd, "-y", "lighthouse", url]

            cmd += [
                "--output=json",
                f"--output-path={tmp_path}",
                "--quiet",
                "--only-categories=performance",
                "--throttling-method=provided",
                "--disable-storage-reset",
                "--skip-audits=screenshot-thumbnails,final-screenshot,full-page-screenshot",
                f"--chrome-flags={' '.join(chrome_flags)}"
            ]

            if device == "desktop":
                cmd.append("--preset=desktop")

            logger.info(f"Running fast Lighthouse audit for {url}")
            timeout = 45 if is_localhost else 60
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

            if result.returncode != 0:
                error_msg = result.stderr.strip()

                if "ECONNREFUSED" in error_msg:
                    return {
                        "status": "error",
                        "error": "Connection refused - server not reachable",
                        "url": url,
                        "suggestion": "Make sure your development server is running"
                    }

                raise RuntimeError(f"Lighthouse failed: {error_msg}")

            # Read and parse results
            with open(tmp_path) as f:
                raw_data = json.load(f)

            # Extract only performance metrics
            categories = raw_data.get('categories', {})
            performance = categories.get('performance', {})

            audits = raw_data.get('audits', {})

            return {
                'status': 'ok',
                'url': url,
                'device': device,
                'mode': 'fast',
                'performance_score': performance.get('score', 0) * 100 if performance.get('score') else 0,
                'metrics': {
                    'first_contentful_paint': audits.get('first-contentful-paint', {}).get('displayValue', 'N/A'),
                    'largest_contentful_paint': audits.get('largest-contentful-paint', {}).get('displayValue', 'N/A'),
                    'speed_index': audits.get('speed-index', {}).get('displayValue', 'N/A'),
                    'total_blocking_time': audits.get('total-blocking-time', {}).get('displayValue', 'N/A'),
                    'cumulative_layout_shift': audits.get('cumulative-layout-shift', {}).get('displayValue', 'N/A')
                },
                'note': 'Fast mode - performance only, limited audits for speed'
            }

        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)

    except subprocess.TimeoutExpired:
        timeout_msg = f"Fast Lighthouse audit timed out after {45 if is_localhost else 60} seconds"
        return {
            'status': 'error',
            'error': timeout_msg,
            'url': url,
            'suggestion': 'Try security_headers or responsive_audit instead'
        }
    except Exception as e:
        logger.error(f"Fast Lighthouse audit failed: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'tool': 'lighthouse_fast',
            'suggestion': 'Try security_headers for immediate results'
        }