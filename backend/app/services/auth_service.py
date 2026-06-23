"""Authentication service."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password, decode_token
from app.models.user import User, UserPreferences
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def register(
        self, email: str, password: str, full_name: str, username: str
    ) -> User:
        # Check uniqueness
        if await self.user_repo.get_by_email(email):
            raise ConflictException(f"Email already registered: {email}")
        if await self.user_repo.get_by_username(username):
            raise ConflictException(f"Username already taken: {username}")

        user = await self.user_repo.create(
            email=email,
            username=username,
            password_hash=hash_password(password),
            full_name=full_name,
        )

        # Create default preferences
        prefs_repo = UserRepository(self.session)
        self.session.add(UserPreferences(user_id=user.id))
        await self.session.flush()

        return user

    async def login(self, email: str, password: str) -> dict:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")
        if user.account_status != "active":
            raise UnauthorizedException("Account is not active")

        # Update last login
        await self.user_repo.update(user, last_login_at=datetime.now(timezone.utc))

        return {
            "access_token": create_access_token(str(user.id), user.email),
            "refresh_token": create_refresh_token(str(user.id)),
            "token_type": "Bearer",
            "expires_in": 3600,
            "user": {
                "user_id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
            },
        }

    async def refresh_token(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid refresh token")

        user = await self.user_repo.get_by_id(payload["sub"])
        if not user:
            raise UnauthorizedException("User not found")

        return {
            "access_token": create_access_token(str(user.id), user.email),
            "token_type": "Bearer",
            "expires_in": 3600,
        }

    async def get_current_user(self, token: str) -> Optional[User]:
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            return None
        return await self.user_repo.get_by_id(payload["sub"])
