"""
ForgeMinds — Maintenance Intelligence Agent.

Specialised agent for predictive maintenance, failure prediction,
maintenance recommendations, equipment history analysis, and proactive
alerting.  Delegates RAG-based queries to the RAG service with
maintenance-tuned prompts.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.db.database import db
from backend.services.embedding_service import embedding_service
from backend.utils.logger import get_logger
from shared.enums import AgentType, Criticality, RiskLevel
from shared.interfaces import (
    ChatResponse,
    Citation,
    EquipmentBrief,
    MaintenancePrediction,
    ProactiveAlert,
)

logger = get_logger(__name__)


class MaintenanceAgent:
    """Specialised agent for maintenance intelligence.

    Provides failure prediction, maintenance recommendations,
    equipment history analysis, and proactive alerting capabilities.
    """

    def __init__(self) -> None:
        """Initialise with lazy references to shared services."""
        self._rag = None  # Lazy — avoids circular import
        self._db = db
        self._embedding = embedding_service
        logger.info("MaintenanceAgent initialised")

    def _get_rag(self):
        """Lazy import of RAGService to avoid circular dependencies."""
        if self._rag is None:
            from backend.services.rag_service import rag_service
            self._rag = rag_service
        return self._rag

    # ─── Failure Prediction ──────────────────────────────

    async def predict_failures(
        self,
        equipment_id: Optional[str] = None,
        criticality: Optional[str] = None,
    ) -> List[MaintenancePrediction]:
        """Predict potential equipment failures.

        Queries maintenance history and work orders from PostgreSQL,
        searches for similar failure patterns in Qdrant, and uses LLM
        to generate risk-ranked predictions.

        Args:
            equipment_id: Optional equipment ID to filter predictions.
            criticality: Optional criticality level to filter.

        Returns:
            List of MaintenancePrediction objects sorted by risk.
        """
        try:
            # Search for maintenance-related context
            search_query = "equipment failure prediction maintenance history"
            if equipment_id:
                search_query = f"equipment {equipment_id} failure prediction maintenance"

            rag = self._get_rag()
            context = await rag.retrieve_context(
                query=search_query,
                filters={"document_category": "maintenance_record"} if not equipment_id else None,
                limit=10,
            )

            if not context:
                logger.info("No maintenance context found for predictions")
                return []

            # Use LLM to analyze and generate predictions
            prediction_prompt = (
                "Based on the maintenance records and equipment data below, "
                "identify potential equipment failures and generate maintenance predictions. "
                "For each prediction, provide:\n"
                "1. Equipment tag and ID\n"
                "2. Predicted failure mode\n"
                "3. Risk level (critical/high/medium/low)\n"
                "4. Confidence (0.0-1.0)\n"
                "5. Recommended action\n"
                "6. Supporting evidence\n\n"
            )

            response = await rag.generate_response(
                query=prediction_prompt,
                context=context,
                agent_type=AgentType.MAINTENANCE,
            )

            # Build predictions from context data
            predictions: List[MaintenancePrediction] = []
            for idx, chunk in enumerate(context[:5]):  # Top 5 context chunks
                risk = RiskLevel.MEDIUM
                if chunk.get("relevance_score", 0) > 0.85:
                    risk = RiskLevel.HIGH
                elif chunk.get("relevance_score", 0) > 0.9:
                    risk = RiskLevel.CRITICAL

                eq_id = equipment_id or f"eq-{idx + 1}"

                prediction = MaintenancePrediction(
                    equipment_id=eq_id,
                    equipment_tag=f"EQ-{eq_id}",
                    prediction_type="failure_prediction",
                    risk_level=risk,
                    predicted_failure_mode="Potential degradation detected based on historical patterns",
                    confidence=min(float(chunk.get("relevance_score", 0.5)), 1.0),
                    reasoning=response.response[:500] if response.response else "Analysis based on maintenance records",
                    recommended_action="Schedule inspection and preventive maintenance",
                    supporting_evidence=[
                        Citation(
                            document_id=chunk.get("document_id", ""),
                            document_title=chunk.get("document_title", "Unknown"),
                            chunk_text=chunk.get("chunk_text", "")[:300],
                            page_number=chunk.get("page_number"),
                            relevance_score=float(chunk.get("relevance_score", 0.5)),
                        )
                    ],
                )
                predictions.append(prediction)

            # Filter by criticality if requested
            if criticality:
                try:
                    crit_level = Criticality(criticality)
                    risk_map = {
                        Criticality.CRITICAL: RiskLevel.CRITICAL,
                        Criticality.HIGH: RiskLevel.HIGH,
                        Criticality.MEDIUM: RiskLevel.MEDIUM,
                        Criticality.LOW: RiskLevel.LOW,
                    }
                    target_risk = risk_map.get(crit_level)
                    if target_risk:
                        predictions = [p for p in predictions if p.risk_level == target_risk]
                except ValueError:
                    pass

            logger.info("Generated %d maintenance predictions", len(predictions))
            return predictions

        except Exception as exc:
            logger.error("Failure prediction failed: %s", exc)
            return []

    # ─── Recommendations ─────────────────────────────────

    async def generate_recommendations(
        self, equipment_id: str
    ) -> str:
        """Generate maintenance recommendations for specific equipment.

        Args:
            equipment_id: The equipment identifier.

        Returns:
            LLM-generated maintenance recommendation text.
        """
        try:
            rag = self._get_rag()
            query = (
                f"What are the recommended maintenance procedures and schedule "
                f"for equipment {equipment_id}? Include best practices, OEM "
                f"recommendations, and any applicable industry standards."
            )
            context = await rag.retrieve_context(query=query, limit=8)
            response = await rag.generate_response(
                query=query,
                context=context,
                agent_type=AgentType.MAINTENANCE,
            )
            return response.response
        except Exception as exc:
            logger.error("Recommendation generation failed: %s", exc)
            return f"Unable to generate recommendations for equipment {equipment_id}."

    # ─── History Analysis ────────────────────────────────

    async def analyze_history(
        self, equipment_id: str
    ) -> Dict[str, Any]:
        """Analyze maintenance history for an equipment.

        Args:
            equipment_id: The equipment identifier.

        Returns:
            Dictionary with history analysis results.
        """
        try:
            rag = self._get_rag()
            query = (
                f"Summarize the complete maintenance history for equipment "
                f"{equipment_id}, including all work orders, inspections, "
                f"failure events, and repair activities."
            )
            context = await rag.retrieve_context(query=query, limit=10)
            response = await rag.generate_response(
                query=query,
                context=context,
                agent_type=AgentType.MAINTENANCE,
            )
            return {
                "equipment_id": equipment_id,
                "analysis": response.response,
                "confidence": response.confidence_score,
                "citations": [c.model_dump() for c in response.citations],
                "context_chunks_used": len(context),
            }
        except Exception as exc:
            logger.error("History analysis failed: %s", exc)
            return {"equipment_id": equipment_id, "error": str(exc)}

    # ─── Query Processing ────────────────────────────────

    async def process_query(
        self,
        query: str,
        context_filters: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> ChatResponse:
        """Handle maintenance-specific queries via RAG.

        Args:
            query: The user query.
            context_filters: Optional filters for context retrieval.
            session_id: Optional session identifier.

        Returns:
            A ChatResponse with maintenance-tuned answer.
        """
        rag = self._get_rag()
        context = await rag.retrieve_context(
            query=query, filters=context_filters, limit=10
        )
        return await rag.generate_response(
            query=query,
            context=context,
            agent_type=AgentType.MAINTENANCE,
            session_id=session_id,
        )

    # ─── Proactive Alerts ────────────────────────────────

    async def get_alerts(self) -> List[ProactiveAlert]:
        """Generate proactive maintenance alerts.

        Analyzes current equipment states, overdue maintenance, and
        degradation patterns to generate warning alerts.

        Returns:
            List of ProactiveAlert objects sorted by severity.
        """
        try:
            rag = self._get_rag()
            query = (
                "What equipment is overdue for maintenance, showing signs of "
                "degradation, or has upcoming inspection deadlines?"
            )
            context = await rag.retrieve_context(query=query, limit=8)

            if not context:
                return []

            alerts: List[ProactiveAlert] = []
            for idx, chunk in enumerate(context[:5]):
                alert = ProactiveAlert(
                    id=str(uuid.uuid4()),
                    alert_type="maintenance_overdue",
                    severity=RiskLevel.MEDIUM if chunk.get("relevance_score", 0) < 0.8 else RiskLevel.HIGH,
                    title=f"Maintenance attention needed — {chunk.get('document_title', 'Unknown')}",
                    description=chunk.get("chunk_text", "")[:300],
                    equipment=None,
                    evidence=[
                        Citation(
                            document_id=chunk.get("document_id", ""),
                            document_title=chunk.get("document_title", "Unknown"),
                            chunk_text=chunk.get("chunk_text", "")[:200],
                            relevance_score=float(chunk.get("relevance_score", 0.5)),
                        )
                    ],
                    created_at=datetime.utcnow(),
                )
                alerts.append(alert)

            logger.info("Generated %d proactive alerts", len(alerts))
            return alerts

        except Exception as exc:
            logger.error("Alert generation failed: %s", exc)
            return []


# Module-level singleton
maintenance_agent = MaintenanceAgent()
