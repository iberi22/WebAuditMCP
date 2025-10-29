"""
Axe accessibility scanning using Playwright.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Literal

logger = logging.getLogger(__name__)

def scan_axe(url: str, device: Literal["mobile", "desktop"] = "mobile") -> dict[str, Any]:
    """
    Run axe accessibility scan using Playwright.

    Args:
        url: The URL to scan
        device: Device type for viewport simulation

    Returns:
        Dict containing violations, passes, incomplete, and raw axe results
    """
    try:
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")

        # Get path to Node script
        node_script = Path(__file__).parent.parent.parent / "node-tools" / "axe-playwright.js"

        if not node_script.exists():
            raise FileNotFoundError(f"Node script not found: {node_script}")

        # Run axe scan via Node script
        cmd = ["node", str(node_script), url, device]

        logger.info(f"Running axe scan for {url} with {device} device")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            raise RuntimeError(f"Axe scan failed: {result.stderr}")

        # Parse JSON output
        raw_data = json.loads(result.stdout)

        # Normalize violations
        violations = []
        for violation in raw_data.get('violations', []):
            violations.append({
                'id': violation.get('id'),
                'impact': violation.get('impact'),
                'description': violation.get('description'),
                'help': violation.get('help'),
                'helpUrl': violation.get('helpUrl'),
                'nodes': len(violation.get('nodes', [])),
                'tags': violation.get('tags', [])
            })

        # Count passes and incomplete
        passes_count = len(raw_data.get('passes', []))
        incomplete_count = len(raw_data.get('incomplete', []))

        return {
            'status': 'ok',
            'url': url,
            'device': device,
            'violations': violations,
            'violationsCount': len(violations),
            'passesCount': passes_count,
            'incompleteCount': incomplete_count,
            'raw': raw_data
        }

    except subprocess.TimeoutExpired:
        return {
            'status': 'error',
            'error': 'Axe scan timed out after 60 seconds'
        }
    except json.JSONDecodeError as e:
        return {
            'status': 'error',
            'error': f'Failed to parse axe output: {e}'
        }
    except Exception as e:
        logger.error(f"Axe scan failed: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }