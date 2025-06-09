"""
Main API v1 router for the Men's Circle Management Platform
"""
from fastapi import APIRouter
from .endpoints import health, circles, meetings
from . import transfer_requests
# from .endpoints import auth  # Temporarily commented out

router = APIRouter(prefix="/api/v1")

# Include endpoint routers
router.include_router(health.router, tags=["Health"])
# router.include_router(auth.router, prefix="/auth", tags=["Authentication"])  # Temporarily commented out
router.include_router(circles.router, prefix="/circles", tags=["Circles"])
router.include_router(meetings.router, prefix="/meetings", tags=["Meetings"])
router.include_router(transfer_requests.router, prefix="/transfer-requests", tags=["Transfer Requests"])

# Placeholder for future endpoint routers
# router.include_router(users.router, prefix="/users", tags=["Users"])
# router.include_router(events.router, prefix="/events", tags=["Events"])
# router.include_router(payments.router, prefix="/payments", tags=["Payments"])
# router.include_router(messages.router, prefix="/messages", tags=["Messages"]) 