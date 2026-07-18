"""
ForgeMinds — Documents API.
Endpoints for document upload, listing, retrieval, deletion, and status.
Assigned to: RUDRA
"""

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from typing import Optional, List

from shared.interfaces import (
    DocumentUploadResponse, PaginatedResponse, DocumentDetailResponse,
    EntityBrief, DocumentStatusResponse,
)
from backend.services.document_service import DocumentService
from backend.services.ingestion_service import IngestionService
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/documents", tags=['Documents'])

document_service = DocumentService()
ingestion_service = IngestionService()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
):
    """Upload a document for processing. Assigned to: RUDRA"""
    try:
        response = await document_service.create(file, category)
        # Kick off the ingestion pipeline as a background task
        background_tasks.add_task(ingestion_service.process_document, response.id)
        logger.info("Upload accepted, ingestion queued: %s", response.id[:8])
        return response
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.error("Upload failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document upload failed",
        )


@router.get("/", response_model=PaginatedResponse)
async def list_documents(
    page: int = 1,
    limit: int = 20,
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
):
    """Assigned to: RUDRA"""
    try:
        return await document_service.list(
            page=page, limit=limit, category=category,
            status=status_filter, search=search,
        )
    except Exception as exc:
        logger.error("list_documents failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list documents",
        )


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(document_id: str):
    """Assigned to: RUDRA"""
    try:
        return await document_service.get(document_id)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    except Exception as exc:
        logger.error("get_document failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document",
        )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str):
    """Assigned to: RUDRA"""
    try:
        await document_service.delete(document_id)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    except Exception as exc:
        logger.error("delete_document failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document",
        )


@router.get("/{document_id}/entities", response_model=List[EntityBrief])
async def get_document_entities(document_id: str):
    """Assigned to: RUDRA"""
    try:
        return await document_service.get_entities(document_id)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    except Exception as exc:
        logger.error("get_document_entities failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve entities",
        )


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(document_id: str):
    """Assigned to: RUDRA"""
    try:
        return await document_service.get_status(document_id)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    except Exception as exc:
        logger.error("get_document_status failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve status",
        )
