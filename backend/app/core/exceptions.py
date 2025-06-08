"""
Custom exceptions for the Men's Circle Management Platform.

Defines application-specific exceptions for better error handling and user experience.
"""
from typing import Any, Dict, Optional


class BaseApplicationException(Exception):
    """Base exception class for all application-specific exceptions."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseApplicationException):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.field = field
        super().__init__(message, details)


class PermissionDenied(BaseApplicationException):
    """Raised when a user lacks required permissions for an action."""
    
    def __init__(self, message: str = "Permission denied", required_permission: Optional[str] = None, 
                 user_id: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        self.required_permission = required_permission
        self.user_id = user_id
        super().__init__(message, details)


class AuthenticationError(BaseApplicationException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(BaseApplicationException):
    """Raised when authorization fails."""
    pass


class ResourceNotFound(BaseApplicationException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: Any, details: Optional[Dict[str, Any]] = None):
        self.resource_type = resource_type
        self.resource_id = resource_id
        message = f"{resource_type} with id '{resource_id}' not found"
        super().__init__(message, details)


class DuplicateResourceError(BaseApplicationException):
    """Raised when attempting to create a resource that already exists."""
    
    def __init__(self, resource_type: str, identifier: str, details: Optional[Dict[str, Any]] = None):
        self.resource_type = resource_type
        self.identifier = identifier
        message = f"{resource_type} with identifier '{identifier}' already exists"
        super().__init__(message, details)


class BusinessRuleViolation(BaseApplicationException):
    """Raised when a business rule is violated."""
    
    def __init__(self, rule: str, message: str, details: Optional[Dict[str, Any]] = None):
        self.rule = rule
        super().__init__(message, details)


class CapacityExceeded(BusinessRuleViolation):
    """Raised when capacity limits are exceeded (e.g., circle member limits)."""
    
    def __init__(self, resource_type: str, current: int, maximum: int, details: Optional[Dict[str, Any]] = None):
        self.resource_type = resource_type
        self.current = current
        self.maximum = maximum
        message = f"{resource_type} capacity exceeded: {current}/{maximum}"
        super().__init__("capacity_exceeded", message, details)


class ConfigurationError(BaseApplicationException):
    """Raised when there's a configuration error."""
    pass


class ExternalServiceError(BaseApplicationException):
    """Raised when an external service call fails."""
    
    def __init__(self, service: str, message: str, status_code: Optional[int] = None, 
                 details: Optional[Dict[str, Any]] = None):
        self.service = service
        self.status_code = status_code
        super().__init__(f"{service} error: {message}", details) 