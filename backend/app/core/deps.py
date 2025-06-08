"""
FastAPI dependencies for authentication and authorization
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_main_db, get_credentials_db
from ..services.auth_service import AuthService, get_auth_service
from ..models.user import User

# HTTP Bearer security scheme for JWT tokens
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """
    Dependency to get the current authenticated user
    
    Args:
        credentials: HTTP Bearer credentials from request header
        auth_service: Authentication service instance
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If authentication fails or token is invalid
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify the access token
    user = await auth_service.verify_access_token(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    """
    Dependency to get the current user if authenticated (optional)
    
    Args:
        credentials: HTTP Bearer credentials from request header
        auth_service: Authentication service instance
        
    Returns:
        User or None: Current authenticated user or None if not authenticated
    """
    if not credentials or not credentials.credentials:
        return None
    
    # Verify the access token
    user = await auth_service.verify_access_token(credentials.credentials)
    if not user or not user.is_active:
        return None
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get the current active user
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current active user
        
    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get the current verified user
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current verified user
        
    Raises:
        HTTPException: If user is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is not verified"
        )
    return current_user 