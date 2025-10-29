"""
Test credentials management for MCP Auditor.
Loads and manages test user credentials for automated testing.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TestUser:
    """Test user credentials."""
    username: str
    password: str
    email: str
    role: str = "user"


class CredentialsManager:
    """Manages test credentials from environment variables."""

    def __init__(self):
        self.users: Dict[str, TestUser] = {}
        self._load_credentials()

    def _load_credentials(self):
        """Load test credentials from environment variables."""
        # Basic test user
        self.users['basic'] = TestUser(
            username=os.getenv('TEST_USERNAME', 'testuser'),
            password=os.getenv('TEST_PASSWORD', 'testpass123'),
            email=os.getenv('TEST_EMAIL', 'test@example.com'),
            role='user'
        )

        # Admin test user
        self.users['admin'] = TestUser(
            username=os.getenv('TEST_ADMIN_USERNAME', 'admin'),
            password=os.getenv('TEST_ADMIN_PASSWORD', 'admin123'),
            email=os.getenv('TEST_ADMIN_EMAIL', 'admin@example.com'),
            role='admin'
        )

        # Student test user (for CGP Sanpatricio)
        self.users['student'] = TestUser(
            username=os.getenv('TEST_STUDENT_USERNAME', 'estudiante.prueba'),
            password=os.getenv('TEST_STUDENT_PASSWORD', 'estudiante123'),
            email=os.getenv('TEST_STUDENT_EMAIL', 'estudiante@cgpsanpatricio.com'),
            role='student'
        )

        # Parent test user (for CGP Sanpatricio)
        self.users['parent'] = TestUser(
            username=os.getenv('TEST_PARENT_USERNAME', 'padre.prueba'),
            password=os.getenv('TEST_PARENT_PASSWORD', 'padre123'),
            email=os.getenv('TEST_PARENT_EMAIL', 'padre@cgpsanpatricio.com'),
            role='parent'
        )

        logger.info(f"Loaded {len(self.users)} test user profiles")

    def get_user(self, role: str = 'basic') -> Optional[TestUser]:
        """Get test user by role."""
        return self.users.get(role)

    def get_credentials(self, role: str = 'basic') -> Dict[str, str]:
        """Get credentials as dictionary."""
        user = self.get_user(role)
        if not user:
            logger.warning(f"Test user role '{role}' not found, using basic")
            user = self.users['basic']

        return {
            'username': user.username,
            'password': user.password,
            'email': user.email,
            'role': user.role
        }

    def list_available_roles(self) -> list[str]:
        """List all available test user roles."""
        return list(self.users.keys())

    def get_login_payload(self, role: str = 'basic',
                         username_field: str = 'username',
                         password_field: str = 'password') -> Dict[str, str]:
        """
        Get login payload for form submission.

        Args:
            role: User role to use
            username_field: Name of username field in form
            password_field: Name of password field in form

        Returns:
            Dictionary with form field names and values
        """
        user = self.get_user(role)
        if not user:
            user = self.users['basic']

        return {
            username_field: user.username,
            password_field: user.password
        }


# Global credentials manager instance
_credentials_manager: Optional[CredentialsManager] = None


def get_credentials_manager() -> CredentialsManager:
    """Get singleton instance of credentials manager."""
    global _credentials_manager
    if _credentials_manager is None:
        _credentials_manager = CredentialsManager()
    return _credentials_manager


def get_test_credentials(role: str = 'basic') -> Dict[str, str]:
    """
    Convenience function to get test credentials.

    Args:
        role: User role ('basic', 'admin', 'student', 'parent')

    Returns:
        Dictionary with username, password, email, and role
    """
    return get_credentials_manager().get_credentials(role)


def prompt_for_credentials(message: str = "Select test user role") -> Dict[str, str]:
    """
    Prompt user to select test credentials.
    For use in interactive tools.

    Args:
        message: Prompt message

    Returns:
        Selected credentials
    """
    manager = get_credentials_manager()
    roles = manager.list_available_roles()

    print(f"\n{message}:")
    for i, role in enumerate(roles, 1):
        user = manager.get_user(role)
        print(f"  {i}. {role.upper()}: {user.username} ({user.email})")

    while True:
        try:
            choice = input(f"\nEnter choice (1-{len(roles)}) or role name: ").strip()

            # Try numeric choice
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(roles):
                    selected_role = roles[idx]
                    break
            # Try role name
            elif choice.lower() in roles:
                selected_role = choice.lower()
                break

            print(f"Invalid choice. Please enter 1-{len(roles)} or role name.")
        except (ValueError, KeyError):
            print(f"Invalid input. Please try again.")

    creds = manager.get_credentials(selected_role)
    print(f"\n✅ Selected: {selected_role.upper()} - {creds['username']}")
    return creds
