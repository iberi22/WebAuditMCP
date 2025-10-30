"""
Quick audit tool - combines fast tools for immediate feedback
"""

import logging
from typing import Any

from .responsive import responsive_audit
from .security_headers import security_headers

logger = logging.getLogger(__name__)

def quick_audit(url: str, include_responsive: bool = True) -> dict[str, Any]:
    """
    Run a quick audit using fast tools only.

    Args:
        url: The URL to audit
        include_responsive: Whether to include responsive audit (slower)

    Returns:
        Dict containing results from multiple fast tools
    """
    try:
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")

        results = {
            'status': 'ok',
            'url': url,
            'timestamp': None,
            'tools_used': [],
            'results': {}
        }

        # Security headers (very fast)
        logger.info(f"Running security headers check for {url}")
        security_result = security_headers(url)
        results['results']['security_headers'] = security_result
        results['tools_used'].append('security_headers')

        # Responsive audit (moderate speed)
        if include_responsive:
            logger.info(f"Running responsive audit for {url}")
            responsive_result = responsive_audit(url, ["375x667", "1024x768"])
            results['results']['responsive'] = responsive_result
            results['tools_used'].append('responsive_audit')

        # Summary
        security_ok = security_result.get('status') == 'ok'
        responsive_ok = responsive_result.get('status') == 'ok' if include_responsive else True

        results['summary'] = {
            'overall_status': 'ok' if (security_ok and responsive_ok) else 'warning',
            'security_headers_found': len(security_result.get('headers', {})) if security_ok else 0,
            'responsive_issues': len(responsive_result.get('issues', [])) if include_responsive and responsive_ok else 0
        }

        return results

    except Exception as e:
        logger.error(f"Quick audit failed: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'tool': 'quick_audit',
            'suggestion': 'Try individual tools: security_headers or responsive_audit'
        }