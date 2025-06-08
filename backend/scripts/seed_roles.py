#!/usr/bin/env python3
"""
Database seeding script for system roles and permissions.

This script initializes the six system roles defined in the product brief:
- Member, Facilitator, PTM, Manager, Director, Admin

Run this script after database migrations to set up the role-based access control system.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.models.role import Role, Permission, SYSTEM_ROLES_DATA, PERMISSION_DESCRIPTIONS
from app.core.database import get_main_engine, get_main_session_local
from app.config import get_settings


async def seed_roles_and_permissions():
    """Seed the database with system roles and permissions."""
    
    # Get database URL from settings
    settings = get_settings()
    database_url = settings.database_url
    print(f"Connecting to database: {database_url.split('@')[1] if '@' in database_url else 'localhost'}")
    
    # Use the existing session factory
    session_local = get_main_session_local()
    
    async with session_local() as session:
        try:
            print("Starting role and permission seeding...")
            
            # First, create all permissions
            print("\n1. Creating permissions...")
            all_permissions = set()
            for role_data in SYSTEM_ROLES_DATA.values():
                all_permissions.update(role_data["permissions"])
            
            permission_objects = {}
            for permission_name in sorted(all_permissions):
                # Check if permission already exists
                result = await session.execute(
                    text("SELECT * FROM permissions WHERE name = :name"),
                    {"name": permission_name}
                )
                existing_permission = result.first()
                
                if existing_permission:
                    print(f"   ✓ Permission '{permission_name}' already exists")
                    # Create a Permission object from the result
                    permission_obj = Permission(
                        id=existing_permission.id,
                        name=existing_permission.name,
                        description=existing_permission.description,
                        resource=existing_permission.resource,
                        action=existing_permission.action,
                        is_system=existing_permission.is_system
                    )
                    permission_objects[permission_name] = permission_obj
                else:
                    # Create new permission
                    description = PERMISSION_DESCRIPTIONS.get(permission_name, f"Permission: {permission_name}")
                    permission = Permission.create_from_string(permission_name, description)
                    session.add(permission)
                    permission_objects[permission_name] = permission
                    print(f"   + Created permission '{permission_name}'")
            
            # Commit permissions first
            await session.commit()
            print(f"   Created {len([p for p in permission_objects.values() if p.id is None])} new permissions")
            
            # Create roles and assign permissions
            print("\n2. Creating roles...")
            for role_name, role_data in SYSTEM_ROLES_DATA.items():
                # Check if role already exists
                result = await session.execute(
                    text("SELECT * FROM roles WHERE name = :name"),
                    {"name": role_name}
                )
                existing_role = result.first()
                
                if existing_role:
                    print(f"   ✓ Role '{role_name}' already exists")
                    continue
                
                # Create new role
                role = Role(
                    name=role_name,
                    description=role_data["description"],
                    priority=role_data["priority"],
                    is_system=True,
                    is_assignable=True
                )
                session.add(role)
                await session.flush()  # Get the role ID
                
                # Add permissions to role using direct SQL
                for permission_name in role_data["permissions"]:
                    permission = permission_objects.get(permission_name)
                    if permission:
                        # Insert into role_permissions table directly
                        await session.execute(
                            text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:role_id, :permission_id)"),
                            {"role_id": role.id, "permission_id": permission.id}
                        )
                
                print(f"   + Created role '{role_name}' with {len(role_data['permissions'])} permissions")
            
            # Final commit
            await session.commit()
            
            print("\n3. Verification...")
            # Verify all roles were created
            result = await session.execute(text("SELECT name, priority FROM roles WHERE is_system = true ORDER BY priority"))
            system_roles = result.fetchall()
            
            print("   System roles created:")
            for role_name, priority in system_roles:
                print(f"     - {role_name} (priority: {priority})")
            
            print(f"\n✅ Successfully seeded {len(system_roles)} system roles and {len(all_permissions)} permissions!")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            await session.rollback()
            raise
        finally:
            pass  # Session will be closed automatically


async def verify_roles():
    """Verify that all system roles are properly configured."""
    session_local = get_main_session_local()
    
    async with session_local() as session:
        try:
            print("Verifying role configuration...")
            
            # Check each expected role
            for role_name in SYSTEM_ROLES_DATA.keys():
                result = await session.execute(
                    text("""
                    SELECT r.name, r.description, r.priority, COUNT(p.id) as permission_count
                    FROM roles r
                    LEFT JOIN role_permissions rp ON r.id = rp.role_id
                    LEFT JOIN permissions p ON rp.permission_id = p.id
                    WHERE r.name = :name
                    GROUP BY r.id, r.name, r.description, r.priority
                    """),
                    {"name": role_name}
                )
                role_info = result.first()
                
                if role_info:
                    expected_permissions = len(SYSTEM_ROLES_DATA[role_name]["permissions"])
                    print(f"   ✓ {role_name}: {role_info.permission_count}/{expected_permissions} permissions")
                    
                    if role_info.permission_count != expected_permissions:
                        print(f"     ⚠️  Expected {expected_permissions} permissions, found {role_info.permission_count}")
                else:
                    print(f"   ❌ {role_name}: Not found")
            
            print("\n✅ Role verification complete!")
            
        except Exception as e:
            print(f"\n❌ Error during verification: {e}")
            raise
        finally:
            pass  # Session will be closed automatically


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed system roles and permissions")
    parser.add_argument("--verify", action="store_true", help="Verify existing roles instead of seeding")
    parser.add_argument("--database-url", help="Override database URL")
    
    args = parser.parse_args()
    
    # Override database URL if provided
    if args.database_url:
        os.environ["DATABASE_URL"] = args.database_url
    
    if args.verify:
        asyncio.run(verify_roles())
    else:
        asyncio.run(seed_roles_and_permissions()) 