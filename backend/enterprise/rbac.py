"""
Role-Based Access Control (RBAC) system for AI UI Builder
Manages user roles, permissions, and access control
"""

from typing import Dict, List, Set, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import json
from ..security.audit_logger import audit_logger, AuditEventType, AuditSeverity

class Permission(Enum):
    """System permissions"""
    # UI Generation
    GENERATE_UI = "generate_ui"
    VIEW_GENERATED_UI = "view_generated_ui"
    EDIT_GENERATED_UI = "edit_generated_ui"
    DELETE_GENERATED_UI = "delete_generated_ui"
    
    # Deployment
    DEPLOY_UI = "deploy_ui"
    VIEW_DEPLOYMENTS = "view_deployments"
    MANAGE_DEPLOYMENTS = "manage_deployments"
    
    # API Keys
    MANAGE_API_KEYS = "manage_api_keys"
    VIEW_API_KEYS = "view_api_keys"
    
    # User Management
    CREATE_USERS = "create_users"
    VIEW_USERS = "view_users"
    EDIT_USERS = "edit_users"
    DELETE_USERS = "delete_users"
    
    # Role Management
    CREATE_ROLES = "create_roles"
    VIEW_ROLES = "view_roles"
    EDIT_ROLES = "edit_roles"
    DELETE_ROLES = "delete_roles"
    ASSIGN_ROLES = "assign_roles"
    
    # System Administration
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_SYSTEM_CONFIG = "manage_system_config"
    VIEW_SYSTEM_METRICS = "view_system_metrics"
    MANAGE_SECURITY = "manage_security"
    
    # Organization Management
    CREATE_ORGANIZATIONS = "create_organizations"
    VIEW_ORGANIZATIONS = "view_organizations"
    EDIT_ORGANIZATIONS = "edit_organizations"
    DELETE_ORGANIZATIONS = "delete_organizations"
    
    # Project Management
    CREATE_PROJECTS = "create_projects"
    VIEW_PROJECTS = "view_projects"
    EDIT_PROJECTS = "edit_projects"
    DELETE_PROJECTS = "delete_projects"
    SHARE_PROJECTS = "share_projects"

@dataclass
class Role:
    """Role definition"""
    name: str
    description: str
    permissions: Set[Permission] = field(default_factory=set)
    is_system_role: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class User:
    """User with roles and permissions"""
    user_id: str
    email: str
    roles: Set[str] = field(default_factory=set)
    organization_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

@dataclass
class Organization:
    """Multi-tenant organization"""
    org_id: str
    name: str
    domain: str
    is_active: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

class RBACManager:
    """Role-Based Access Control Manager"""
    
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.users: Dict[str, User] = {}
        self.organizations: Dict[str, Organization] = {}
        self._initialize_system_roles()
    
    def _initialize_system_roles(self):
        """Initialize default system roles"""
        # Super Admin - Full system access
        super_admin = Role(
            name="super_admin",
            description="Full system administrator with all permissions",
            permissions=set(Permission),
            is_system_role=True
        )
        
        # Organization Admin - Manage organization
        org_admin = Role(
            name="org_admin",
            description="Organization administrator",
            permissions={
                Permission.CREATE_USERS, Permission.VIEW_USERS, 
                Permission.EDIT_USERS, Permission.DELETE_USERS,
                Permission.VIEW_ROLES, Permission.ASSIGN_ROLES,
                Permission.CREATE_PROJECTS, Permission.VIEW_PROJECTS,
                Permission.EDIT_PROJECTS, Permission.DELETE_PROJECTS,
                Permission.VIEW_AUDIT_LOGS, Permission.VIEW_SYSTEM_METRICS,
                Permission.GENERATE_UI, Permission.VIEW_GENERATED_UI,
                Permission.EDIT_GENERATED_UI, Permission.DELETE_GENERATED_UI,
                Permission.DEPLOY_UI, Permission.VIEW_DEPLOYMENTS,
                Permission.MANAGE_DEPLOYMENTS, Permission.MANAGE_API_KEYS
            },
            is_system_role=True
        )
        
        # Developer - Create and manage UI projects
        developer = Role(
            name="developer",
            description="UI developer with project creation and management rights",
            permissions={
                Permission.CREATE_PROJECTS, Permission.VIEW_PROJECTS,
                Permission.EDIT_PROJECTS, Permission.SHARE_PROJECTS,
                Permission.GENERATE_UI, Permission.VIEW_GENERATED_UI,
                Permission.EDIT_GENERATED_UI, Permission.DEPLOY_UI,
                Permission.VIEW_DEPLOYMENTS, Permission.MANAGE_API_KEYS,
                Permission.VIEW_API_KEYS
            },
            is_system_role=True
        )
        
        # Designer - UI design and generation
        designer = Role(
            name="designer",
            description="UI designer with generation and editing rights",
            permissions={
                Permission.VIEW_PROJECTS, Permission.GENERATE_UI,
                Permission.VIEW_GENERATED_UI, Permission.EDIT_GENERATED_UI,
                Permission.VIEW_DEPLOYMENTS
            },
            is_system_role=True
        )
        
        # Viewer - Read-only access
        viewer = Role(
            name="viewer",
            description="Read-only access to projects and generated UIs",
            permissions={
                Permission.VIEW_PROJECTS, Permission.VIEW_GENERATED_UI,
                Permission.VIEW_DEPLOYMENTS
            },
            is_system_role=True
        )
        
        # Store system roles
        for role in [super_admin, org_admin, developer, designer, viewer]:
            self.roles[role.name] = role
    
    def create_role(self, name: str, description: str, 
                   permissions: List[Permission], creator_id: str) -> bool:
        """Create a new custom role"""
        try:
            if name in self.roles:
                return False
            
            role = Role(
                name=name,
                description=description,
                permissions=set(permissions),
                is_system_role=False
            )
            
            self.roles[name] = role
            
            audit_logger.log_event(
                event_type=AuditEventType.DATA_MODIFICATION,
                severity=AuditSeverity.MEDIUM,
                action="create_role",
                result="success",
                user_id=creator_id,
                resource=f"role:{name}",
                details={"role_name": name, "permissions": [p.value for p in permissions]}
            )
            
            return True
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.HIGH,
                action="create_role",
                result="error",
                user_id=creator_id,
                details={"error": str(e)}
            )
            return False
    
    def update_role(self, name: str, permissions: List[Permission], 
                   updater_id: str) -> bool:
        """Update role permissions"""
        try:
            if name not in self.roles:
                return False
            
            role = self.roles[name]
            if role.is_system_role:
                return False  # Cannot modify system roles
            
            old_permissions = role.permissions.copy()
            role.permissions = set(permissions)
            role.updated_at = datetime.utcnow()
            
            audit_logger.log_event(
                event_type=AuditEventType.DATA_MODIFICATION,
                severity=AuditSeverity.MEDIUM,
                action="update_role",
                result="success",
                user_id=updater_id,
                resource=f"role:{name}",
                details={
                    "role_name": name,
                    "old_permissions": [p.value for p in old_permissions],
                    "new_permissions": [p.value for p in permissions]
                }
            )
            
            return True
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.HIGH,
                action="update_role",
                result="error",
                user_id=updater_id,
                details={"error": str(e)}
            )
            return False
    
    def delete_role(self, name: str, deleter_id: str) -> bool:
        """Delete a custom role"""
        try:
            if name not in self.roles:
                return False
            
            role = self.roles[name]
            if role.is_system_role:
                return False  # Cannot delete system roles
            
            # Check if role is assigned to any users
            users_with_role = [
                user for user in self.users.values()
                if name in user.roles
            ]
            
            if users_with_role:
                return False  # Cannot delete role that's still assigned
            
            del self.roles[name]
            
            audit_logger.log_event(
                event_type=AuditEventType.DATA_DELETION,
                severity=AuditSeverity.MEDIUM,
                action="delete_role",
                result="success",
                user_id=deleter_id,
                resource=f"role:{name}",
                details={"role_name": name}
            )
            
            return True
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.HIGH,
                action="delete_role",
                result="error",
                user_id=deleter_id,
                details={"error": str(e)}
            )
            return False
    
    def create_user(self, user_id: str, email: str, roles: List[str],
                   organization_id: str = None, creator_id: str = None) -> bool:
        """Create a new user"""
        try:
            if user_id in self.users:
                return False
            
            # Validate roles exist
            for role_name in roles:
                if role_name not in self.roles:
                    return False
            
            user = User(
                user_id=user_id,
                email=email,
                roles=set(roles),
                organization_id=organization_id
            )
            
            self.users[user_id] = user
            
            audit_logger.log_event(
                event_type=AuditEventType.DATA_MODIFICATION,
                severity=AuditSeverity.MEDIUM,
                action="create_user",
                result="success",
                user_id=creator_id,
                resource=f"user:{user_id}",
                details={"user_id": user_id, "email": email, "roles": roles}
            )
            
            return True
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.HIGH,
                action="create_user",
                result="error",
                user_id=creator_id,
                details={"error": str(e)}
            )
            return False
    
    def assign_role(self, user_id: str, role_name: str, assigner_id: str) -> bool:
        """Assign role to user"""
        try:
            if user_id not in self.users or role_name not in self.roles:
                return False
            
            user = self.users[user_id]
            user.roles.add(role_name)
            
            audit_logger.log_event(
                event_type=AuditEventType.DATA_MODIFICATION,
                severity=AuditSeverity.MEDIUM,
                action="assign_role",
                result="success",
                user_id=assigner_id,
                resource=f"user:{user_id}",
                details={"user_id": user_id, "role": role_name}
            )
            
            return True
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.HIGH,
                action="assign_role",
                result="error",
                user_id=assigner_id,
                details={"error": str(e)}
            )
            return False
    
    def revoke_role(self, user_id: str, role_name: str, revoker_id: str) -> bool:
        """Revoke role from user"""
        try:
            if user_id not in self.users:
                return False
            
            user = self.users[user_id]
            if role_name in user.roles:
                user.roles.remove(role_name)
                
                audit_logger.log_event(
                    event_type=AuditEventType.DATA_MODIFICATION,
                    severity=AuditSeverity.MEDIUM,
                    action="revoke_role",
                    result="success",
                    user_id=revoker_id,
                    resource=f"user:{user_id}",
                    details={"user_id": user_id, "role": role_name}
                )
                
                return True
            
            return False
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.HIGH,
                action="revoke_role",
                result="error",
                user_id=revoker_id,
                details={"error": str(e)}
            )
            return False
    
    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has specific permission"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        if not user.is_active:
            return False
        
        # Check all user's roles for the permission
        for role_name in user.roles:
            if role_name in self.roles:
                role = self.roles[role_name]
                if permission in role.permissions:
                    return True
        
        return False
    
    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Get all permissions for a user"""
        if user_id not in self.users:
            return set()
        
        user = self.users[user_id]
        if not user.is_active:
            return set()
        
        permissions = set()
        for role_name in user.roles:
            if role_name in self.roles:
                role = self.roles[role_name]
                permissions.update(role.permissions)
        
        return permissions
    
    def create_organization(self, org_id: str, name: str, domain: str,
                          creator_id: str) -> bool:
        """Create a new organization"""
        try:
            if org_id in self.organizations:
                return False
            
            org = Organization(
                org_id=org_id,
                name=name,
                domain=domain
            )
            
            self.organizations[org_id] = org
            
            audit_logger.log_event(
                event_type=AuditEventType.DATA_MODIFICATION,
                severity=AuditSeverity.MEDIUM,
                action="create_organization",
                result="success",
                user_id=creator_id,
                resource=f"org:{org_id}",
                details={"org_id": org_id, "name": name, "domain": domain}
            )
            
            return True
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.HIGH,
                action="create_organization",
                result="error",
                user_id=creator_id,
                details={"error": str(e)}
            )
            return False
    
    def check_access(self, user_id: str, resource: str, action: str,
                    context: Dict[str, Any] = None) -> bool:
        """Check if user has access to perform action on resource"""
        # Map actions to permissions
        action_permission_map = {
            'create_ui': Permission.GENERATE_UI,
            'view_ui': Permission.VIEW_GENERATED_UI,
            'edit_ui': Permission.EDIT_GENERATED_UI,
            'delete_ui': Permission.DELETE_GENERATED_UI,
            'deploy_ui': Permission.DEPLOY_UI,
            'view_deployments': Permission.VIEW_DEPLOYMENTS,
            'manage_deployments': Permission.MANAGE_DEPLOYMENTS,
            'create_project': Permission.CREATE_PROJECTS,
            'view_project': Permission.VIEW_PROJECTS,
            'edit_project': Permission.EDIT_PROJECTS,
            'delete_project': Permission.DELETE_PROJECTS,
            'share_project': Permission.SHARE_PROJECTS,
        }
        
        required_permission = action_permission_map.get(action)
        if not required_permission:
            return False
        
        # Check basic permission
        if not self.has_permission(user_id, required_permission):
            audit_logger.log_event(
                event_type=AuditEventType.PERMISSION_DENIED,
                severity=AuditSeverity.MEDIUM,
                action=action,
                result="denied",
                user_id=user_id,
                resource=resource,
                details={"required_permission": required_permission.value}
            )
            return False
        
        # Additional context-based checks can be added here
        # For example, checking if user belongs to the same organization
        # as the resource they're trying to access
        
        audit_logger.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            severity=AuditSeverity.LOW,
            action=action,
            result="allowed",
            user_id=user_id,
            resource=resource,
            details={"permission": required_permission.value}
        )
        
        return True

# Global RBAC manager instance
rbac_manager = RBACManager()