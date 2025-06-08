#!/usr/bin/env python3
"""
Migration management script for Men's Circle Management Platform

This script provides convenient commands to manage database migrations
for both the main application database and the credentials database.

Usage:
    python migrate.py init          # Initialize both databases
    python migrate.py upgrade      # Upgrade both databases to latest
    python migrate.py revision     # Create new migration for main DB
    python migrate.py revision-creds # Create new migration for credentials DB
    python migrate.py downgrade    # Downgrade both databases by one revision
    python migrate.py current      # Show current revision for both databases
    python migrate.py history      # Show migration history for both databases
"""

import asyncio
import subprocess
import sys
from pathlib import Path

def run_command(command: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n🔄 {description}")
    print(f"Running: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def init_databases():
    """Initialize both databases with Alembic."""
    print("🚀 Initializing databases...")
    
    # Initialize main database
    success1 = run_command(
        ["alembic", "upgrade", "head"],
        "Initializing main database"
    )
    
    # Initialize credentials database
    success2 = run_command(
        ["alembic", "-c", "alembic-credentials.ini", "upgrade", "head"],
        "Initializing credentials database"
    )
    
    if success1 and success2:
        print("✅ Both databases initialized successfully!")
    else:
        print("❌ Database initialization failed!")
        return False
    return True

def upgrade_databases():
    """Upgrade both databases to latest revision."""
    print("⬆️  Upgrading databases...")
    
    # Upgrade main database
    success1 = run_command(
        ["alembic", "upgrade", "head"],
        "Upgrading main database"
    )
    
    # Upgrade credentials database
    success2 = run_command(
        ["alembic", "-c", "alembic-credentials.ini", "upgrade", "head"],
        "Upgrading credentials database"
    )
    
    if success1 and success2:
        print("✅ Both databases upgraded successfully!")
    else:
        print("❌ Database upgrade failed!")
        return False
    return True

def create_revision(message: str = None, credentials: bool = False):
    """Create a new migration revision."""
    db_type = "credentials" if credentials else "main"
    print(f"📝 Creating new {db_type} database revision...")
    
    command = ["alembic"]
    if credentials:
        command.extend(["-c", "alembic-credentials.ini"])
    
    command.extend(["revision", "--autogenerate"])
    
    if message:
        command.extend(["-m", message])
    else:
        command.extend(["-m", f"Auto-generated {db_type} migration"])
    
    success = run_command(command, f"Creating {db_type} database revision")
    
    if success:
        print(f"✅ {db_type.title()} database revision created successfully!")
    else:
        print(f"❌ {db_type.title()} database revision creation failed!")
    return success

def downgrade_databases():
    """Downgrade both databases by one revision."""
    print("⬇️  Downgrading databases...")
    
    # Downgrade main database
    success1 = run_command(
        ["alembic", "downgrade", "-1"],
        "Downgrading main database"
    )
    
    # Downgrade credentials database
    success2 = run_command(
        ["alembic", "-c", "alembic-credentials.ini", "downgrade", "-1"],
        "Downgrading credentials database"
    )
    
    if success1 and success2:
        print("✅ Both databases downgraded successfully!")
    else:
        print("❌ Database downgrade failed!")
        return False
    return True

def show_current():
    """Show current revision for both databases."""
    print("📍 Current database revisions:")
    
    # Show main database current revision
    run_command(
        ["alembic", "current"],
        "Main database current revision"
    )
    
    # Show credentials database current revision
    run_command(
        ["alembic", "-c", "alembic-credentials.ini", "current"],
        "Credentials database current revision"
    )

def show_history():
    """Show migration history for both databases."""
    print("📚 Database migration history:")
    
    # Show main database history
    run_command(
        ["alembic", "history"],
        "Main database migration history"
    )
    
    # Show credentials database history
    run_command(
        ["alembic", "-c", "alembic-credentials.ini", "history"],
        "Credentials database migration history"
    )

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "init":
        init_databases()
    elif command == "upgrade":
        upgrade_databases()
    elif command == "revision":
        message = sys.argv[2] if len(sys.argv) > 2 else None
        create_revision(message, credentials=False)
    elif command == "revision-creds":
        message = sys.argv[2] if len(sys.argv) > 2 else None
        create_revision(message, credentials=True)
    elif command == "downgrade":
        downgrade_databases()
    elif command == "current":
        show_current()
    elif command == "history":
        show_history()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main() 