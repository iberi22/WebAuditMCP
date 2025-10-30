"""
Automated login helper for web applications.
Handles authentication flows with test credentials.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any

from playwright.async_api import async_playwright

from .credentials import get_test_credentials

logger = logging.getLogger(__name__)


async def login_with_playwright(
    url: str,
    role: str = 'basic',
    username_selector: str = '#username',
    password_selector: str = '#password',
    submit_selector: str = 'button[type="submit"]',
    success_selector: str = '.dashboard',
    headless: bool = True,
    screenshot_path: str | None = None
) -> dict[str, Any]:
    """
    Perform automated login using Playwright.

    Args:
        url: Login page URL
        role: Test user role to use
        username_selector: CSS selector for username field
        password_selector: CSS selector for password field
        submit_selector: CSS selector for submit button
        success_selector: CSS selector to verify successful login
        headless: Run browser in headless mode
        screenshot_path: Optional path to save screenshot after login

    Returns:
        Dictionary with login result and details
    """
    try:
        # Get test credentials
        creds = get_test_credentials(role)
        logger.info(f"Attempting login as {creds['username']} ({creds['role']})")

        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=headless)
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='MCP-Auditor/1.0'
            )
            page = await context.new_page()

            # Navigate to login page
            await page.goto(url, wait_until='networkidle')

            # Fill credentials
            await page.fill(username_selector, creds['username'])
            await page.fill(password_selector, creds['password'])

            # Submit form
            await page.click(submit_selector)

            # Wait for navigation or success indicator
            try:
                await page.wait_for_selector(success_selector, timeout=10000)
                login_success = True
                message = f"Login successful as {creds['username']}"
            except Exception as e:
                login_success = False
                message = f"Login may have failed: {str(e)}"

            # Take screenshot if requested
            screenshot_data = None
            if screenshot_path or not login_success:
                artifacts_dir = Path(__file__).parent.parent.parent / "artifacts"
                artifacts_dir.mkdir(exist_ok=True)

                if not screenshot_path:
                    import time
                    screenshot_path = str(artifacts_dir / f"login-{role}-{int(time.time())}.png")

                await page.screenshot(path=screenshot_path, full_page=True)
                screenshot_data = screenshot_path

            # Get current URL and title
            current_url = page.url
            title = await page.title()

            # Get cookies for session persistence
            cookies = await context.cookies()

            await browser.close()

            return {
                'status': 'ok' if login_success else 'warning',
                'success': login_success,
                'message': message,
                'credentials_used': {
                    'username': creds['username'],
                    'role': creds['role']
                },
                'current_url': current_url,
                'page_title': title,
                'screenshot': screenshot_data,
                'cookies': cookies,
                'session_ready': login_success
            }

    except Exception as e:
        logger.error(f"Login automation failed: {e}")
        return {
            'status': 'error',
            'success': False,
            'error': str(e)
        }


def auto_login(
    url: str,
    role: str = 'basic',
    username_selector: str = '#username',
    password_selector: str = '#password',
    submit_selector: str = 'button[type="submit"]',
    success_selector: str = '.dashboard',
    headless: bool = True
) -> dict[str, Any]:
    """
    Synchronous wrapper for automated login.

    Args:
        url: Login page URL
        role: Test user role ('basic', 'admin', 'student', 'parent')
        username_selector: CSS selector for username field
        password_selector: CSS selector for password field
        submit_selector: CSS selector for submit button
        success_selector: CSS selector to verify login success
        headless: Run browser in headless mode

    Returns:
        Dictionary with login result
    """
    return asyncio.run(login_with_playwright(
        url=url,
        role=role,
        username_selector=username_selector,
        password_selector=password_selector,
        submit_selector=submit_selector,
        success_selector=success_selector,
        headless=headless
    ))


def get_available_test_users() -> dict[str, Any]:
    """
    Get information about available test users.

    Returns:
        Dictionary with available roles and their details
    """
    from .credentials import get_credentials_manager

    manager = get_credentials_manager()
    roles = manager.list_available_roles()

    users_info = {}
    for role in roles:
        user = manager.get_user(role)
        users_info[role] = {
            'username': user.username,
            'email': user.email,
            'role': user.role
        }

    return {
        'status': 'ok',
        'available_roles': roles,
        'users': users_info,
        'usage': 'Call auto_login with role parameter: basic, admin, student, or parent'
    }
