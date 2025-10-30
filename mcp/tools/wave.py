"""
WAVE API integration with asyncio fix.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import httpx

logger = logging.getLogger(__name__)


def scan_wave(
    url: str,
    report_type: Literal["json", "html"] = "json",
    api_options: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Run a WAVE accessibility scan for the provided URL.

    Args:
        url: Target URL to audit. Must include http:// or https://.
        report_type: Desired output type. The API currently returns JSON which is saved to disk.
        api_options: Optional dictionary with additional query parameters supported by WAVE.

    Returns:
        Dictionary with status, accessibility summary, and path to the raw WAVE report.
    """
    try:
        api_key = os.getenv("WAVE_API_KEY")
        if not api_key:
            return {
                'status': 'error',
                'error': 'WAVE_API_KEY required (try the scan_axe tool for accessibility checks without the API key)'
            }

        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")

        api_base = os.getenv("WAVE_API_BASE", "https://wave.webaim.org/api")

        if api_options is None:
            api_options = {}

        try:
            asyncio.get_running_loop()
            logger.info("Using sync HTTP client")
            return _run_sync(url, report_type, api_options, api_key, api_base)
        except RuntimeError:
            return asyncio.run(_run_async(url, report_type, api_options, api_key, api_base))

    except Exception as e:
        logger.error(f"WAVE scan failed: {e}")
        return {'status': 'error', 'error': str(e)}


def _run_sync(url: str, report_type: str, api_options: dict, api_key: str, api_base: str) -> dict:
    params = {'key': api_key, 'url': url, 'format': 'json', **api_options}
    with httpx.Client(timeout=120.0) as client:
        response = client.get(f"{api_base}/request", params=params)
        response.raise_for_status()
        return _process(response.json(), url, report_type)


async def _run_async(url: str, report_type: str, api_options: dict, api_key: str, api_base: str) -> dict:
    params = {'key': api_key, 'url': url, 'format': 'json', **api_options}
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.get(f"{api_base}/request", params=params)
        response.raise_for_status()
        return _process(response.json(), url, report_type)


def _process(raw_data: dict, url: str, report_type: str) -> dict:
    categories = raw_data.get('categories', {})

    errors = categories.get('error', {}).get('count', 0)
    alerts = categories.get('alert', {}).get('count', 0)

    score = max(0, 100 - ((errors + alerts) / 50 * 100))

    artifacts_dir = Path(__file__).parent.parent.parent / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = artifacts_dir / f"wave-{timestamp}.json"

    with open(report_path, 'w') as f:
        json.dump(raw_data, f, indent=2)

    return {
        'status': 'ok',
        'url': url,
        'score': round(score, 1),
        'summary': {
            'errors': errors,
            'alerts': alerts,
            'features': categories.get('feature', {}).get('count', 0)
        },
        'report_path': str(report_path)
    }
