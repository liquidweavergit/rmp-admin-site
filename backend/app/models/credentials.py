"""
User credentials model for the credentials database
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, LargeBinary
from sqlalchemy.sql import func
from ..core.database import CredentialsBase


class UserCredentials(CredentialsBase):
    """
    User credentials model for sensitive authentication data
    
    This model stores sensitive authentication information in a separate database
    for enhanced security as per the tech spec.
    """
    __tablename__ = "user_credentials"
    
    # Primary key (matches user.id in main database)
    user_id = Column(Integer, primary_key=True, index=True)
    
    # Authentication credentials
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)
    
    # Two-factor authentication
    totp_secret = Column(String(255), nullable=True)
    backup_codes = Column(String(1000), nullable=True)  # JSON array of backup codes
    
    # OAuth tokens (encrypted)
    google_oauth_token = Column(LargeBinary, nullable=True)
    google_user_id = Column(String(255), nullable=True, unique=True)  # Google sub claim
    google_access_token = Column(LargeBinary, nullable=True)  # Encrypted access token
    google_refresh_token = Column(LargeBinary, nullable=True)  # Encrypted refresh token
    refresh_token_hash = Column(String(255), nullable=True)
    
    # Phone verification
    phone_verification_code = Column(String(10), nullable=True)
    phone_verification_expires_at = Column(DateTime(timezone=True), nullable=True)
    phone_verification_attempts = Column(Integer, default=0, nullable=False)
    
    # Password reset
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires_at = Column(DateTime(timezone=True), nullable=True)
    password_reset_attempts = Column(Integer, default=0, nullable=False)
    
    # Security tracking
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_password_attempt = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<UserCredentials(user_id={self.user_id})>" 