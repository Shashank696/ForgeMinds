"""
ForgeMinds — Agent Orchestrator.

Central routing hub for the multi-agent system.  Classifies user intent,
dispatches queries to the appropriate specialist agent, manages chat
history, and aggregates multi-agent responses when needed.
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.db.database import db
from backend.utils.logger import get_logger
from shared.enums import AgentType
from shared.interfaces import (
    ChatMessageResponse,
    ChatResponse,
    SessionBrief,
)

logger = get_logger(__name__)


class AgentOrchestrator:
    """Routes queries to specialised agents.

    Provides intent classification (keyword + LLM), query routing,
    chat history persistence, session management, and multi-agent
    response aggregation.
    """

    def __init__(self) -> None:
        """Initialise with lazy references to agents and services."""
        self._rag = None
        self._maintenance = None
        self._compliance = None
        self._rca = None
        self._lessons = None
        self._db = db
        logger.info("AgentOrchestrator initialised")

    # ─── Lazy Agent Accessors ────────────────────────────

    def _get_rag(self):
        if self._rag is None:
            from backend.services.rag_service import rag_service
            self._rag = rag_service
        return self._rag

    def _get_maintenance(self):
        if self._maintenance is None:
            from backend.services.maintenance_agent import maintenance_agent
            self._maintenance = maintenance_agent
        return self._maintenance

    def _get_compliance(self):
        if self._compliance is None:
            from backend.services.compliance_agent import compliance_agent
            self._compliance = compliance_agent
        return self._compliance

    def _get_rca(self):
        if self._rca is None:
            from backend.services.rca_agent import rca_agent
            self._rca = rca_agent
        return self._rca

    def _get_lessons(self):
        if self._lessons is None:
            from backend.services.lessons_agent import lessons_agent
            self._lessons = lessons_agent
        return self._lessons

    # ─── Intent Classification ───────────────────────────

    async def classify_intent(self, query: str) -> AgentType:
        """Classify a user query to determine which agent should handle it.

        Uses keyword scoring as a fast path, falling back to LLM-based
        classification when keywords are ambiguous.

        Args:
            query: The user query string.

        Returns:
            The classified AgentType.
        """
        rag = self._get_rag()
        return await rag._classify_intent(query)

    # ─── Query Routing ───────────────────────────────────

    async def route_query(
        self,
        query: str,
        session_id: Optional[str] = None,
        agent_type: AgentType = AgentType.AUTO,
        context_filters: Optional[Dict[str, Any]] = None,
    ) -> ChatResponse:
        """Route a user query to the appropriate agent.

        If agent_type is AUTO, the orchestrator first classifies the
        query intent.  Then it dispatches to the matching specialist
        agent or the general RAG pipeline.  Chat messages are saved to
        PostgreSQL for history retrieval.

        Args:
            query: The user message.
            session_id: Session UUID (generated if not provided).
            agent_type: Explicit agent hint or AUTO for classification.
            context_filters: Optional metadata filters for retrieval.

        Returns:
            A fully populated ChatResponse.
        """
        effective_session = session_id or str(uuid.uuid4())

        # Auto-classify if needed
        if agent_type == AgentType.AUTO:
            agent_type = await self.classify_intent(query)
            logger.info("Auto-classified query as %s", agent_type.value)

        # Save the user message
        await self._save_chat_message(
            session_id=effective_session,
            role="user",
            message=query,
            agent_type=agent_type,
        )

        # Dispatch to the appropriate agent
        try:
            response = await self._dispatch(
                query=query,
                agent_type=agent_type,
                context_filters=context_filters,
                session_id=effective_session,
            )
        except Exception as exc:
            logger.error(
                "Agent dispatch failed for type=%s: %s", agent_type.value, exc
            )
            # Fallback to general RAG
            response = await self._dispatch(
                query=query,
                agent_type=AgentType.GENERAL,
                context_filters=context_filters,
                session_id=effective_session,
            )

        # Ensure session_id is set
        response.session_id = effective_session

        # Save the assistant response
        await self._save_chat_message(
            session_id=effective_session,
            role="assistant",
            message=response.response,
            agent_type=response.agent_type,
            citations=response.citations,
            confidence=response.confidence_score,
        )

        return response

    async def _dispatch(
        self,
        query: str,
        agent_type: AgentType,
        context_filters: Optional[Dict[str, Any]],
        session_id: str,
    ) -> ChatResponse:
        """Dispatch to the correct agent's process_query method.

        Args:
            query: The user query.
            agent_type: The target agent type.
            context_filters: Optional metadata filters.
            session_id: The session identifier.

        Returns:
            ChatResponse from the dispatched agent.
        """
        if agent_type == AgentType.MAINTENANCE:
            return await self._get_maintenance().process_query(
                query=query,
                context_filters=context_filters,
                session_id=session_id,
            )
        elif agent_type == AgentType.COMPLIANCE:
            return await self._get_compliance().process_query(
                query=query,
                context_filters=context_filters,
                session_id=session_id,
            )
        elif agent_type == AgentType.RCA:
            return await self._get_rca().process_query(
                query=query,
                context_filters=context_filters,
                session_id=session_id,
            )
        elif agent_type == AgentType.LESSONS_LEARNED:
            return await self._get_lessons().process_query(
                query=query,
                context_filters=context_filters,
                session_id=session_id,
            )
        else:
            # GENERAL or any other — use RAG directly
            rag = self._get_rag()
            context = await rag.retrieve_context(
                query=query, filters=context_filters, limit=10
            )
            return await rag.generate_response(
                query=query,
                context=context,
                agent_type=AgentType.GENERAL,
                session_id=session_id,
            )

    # ─── Response Aggregation ────────────────────────────

    async def aggregate_response(
        self, responses: List[ChatResponse]
    ) -> ChatResponse:
        """Aggregate responses from multiple agents.

        Merges response texts, combines citations (deduplicated),
        averages confidence scores, and unions follow-up suggestions.

        Args:
            responses: List of ChatResponse from different agents.

        Returns:
            A single merged ChatResponse.
        """
        if not responses:
            return ChatResponse(
                session_id=str(uuid.uuid4()),
                response="No responses to aggregate.",
                agent_type=AgentType.GENERAL,
                confidence_score=0.0,
            )

        if len(responses) == 1:
            return responses[0]

        # Merge response texts
        merged_parts: List[str] = []
        for resp in responses:
            agent_label = resp.agent_type.value.replace("_", " ").title()
            merged_parts.append(
                f"**{agent_label} Perspective:**\n{resp.response}"
            )
        merged_text = "\n\n---\n\n".join(merged_parts)

        # Combine and deduplicate citations
        seen_doc_ids: set = set()
        all_citations = []
        for resp in responses:
            for cit in resp.citations:
                key = f"{cit.document_id}:{cit.page_number}"
                if key not in seen_doc_ids:
                    seen_doc_ids.add(key)
                    all_citations.append(cit)

        # Average confidence
        avg_confidence = sum(r.confidence_score for r in responses) / len(responses)

        # Union follow-ups (deduplicated)
        seen_followups: set = set()
        all_followups: List[str] = []
        for resp in responses:
            for fu in resp.suggested_followups:
                if fu not in seen_followups:
                    seen_followups.add(fu)
                    all_followups.append(fu)

        # Combine related entities
        seen_ents: set = set()
        all_entities = []
        for resp in responses:
            for ent in resp.related_entities:
                if ent.id not in seen_ents:
                    seen_ents.add(ent.id)
                    all_entities.append(ent)

        return ChatResponse(
            session_id=responses[0].session_id,
            response=merged_text,
            agent_type=AgentType.GENERAL,
            confidence_score=round(avg_confidence, 2),
            citations=all_citations[:15],
            related_entities=all_entities[:10],
            suggested_followups=all_followups[:5],
            metadata={
                "aggregated_from": [r.agent_type.value for r in responses],
                "agent_count": len(responses),
            },
        )

    # ─── Chat History ────────────────────────────────────

    async def _save_chat_message(
        self,
        session_id: str,
        role: str,
        message: str,
        agent_type: AgentType,
        citations: Optional[list] = None,
        confidence: Optional[float] = None,
    ) -> None:
        """Persist a chat message to PostgreSQL.

        Args:
            session_id: The session identifier.
            role: 'user' or 'assistant'.
            message: The message text.
            agent_type: The agent type that handled the query.
            citations: Optional list of Citation objects.
            confidence: Optional confidence score.
        """
        try:
            citations_json = "[]"
            if citations:
                citations_json = json.dumps(
                    [c.model_dump() for c in citations], default=str
                )

            sql = """
                INSERT INTO chat_history
                    (id, session_id, role, message, agent_type,
                     citations, confidence_score, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """
            await self._db.execute(
                sql,
                str(uuid.uuid4()),
                session_id,
                role,
                message,
                agent_type.value,
                citations_json,
                confidence or 0.0,
                datetime.utcnow(),
            )
        except Exception as exc:
            # Non-fatal — log and continue
            logger.warning("Failed to save chat message: %s", exc)

    async def get_chat_history(
        self, session_id: str
    ) -> List[ChatMessageResponse]:
        """Retrieve conversation history for a session.

        Args:
            session_id: The session identifier.

        Returns:
            Ordered list of ChatMessageResponse objects.
        """
        try:
            sql = """
                SELECT id, role, message, agent_type,
                       citations, confidence_score, created_at
                FROM chat_history
                WHERE session_id = $1
                ORDER BY created_at ASC
            """
            rows = await self._db.fetch_all(sql, session_id)

            if not rows:
                return []

            messages: List[ChatMessageResponse] = []
            for row in rows:
                r = row if isinstance(row, dict) else dict(row) if row else {}
                # Parse citations JSON
                citations_data = r.get("citations", "[]")
                try:
                    from shared.interfaces import Citation
                    citations_list = json.loads(citations_data) if isinstance(citations_data, str) else citations_data
                    citations = [Citation(**c) for c in (citations_list or [])]
                except Exception:
                    citations = []

                # Parse agent type
                agent_type = None
                if r.get("agent_type"):
                    try:
                        agent_type = AgentType(r["agent_type"])
                    except ValueError:
                        pass

                messages.append(ChatMessageResponse(
                    id=str(r.get("id", "")),
                    role=r.get("role", "user"),
                    message=r.get("message", ""),
                    agent_type=agent_type,
                    citations=citations,
                    confidence_score=r.get("confidence_score"),
                    created_at=r.get("created_at", datetime.utcnow()),
                ))

            return messages

        except Exception as exc:
            logger.warning("Failed to fetch chat history: %s", exc)
            return []

    async def list_sessions(
        self, page: int = 1, limit: int = 20
    ) -> List[SessionBrief]:
        """List chat sessions with pagination.

        Args:
            page: Page number (1-indexed).
            limit: Results per page.

        Returns:
            List of SessionBrief objects.
        """
        try:
            offset = (page - 1) * limit
            sql = """
                SELECT session_id,
                       MIN(message) AS first_message,
                       COUNT(*) AS message_count,
                       MAX(created_at) AS last_message_at,
                       MAX(agent_type) AS agent_type
                FROM chat_history
                GROUP BY session_id
                ORDER BY last_message_at DESC
                LIMIT $1 OFFSET $2
            """
            rows = await self._db.fetch_all(sql, limit, offset)

            if not rows:
                return []

            sessions: List[SessionBrief] = []
            for row in rows:
                r = row if isinstance(row, dict) else dict(row) if row else {}

                agent_type = None
                if r.get("agent_type"):
                    try:
                        agent_type = AgentType(r["agent_type"])
                    except ValueError:
                        pass

                # Derive title from first message
                first_msg = r.get("first_message", "")
                title = first_msg[:80] + "…" if len(first_msg) > 80 else first_msg

                sessions.append(SessionBrief(
                    session_id=r.get("session_id", ""),
                    title=title or None,
                    message_count=int(r.get("message_count", 0)),
                    last_message_at=r.get("last_message_at", datetime.utcnow()),
                    agent_type=agent_type,
                ))

            return sessions

        except Exception as exc:
            logger.warning("Failed to list sessions: %s", exc)
            return []


# Module-level singleton
orchestrator = AgentOrchestrator()
