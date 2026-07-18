"""
ForgeMinds — Authentication Service.
Handles user registration, login, JWT token generation, and token validation.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from shared.enums import UserRole
from shared.interfaces import UserCreate, UserResponse, UserLogin, TokenResponse
from backend.config import get_settings
from backend.db.database import db
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Handles authentication and user management."""

    def __init__(self):
        self.settings = get_settings()

    async def register(self, data: UserCreate) -> UserResponse:
        """Register a new user in the PostgreSQL database."""
        # Check if user already exists
        existing = await db.fetch_one("SELECT * FROM users WHERE email = $1", data.email)
        if existing:
            raise ValueError(f"User with email {data.email} already exists")

        hashed_password = await self.hash_password(data.password)
        user_id = str(uuid.uuid4())

        query = """
            INSERT INTO users (id, email, password_hash, full_name, role, department)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id, email, full_name, role, department, created_at
        """
        try:
            logger.info("Registering user: %s (%s)", data.full_name, data.email)
            row = await db.fetch_one(
                query,
                user_id,
                data.email,
                hashed_password,
                data.full_name,
                data.role.value if hasattr(data.role, "value") else str(data.role),
                data.department,
            )
            return UserResponse(
                id=str(row["id"]),
                email=row["email"],
                full_name=row["full_name"],
                role=UserRole(row["role"]),
                department=row["department"],
                created_at=row["created_at"],
            )
        except Exception as exc:
            logger.error("Failed to register user: %s", exc)
            raise

    async def login(self, data: UserLogin) -> TokenResponse:
        """Authenticate user credentials and return a JWT access token."""
        row = await db.fetch_one("SELECT * FROM users WHERE email = $1", data.email)
        if not row or not pwd_context.verify(data.password, row["password_hash"]):
            raise ValueError("Invalid email or password")

        # Update last login time
        await db.execute("UPDATE users SET last_login = NOW() WHERE id = $1", row["id"])

        user_resp = UserResponse(
            id=str(row["id"]),
            email=row["email"],
            full_name=row["full_name"],
            role=UserRole(row["role"]),
            department=row["department"],
            created_at=row["created_at"],
        )

        # Generate JWT token
        expire = datetime.utcnow() + timedelta(minutes=self.settings.JWT_EXPIRY_MINUTES)
        payload = {
            "sub": str(row["id"]),
            "email": row["email"],
            "role": row["role"],
            "exp": expire,
        }
        token = jwt.encode(payload, self.settings.JWT_SECRET_KEY, algorithm=self.settings.JWT_ALGORITHM)

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=user_resp,
        )

    async def get_current_user(self, token: str) -> UserResponse:
        """Get the current authenticated user from token payload."""
        payload = await self.verify_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token payload")

        row = await db.fetch_one("SELECT * FROM users WHERE id = $1 AND is_active = TRUE", user_id)
        if not row:
            raise ValueError("User not found or inactive")

        return UserResponse(
            id=str(row["id"]),
            email=row["email"],
            full_name=row["full_name"],
            role=UserRole(row["role"]),
            department=row["department"],
            created_at=row["created_at"],
        )

    async def verify_token(self, token: str) -> dict:
        """Verify JWT token and return decoded payload."""
        try:
            payload = jwt.decode(
                token,
                self.settings.JWT_SECRET_KEY,
                algorithms=[self.settings.JWT_ALGORITHM],
            )
            return payload
        except JWTError as exc:
            logger.warning("Token verification failed: %s", exc)
            raise ValueError("Invalid token or token expired")

    async def hash_password(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)


auth_service = AuthService()
