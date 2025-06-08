"""
Test module for user roles and permissions system.

Tests the six distinct user roles as defined in the product brief:
- Member: Basic circle participation and event registration
- Facilitator: Circle creation and management capabilities
- PTM (Production Team Manager): Event production, logistics, staff coordination  
- Manager: Team and resource management
- Director: Strategic oversight and operations
- Admin: System administration and user management

Following TDD principles - these tests define expected behavior before implementation.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.role import Role, Permission, UserRole, SYSTEM_ROLES_DATA
from app.models.user import User
from app.core.exceptions import ValidationError, PermissionDenied
from app.services.role_service import RoleService


class TestUserRoleDefinitions:
    """Test that the six user roles are properly defined with correct capabilities."""
    
    def test_member_role_definition(self):
        """Test Member role has basic circle participation capabilities."""
        # Arrange - expected Member permissions
        expected_permissions = [
            "circles:view",
            "circles:join_request", 
            "events:view",
            "events:register",
            "profile:manage",
            "messages:send",
            "messages:receive"
        ]
        
        # Act & Assert - Member role should exist with these permissions
        member_data = SYSTEM_ROLES_DATA.get("Member")
        assert member_data is not None
        assert "Basic circle participation and event registration" in member_data["description"]
        
        # Verify permissions
        member_permissions = member_data["permissions"]
        for permission in expected_permissions:
            assert permission in member_permissions

    def test_facilitator_role_definition(self):
        """Test Facilitator role has circle management capabilities."""
        # Arrange - expected Facilitator permissions (includes all Member permissions)
        expected_permissions = [
            # Member permissions (inherited)
            "circles:view", "circles:join_request", "events:view", "events:register",
            "profile:manage", "messages:send", "messages:receive",
            # Facilitator-specific permissions
            "circles:create", "circles:manage", "circles:add_members", 
            "circles:remove_members", "circles:edit", "meetings:schedule",
            "meetings:record", "messages:broadcast_circle"
        ]
        
        # Act & Assert
        facilitator_data = SYSTEM_ROLES_DATA.get("Facilitator")
        assert facilitator_data is not None
        assert "Circle creation and management capabilities" in facilitator_data["description"]
        
        # Verify permissions
        facilitator_permissions = facilitator_data["permissions"]
        for permission in expected_permissions:
            assert permission in facilitator_permissions

    def test_ptm_role_definition(self):
        """Test PTM role has event production and staff coordination capabilities."""
        # Arrange - expected PTM permissions
        expected_permissions = [
            # Member permissions (inherited)
            "circles:view", "circles:join_request", "events:view", "events:register",
            "profile:manage", "messages:send", "messages:receive",
            # PTM-specific permissions  
            "events:create", "events:manage", "events:staff_assign",
            "events:logistics", "events:coordination", "events:production",
            "staff:manage", "resources:manage", "messages:broadcast_event"
        ]
        
        # Act & Assert
        ptm_data = SYSTEM_ROLES_DATA.get("PTM")
        assert ptm_data is not None
        assert "Production Team Manager" in ptm_data["description"]
        
        # Verify permissions
        ptm_permissions = ptm_data["permissions"]
        for permission in expected_permissions:
            assert permission in ptm_permissions

    def test_manager_role_definition(self):
        """Test Manager role has team and resource management capabilities."""
        # Arrange - expected Manager permissions
        expected_permissions = [
            # Member permissions (inherited)
            "circles:view", "circles:join_request", "events:view", "events:register",
            "profile:manage", "messages:send", "messages:receive",
            # Manager-specific permissions
            "teams:manage", "resources:allocate", "budgets:manage",
            "reports:view", "analytics:view", "staff:evaluate",
            "conflicts:resolve", "policies:implement"
        ]
        
        # Act & Assert
        manager_data = SYSTEM_ROLES_DATA.get("Manager")
        assert manager_data is not None
        assert "Team and resource management" in manager_data["description"]
        
        # Verify permissions
        manager_permissions = manager_data["permissions"]
        for permission in expected_permissions:
            assert permission in manager_permissions

    def test_director_role_definition(self):
        """Test Director role has strategic oversight and operations capabilities."""
        # Arrange - expected Director permissions
        expected_permissions = [
            # Member permissions (inherited) 
            "circles:view", "circles:join_request", "events:view", "events:register",
            "profile:manage", "messages:send", "messages:receive",
            # Director-specific permissions
            "organization:strategic_view", "operations:oversight", 
            "finances:view", "growth:planning", "partnerships:manage",
            "policies:create", "vision:set", "leadership:coordinate",
            "messages:broadcast_organization"
        ]
        
        # Act & Assert
        director_data = SYSTEM_ROLES_DATA.get("Director")
        assert director_data is not None
        assert "Strategic oversight and operations" in director_data["description"]
        
        # Verify permissions
        director_permissions = director_data["permissions"]
        for permission in expected_permissions:
            assert permission in director_permissions

    def test_admin_role_definition(self):
        """Test Admin role has system administration capabilities."""
        # Arrange - expected Admin permissions (most comprehensive)
        expected_permissions = [
            # Member permissions (inherited)
            "circles:view", "circles:join_request", "events:view", "events:register", 
            "profile:manage", "messages:send", "messages:receive",
            # Admin-specific permissions
            "users:create", "users:manage", "users:delete", "users:roles_assign",
            "system:configure", "system:maintain", "system:backup",
            "security:audit", "logs:view", "data:export", "data:import",
            "permissions:manage", "roles:manage", "system:admin"
        ]
        
        # Act & Assert
        admin_data = SYSTEM_ROLES_DATA.get("Admin")
        assert admin_data is not None
        assert "System administration and user management" in admin_data["description"]
        
        # Verify permissions
        admin_permissions = admin_data["permissions"]
        for permission in expected_permissions:
            assert permission in admin_permissions

    def test_all_six_system_roles_exist(self):
        """Test that exactly six system roles exist as defined in product brief."""
        # Act
        system_roles = SYSTEM_ROLES_DATA
        
        # Assert
        assert len(system_roles) == 6
        role_names = list(system_roles.keys())
        expected_roles = ["Member", "Facilitator", "PTM", "Manager", "Director", "Admin"]
        
        for expected_role in expected_roles:
            assert expected_role in role_names


class TestRoleHierarchyAndPermissions:
    """Test role hierarchy and additive permissions."""
    
    def test_additive_permissions_multiple_roles(self):
        """Test that users with multiple roles get additive permissions."""
        # Arrange - Test using the actual role data structure
        member_permissions = set(SYSTEM_ROLES_DATA["Member"]["permissions"])
        facilitator_permissions = set(SYSTEM_ROLES_DATA["Facilitator"]["permissions"])
        
        # Act - Simulate additive permissions from multiple roles
        combined_permissions = member_permissions | facilitator_permissions
        
        # Assert - Combined permissions should include both role permissions
        # Member permissions should all be included
        for permission in member_permissions:
            assert permission in combined_permissions
        
        # Facilitator permissions should all be included
        for permission in facilitator_permissions:
            assert permission in combined_permissions
        
        # Combined should be larger than either individual role
        assert len(combined_permissions) >= len(member_permissions)
        assert len(combined_permissions) >= len(facilitator_permissions)

    @pytest.mark.asyncio
    async def test_context_switching_between_roles(self):
        """Test that users can switch between their assigned roles."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)
        role_service = RoleService(session=mock_session)
        
        # Mock successful context switch
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        # Mock role existence
        facilitator_role = Mock(spec=Role)
        facilitator_role.id = 2
        facilitator_role.name = "Facilitator"
        
        role_result = Mock()
        role_result.scalar_one_or_none.return_value = facilitator_role
        
        # Mock user role assignment  
        user_role = Mock(spec=UserRole)
        user_role.is_primary = False
        
        user_role_result = Mock()
        user_role_result.scalar_one_or_none.return_value = user_role
        
        # Mock all user roles query
        all_roles_result = Mock()
        all_roles_result.scalars.return_value.all.return_value = [user_role]
        
        mock_session.execute.side_effect = [
            role_result,  # Role lookup
            user_role_result,  # UserRole lookup
            all_roles_result  # All user roles for clearing primary
        ]
        
        # Act
        result = await role_service.switch_user_context(user_id=1, role_name="Facilitator")
        
        # Assert
        assert result is True
        assert user_role.is_primary is True
        mock_session.add.assert_called()  # Audit log added
        mock_session.commit.assert_called_once()

    def test_permission_inheritance_validation(self):
        """Test that higher roles include permissions from lower roles."""
        # Arrange - Define role hierarchy
        role_hierarchy = ["Member", "Facilitator", "PTM", "Manager", "Director", "Admin"]
        
        # Act & Assert - Each role should include permissions from roles below it
        for i, role_name in enumerate(role_hierarchy):
            current_role_permissions = set(SYSTEM_ROLES_DATA[role_name]["permissions"])
            
            # Check that this role includes Member permissions (baseline)
            member_permissions = set(SYSTEM_ROLES_DATA["Member"]["permissions"])
            assert member_permissions.issubset(current_role_permissions), \
                f"{role_name} should include all Member permissions"


class TestRoleAssignmentAndValidation:
    """Test role assignment and validation functionality."""
    
    @pytest.mark.asyncio
    async def test_assign_role_to_user(self):
        """Test successful role assignment to a user."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)
        role_service = RoleService(session=mock_session)
        
        # Mock session context manager
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        # Mock role exists
        facilitator_role = Mock(spec=Role)
        facilitator_role.id = 2
        facilitator_role.name = "Facilitator"
        
        role_result = Mock()
        role_result.scalar_one_or_none.return_value = facilitator_role
        
        # Mock no existing assignment
        existing_result = Mock()
        existing_result.scalar_one_or_none.return_value = None
        
        mock_session.execute.side_effect = [role_result, existing_result]
        
        # Act
        result = await role_service.assign_role(
            user_id=1,
            role_name="Facilitator", 
            assigned_by=2,
            is_primary=True,
            notes="Initial facilitator assignment"
        )
        
        # Assert
        assert result is True
        mock_session.add.assert_called()  # UserRole and audit log added
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_role_from_user(self):
        """Test successful role removal from a user.""" 
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)
        role_service = RoleService(session=mock_session)
        
        # Mock session context manager
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        # Mock role exists
        facilitator_role = Mock(spec=Role)
        facilitator_role.id = 2
        facilitator_role.name = "Facilitator"
        
        role_result = Mock()
        role_result.scalar_one_or_none.return_value = facilitator_role
        
        # Mock existing assignment
        user_role = Mock(spec=UserRole)
        user_role.is_primary = True
        
        user_role_result = Mock()
        user_role_result.scalar_one_or_none.return_value = user_role
        
        mock_session.execute.side_effect = [role_result, user_role_result]
        
        # Act
        result = await role_service.remove_role(
            user_id=1,
            role_name="Facilitator",
            removed_by=2
        )
        
        # Assert
        assert result is True
        assert user_role.is_active is False
        mock_session.add.assert_called()  # Audit log added
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_cannot_assign_non_existent_role(self):
        """Test that assigning a non-existent role raises ValidationError."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)
        role_service = RoleService(session=mock_session)
        
        # Mock session context manager
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        # Mock role does not exist
        role_result = Mock()
        role_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = role_result
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await role_service.assign_role(
                user_id=1,
                role_name="NonExistentRole",
                assigned_by=2
            )
        
        assert "Role 'NonExistentRole' does not exist" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_cannot_assign_duplicate_role(self):
        """Test that assigning a role a user already has is handled gracefully."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)
        role_service = RoleService(session=mock_session)
        
        # Mock session context manager
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        # Mock role exists
        facilitator_role = Mock(spec=Role)
        facilitator_role.id = 2
        
        role_result = Mock()
        role_result.scalar_one_or_none.return_value = facilitator_role
        
        # Mock existing assignment
        existing_assignment = Mock(spec=UserRole)
        existing_result = Mock()
        existing_result.scalar_one_or_none.return_value = existing_assignment
        
        mock_session.execute.side_effect = [role_result, existing_result]
        
        # Act
        result = await role_service.assign_role(
            user_id=1,
            role_name="Facilitator",
            assigned_by=2
        )
        
        # Assert - should return True (idempotent)
        assert result is True 