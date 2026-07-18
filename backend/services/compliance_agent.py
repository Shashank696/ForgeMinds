"""
ForgeMinds — Compliance Intelligence Agent.

Specialised agent for regulatory compliance assessment, gap detection,
evidence package generation, and compliance status reporting.
Supports Indian industrial regulations (OISD, PESO, Factories Act, BIS)
and other international standards.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.db.database import db
from backend.utils.logger import get_logger
from shared.enums import AgentType, ComplianceStatus, RiskLevel
from shared.interfaces import (
    ChatResponse,
    Citation,
    ComplianceAssessRequest,
    ComplianceGap,
    ComplianceOverview,
    EquipmentBrief,
)

logger = get_logger(__name__)


class ComplianceAgent:
    """Specialised agent for compliance tracking and assessment.

    Provides compliance status overview, gap detection, targeted
    compliance assessment, evidence package generation, and
    compliance-specific query handling.
    """

    def __init__(self) -> None:
        """Initialise with lazy references to shared services."""
        self._rag = None  # Lazy — avoids circular import
        self._db = db
        logger.info("ComplianceAgent initialised")

    def _get_rag(self):
        """Lazy import of RAGService to avoid circular dependencies."""
        if self._rag is None:
            from backend.services.rag_service import rag_service
            self._rag = rag_service
        return self._rag

    # ─── Compliance Status ───────────────────────────────

    async def get_status(self) -> ComplianceOverview:
        """Retrieve overall compliance posture.

        Aggregates compliance scores across all tracked regulations
        by querying the compliance_records table and contextual
        analysis of regulatory documents.

        Returns:
            ComplianceOverview with overall score and per-regulation breakdown.
        """
        try:
            # Try fetching from database first
            by_regulation: List[Dict[str, Any]] = []

            try:
                sql = """
                    SELECT regulation_code, regulation_name,
                           compliance_status, COUNT(*) as record_count
                    FROM compliance_records
                    GROUP BY regulation_code, regulation_name, compliance_status
                    ORDER BY regulation_code
                """
                rows = await self._db.fetch_all(sql)
                if rows:
                    regulation_data: Dict[str, Dict[str, Any]] = {}
                    for row in rows:
                        r = row if isinstance(row, dict) else dict(row) if row else {}
                        code = r.get("regulation_code", "")
                        if code not in regulation_data:
                            regulation_data[code] = {
                                "regulation_code": code,
                                "regulation_name": r.get("regulation_name", code),
                                "compliant_count": 0,
                                "total_count": 0,
                            }
                        status = r.get("compliance_status", "")
                        count = int(r.get("record_count", 0))
                        regulation_data[code]["total_count"] += count
                        if status == "compliant":
                            regulation_data[code]["compliant_count"] += count

                    for data in regulation_data.values():
                        total = data["total_count"]
                        compliant = data["compliant_count"]
                        score = (compliant / total * 100) if total > 0 else 0.0
                        by_regulation.append({
                            "regulation_code": data["regulation_code"],
                            "regulation_name": data["regulation_name"],
                            "compliance_score": round(score, 1),
                            "compliant": compliant,
                            "total": total,
                        })
            except Exception:
                # Database not available — use contextual analysis
                pass

            # If no DB data, use RAG to provide an assessment
            if not by_regulation:
                rag = self._get_rag()
                context = await rag.retrieve_context(
                    query="compliance status overview regulations OISD PESO",
                    filters={"document_category": "regulatory"},
                    limit=8,
                )

                if context:
                    by_regulation = [
                        {
                            "regulation_code": "ASSESSMENT_PENDING",
                            "regulation_name": "Comprehensive Assessment Required",
                            "compliance_score": 0.0,
                            "note": "Full compliance records not yet loaded",
                            "documents_found": len(context),
                        }
                    ]

            # Compute overall score
            if by_regulation:
                scores = [r.get("compliance_score", 0.0) for r in by_regulation if isinstance(r.get("compliance_score"), (int, float))]
                overall = sum(scores) / len(scores) if scores else 0.0
            else:
                overall = 0.0

            return ComplianceOverview(
                overall_compliance_score=round(overall, 1),
                by_regulation=by_regulation,
            )

        except Exception as exc:
            logger.error("Compliance status retrieval failed: %s", exc)
            return ComplianceOverview(
                overall_compliance_score=0.0,
                by_regulation=[],
            )

    # ─── Gap Detection ───────────────────────────────────

    async def detect_gaps(self) -> List[ComplianceGap]:
        """Detect compliance gaps across all tracked regulations.

        Scans compliance_records for non-compliant items and enriches
        findings with document context via RAG.

        Returns:
            List of ComplianceGap objects describing detected gaps.
        """
        try:
            gaps: List[ComplianceGap] = []

            # Try DB-based gap detection
            try:
                sql = """
                    SELECT id, regulation_code, regulation_name,
                           requirement_text, compliance_status,
                           gap_description, remediation_action, due_date
                    FROM compliance_records
                    WHERE compliance_status IN ('non_compliant', 'partially_compliant')
                    ORDER BY due_date ASC
                """
                rows = await self._db.fetch_all(sql)
                if rows:
                    for row in rows:
                        r = row if isinstance(row, dict) else dict(row) if row else {}
                        try:
                            status = ComplianceStatus(r.get("compliance_status", "unknown"))
                        except ValueError:
                            status = ComplianceStatus.UNKNOWN

                        gaps.append(ComplianceGap(
                            id=str(r.get("id", uuid.uuid4())),
                            regulation_code=r.get("regulation_code", ""),
                            regulation_name=r.get("regulation_name", ""),
                            requirement_text=r.get("requirement_text", ""),
                            compliance_status=status,
                            gap_description=r.get("gap_description"),
                            remediation_action=r.get("remediation_action"),
                            affected_equipment=[],
                            due_date=r.get("due_date"),
                        ))
            except Exception:
                pass

            # If no DB results, try RAG-based gap analysis
            if not gaps:
                rag = self._get_rag()
                context = await rag.retrieve_context(
                    query="compliance gaps non-compliant regulatory requirements",
                    limit=8,
                )
                if context:
                    response = await rag.generate_response(
                        query="Identify any compliance gaps or non-compliant areas based on the available documents.",
                        context=context,
                        agent_type=AgentType.COMPLIANCE,
                    )
                    # Create a single summary gap from the RAG analysis
                    gaps.append(ComplianceGap(
                        id=str(uuid.uuid4()),
                        regulation_code="RAG_ANALYSIS",
                        regulation_name="AI-Detected Compliance Concerns",
                        requirement_text="Based on document analysis",
                        compliance_status=ComplianceStatus.UNKNOWN,
                        gap_description=response.response[:500],
                        remediation_action="Review the identified areas and verify compliance status",
                        affected_equipment=[],
                    ))

            logger.info("Detected %d compliance gaps", len(gaps))
            return gaps

        except Exception as exc:
            logger.error("Compliance gap detection failed: %s", exc)
            return []

    # ─── Targeted Assessment ─────────────────────────────

    async def assess_compliance(
        self, request: ComplianceAssessRequest
    ) -> List[ComplianceGap]:
        """Assess compliance for a specific regulation.

        Retrieves regulation requirements from the document corpus and
        compliance records from PostgreSQL, then uses LLM to evaluate
        compliance status per equipment.

        Args:
            request: ComplianceAssessRequest with regulation_code and
                     optional equipment_ids.

        Returns:
            List of ComplianceGap objects for the targeted assessment.
        """
        try:
            rag = self._get_rag()
            regulation_code = request.regulation_code

            # Search for regulation requirements
            query = (
                f"What are the requirements of regulation {regulation_code}? "
                f"What are the compliance criteria and inspection requirements?"
            )
            context = await rag.retrieve_context(
                query=query,
                filters={"document_category": "regulatory"},
                limit=10,
            )

            if not context:
                # Broaden search
                context = await rag.retrieve_context(
                    query=f"regulation {regulation_code} requirements compliance",
                    limit=8,
                )

            # Generate assessment via LLM
            assessment_query = (
                f"Assess compliance with regulation {regulation_code}. "
                f"Identify any gaps, non-compliant areas, and required actions. "
                f"For each gap found, specify: requirement, current status, "
                f"gap description, and remediation action."
            )
            response = await rag.generate_response(
                query=assessment_query,
                context=context,
                agent_type=AgentType.COMPLIANCE,
            )

            # Build gap results
            gaps: List[ComplianceGap] = []
            gaps.append(ComplianceGap(
                id=str(uuid.uuid4()),
                regulation_code=regulation_code,
                regulation_name=f"Assessment: {regulation_code}",
                requirement_text=f"Comprehensive assessment of {regulation_code}",
                compliance_status=ComplianceStatus.UNKNOWN,
                gap_description=response.response[:800],
                remediation_action="Review assessment findings and take corrective action",
                affected_equipment=[],
            ))

            logger.info(
                "Compliance assessment for %s: %d gaps identified",
                regulation_code,
                len(gaps),
            )
            return gaps

        except Exception as exc:
            logger.error("Compliance assessment failed: %s", exc)
            return []

    # ─── Evidence Package ────────────────────────────────

    async def generate_evidence(
        self, regulation_code: str
    ) -> Dict[str, Any]:
        """Generate an evidence package for a regulatory audit.

        Assembles all relevant inspection reports, procedures,
        compliance records, and document citations for the specified
        regulation code.

        Args:
            regulation_code: The regulation identifier.

        Returns:
            Dictionary containing the evidence package.
        """
        try:
            rag = self._get_rag()
            query = (
                f"Find all evidence, inspection reports, compliance records, "
                f"and documentation related to regulation {regulation_code}."
            )
            context = await rag.retrieve_context(query=query, limit=15)

            documents: List[Dict[str, Any]] = []
            for chunk in context:
                documents.append({
                    "document_id": chunk.get("document_id", ""),
                    "document_title": chunk.get("document_title", ""),
                    "page_number": chunk.get("page_number"),
                    "excerpt": chunk.get("chunk_text", "")[:500],
                    "relevance_score": chunk.get("relevance_score", 0.0),
                })

            evidence = {
                "regulation_code": regulation_code,
                "generated_at": datetime.utcnow().isoformat(),
                "total_documents": len(documents),
                "documents": documents,
                "compliance_records": [],  # Populated from DB when available
                "assessment_summary": f"Evidence package for {regulation_code}",
            }

            # Try to add compliance records from DB
            try:
                sql = """
                    SELECT * FROM compliance_records
                    WHERE regulation_code = $1
                    ORDER BY created_at DESC
                """
                rows = await self._db.fetch_all(sql, regulation_code)
                if rows:
                    evidence["compliance_records"] = [
                        dict(r) if not isinstance(r, dict) else r
                        for r in rows
                    ]
            except Exception:
                pass

            logger.info(
                "Evidence package for %s: %d documents",
                regulation_code,
                len(documents),
            )
            return evidence

        except Exception as exc:
            logger.error("Evidence generation failed: %s", exc)
            return {
                "regulation_code": regulation_code,
                "error": str(exc),
                "documents": [],
            }

    # ─── Query Processing ────────────────────────────────

    async def process_query(
        self,
        query: str,
        context_filters: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> ChatResponse:
        """Handle compliance-specific queries via RAG.

        Args:
            query: The user query.
            context_filters: Optional filters for context retrieval.
            session_id: Optional session identifier.

        Returns:
            A ChatResponse with compliance-tuned answer.
        """
        rag = self._get_rag()
        context = await rag.retrieve_context(
            query=query, filters=context_filters, limit=10
        )
        return await rag.generate_response(
            query=query,
            context=context,
            agent_type=AgentType.COMPLIANCE,
            session_id=session_id,
        )


# Module-level singleton
compliance_agent = ComplianceAgent()
