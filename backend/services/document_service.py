"""
ForgeMinds — Document Service.
CRUD operations for documents backed by PostgreSQL, with KG entity lookup.
Assigned to: RUDRA
"""

import uuid
import hashlib
import os
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from shared.interfaces import (
    DocumentUploadResponse, DocumentResponse, DocumentDetailResponse,
    DocumentStatusResponse, PaginatedResponse, EntityBrief,
)
from shared.enums import UploadStatus, ProcessingStage, EntityType
from shared.constants import MAX_FILE_SIZE_BYTES, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

from backend.db.database import db
from backend.services.knowledge_graph_service import KnowledgeGraphService
from backend.utils.file_utils import (
    save_uploaded_file, get_file_extension, validate_file_type, generate_filename,
)
from backend.utils.logger import get_logger
from backend.config import get_settings

logger = get_logger(__name__)


class DocumentService:
    """Handles document CRUD and processing. Assigned to: RUDRA"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.settings = get_settings()
        self.kg_service = KnowledgeGraphService()

    # ──────────────────────────────────────────────
    # CREATE
    # ──────────────────────────────────────────────

    async def create(self, file, category=None) -> DocumentUploadResponse:
        """Save uploaded file and create document record."""
        original_filename = file.filename or "unknown"

        # Validate file type
        if not validate_file_type(original_filename):
            raise ValueError(f"Unsupported file type: {get_file_extension(original_filename)}")

        # Read content for size check and checksum
        content = await file.read()
        await file.seek(0)  # Reset for save

        if len(content) > MAX_FILE_SIZE_BYTES:
            raise ValueError(
                f"File too large: {len(content)} bytes exceeds "
                f"limit of {MAX_FILE_SIZE_BYTES} bytes"
            )

        # Generate unique filename and save
        stored_filename = generate_filename(original_filename)
        storage_dir = self.settings.STORAGE_PATH
        os.makedirs(storage_dir, exist_ok=True)
        file_path = os.path.join(storage_dir, stored_filename)

        # Save file content directly
        import aiofiles
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        # Compute checksum
        checksum = hashlib.md5(content).hexdigest()

        # Determine file type
        ext = get_file_extension(original_filename).lstrip(".")
        file_type = ext if ext else "unknown"

        # Generate document ID
        doc_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        # Insert into PostgreSQL
        try:
            await db.execute(
                """
                INSERT INTO documents
                    (id, filename, original_filename, file_path, file_type,
                     document_category, file_size_bytes, upload_status,
                     processing_stage, metadata, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """,
                doc_id, stored_filename, original_filename, file_path,
                file_type, category, len(content),
                UploadStatus.PENDING.value, ProcessingStage.UPLOADED.value,
                json.dumps({"checksum": checksum}),
                now, now,
            )
        except Exception as exc:
            self.logger.error("Failed to insert document record: %s", exc)
            # Clean up saved file
            if os.path.exists(file_path):
                os.remove(file_path)
            raise

        self.logger.info("Document created: %s (%s)", doc_id[:8], original_filename)

        return DocumentUploadResponse(
            id=doc_id,
            filename=stored_filename,
            file_type=file_type,
            document_category=category,
            upload_status=UploadStatus.PROCESSING.value,
            created_at=now,
        )

    # ──────────────────────────────────────────────
    # READ
    # ──────────────────────────────────────────────

    async def get(self, document_id: str) -> DocumentDetailResponse:
        """Retrieve a specific document with full details."""
        row = await db.fetch_one(
            "SELECT * FROM documents WHERE id = $1", document_id,
        )
        if not row:
            raise LookupError(f"Document not found: {document_id}")

        # Get entity count and entities
        entities = await self.get_entities(document_id)

        # Get chunk count
        chunk_row = await db.fetch_one(
            "SELECT count(*) AS cnt FROM document_chunks WHERE document_id = $1",
            document_id,
        )
        chunk_count = chunk_row["cnt"] if chunk_row else 0

        return DocumentDetailResponse(
            id=str(row["id"]),
            filename=row["filename"],
            original_filename=row["original_filename"],
            file_type=row["file_type"],
            document_category=row.get("document_category"),
            file_size_bytes=row.get("file_size_bytes"),
            page_count=row.get("page_count"),
            upload_status=row["upload_status"],
            processing_stage=row.get("processing_stage"),
            entity_count=len(entities),
            created_at=row["created_at"],
            extracted_text=row.get("extracted_text"),
            metadata=json.loads(row["metadata"]) if row.get("metadata") else {},
            entities=entities,
            linked_equipment=[],
            chunk_count=chunk_count,
        )

    async def list(
        self,
        page: int = 1,
        limit: int = 20,
        category: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> PaginatedResponse:
        """List documents with filtering and pagination."""
        limit = min(limit, MAX_PAGE_SIZE)
        offset = (page - 1) * limit

        # Build dynamic WHERE
        conditions: List[str] = []
        params: List[Any] = []
        param_idx = 1

        if category:
            conditions.append(f"document_category = ${param_idx}")
            params.append(category)
            param_idx += 1
        if status:
            conditions.append(f"upload_status = ${param_idx}")
            params.append(status)
            param_idx += 1
        if search:
            conditions.append(f"(original_filename ILIKE ${param_idx} OR extracted_text ILIKE ${param_idx})")
            params.append(f"%{search}%")
            param_idx += 1

        where_clause = (" WHERE " + " AND ".join(conditions)) if conditions else ""

        # Count total
        count_row = await db.fetch_one(
            f"SELECT count(*) AS cnt FROM documents{where_clause}", *params,
        )
        total = count_row["cnt"] if count_row else 0

        # Fetch page
        rows = await db.fetch_all(
            f"SELECT * FROM documents{where_clause} "
            f"ORDER BY created_at DESC "
            f"LIMIT ${param_idx} OFFSET ${param_idx + 1}",
            *params, limit, offset,
        )

        items = [
            DocumentResponse(
                id=str(r["id"]),
                filename=r["filename"],
                original_filename=r["original_filename"],
                file_type=r["file_type"],
                document_category=r.get("document_category"),
                file_size_bytes=r.get("file_size_bytes"),
                page_count=r.get("page_count"),
                upload_status=r["upload_status"],
                processing_stage=r.get("processing_stage"),
                entity_count=0,
                created_at=r["created_at"],
            )
            for r in (rows or [])
        ]

        return PaginatedResponse(items=items, total=total, page=page, limit=limit)

    # ──────────────────────────────────────────────
    # DELETE
    # ──────────────────────────────────────────────

    async def delete(self, document_id: str):
        """Delete a document and its file."""
        row = await db.fetch_one(
            "SELECT file_path FROM documents WHERE id = $1", document_id,
        )
        if not row:
            raise LookupError(f"Document not found: {document_id}")

        # Delete DB record (CASCADE deletes chunks)
        await db.execute("DELETE FROM documents WHERE id = $1", document_id)

        # Delete physical file
        file_path = row.get("file_path", "")
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as exc:
                self.logger.warning("Could not delete file %s: %s", file_path, exc)

        self.logger.info("Document deleted: %s", document_id[:8])

    # ──────────────────────────────────────────────
    # ENTITIES
    # ──────────────────────────────────────────────

    async def get_entities(self, document_id: str) -> List[EntityBrief]:
        """Get entities linked to a document, from PostgreSQL kg_entities table."""
        try:
            rows = await db.fetch_all(
                """
                SELECT id, entity_type, name, properties
                FROM kg_entities
                WHERE properties->>'source_document_id' = $1
                """,
                document_id,
            )
            if not rows:
                return []

            return [
                EntityBrief(
                    id=str(r["id"]),
                    entity_type=r["entity_type"],
                    name=r["name"],
                    properties=json.loads(r["properties"]) if isinstance(r["properties"], str) else (r["properties"] or {}),
                )
                for r in rows
            ]
        except Exception as exc:
            self.logger.warning("get_entities query failed: %s", exc)
            return []

    # ──────────────────────────────────────────────
    # STATUS
    # ──────────────────────────────────────────────

    async def get_status(self, document_id: str) -> DocumentStatusResponse:
        """Get processing status of a document."""
        row = await db.fetch_one(
            "SELECT upload_status, processing_stage FROM documents WHERE id = $1",
            document_id,
        )
        if not row:
            raise LookupError(f"Document not found: {document_id}")

        # Calculate progress based on processing stage
        stage = row.get("processing_stage")
        progress_map = {
            ProcessingStage.UPLOADED.value: 10,
            ProcessingStage.OCR_COMPLETE.value: 40,
            ProcessingStage.ENTITIES_EXTRACTED.value: 65,
            ProcessingStage.EMBEDDED.value: 85,
            ProcessingStage.GRAPH_LINKED.value: 100,
        }
        progress = progress_map.get(stage, 0)
        if row["upload_status"] == UploadStatus.COMPLETED.value:
            progress = 100
        elif row["upload_status"] == UploadStatus.FAILED.value:
            progress = 0

        return DocumentStatusResponse(
            upload_status=row["upload_status"],
            processing_stage=stage,
            progress_percent=progress,
        )
