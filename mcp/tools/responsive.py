"""
Responsive design audit tool.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

def responsive_audit(url: str, viewports: list[str] = None) -> dict[str, Any]:
    """
    Run responsive design audit across multiple viewports.

    Args:
        url: The URL to audit
        viewports: List of viewport sizes (e.g., ["360x640", "768x1024"])

    Returns:
        Dict containing responsive audit results and screenshots
    """
    try:
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")

        # Default viewports if none provided
        if viewports is None:
            viewports = ["360x640", "768x1024", "1280x800"]

        # Get path to Node script
        node_script = Path(__file__).parent.parent.parent / "node-tools" / "responsive.js"

        if not node_script.exists():
            raise FileNotFoundError(f"Node script not found: {node_script}")

        # Prepare command with viewports
        cmd = ["node", str(node_script), url] + viewports

        logger.info(f"Running responsive audit for {url} with viewports: {viewports}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            raise RuntimeError(f"Responsive audit failed: {result.stderr}")

        # Parse JSON output
        raw_data = json.loads(result.stdout)

        # Calculate overall responsive score
        summaries = raw_data.get('summaries', [])
        total_issues = sum(
            summary.get('overflowCount', 0) + summary.get('badTapTargets', 0)
            for summary in summaries
        )

        # Simple scoring: fewer issues = higher score
        responsive_score = max(0, 100 - (total_issues * 5))  # Deduct 5 points per issue

        return {
            'status': 'ok',
            'url': url,
            'viewports': viewports,
            'responsiveScore': round(responsive_score, 1),
            'summaries': summaries,
            'totalIssues': total_issues,
            'raw': raw_data
        }

    except subprocess.TimeoutExpired:
        return {
            'status': 'error',
            'error': 'Responsive audit timed out after 120 seconds'
        }
    except json.JSONDecodeError as e:
        return {
            'status': 'error',
            'error': f'Failed to parse responsive audit output: {e}'
        }
    except Exception as e:
        logger.error(f"Responsive audit failed: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }