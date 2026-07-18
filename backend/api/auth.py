"""
ForgeMinds — Authentication API Endpoints.
Provides user login, registration, and active profile retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from shared.interfaces import UserLogin, TokenResponse, UserCreate, UserResponse, ErrorResponse, ErrorDetail
from backend.services.auth_service import auth_service
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/auth", tags=['Authentication'])

# JWT Bearer Token Security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> UserResponse:
    """Dependency injection helper to retrieve and validate the active user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    try:
        return await auth_service.get_current_user(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
)
async def register(data: UserCreate) -> UserResponse:
    """Register a new user account."""
    try:
        return await auth_service.register(data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorDetail(
                code="REGISTRATION_FAILED",
                message=str(exc),
            ).model_dump(),
        )
    except Exception as exc:
        logger.error("User registration failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to an internal error.",
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={401: {"model": ErrorResponse}},
)
async def login(data: UserLogin) -> TokenResponse:
    """Login and receive a JWT access token."""
    try:
        return await auth_service.login(data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorDetail(
                code="UNAUTHORIZED",
                message=str(exc),
            ).model_dump(),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as exc:
        logger.error("User login failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to an internal error.",
        )


@router.get(
    "/me",
    response_model=UserResponse,
    responses={401: {"model": ErrorResponse}},
)
async def me(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Get the profile details of the currently authenticated user."""
    return current_user
