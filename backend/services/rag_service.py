"""
ForgeMinds — RAG Service & LLM Abstraction Layer.

Provides the core Retrieval-Augmented Generation pipeline including:
- LLMClient: Gemini API abstraction with fallback support
- RAGService: Full RAG pipeline with caching, citation extraction,
  confidence scoring, and contextual follow-up generation
"""

import asyncio
import hashlib
import json
import os
import re
from typing import Any, Dict, List, Optional

import google.generativeai as genai

from backend.db.redis_client import cache
from backend.services.search_service import SearchService
from backend.utils.logger import get_logger
from shared.constants import (
    DEFAULT_LLM_MODEL,
    DEFAULT_SEARCH_LIMIT,
    FALLBACK_LLM_MODEL,
    LLM_CACHE_TTL_SECONDS,
    LLM_TEMPERATURE,
    MAX_LLM_TOKENS,
)
from shared.enums import AgentType
from shared.interfaces import ChatResponse, Citation, EntityBrief

logger = get_logger(__name__)

# ═══════════════════════════════════════════════════════
#  System Prompt Templates per Agent Type
# ═══════════════════════════════════════════════════════

_SYSTEM_PROMPTS: Dict[AgentType, str] = {
    AgentType.GENERAL: (
        "You are ForgeMinds, an AI-powered Industrial Knowledge Intelligence assistant. "
        "You help engineers, operators, and managers find information across industrial documents, "
        "maintenance records, compliance regulations, and equipment data. "
        "Answer questions accurately using the provided context. "
        "Always cite your sources using bracket notation like [1], [2], etc. "
        "If the context does not contain enough information, say so clearly."
    ),
    AgentType.MAINTENANCE: (
        "You are ForgeMinds Maintenance Intelligence Agent — an expert in industrial equipment "
        "health, predictive maintenance, failure analysis, and maintenance planning. "
        "Focus on equipment condition assessment, maintenance scheduling, and failure prevention. "
        "When discussing equipment, reference specific tags, types, and criticality levels. "
        "Always cite your sources using bracket notation like [1], [2], etc. "
        "Provide actionable maintenance recommendations backed by evidence."
    ),
    AgentType.COMPLIANCE: (
        "You are ForgeMinds Compliance Intelligence Agent — an expert in industrial regulations "
        "including OISD standards, PESO rules, the Factories Act 1948, BIS standards, and other "
        "Indian industrial safety regulations. "
        "Focus on compliance status, gap identification, and remediation actions. "
        "Always cite the specific regulation clauses and sections. "
        "Cite your sources using bracket notation like [1], [2], etc. "
        "Provide clear compliance assessments with supporting evidence."
    ),
    AgentType.RCA: (
        "You are ForgeMinds Root Cause Analysis Agent — an expert in the 5-Why methodology, "
        "fishbone analysis, and systematic failure investigation for industrial equipment. "
        "Analyze failures methodically, identify root causes with confidence levels, "
        "and recommend corrective and preventive actions. "
        "Cite your sources using bracket notation like [1], [2], etc. "
        "Reference similar historical incidents when available."
    ),
    AgentType.LESSONS_LEARNED: (
        "You are ForgeMinds Lessons Learned Agent — an expert in analyzing historical incidents, "
        "identifying recurring patterns, and synthesizing actionable lessons for industrial operations. "
        "Focus on pattern recognition across incidents, knowledge transfer, and proactive warnings. "
        "Cite your sources using bracket notation like [1], [2], etc. "
        "Highlight common themes and provide recommendations to prevent recurrence."
    ),
}

# Keyword sets for fast-path intent classification
_INTENT_KEYWORDS: Dict[AgentType, List[str]] = {
    AgentType.MAINTENANCE: [
        "maintenance", "repair", "failure", "pump", "valve", "compressor",
        "inspection", "overhaul", "vibration", "bearing", "seal", "lubrication",
        "breakdown", "preventive", "corrective", "predictive", "work order",
        "equipment health", "shutdown", "turnaround",
    ],
    AgentType.COMPLIANCE: [
        "compliance", "regulation", "audit", "oisd", "peso", "factory act",
        "factories act", "bis", "statutory", "inspection certificate",
        "license", "permit", "regulatory", "standard", "non-compliant",
        "compliant", "gap", "certification",
    ],
    AgentType.RCA: [
        "root cause", "why did", "failure analysis", "investigate",
        "5 why", "five why", "fishbone", "ishikawa", "cause",
        "what caused", "fault tree", "incident investigation",
    ],
    AgentType.LESSONS_LEARNED: [
        "lessons", "learned", "incident", "historical", "pattern",
        "similar", "recurring", "trend", "past event", "knowledge base",
        "lessons learned", "what happened",
    ],
}

# Hedging words that reduce confidence
_HEDGING_WORDS = [
    "might", "possibly", "unclear", "I don't have enough",
    "uncertain", "may not", "it's possible", "not sure",
    "insufficient", "cannot determine", "limited information",
]


# ═══════════════════════════════════════════════════════
#  LLM Client
# ═══════════════════════════════════════════════════════


class LLMClient:
    """Abstraction layer for Google Gemini LLM API calls.

    Supports primary model with automatic fallback, async execution
    via thread pooling, and structured error handling.
    """

    def __init__(self) -> None:
        """Initialise the LLM client with Gemini API configuration."""
        self._api_key = os.getenv("GEMINI_API_KEY", "")
        self._primary_model = DEFAULT_LLM_MODEL
        self._fallback_model = FALLBACK_LLM_MODEL
        self._configured = False

        if self._api_key:
            try:
                genai.configure(api_key=self._api_key)
                self._configured = True
                logger.info("Gemini API configured with model=%s", self._primary_model)
            except Exception as exc:
                logger.error("Failed to configure Gemini API: %s", exc)
        else:
            logger.warning("GEMINI_API_KEY not set — LLM calls will return fallback responses")

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Generate a response from the Gemini LLM.

        Args:
            prompt: The user/task prompt to send.
            system_instruction: Optional system-level instruction for the model.
            temperature: Sampling temperature override; defaults to LLM_TEMPERATURE.

        Returns:
            The generated text response.
        """
        if not self._configured:
            logger.warning("LLM not configured — returning placeholder response")
            return self._fallback_response(prompt)

        temp = temperature if temperature is not None else LLM_TEMPERATURE

        # Try primary model first, then fallback
        for model_name in [self._primary_model, self._fallback_model]:
            try:
                response_text = await self._call_model(
                    model_name, prompt, system_instruction, temp
                )
                return response_text
            except Exception as exc:
                logger.warning(
                    "LLM call failed for model=%s: %s", model_name, exc
                )
                if model_name == self._fallback_model:
                    logger.error("Both primary and fallback LLM models failed")
                    return self._fallback_response(prompt)

        return self._fallback_response(prompt)

    async def _call_model(
        self,
        model_name: str,
        prompt: str,
        system_instruction: Optional[str],
        temperature: float,
    ) -> str:
        """Execute a synchronous Gemini API call on a background thread.

        Args:
            model_name: Gemini model identifier.
            prompt: The prompt text.
            system_instruction: Optional system instruction.
            temperature: Sampling temperature.

        Returns:
            Generated text from the model.
        """
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=MAX_LLM_TOKENS,
        )

        model_kwargs: Dict[str, Any] = {"model_name": model_name}
        if system_instruction:
            model_kwargs["system_instruction"] = system_instruction

        model = genai.GenerativeModel(**model_kwargs)

        def _sync_generate() -> str:
            result = model.generate_content(
                prompt,
                generation_config=generation_config,
            )
            return result.text

        text = await asyncio.to_thread(_sync_generate)
        logger.info("LLM response generated via model=%s, length=%d", model_name, len(text))
        return text

    @staticmethod
    def _fallback_response(prompt: str) -> str:
        """Return a graceful fallback when the LLM is unavailable.

        Args:
            prompt: The original prompt (used for context-aware fallback).

        Returns:
            A helpful fallback message.
        """
        return (
            "I'm currently unable to generate a detailed AI response because the LLM service "
            "is unavailable. However, I can still help you search through the knowledge base. "
            "Please try again shortly, or refine your query for a document search."
        )


# ═══════════════════════════════════════════════════════
#  RAG Service
# ═══════════════════════════════════════════════════════


class RAGService:
    """Retrieval-Augmented Generation service.

    Orchestrates the full RAG pipeline: context retrieval via hybrid search,
    prompt construction, LLM generation, citation extraction, confidence
    scoring, follow-up generation, and Redis response caching.
    """

    def __init__(self) -> None:
        """Initialise RAGService with search, LLM, and cache dependencies."""
        self.search_service = SearchService()
        self.llm_client = LLMClient()
        self._cache = cache
        logger.info("RAGService initialised")

    # ─── Context Retrieval ───────────────────────────────

    async def retrieve_context(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = DEFAULT_SEARCH_LIMIT,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant document chunks via hybrid search.

        Args:
            query: The user query to search for.
            filters: Optional filter criteria for the search.
            limit: Maximum number of results to return.

        Returns:
            List of context dicts with chunk_text, document_id,
            document_title, page_number, relevance_score, and entities.
        """
        try:
            results = await self.search_service.hybrid_search(
                query=query, filters=filters, limit=limit
            )
            context = []
            for item in results:
                context.append({
                    "chunk_text": item.chunk_text,
                    "document_id": item.document_id,
                    "document_title": item.document_title,
                    "page_number": item.page_number,
                    "relevance_score": item.relevance_score,
                    "entities": [
                        ent.model_dump() for ent in item.entities
                    ] if item.entities else [],
                })
            logger.info("Retrieved %d context chunks for query='%s'", len(context), query[:80])
            return context

        except NotImplementedError:
            logger.warning("Search service not implemented — returning empty context")
            return []
        except Exception as exc:
            logger.error("Context retrieval failed: %s", exc)
            return []

    # ─── Intent Classification ───────────────────────────

    async def _classify_intent(self, query: str) -> AgentType:
        """Classify user query intent to route to the correct agent.

        Uses keyword matching as a fast path. Falls back to LLM-based
        classification only when keyword matching is ambiguous.

        Args:
            query: The user query string.

        Returns:
            The classified AgentType.
        """
        query_lower = query.lower()

        # Fast path: keyword scoring
        scores: Dict[AgentType, int] = {}
        for agent_type, keywords in _INTENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                scores[agent_type] = score

        if scores:
            best = max(scores, key=scores.get)  # type: ignore[arg-type]
            second_best_score = sorted(scores.values(), reverse=True)[1] if len(scores) > 1 else 0
            # Clear winner — no ambiguity
            if scores[best] >= 2 or (scores[best] == 1 and second_best_score == 0):
                logger.info("Intent classified via keywords: %s (score=%d)", best.value, scores[best])
                return best

        # Ambiguous or no keywords matched — try LLM classification
        try:
            classification_prompt = (
                "Classify the following industrial query into exactly one category. "
                "Reply with ONLY the category name, nothing else.\n\n"
                "Categories:\n"
                "- MAINTENANCE: equipment health, repairs, failures, pumps, valves, compressors, inspections\n"
                "- COMPLIANCE: regulations, audits, OISD, PESO, Factories Act, BIS standards\n"
                "- RCA: root cause analysis, failure investigation, why something failed\n"
                "- LESSONS_LEARNED: historical incidents, patterns, lessons, recurring issues\n"
                "- GENERAL: anything else\n\n"
                f"Query: {query}\n\nCategory:"
            )
            result = await self.llm_client.generate(classification_prompt, temperature=0.1)
            result_clean = result.strip().upper().replace(" ", "_")

            agent_map = {
                "MAINTENANCE": AgentType.MAINTENANCE,
                "COMPLIANCE": AgentType.COMPLIANCE,
                "RCA": AgentType.RCA,
                "LESSONS_LEARNED": AgentType.LESSONS_LEARNED,
                "GENERAL": AgentType.GENERAL,
            }
            classified = agent_map.get(result_clean, AgentType.GENERAL)
            logger.info("Intent classified via LLM: %s", classified.value)
            return classified

        except Exception as exc:
            logger.warning("LLM intent classification failed: %s — defaulting to GENERAL", exc)
            return AgentType.GENERAL

    # ─── Prompt Construction ─────────────────────────────

    async def build_prompt(
        self,
        query: str,
        context: List[Dict[str, Any]],
        agent_type: AgentType = AgentType.GENERAL,
    ) -> str:
        """Build a structured prompt with context for the LLM.

        Args:
            query: The user query.
            context: List of retrieved context dicts.
            agent_type: The agent type to tailor the system instruction.

        Returns:
            The fully constructed prompt string.
        """
        # Context section with numbered references
        if context:
            context_parts = []
            for idx, chunk in enumerate(context, 1):
                title = chunk.get("document_title", "Unknown")
                page = chunk.get("page_number")
                text = chunk.get("chunk_text", "")
                page_str = f", Page: {page}" if page else ""
                context_parts.append(f"[{idx}] Source: {title}{page_str}\n{text}")
            context_section = "\n\n".join(context_parts)
        else:
            context_section = "No relevant documents were found in the knowledge base."

        prompt = (
            "### CONTEXT (Retrieved Documents)\n\n"
            f"{context_section}\n\n"
            "### INSTRUCTIONS\n"
            "- Answer the user's question based ONLY on the context above.\n"
            "- Cite sources using bracket notation: [1], [2], etc.\n"
            "- If the context is insufficient, state that clearly.\n"
            "- Be concise, accurate, and actionable.\n\n"
            "### USER QUESTION\n"
            f"{query}"
        )
        return prompt

    # ─── Response Generation ─────────────────────────────

    async def generate_response(
        self,
        query: str,
        context: List[Dict[str, Any]],
        agent_type: AgentType = AgentType.GENERAL,
        session_id: Optional[str] = None,
    ) -> ChatResponse:
        """Generate a complete RAG response.

        Orchestrates prompt building, LLM call, citation extraction,
        confidence scoring, and follow-up generation.

        Args:
            query: The user query.
            context: Retrieved context chunks.
            agent_type: Agent type for prompt specialisation.
            session_id: Optional session identifier.

        Returns:
            A fully populated ChatResponse.
        """
        import uuid

        effective_session = session_id or str(uuid.uuid4())

        # Check cache first
        cache_key = self._make_cache_key(query, agent_type)
        cached = await self._check_cache(cache_key)
        if cached:
            cached.session_id = effective_session
            logger.info("Returning cached response for query='%s'", query[:80])
            return cached

        # Build prompt and generate
        prompt = await self.build_prompt(query, context, agent_type)
        system_instruction = _SYSTEM_PROMPTS.get(agent_type, _SYSTEM_PROMPTS[AgentType.GENERAL])
        response_text = await self.llm_client.generate(
            prompt=prompt,
            system_instruction=system_instruction,
        )

        # Post-process
        citations = await self._extract_citations(response_text, context)
        confidence = await self._compute_confidence(response_text, context)
        followups = await self._generate_followups(query, response_text, agent_type)

        # Collect related entities from context
        related_entities: List[EntityBrief] = []
        seen_entity_ids: set = set()
        for chunk in context:
            for ent_data in chunk.get("entities", []):
                ent_id = ent_data.get("id", "")
                if ent_id and ent_id not in seen_entity_ids:
                    seen_entity_ids.add(ent_id)
                    try:
                        related_entities.append(EntityBrief(**ent_data))
                    except Exception:
                        pass

        chat_response = ChatResponse(
            session_id=effective_session,
            response=response_text,
            agent_type=agent_type,
            confidence_score=confidence,
            citations=citations,
            related_entities=related_entities[:10],
            suggested_followups=followups,
            metadata={
                "context_chunks_used": len(context),
                "model": self.llm_client._primary_model,
            },
        )

        # Cache the response
        await self._cache_response(cache_key, chat_response)

        return chat_response

    # ─── Citation Extraction ─────────────────────────────

    async def _extract_citations(
        self, response_text: str, context: List[Dict[str, Any]]
    ) -> List[Citation]:
        """Parse bracket-notation citations from the response and map to source chunks.

        Args:
            response_text: The LLM-generated response text.
            context: The context chunks used for generation.

        Returns:
            List of Citation objects referenced in the response.
        """
        citations: List[Citation] = []
        # Find all [N] references
        ref_pattern = re.compile(r"\[(\d+)\]")
        referenced_indices = set()
        for match in ref_pattern.finditer(response_text):
            try:
                idx = int(match.group(1))
                referenced_indices.add(idx)
            except ValueError:
                continue

        for idx in sorted(referenced_indices):
            # Context is 1-indexed in the prompt
            context_idx = idx - 1
            if 0 <= context_idx < len(context):
                chunk = context[context_idx]
                citations.append(Citation(
                    document_id=chunk.get("document_id", ""),
                    document_title=chunk.get("document_title", "Unknown"),
                    chunk_text=chunk.get("chunk_text", "")[:500],
                    page_number=chunk.get("page_number"),
                    relevance_score=float(chunk.get("relevance_score", 0.5)),
                ))

        logger.info("Extracted %d citations from response", len(citations))
        return citations

    # ─── Confidence Scoring ──────────────────────────────

    async def _compute_confidence(
        self, response_text: str, context: List[Dict[str, Any]]
    ) -> float:
        """Compute a heuristic confidence score for the generated response.

        Scoring rules:
        - Base score: 0.5
        - +0.1 per citation found (max +0.3)
        - +0.1 if average context relevance > 0.7
        - -0.1 if hedging language detected
        - Clamped to [0.0, 1.0]

        Args:
            response_text: The LLM-generated response.
            context: The context chunks used.

        Returns:
            Confidence score between 0.0 and 1.0.
        """
        score = 0.5

        # Citation bonus
        ref_pattern = re.compile(r"\[(\d+)\]")
        citation_count = len(set(ref_pattern.findall(response_text)))
        score += min(citation_count * 0.1, 0.3)

        # Context relevance bonus
        if context:
            avg_relevance = sum(
                float(c.get("relevance_score", 0.0)) for c in context
            ) / len(context)
            if avg_relevance > 0.7:
                score += 0.1

        # Hedging penalty
        response_lower = response_text.lower()
        if any(hedge in response_lower for hedge in _HEDGING_WORDS):
            score -= 0.1

        # Clamp
        return max(0.0, min(1.0, round(score, 2)))

    # ─── Follow-up Generation ────────────────────────────

    async def _generate_followups(
        self, query: str, response_text: str, agent_type: AgentType
    ) -> List[str]:
        """Generate contextual follow-up question suggestions.

        Uses rule-based generation per agent type for speed.

        Args:
            query: The original user query.
            response_text: The generated response.
            agent_type: The current agent type.

        Returns:
            List of 2-3 follow-up question strings.
        """
        followups: List[str] = []

        if agent_type == AgentType.MAINTENANCE:
            followups = [
                "What is the recommended maintenance schedule for this equipment?",
                "Are there any similar equipment units at risk of the same failure?",
                "What spare parts should be kept in inventory for this issue?",
            ]
        elif agent_type == AgentType.COMPLIANCE:
            followups = [
                "What are the upcoming compliance deadlines?",
                "Which equipment is most at risk for non-compliance?",
                "What documentation is needed for the next audit?",
            ]
        elif agent_type == AgentType.RCA:
            followups = [
                "Have there been similar failures in other units?",
                "What preventive measures can avoid this failure in the future?",
                "What is the estimated cost impact of this failure?",
            ]
        elif agent_type == AgentType.LESSONS_LEARNED:
            followups = [
                "What recurring patterns have been identified across incidents?",
                "Which equipment types are most frequently involved in incidents?",
                "What corrective actions from past incidents are still pending?",
            ]
        else:
            followups = [
                "Can you provide more details on this topic?",
                "What related equipment or documents should I review?",
                "Are there any safety considerations I should be aware of?",
            ]

        return followups[:3]

    # ─── Caching ─────────────────────────────────────────

    async def _cache_response(self, cache_key: str, response: ChatResponse) -> None:
        """Store a ChatResponse in Redis cache.

        Args:
            cache_key: The cache key string.
            response: The ChatResponse to cache.
        """
        try:
            serialised = response.model_dump_json()
            await self._cache.set(cache_key, serialised, expire=LLM_CACHE_TTL_SECONDS)
            logger.info("Cached LLM response with key=%s", cache_key[:40])
        except Exception as exc:
            logger.warning("Failed to cache response: %s", exc)

    async def _check_cache(self, cache_key: str) -> Optional[ChatResponse]:
        """Check Redis for a cached ChatResponse.

        Args:
            cache_key: The cache key to look up.

        Returns:
            The cached ChatResponse if found, else None.
        """
        try:
            cached_data = await self._cache.get(cache_key)
            if cached_data:
                response = ChatResponse.model_validate_json(cached_data)
                logger.info("Cache hit for key=%s", cache_key[:40])
                return response
        except Exception as exc:
            logger.warning("Cache lookup failed: %s", exc)
        return None

    @staticmethod
    def _make_cache_key(query: str, agent_type: AgentType) -> str:
        """Generate a deterministic cache key from query and agent type.

        Args:
            query: The user query.
            agent_type: The agent type.

        Returns:
            A prefixed SHA-256 hash string.
        """
        raw = f"{query.strip().lower()}|{agent_type.value}"
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return f"rag:response:{digest}"


# Module-level singleton
rag_service = RAGService()
