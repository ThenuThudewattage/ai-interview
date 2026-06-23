"""Auth API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.auth import (
    LoginRequest, LoginResponse, RefreshTokenRequest,
    RegisterRequest, RegisterResponse, TokenResponse,
)
from app.core.exceptions import AppException
from app.db.session import get_db
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    try:
        svc = AuthService(db)
        user = await svc.register(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            username=request.username,
        )
        return RegisterResponse(
            user_id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            created_at=user.created_at.isoformat(),
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate and receive JWT tokens."""
    try:
        svc = AuthService(db)
        result = await svc.login(email=request.email, password=request.password)
        return LoginResponse(**result)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token."""
    try:
        svc = AuthService(db)
        result = await svc.refresh_token(request.refresh_token)
        return TokenResponse(**result)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
