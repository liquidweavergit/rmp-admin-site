"""
Google OAuth Service

This service handles Google OAuth integration including:
- OAuth flow management
- User profile retrieval from Google
- Account linking for existing users
- Secure token validation
"""
import secrets
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests
import httpx

from ..config import get_settings


class GoogleOAuthService:
    """Service class for handling Google OAuth operations"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client_id = self.settings.google_client_id
        self.client_secret = self.settings.google_client_secret
        
        if not self.client_id or not self.client_secret:
            self.mock_mode = True
        else:
            self.mock_mode = False
    
    def get_authorization_url(self, redirect_uri: str, state: Optional[str] = None) -> str:
        """
        Generate Google OAuth authorization URL
        
        Args:
            redirect_uri: Where Google should redirect after authentication
            state: Optional state parameter for CSRF protection
            
        Returns:
            str: Authorization URL for Google OAuth
        """
        if self.mock_mode:
            # Return mock URL for development
            return f"https://accounts.google.com/oauth/authorize?mock=true&state={state or 'mock'}"
        
        if not state:
            state = secrets.token_urlsafe(32)
        
        # Build OAuth authorization URL
        base_url = "https://accounts.google.com/o/oauth2/auth"
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": "openid email profile",
            "response_type": "code",
            "state": state,
            "access_type": "offline",
            "prompt": "select_account"
        }
        
        # Build query string
        query_parts = []
        for key, value in params.items():
            query_parts.append(f"{key}={value}")
        query_string = "&".join(query_parts)
        
        return f"{base_url}?{query_string}"
    
    async def exchange_code_for_tokens(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access tokens
        
        Args:
            code: Authorization code from Google
            redirect_uri: Redirect URI used in authorization
            
        Returns:
            Dict containing access_token, id_token, and other token info
            
        Raises:
            HTTPException: If token exchange fails
        """
        if self.mock_mode:
            # Return mock tokens for development
            return {
                "access_token": "mock_access_token",
                "id_token": "mock_id_token",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "mock_refresh_token"
            }
        
        # Exchange code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(token_url, data=token_data)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange code for tokens: {e.response.text}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google OAuth service unavailable"
            )
    
    async def verify_id_token(self, id_token_str: str) -> Dict[str, Any]:
        """
        Verify and decode Google ID token
        
        Args:
            id_token_str: Google ID token to verify
            
        Returns:
            Dict containing user information from token
            
        Raises:
            HTTPException: If token verification fails
        """
        if self.mock_mode:
            # Return mock user info for development
            return {
                "sub": "mock_google_user_id",
                "email": "test@example.com",
                "email_verified": True,
                "name": "Test User",
                "given_name": "Test",
                "family_name": "User",
                "picture": "https://example.com/avatar.jpg"
            }
        
        try:
            # Verify the token using Google's library
            idinfo = id_token.verify_oauth2_token(
                id_token_str, 
                requests.Request(), 
                self.client_id
            )
            
            # Verify the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Invalid issuer')
            
            return idinfo
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid ID token: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Token verification service unavailable"
            )
    
    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """
        Get user profile information from Google
        
        Args:
            access_token: Google access token
            
        Returns:
            Dict containing user profile information
            
        Raises:
            HTTPException: If profile retrieval fails
        """
        if self.mock_mode:
            # Return mock profile for development
            return {
                "id": "mock_google_user_id",
                "email": "test@example.com",
                "verified_email": True,
                "name": "Test User",
                "given_name": "Test",
                "family_name": "User",
                "picture": "https://example.com/avatar.jpg"
            }
        
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v1/userinfo",
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get user profile: {e.response.text}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google profile service unavailable"
            )
    
    def validate_email_domain(self, email: str, allowed_domains: Optional[list] = None) -> bool:
        """
        Validate email domain if domain restrictions are configured
        
        Args:
            email: Email address to validate
            allowed_domains: List of allowed domains (None = allow all)
            
        Returns:
            bool: True if email domain is allowed
        """
        if not allowed_domains:
            return True
            
        domain = email.split('@')[-1].lower()
        return domain in [d.lower() for d in allowed_domains]


def get_google_oauth_service() -> GoogleOAuthService:
    """Get Google OAuth service instance"""
    return GoogleOAuthService() 