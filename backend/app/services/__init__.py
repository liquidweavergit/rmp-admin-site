"""
Services package for the Men's Circle Management Platform
"""

from .auth_service import AuthService, get_auth_service

__all__ = ["AuthService", "get_auth_service"] 