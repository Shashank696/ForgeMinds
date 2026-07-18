"""
ForgeMinds — Ingestion Service.
Orchestrates the full document processing pipeline:
Upload → OCR → Text Cleaning → Chunking → Entity Extraction →
Relationship Extraction → Knowledge Graph.
Assigned to: RUDRA
"""

import json
import uuid
import os
from typing import List, Dict, Any

from shared.enums import UploadStatus, ProcessingStage
from shared.constants import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP

from backend.db.database import db
from backend.services.ocr_service import OCRService
from backend.services.entity_extraction import EntityExtractionService
from backend.services.knowledge_graph_service import KnowledgeGraphService
from backend.utils.text_utils import clean_text, chunk_text
from backend.utils.file_utils import get_file_extension
from backend.utils.logger import get_logger
from backend.config import get_settings

logger = get_logger(__name__)


class IngestionService:
    """Handles document ingestion pipeline. Assigned to: RUDRA"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.ocr_service = OCRService()
        self.entity_service = EntityExtractionService()
        self.kg_service = KnowledgeGraphService()
        self.settings = get_settings()

    # ──────────────────────────────────────────────
    # Main pipeline
    # ──────────────────────────────────────────────

    async def process_document(self, document_id: str) -> None:
        """
        Main pipeline to process a document end-to-end.

        Steps:
        1. Fetch document → update status to PROCESSING
        2. OCR / text extraction → store extracted_text
        3. Clean text → chunk → store chunks
        4. Entity extraction per chunk
        5. Relationship extraction across all entities
        6. Link entities + relationships in Neo4j
        7. Update status to COMPLETED
        """
        self.logger.info("Pipeline started for document %s", document_id[:8])

        try:
            # ── Step 1: Fetch document record ──
            doc = await db.fetch_one(
                "SELECT * FROM documents WHERE id = $1", document_id,
            )
            if not doc:
                self.logger.error("Document not found: %s", document_id)
                return

            # Update status to PROCESSING
            await self._update_status(document_id, UploadStatus.PROCESSING)

            # ── Step 2: Text extraction (OCR) ──
            file_path = doc["file_path"]
            file_type = await self.detect_type(file_path)

            ocr_result = await self.ocr_service.extract_text(file_path, file_type)
            raw_text = ocr_result.get("text", "")
            page_count = ocr_result.get("metadata", {}).get("page_count")

            # Store extracted text and page count
            await db.execute(
                """
                UPDATE documents
                SET extracted_text = $2, page_count = $3,
                    processing_stage = $4, updated_at = NOW()
                WHERE id = $1
                """,
                document_id, raw_text, page_count,
                ProcessingStage.OCR_COMPLETE.value,
            )
            self.logger.info("OCR complete for %s (%d chars)", document_id[:8], len(raw_text))

            # ── Step 3: Clean & chunk text ──
            cleaned = clean_text(raw_text)
            chunks = chunk_text(cleaned, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP)

            # Insert chunks into document_chunks table
            for chunk in chunks:
                chunk_id = str(uuid.uuid4())
                chunk["id"] = chunk_id
                await db.execute(
                    """
                    INSERT INTO document_chunks
                        (id, document_id, chunk_index, chunk_text, chunk_metadata)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    chunk_id, document_id, chunk["chunk_index"],
                    chunk["text"],
                    json.dumps({
                        "start_char": chunk["start_char"],
                        "end_char": chunk["end_char"],
                    }),
                )

            self.logger.info("Chunked into %d chunks for %s", len(chunks), document_id[:8])

            # ── Step 4: Entity extraction per chunk ──
            all_entities = []
            for chunk in chunks:
                entities = await self.entity_service.extract_entities(
                    chunk["text"],
                    document_id=document_id,
                    chunk_id=chunk.get("id", ""),
                )
                all_entities.extend(entities)

            # Deduplicate across all chunks
            all_entities = await self.entity_service.resolve_entities(all_entities)

            await self._update_stage(document_id, ProcessingStage.ENTITIES_EXTRACTED)
            self.logger.info(
                "Extracted %d entities for %s", len(all_entities), document_id[:8],
            )

            # Persist entities to kg_entities table
            for entity in all_entities:
                await db.execute(
                    """
                    INSERT INTO kg_entities (id, entity_type, name, properties)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT DO NOTHING
                    """,
                    entity.id, entity.entity_type.value, entity.name,
                    json.dumps(entity.properties),
                )

            # ── Step 5: Relationship extraction ──
            relationships = await self.entity_service.extract_relationships(
                all_entities, cleaned, document_id,
            )

            # Persist relationships to kg_relationships table
            for rel in relationships:
                rel_id = str(uuid.uuid4())
                await db.execute(
                    """
                    INSERT INTO kg_relationships
                        (id, source_id, target_id, relationship_type, properties)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT DO NOTHING
                    """,
                    rel_id,
                    rel["source_entity_id"],
                    rel["target_entity_id"],
                    rel["relationship_type"],
                    json.dumps({
                        "confidence": rel.get("confidence", 0.75),
                        "source_document_id": document_id,
                    }),
                )

            # ── Step 6: Link in Knowledge Graph (Neo4j) ──
            try:
                link_result = await self.kg_service.link_entities(
                    document_id, all_entities, relationships,
                )
                self.logger.info(
                    "KG linked: %d nodes, %d edges for %s",
                    link_result.get("nodes_created", 0),
                    link_result.get("edges_created", 0),
                    document_id[:8],
                )
            except Exception as kg_exc:
                # KG linking failure is non-fatal — log and continue
                self.logger.warning(
                    "KG linking failed for %s (non-fatal): %s",
                    document_id[:8], kg_exc,
                )

            # ── Step 7: Finalise ──
            await self._update_stage(document_id, ProcessingStage.GRAPH_LINKED)
            await self._update_status(document_id, UploadStatus.COMPLETED)

            self.logger.info("Pipeline completed for document %s", document_id[:8])

        except Exception as exc:
            self.logger.error(
                "Pipeline FAILED for document %s: %s", document_id[:8], exc,
                exc_info=True,
            )
            await self._update_status(document_id, UploadStatus.FAILED)

    # ──────────────────────────────────────────────
    # Sub-steps
    # ──────────────────────────────────────────────

    async def detect_type(self, file_path: str) -> str:
        """Detect document type from file extension."""
        ext = get_file_extension(file_path).lstrip(".")
        return ext if ext else "txt"

    async def extract_text(self, document_id: str) -> str:
        """Extract text from a document (delegates to OCR service)."""
        doc = await db.fetch_one(
            "SELECT file_path, file_type FROM documents WHERE id = $1",
            document_id,
        )
        if not doc:
            raise LookupError(f"Document not found: {document_id}")

        result = await self.ocr_service.extract_text(
            doc["file_path"], doc["file_type"],
        )
        text = result.get("text", "")

        # Store extracted text
        await db.execute(
            "UPDATE documents SET extracted_text = $2, updated_at = NOW() WHERE id = $1",
            document_id, text,
        )
        return text

    async def chunk_document(self, document_id: str) -> List[Dict[str, Any]]:
        """Chunk document text and store in document_chunks."""
        doc = await db.fetch_one(
            "SELECT extracted_text FROM documents WHERE id = $1", document_id,
        )
        if not doc or not doc.get("extracted_text"):
            return []

        cleaned = clean_text(doc["extracted_text"])
        chunks = chunk_text(cleaned, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP)

        for chunk in chunks:
            chunk_id = str(uuid.uuid4())
            await db.execute(
                """
                INSERT INTO document_chunks
                    (id, document_id, chunk_index, chunk_text, chunk_metadata)
                VALUES ($1, $2, $3, $4, $5)
                """,
                chunk_id, document_id, chunk["chunk_index"],
                chunk["text"],
                json.dumps({
                    "start_char": chunk["start_char"],
                    "end_char": chunk["end_char"],
                }),
            )

        return chunks

    # ──────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────

    @staticmethod
    async def _update_status(document_id: str, status: UploadStatus) -> None:
        await db.execute(
            "UPDATE documents SET upload_status = $2, updated_at = NOW() WHERE id = $1",
            document_id, status.value,
        )

    @staticmethod
    async def _update_stage(document_id: str, stage: ProcessingStage) -> None:
        await db.execute(
            "UPDATE documents SET processing_stage = $2, updated_at = NOW() WHERE id = $1",
            document_id, stage.value,
        )
