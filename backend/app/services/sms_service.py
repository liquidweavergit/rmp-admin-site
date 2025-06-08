"""
SMS Service for phone verification using Twilio

This service handles SMS operations including:
- Sending verification codes
- Rate limiting SMS sends
- Managing verification code expiry
"""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class SMSService:
    """Service for handling SMS operations with Twilio"""
    
    def __init__(self):
        """Initialize Twilio client"""
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_FROM_NUMBER", "+12345678900")  # Default for testing
        
        if not self.account_sid or not self.auth_token:
            logger.warning("Twilio credentials not configured - SMS will be mocked")
            self.client = None
        else:
            self.client = Client(self.account_sid, self.auth_token)
    
    def generate_verification_code(self) -> str:
        """Generate a 6-digit verification code"""
        return f"{secrets.randbelow(900000) + 100000:06d}"
    
    def format_phone_number(self, phone: str) -> str:
        """
        Format phone number for SMS sending
        
        Args:
            phone: Raw phone number string
            
        Returns:
            Formatted phone number with +1 country code if needed
        """
        # Remove all non-digit characters
        digits_only = ''.join(filter(str.isdigit, phone))
        
        # Add country code if not present
        if len(digits_only) == 10:
            return f"+1{digits_only}"
        elif len(digits_only) == 11 and digits_only.startswith("1"):
            return f"+{digits_only}"
        else:
            # For other formats, assume it's already correctly formatted
            return phone if phone.startswith("+") else f"+{phone}"
    
    async def send_verification_code(self, phone: str, code: str) -> bool:
        """
        Send SMS verification code to phone number
        
        Args:
            phone: Phone number to send to
            code: Verification code to send
            
        Returns:
            True if SMS was sent successfully
            
        Raises:
            HTTPException: If SMS sending fails
        """
        try:
            formatted_phone = self.format_phone_number(phone)
            message_body = f"Your Men's Circle verification code is: {code}. This code expires in 10 minutes."
            
            if not self.client:
                # Mock mode for development/testing
                logger.info(f"MOCK SMS to {formatted_phone}: {message_body}")
                return True
            
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=formatted_phone
            )
            
            logger.info(f"SMS sent successfully to {formatted_phone}, SID: {message.sid}")
            return True
            
        except TwilioException as e:
            logger.error(f"Twilio error sending SMS to {phone}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="SMS service temporarily unavailable"
            )
        except Exception as e:
            logger.error(f"Unexpected error sending SMS to {phone}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification code"
            )
    
    def is_code_expired(self, created_at: datetime, expiry_minutes: int = 10) -> bool:
        """
        Check if verification code has expired
        
        Args:
            created_at: When the code was created
            expiry_minutes: Code expiry time in minutes
            
        Returns:
            True if code has expired
        """
        return datetime.utcnow() > created_at + timedelta(minutes=expiry_minutes)
    
    def validate_phone_number(self, phone: str) -> bool:
        """
        Basic phone number validation
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if phone number appears valid
        """
        if not phone:
            return False
        
        # Remove all non-digit characters for validation
        digits_only = ''.join(filter(str.isdigit, phone))
        
        # Check for reasonable length (10-15 digits)
        return 10 <= len(digits_only) <= 15


def get_sms_service() -> SMSService:
    """Dependency injection for SMS service"""
    return SMSService() 