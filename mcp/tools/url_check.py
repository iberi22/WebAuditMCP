"""
URL connectivity check tool
"""

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

def url_check(url: str) -> dict[str, Any]:
    """
    Check if a URL is reachable before running audits.

    Args:
        url: The URL to check

    Returns:
        Dict containing connectivity status and basic info
    """
    try:
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")

        logger.info(f"Checking connectivity to {url}")

        # Quick HEAD request with short timeout
        response = requests.head(url, timeout=5, allow_redirects=True)

        return {
            'status': 'ok',
            'url': url,
            'reachable': True,
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'final_url': response.url,
            'message': f"Server is reachable (HTTP {response.status_code})"
        }

    except requests.exceptions.ConnectionError:
        return {
            'status': 'error',
            'url': url,
            'reachable': False,
            'error': 'Connection refused - server not running',
            'suggestion': 'Start your development server first',
            'common_commands': [
                'npm run dev',
                'yarn dev',
                'npm start',
                'python manage.py runserver',
                'php -S localhost:3000'
            ]
        }
    except requests.exceptions.Timeout:
        return {
            'status': 'error',
            'url': url,
            'reachable': False,
            'error': 'Connection timeout - server too slow',
            'suggestion': 'Check if server is overloaded or use a different URL'
        }
    except Exception as e:
        logger.error(f"URL check failed: {e}")
        return {
            'status': 'error',
            'url': url,
            'reachable': False,
            'error': str(e),
            'suggestion': 'Verify the URL is correct and accessible'
        }