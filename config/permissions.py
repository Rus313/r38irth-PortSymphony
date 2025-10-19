"""
Permissions Module
Defines role-based access control (RBAC)
"""

from enum import Enum
from typing import Set, List
import logging

logger = logging.getLogger(__name__)


class Permission(Enum):
    """
    All possible permissions in the system
    Think of these as keys to different rooms
    """
    # View permissions
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_VESSELS = "view_vessels"
    VIEW_ANALYTICS = "view_analytics"
    VIEW_SUSTAINABILITY = "view_sustainability"
    VIEW_BERTH_MANAGEMENT = "view_berth_management"
    
    # Data permissions
    EXPORT_DATA = "export_data"
    IMPORT_DATA = "import_data"
    
    # Management permissions
    MANAGE_USERS = "manage_users"
    MODIFY_DATA = "modify_data"
    DELETE_DATA = "delete_data"
    
    # Admin permissions
    SYSTEM_SETTINGS = "system_settings"
    VIEW_LOGS = "view_logs"
    MANAGE_API_KEYS = "manage_api_keys"


class Role(Enum):
    """User roles"""
    VIEWER = "viewer"
    USER = "user"
    OPERATIONS = "operations"
    SUSTAINABILITY = "sustainability"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


# Define what each role can do
ROLE_PERMISSIONS = {
    Role.VIEWER: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_VESSELS,
    },
    
    Role.USER: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_VESSELS,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_DATA,
    },
    
    Role.OPERATIONS: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_VESSELS,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_BERTH_MANAGEMENT,
        Permission.EXPORT_DATA,
        Permission.MODIFY_DATA,
    },
    
    Role.SUSTAINABILITY: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_VESSELS,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_SUSTAINABILITY,
        Permission.EXPORT_DATA,
    },
    
    Role.ADMIN: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_VESSELS,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_SUSTAINABILITY,
        Permission.VIEW_BERTH_MANAGEMENT,
        Permission.EXPORT_DATA,
        Permission.IMPORT_DATA,
        Permission.MODIFY_DATA,
        Permission.DELETE_DATA,
        Permission.MANAGE_USERS,
        Permission.VIEW_LOGS,
    },
    
    Role.SUPERADMIN: set(Permission),  # All permissions
}


class PermissionChecker:
    """
    Checks if a user has permission to do something
    """
    
    @staticmethod
    def has_permission(user_role: str, required_permission: Permission) -> bool:
        """
        Check if user role has the required permission
        
        Args:
            user_role: User's role (string)
            required_permission: Permission to check
        
        Returns:
            True if user has permission, False otherwise
        """
        try:
            # Convert string to Role enum
            role = Role(user_role.lower())
        except ValueError:
            logger.warning(f"Invalid role: {user_role}")
            return False
        
        # Get permissions for this role
        role_perms = ROLE_PERMISSIONS.get(role, set())
        
        # Check if permission is in the set
        return required_permission in role_perms
    
    @staticmethod
    def get_user_permissions(user_role: str) -> Set[Permission]:
        """
        Get all permissions for a user role
        """
        try:
            role = Role(user_role.lower())
            return ROLE_PERMISSIONS.get(role, set())
        except ValueError:
            return set()
    
    @staticmethod
    def require_permission(user_role: str, required_permission: Permission):
        """
        Require a permission or stop execution
        Use this at the top of protected functions
        """
        import streamlit as st
        
        if not PermissionChecker.has_permission(user_role, required_permission):
            st.error(f"⛔ You don't have permission: {required_permission.value}")
            logger.warning(f"Permission denied: {user_role} tried to access {required_permission.value}")
            st.stop()


# Quick helper functions
def has_permission(required_permission: Permission) -> bool:
    """
    Check if current user has permission
    """
    import streamlit as st
    user_role = st.session_state.get('user_role', 'viewer')
    return PermissionChecker.has_permission(user_role, required_permission)


def require_permission(required_permission: Permission):
    """
    Require permission or stop
    """
    import streamlit as st
    user_role = st.session_state.get('user_role', 'viewer')
    PermissionChecker.require_permission(user_role, required_permission)