from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from shared.interfaces import ChatRequest, ChatResponse, ChatMessageResponse, SessionBrief

router = APIRouter(prefix="/api/chat", tags=['Chat'])

@router.post("/", response_model=ChatResponse)
async def chat(data: ChatRequest):
    """Assigned to: HARSH"""
    # TODO: Implement — HARSH
    raise HTTPException(status_code=501, detail="Not implemented")

@router.get("/history/{session_id}", response_model=List[ChatMessageResponse])
async def get_chat_history(session_id: str):
    """Assigned to: HARSH"""
    # TODO: Implement — HARSH
    raise HTTPException(status_code=501, detail="Not implemented")

@router.get("/sessions", response_model=List[SessionBrief])
async def list_sessions(page: int = 1, limit: int = 20):
    """Assigned to: HARSH"""
    # TODO: Implement — HARSH
    raise HTTPException(status_code=501, detail="Not implemented")
