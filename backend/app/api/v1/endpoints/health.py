"""
Health check endpoints for the Men's Circle Management Platform
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any
import asyncio
import redis
from datetime import datetime

from ....config import get_settings

router = APIRouter()

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str
    version: str
    timestamp: datetime
    checks: Dict[str, Any]


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Comprehensive health check endpoint for Docker and monitoring
    
    Returns:
        HealthResponse: Health status with service information and dependency checks
    """
    settings = get_settings()
    checks = {}
    overall_status = "healthy"
    
    # Check Redis connection
    try:
        redis_client = redis.from_url(settings.redis_url)
        redis_client.ping()
        checks["redis"] = {"status": "healthy", "message": "Connection successful"}
    except Exception as e:
        checks["redis"] = {"status": "unhealthy", "message": f"Connection failed: {str(e)}"}
        overall_status = "degraded"
    
    # TODO: Add database health checks when database is configured
    # checks["database"] = await check_database_health()
    # checks["credentials_database"] = await check_credentials_database_health()
    
    return HealthResponse(
        status=overall_status,
        service="mens-circle-backend",
        version=settings.app_version,
        timestamp=datetime.utcnow(),
        checks=checks
    )


@router.get("/health/ready", response_model=Dict[str, str])
async def readiness_check():
    """
    Kubernetes readiness probe endpoint
    
    Returns:
        Dict: Simple ready status
    """
    # TODO: Add comprehensive readiness checks (database connectivity, etc.)
    return {"status": "ready"}


@router.get("/health/live", response_model=Dict[str, str])
async def liveness_check():
    """
    Kubernetes liveness probe endpoint
    
    Returns:
        Dict: Simple alive status
    """
    return {"status": "alive"} 