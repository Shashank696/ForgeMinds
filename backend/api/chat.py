"""
Chat API endpoints for the ForgeMinds copilot.

Provides conversational AI access through session-based chat,
history retrieval, and session listing.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from shared.interfaces import (
    ChatRequest,
    ChatResponse,
    ChatMessageResponse,
    SessionBrief,
    ErrorResponse,
    ErrorDetail,
)
from shared.enums import AgentType
from backend.services.agent_orchestrator import orchestrator
from backend.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/chat", tags=['Chat'])


@router.post(
    "/",
    response_model=ChatResponse,
    responses={500: {"model": ErrorResponse}},
)
async def chat(data: ChatRequest) -> ChatResponse:
    """Send a message to the ForgeMinds copilot.

    Accepts a user message, optionally with a session_id and agent_type hint.
    If no session_id is provided, a new session is created automatically.

    Args:
        data: The chat request containing the user message and optional
              session_id, agent_type, and context_filters.

    Returns:
        ChatResponse with the AI-generated answer, citations, and metadata.

    Raises:
        HTTPException: 500 if an internal error occurs during query routing.
    """
    try:
        session_id = data.session_id or str(uuid.uuid4())
        logger.info(
            "Chat request received — session=%s agent_type=%s message_length=%d",
            session_id,
            data.agent_type.value,
            len(data.message),
        )

        response: ChatResponse = await orchestrator.route_query(
            query=data.message,
            session_id=session_id,
            agent_type=data.agent_type,
            context_filters=data.context_filters,
        )

        logger.info(
            "Chat response generated — session=%s agent=%s confidence=%.2f",
            response.session_id,
            response.agent_type.value,
            response.confidence_score,
        )
        return response

    except NotImplementedError:
        logger.warning("Orchestrator route_query not yet implemented")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=ErrorDetail(
                code="NOT_IMPLEMENTED",
                message="The chat service is not yet available.",
            ).model_dump(),
        )
    except Exception as exc:
        logger.error("Chat endpoint failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorDetail(
                code="CHAT_ERROR",
                message="An error occurred while processing your message.",
                details={"error": str(exc)},
            ).model_dump(),
        )


@router.get(
    "/history/{session_id}",
    response_model=List[ChatMessageResponse],
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def get_chat_history(session_id: str) -> List[ChatMessageResponse]:
    """Retrieve the full message history for a chat session.

    Args:
        session_id: The UUID identifying the chat session.

    Returns:
        Ordered list of ChatMessageResponse objects for the session.

    Raises:
        HTTPException: 404 if the session does not exist, 500 on internal error.
    """
    try:
        logger.info("Fetching chat history for session=%s", session_id)
        history: List[ChatMessageResponse] = await orchestrator.get_chat_history(
            session_id=session_id,
        )
        logger.info(
            "Returned %d messages for session=%s", len(history), session_id
        )
        return history

    except NotImplementedError:
        logger.warning("Orchestrator get_chat_history not yet implemented")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=ErrorDetail(
                code="NOT_IMPLEMENTED",
                message="Chat history retrieval is not yet available.",
            ).model_dump(),
        )
    except Exception as exc:
        logger.error(
            "Failed to fetch chat history for session=%s: %s",
            session_id,
            exc,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorDetail(
                code="HISTORY_ERROR",
                message="An error occurred while retrieving chat history.",
                details={"session_id": session_id, "error": str(exc)},
            ).model_dump(),
        )


@router.get(
    "/sessions",
    response_model=List[SessionBrief],
    responses={500: {"model": ErrorResponse}},
)
async def list_sessions(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
) -> List[SessionBrief]:
    """List all chat sessions with pagination.

    Args:
        page: The page number to retrieve (1-indexed, default 1).
        limit: Maximum number of sessions per page (default 20, max 100).

    Returns:
        List of SessionBrief objects for the requested page.

    Raises:
        HTTPException: 500 on internal error.
    """
    try:
        logger.info("Listing sessions — page=%d limit=%d", page, limit)
        sessions: List[SessionBrief] = await orchestrator.list_sessions(
            page=page,
            limit=limit,
        )
        logger.info("Returned %d sessions", len(sessions))
        return sessions

    except NotImplementedError:
        logger.warning("Orchestrator list_sessions not yet implemented")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=ErrorDetail(
                code="NOT_IMPLEMENTED",
                message="Session listing is not yet available.",
            ).model_dump(),
        )
    except Exception as exc:
        logger.error("Failed to list sessions: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorDetail(
                code="SESSIONS_ERROR",
                message="An error occurred while listing chat sessions.",
                details={"error": str(exc)},
            ).model_dump(),
        )
