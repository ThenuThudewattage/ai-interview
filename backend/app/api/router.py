"""Main API router — assembles all sub-routers."""
from fastapi import APIRouter

from app.api.v1 import auth, users, interviews, learning, analytics, websocket

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(interviews.router)
api_router.include_router(learning.router)
api_router.include_router(analytics.router)
api_router.include_router(websocket.router)
