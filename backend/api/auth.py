from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List
from shared.interfaces import UserLogin, TokenResponse, UserCreate, UserResponse

router = APIRouter(prefix="/api/auth", tags=['Authentication'])

@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    """Assigned to: SP"""
    # TODO: Implement - SP
    raise HTTPException(status_code=501, detail="Not implemented")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate):
    """Assigned to: SP"""
    # TODO: Implement - SP
    raise HTTPException(status_code=501, detail="Not implemented")

@router.get("/me", response_model=UserResponse)
async def me():
    """Assigned to: SP"""
    # TODO: Implement - SP
    raise HTTPException(status_code=501, detail="Not implemented")
