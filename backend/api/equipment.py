"""
ForgeMinds — Equipment API.
Endpoints for equipment listing, detail, maintenance & failure history.
Assigned to: RUDRA
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional

from shared.interfaces import PaginatedResponse, EquipmentDetailResponse
from shared.enums import EquipmentType, EquipmentStatus, Criticality
from backend.db.database import db
from backend.db.neo4j_client import neo4j_db
from backend.utils.logger import get_logger

import json

logger = get_logger(__name__)
router = APIRouter(prefix="/api/equipment", tags=['Equipment'])


@router.get("/", response_model=PaginatedResponse)
async def list_equipment(
    type: Optional[str] = None,
    status_filter: Optional[str] = None,
    criticality: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
):
    """Assigned to: RUDRA"""
    try:
        offset = (page - 1) * limit
        conditions = []
        params = []
        idx = 1

        if type:
            conditions.append(f"equipment_type = ${idx}")
            params.append(type)
            idx += 1
        if status_filter:
            conditions.append(f"status = ${idx}")
            params.append(status_filter)
            idx += 1
        if criticality:
            conditions.append(f"criticality = ${idx}")
            params.append(criticality)
            idx += 1
        if search:
            conditions.append(f"(name ILIKE ${idx} OR tag ILIKE ${idx} OR description ILIKE ${idx})")
            params.append(f"%{search}%")
            idx += 1

        where = (" WHERE " + " AND ".join(conditions)) if conditions else ""

        count_row = await db.fetch_one(
            f"SELECT count(*) AS cnt FROM equipment{where}", *params,
        )
        total = count_row["cnt"] if count_row else 0

        rows = await db.fetch_all(
            f"SELECT * FROM equipment{where} ORDER BY tag LIMIT ${idx} OFFSET ${idx + 1}",
            *params, limit, offset,
        )

        items = [
            {
                "id": str(r["id"]),
                "tag": r["tag"],
                "name": r["name"],
                "equipment_type": r["equipment_type"],
                "description": r.get("description"),
                "location": r.get("location"),
                "plant": r.get("plant"),
                "unit": r.get("unit"),
                "criticality": r.get("criticality", "medium"),
                "status": r.get("status", "operational"),
                "manufacturer": r.get("manufacturer"),
            }
            for r in (rows or [])
        ]

        return PaginatedResponse(items=items, total=total, page=page, limit=limit)
    except Exception as exc:
        logger.error("list_equipment failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list equipment",
        )


@router.get("/{equipment_id}", response_model=EquipmentDetailResponse)
async def get_equipment(equipment_id: str):
    """Assigned to: RUDRA"""
    try:
        row = await db.fetch_one(
            "SELECT * FROM equipment WHERE id = $1", equipment_id,
        )
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found")

        # Get related documents
        doc_rows = await db.fetch_all(
            """
            SELECT d.* FROM documents d
            WHERE d.extracted_text ILIKE $1 OR d.extracted_text ILIKE $2
            LIMIT 20
            """,
            f"%{row['tag']}%", f"%{row['name']}%",
        )
        related_docs = [
            {
                "id": str(d["id"]),
                "filename": d["filename"],
                "original_filename": d["original_filename"],
                "file_type": d["file_type"],
                "document_category": d.get("document_category"),
                "file_size_bytes": d.get("file_size_bytes"),
                "page_count": d.get("page_count"),
                "upload_status": d["upload_status"],
                "processing_stage": d.get("processing_stage"),
                "entity_count": 0,
                "created_at": d["created_at"],
            }
            for d in (doc_rows or [])
        ]

        # Get maintenance records
        maint_rows = await db.fetch_all(
            "SELECT * FROM maintenance_records WHERE equipment_id = $1 ORDER BY date DESC LIMIT 50",
            equipment_id,
        )
        maintenance_records = [
            {"id": str(m["id"]), "date": str(m["date"]), "details": m["details"]}
            for m in (maint_rows or [])
        ]

        return EquipmentDetailResponse(
            id=str(row["id"]),
            tag=row["tag"],
            name=row["name"],
            equipment_type=row["equipment_type"],
            description=row.get("description"),
            location=row.get("location"),
            plant=row.get("plant"),
            unit=row.get("unit"),
            criticality=row.get("criticality", "medium"),
            status=row.get("status", "operational"),
            manufacturer=row.get("manufacturer"),
            model=row.get("model"),
            serial_number=row.get("serial_number"),
            installation_date=row.get("installation_date"),
            specifications={},
            related_documents=related_docs,
            maintenance_records=maintenance_records,
            failure_events=[],
            compliance_records=[],
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("get_equipment failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve equipment",
        )


@router.get("/{equipment_id}/maintenance-history")
async def get_maintenance_history(equipment_id: str):
    """Assigned to: RUDRA"""
    try:
        rows = await db.fetch_all(
            """
            SELECT mr.*, wo.title AS work_order_title, wo.type AS work_order_type
            FROM maintenance_records mr
            LEFT JOIN work_orders wo ON mr.work_order_id = wo.id
            WHERE mr.equipment_id = $1
            ORDER BY mr.date DESC
            LIMIT 100
            """,
            equipment_id,
        )

        records = [
            {
                "id": str(r["id"]),
                "date": str(r["date"]),
                "details": r["details"],
                "work_order_title": r.get("work_order_title"),
                "work_order_type": r.get("work_order_type"),
            }
            for r in (rows or [])
        ]

        return {"records": records}
    except Exception as exc:
        logger.error("get_maintenance_history failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve maintenance history",
        )


@router.get("/{equipment_id}/failure-history")
async def get_failure_history(equipment_id: str):
    """Assigned to: RUDRA"""
    try:
        # Look up equipment tag for Neo4j search
        row = await db.fetch_one(
            "SELECT tag, name FROM equipment WHERE id = $1", equipment_id,
        )
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found")

        # Query Neo4j for failure events linked to this equipment
        events = []
        try:
            records = await neo4j_db.run_query(
                """
                MATCH (e:Equipment)-[:AFFECTS|CAUSES]-(f:FailureEvent)
                WHERE e.name CONTAINS $name OR e.name CONTAINS $tag
                RETURN f.id AS id, f.name AS name, f.entity_type AS entity_type,
                       f.confidence AS confidence
                LIMIT 50
                """,
                {"name": row["name"], "tag": row["tag"]},
            )
            events = [
                {
                    "id": r.get("id", ""),
                    "description": r.get("name", ""),
                    "entity_type": r.get("entity_type", "failure_event"),
                    "confidence": r.get("confidence"),
                }
                for r in records
            ]
        except Exception as neo_exc:
            logger.warning("Neo4j failure history query failed: %s", neo_exc)

        return {"events": events}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("get_failure_history failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve failure history",
        )
