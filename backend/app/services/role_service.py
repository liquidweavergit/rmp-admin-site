"""
Role-based access control service for the Men's Circle Management Platform.

This module provides services for managing user roles, permissions, and access control.
It implements the six-role system defined in the product brief with additive permissions.
"""
import json
from typing import List, Set, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select
from sqlalchemy.orm import selectinload

from ..models.role import Role, Permission, UserRole, RoleAuditLog, SYSTEM_ROLES_DATA, PERMISSION_DESCRIPTIONS
from ..models.user import User
from ..core.exceptions import ValidationError, PermissionDenied, ResourceNotFound, DuplicateResourceError
from ..core.database import get_main_db, get_main_session_local


class RoleService:
    """Service for managing user roles and permissions."""
    
    def __init__(self, session: AsyncSession = None):
        self.session = session
    
    async def get_session(self) -> AsyncSession:
        """Get database session"""
        if self.session:
            return self.session
        
        session_local = get_main_session_local()
        return session_local()
    
    async def assign_role(self, user_id: int, role_name: str, assigned_by: int, 
                         is_primary: bool = False, notes: Optional[str] = None) -> bool:
        """
        Assign a role to a user.
        
        Args:
            user_id: ID of the user to assign role to
            role_name: Name of the role to assign
            assigned_by: ID of the user performing the assignment
            is_primary: Whether this should be the user's primary role
            notes: Optional notes about the assignment
            
        Returns:
            True if assignment was successful
            
        Raises:
            ValidationError: If role doesn't exist
            DuplicateResourceError: If user already has the role (handled gracefully)
        """
        async with await self.get_session() as session:
            # Verify role exists
            result = await session.execute(select(Role).where(Role.name == role_name))
            role = result.scalar_one_or_none()
            
            if not role:
                raise ValidationError(f"Role '{role_name}' does not exist")
            
            # Check if user already has this role
            result = await session.execute(
                select(UserRole).where(
                    and_(UserRole.user_id == user_id, UserRole.role_id == role.id, UserRole.is_active == True)
                )
            )
            existing_assignment = result.scalar_one_or_none()
            
            if existing_assignment:
                # Role already assigned - this is idempotent, just return True
                return True
            
            # Create new role assignment
            user_role = UserRole(
                user_id=user_id,
                role_id=role.id,
                is_primary=is_primary,
                assigned_by=assigned_by,
                notes=notes
            )
            
            session.add(user_role)
            
            # Create audit log
            audit_log = RoleAuditLog(
                user_id=user_id,
                role_id=role.id,
                role_name=role_name,
                action="ROLE_ASSIGNED",
                performed_by=assigned_by,
                new_value=json.dumps({
                    "role_name": role_name,
                    "is_primary": is_primary,
                    "notes": notes
                })
            )
            
            session.add(audit_log)
            await session.commit()
            
            return True
    
    async def remove_role(self, user_id: int, role_name: str, removed_by: Optional[int] = None) -> bool:
        """
        Remove a role from a user.
        
        Args:
            user_id: ID of the user to remove role from
            role_name: Name of the role to remove
            removed_by: ID of the user performing the removal
            
        Returns:
            True if removal was successful
        """
        async with await self.get_session() as session:
            # Find the role assignment
            result = await session.execute(select(Role).where(Role.name == role_name))
            role = result.scalar_one_or_none()
            
            if not role:
                return False
            
            result = await session.execute(
                select(UserRole).where(
                    and_(UserRole.user_id == user_id, UserRole.role_id == role.id, UserRole.is_active == True)
                )
            )
            user_role = result.scalar_one_or_none()
            
            if not user_role:
                return False
            
            # Deactivate the role assignment
            user_role.is_active = False
            
            # Create audit log
            audit_log = RoleAuditLog(
                user_id=user_id,
                role_id=role.id,
                role_name=role_name,
                action="ROLE_REMOVED",
                performed_by=removed_by,
                old_value=json.dumps({
                    "role_name": role_name,
                    "was_primary": user_role.is_primary
                })
            )
            
            session.add(audit_log)
            await session.commit()
            
            return True
    
    async def get_user_roles(self, user_id: int) -> List[Role]:
        """Get all active roles for a user."""
        async with await self.get_session() as session:
            result = await session.execute(
                select(UserRole).options(selectinload(UserRole.role)).where(
                    and_(UserRole.user_id == user_id, UserRole.is_active == True)
                )
            )
            user_roles = result.scalars().all()
            
            return [ur.role for ur in user_roles]
    
    async def get_user_permissions(self, user_id: int) -> Set[str]:
        """
        Get all permissions for a user across all their roles.
        Implements additive permissions.
        """
        user_roles = await self.get_user_roles(user_id)
        permissions = set()
        
        async with await self.get_session() as session:
            for role in user_roles:
                # Load permissions for this role
                result = await session.execute(
                    select(Role).options(selectinload(Role.permissions)).where(Role.id == role.id)
                )
                role_with_permissions = result.scalar_one_or_none()
                
                if role_with_permissions:
                    for permission in role_with_permissions.permissions:
                        permissions.add(permission.name)
        
        return permissions
    
    async def switch_user_context(self, user_id: int, role_name: str) -> bool:
        """
        Switch user's current context to a specific role.
        
        Args:
            user_id: ID of the user
            role_name: Name of the role to switch to
            
        Returns:
            True if context switch was successful, False if user doesn't have the role
        """
        async with await self.get_session() as session:
            # Verify user has this role
            result = await session.execute(select(Role).where(Role.name == role_name))
            role = result.scalar_one_or_none()
            
            if not role:
                return False
            
            result = await session.execute(
                select(UserRole).where(
                    and_(UserRole.user_id == user_id, UserRole.role_id == role.id, UserRole.is_active == True)
                )
            )
            user_role = result.scalar_one_or_none()
            
            if not user_role:
                return False
            
            # Clear any existing primary role
            result = await session.execute(
                select(UserRole).where(
                    and_(UserRole.user_id == user_id, UserRole.is_active == True)
                )
            )
            all_user_roles = result.scalars().all()
            
            for ur in all_user_roles:
                ur.is_primary = False
            
            # Set this role as primary
            user_role.is_primary = True
            
            # Create audit log
            audit_log = RoleAuditLog(
                user_id=user_id,
                role_id=role.id,
                role_name=role_name,
                action="CONTEXT_SWITCHED",
                performed_by=user_id,  # User switching their own context
                new_value=json.dumps({"new_primary_role": role_name})
            )
            
            session.add(audit_log)
            await session.commit()
            
            return True
    
    async def get_current_context(self, user_id: int) -> Optional[str]:
        """Get the user's current primary role context."""
        async with await self.get_session() as session:
            result = await session.execute(
                select(UserRole).options(selectinload(UserRole.role)).where(
                    and_(UserRole.user_id == user_id, UserRole.is_primary == True, UserRole.is_active == True)
                )
            )
            primary_role = result.scalar_one_or_none()
            
            return primary_role.role.name if primary_role else None
    
    async def get_audit_logs(self, user_id: int, limit: int = 50) -> List[RoleAuditLog]:
        """Get audit logs for a user's role changes."""
        async with await self.get_session() as session:
            result = await session.execute(
                select(RoleAuditLog).where(RoleAuditLog.user_id == user_id)
                .order_by(RoleAuditLog.created_at.desc()).limit(limit)
            )
            return list(result.scalars().all())
    
    @staticmethod
    async def get_user_permissions_static(user_id: int) -> Set[str]:
        """Static method for getting user permissions (used in tests)."""
        service = RoleService()
        return await service.get_user_permissions(user_id)


class PermissionChecker:
    """Utility class for checking permissions."""
    
    def __init__(self, session: AsyncSession = None):
        self.role_service = RoleService(session)
    
    async def has_permission(self, user_id: int, permission_name: str) -> bool:
        """Check if a user has a specific permission."""
        user_permissions = await self.role_service.get_user_permissions(user_id)
        return permission_name in user_permissions
    
    async def require_permission(self, user_id: int, permission_name: str) -> None:
        """Require a user to have a specific permission, raise exception if not."""
        if not await self.has_permission(user_id, permission_name):
            raise PermissionDenied(
                f"Permission '{permission_name}' required",
                required_permission=permission_name,
                user_id=user_id
            )


def require_permission(permission_name: str):
    """
    Decorator to require a specific permission for a function.
    
    Usage:
        @require_permission("circles:create")
        async def create_circle(current_user):
            # Function implementation
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract current_user from arguments
            current_user = None
            if args:
                current_user = args[0]  # Assume first argument is current_user
            elif 'current_user' in kwargs:
                current_user = kwargs['current_user']
            
            if current_user is None:
                raise PermissionDenied("No user context provided")
            
            # Check permission
            checker = PermissionChecker()
            await checker.require_permission(current_user.id, permission_name)
            
            # Call original function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


 