from typing import List
from src.config import ALLOWED_ROLES

def check_access(user_role: str, allowed_roles: List[str]) -> bool:
    """Verifies if the current user's role is permitted to execute an action."""
    if user_role not in ALLOWED_ROLES:
        return False
    return user_role in allowed_roles

def require_role(user_role: str, required_roles: List[str]):
    """Throws a security exception if the user lacks the required role."""
    if not check_access(user_role, required_roles):
        raise PermissionError(f"Access Denied: Role '{user_role}' lacks permissions for this action. Required: {required_roles}")