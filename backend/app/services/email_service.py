"""
Email Service for sending notifications using SendGrid

This service handles email operations including:
- Sending password reset emails
- Email template rendering
- Rate limiting email sends
"""
import os
import logging
import re
from typing import Optional
from fastapi import HTTPException, status

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, From, To, Subject, PlainTextContent, HtmlContent
    from sendgrid.exceptions import SendGridException
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    SendGridAPIClient = None
    Mail = None
    From = None
    To = None
    Subject = None
    PlainTextContent = None
    HtmlContent = None
    SendGridException = Exception

logger = logging.getLogger(__name__)


class EmailService:
    """Service for handling email operations with SendGrid"""
    
    def __init__(self):
        """Initialize SendGrid client"""
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@menscircle.app")
        self.from_name = os.getenv("FROM_NAME", "Men's Circle Management")
        
        if not SENDGRID_AVAILABLE:
            logger.warning("SendGrid not available - emails will be mocked")
            self.client = None
        elif not self.api_key:
            logger.warning("SendGrid API key not configured - emails will be mocked")
            self.client = None
        else:
            self.client = SendGridAPIClient(api_key=self.api_key)
    
    async def send_password_reset_email(self, to_email: str, first_name: str, reset_token: str) -> bool:
        """
        Send password reset email with token
        
        Args:
            to_email: Recipient email address
            first_name: Recipient's first name for personalization
            reset_token: Password reset token
            
        Returns:
            True if email was sent successfully
            
        Raises:
            HTTPException: If email sending fails
        """
        try:
            # Generate reset URL (in production this would be the frontend URL)
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            reset_url = f"{frontend_url}/reset-password?token={reset_token}"
            
            # Email subject
            subject = "Reset Your Men's Circle Password"
            
            # Plain text content
            plain_text = f"""
Hi {first_name},

You requested a password reset for your Men's Circle account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour for security.

If you didn't request this reset, please ignore this email.

Best regards,
The Men's Circle Team
            """.strip()
            
            # HTML content
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Reset Your Password</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #1976d2; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .button {{ 
            display: inline-block; 
            padding: 12px 24px; 
            background-color: #1976d2; 
            color: white; 
            text-decoration: none; 
            border-radius: 4px; 
            margin: 20px 0;
        }}
        .footer {{ padding: 20px; font-size: 12px; color: #666; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Men's Circle</h1>
        </div>
        <div class="content">
            <h2>Reset Your Password</h2>
            <p>Hi {first_name},</p>
            <p>You requested a password reset for your Men's Circle account.</p>
            <p>Click the button below to reset your password:</p>
            <a href="{reset_url}" class="button">Reset Password</a>
            <p>Or copy and paste this link in your browser:</p>
            <p><a href="{reset_url}">{reset_url}</a></p>
            <p><strong>This link will expire in 1 hour for security.</strong></p>
            <p>If you didn't request this reset, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>Best regards,<br>The Men's Circle Team</p>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            return await self._send_email(to_email, subject, plain_text, html_content)
            
        except Exception as e:
            logger.error(f"Error sending password reset email to {to_email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send password reset email"
            )
    
    async def send_welcome_email(self, to_email: str, first_name: str) -> bool:
        """
        Send welcome email to new users
        
        Args:
            to_email: Recipient email address
            first_name: Recipient's first name
            
        Returns:
            True if email was sent successfully
        """
        try:
            subject = "Welcome to Men's Circle!"
            
            plain_text = f"""
Hi {first_name},

Welcome to Men's Circle! Your account has been successfully created.

We're excited to have you join our community of men committed to personal growth and development.

Next steps:
1. Verify your phone number if you haven't already
2. Complete your profile
3. Explore available circles and events

If you have any questions, please don't hesitate to reach out.

Best regards,
The Men's Circle Team
            """.strip()
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Welcome to Men's Circle</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #1976d2; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .footer {{ padding: 20px; font-size: 12px; color: #666; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to Men's Circle!</h1>
        </div>
        <div class="content">
            <p>Hi {first_name},</p>
            <p>Welcome to Men's Circle! Your account has been successfully created.</p>
            <p>We're excited to have you join our community of men committed to personal growth and development.</p>
            <h3>Next steps:</h3>
            <ul>
                <li>Verify your phone number if you haven't already</li>
                <li>Complete your profile</li>
                <li>Explore available circles and events</li>
            </ul>
            <p>If you have any questions, please don't hesitate to reach out.</p>
        </div>
        <div class="footer">
            <p>Best regards,<br>The Men's Circle Team</p>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            return await self._send_email(to_email, subject, plain_text, html_content)
            
        except Exception as e:
            logger.error(f"Error sending welcome email to {to_email}: {str(e)}")
            # Don't raise exception for welcome emails, just log the error
            return False
    
    async def _send_email(
        self, 
        to_email: str, 
        subject: str, 
        plain_text: str, 
        html_content: Optional[str] = None
    ) -> bool:
        """
        Internal method to send email via SendGrid
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            plain_text: Plain text content
            html_content: HTML content (optional)
            
        Returns:
            True if email was sent successfully
            
        Raises:
            HTTPException: If email sending fails
        """
        try:
            if not self.client:
                # Mock mode for development/testing
                logger.info(f"MOCK EMAIL to {to_email}: {subject}")
                logger.info(f"Content: {plain_text[:100]}...")
                return True
            
            # Create SendGrid Mail object
            mail = Mail(
                from_email=From(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=Subject(subject),
                plain_text_content=PlainTextContent(plain_text)
            )
            
            # Add HTML content if provided
            if html_content:
                mail.content = [
                    PlainTextContent(plain_text),
                    HtmlContent(html_content)
                ]
            
            # Send the email
            response = self.client.send(mail)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully to {to_email}, status: {response.status_code}")
                return True
            else:
                logger.error(f"SendGrid returned status {response.status_code} for {to_email}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Email service temporarily unavailable"
                )
                
        except SendGridException as e:
            logger.error(f"SendGrid error sending email to {to_email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Email service temporarily unavailable"
            )
        except Exception as e:
            logger.error(f"Unexpected error sending email to {to_email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email"
            )
    
    def validate_email_address(self, email: str) -> bool:
        """
        Basic email validation
        
        Args:
            email: Email address to validate
            
        Returns:
            True if email format is valid
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


def get_email_service() -> EmailService:
    """Dependency injection for email service"""
    return EmailService() 