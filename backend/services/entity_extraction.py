"""
ForgeMinds — Entity Extraction Service.
Rule-based + regex extraction of industrial entities and relationships.
Assigned to: RUDRA
"""

import re
import uuid
from typing import List, Dict, Any, Optional

from shared.enums import EntityType
from shared.interfaces import EntityBrief
from backend.utils.text_utils import extract_sentences
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class EntityExtractionService:
    """Extracts structured entities from text. Assigned to: RUDRA"""

    # ════════════════════════════════════════════════
    # Regex pattern banks
    # ════════════════════════════════════════════════

    EQUIPMENT_TAG_PATTERNS = [
        re.compile(r"\b([A-Z]{1,4}-\d{3,6}[A-Z]?)\b"),                       # P-1001A, V-2001
        re.compile(r"\b(?:TAG|Tag)[:\s]*([A-Z0-9][A-Z0-9\-]+)\b"),           # TAG: ABC-123
    ]
    EQUIPMENT_KEYWORD_PATTERN = re.compile(
        r"\b((?:centrifugal\s+)?(?:pump|motor|valve|compressor|turbine|generator|"
        r"boiler|heat\s*exchanger|reactor|vessel|tank|conveyor|crane|transformer|"
        r"piping|instrument|sensor|actuator|bearing|seal|impeller|coupling|gearbox|"
        r"condenser|evaporator|separator|filter|dryer|mixer|agitator|blower|fan)s?)\b",
        re.IGNORECASE,
    )

    STANDARD_PATTERNS = [
        re.compile(r"\b((?:ISO|ASME|API|ASTM|IEC|IEEE|NFPA|OSHA|EN|DIN|BS)\s*\d+[\w.:\-/]*)\b", re.IGNORECASE),
        re.compile(r"\b(IS\s*\d+(?::\d{4})?(?:\s*Part\s*\d+)?)\b"),            # Indian Standards
        re.compile(r"\b(ANSI[\s/]\w+[\s.]\d+[\w.\-]*)\b", re.IGNORECASE),
    ]

    REGULATION_PATTERNS = [
        re.compile(r"\b(Factory\s*Act(?:\s*\d{4})?(?:,?\s*Section\s*\d+)?)\b", re.IGNORECASE),
        re.compile(r"\b(OISD[\s\-]*(?:Standard\s*)?\d+)\b", re.IGNORECASE),
        re.compile(r"\b(PESO[\s\-]*\w*)\b"),
        re.compile(r"\b((?:CPCB|SPCB|MoEFCC|BIS)(?:\s+\w+)*)\b"),
    ]

    DATE_PATTERNS = [
        re.compile(r"\b(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\b"),
        re.compile(
            r"\b((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
            r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
            r"\s+\d{1,2},?\s+\d{4})\b",
            re.IGNORECASE,
        ),
        re.compile(r"\b(\d{4}-\d{2}-\d{2})\b"),
    ]

    PARAMETER_PATTERNS = [
        re.compile(
            r"\b(\d+\.?\d*\s*(?:°[CF]|bar|psi|kPa|MPa|rpm|Hz|kW|MW|m³/h|kg/h|"
            r"L/min|mm/s|m/s|kg/cm²|atm))\b",
            re.IGNORECASE,
        ),
    ]

    PERSONNEL_PATTERNS = [
        re.compile(
            r"(?:Prepared\s+by|Approved\s+by|Reviewed\s+by|Inspected\s+by|"
            r"Engineer|Operator|Technician|Manager|Supervisor|Inspector)"
            r"[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
        ),
    ]

    FAILURE_MODE_KEYWORDS = [
        "failure", "leak", "leakage", "crack", "cracking", "corrosion",
        "erosion", "wear", "vibration", "overheating", "seizure",
        "misalignment", "cavitation", "fatigue", "fracture", "degradation",
        "deformation", "blockage", "fouling", "contamination",
    ]

    MAINTENANCE_ACTION_KEYWORDS = [
        "replace", "repair", "inspect", "align", "realign", "lubricate",
        "install", "calibrate", "overhaul", "clean", "tighten", "balance",
        "test", "flush", "refurbish", "weld", "coat", "monitor", "update",
    ]

    LOCATION_PATTERNS = [
        re.compile(
            r"\b((?:Unit|Area|Zone|Block|Plant|Section|Bay|Floor|Level|Building|Room)"
            r"[\s\-]*[A-Z0-9]+(?:[\s,\-]+[A-Z0-9]+)*)\b",
        ),
    ]

    def __init__(self):
        self.logger = get_logger(__name__)

    # ════════════════════════════════════════════════
    # Public API
    # ════════════════════════════════════════════════

    async def extract_entities(
        self,
        text: str,
        document_id: str = "",
        chunk_id: str = "",
    ) -> List[EntityBrief]:
        """Extract all entity types from text. Returns deduplicated EntityBrief list."""
        if not text or not text.strip():
            return []

        all_entities: List[EntityBrief] = []
        all_entities.extend(await self.extract_equipment_tags(text, document_id, chunk_id))
        all_entities.extend(await self.extract_dates(text, document_id, chunk_id))
        all_entities.extend(await self.extract_regulations(text, document_id, chunk_id))
        all_entities.extend(await self._extract_standards(text, document_id, chunk_id))
        all_entities.extend(await self._extract_parameters(text, document_id, chunk_id))
        all_entities.extend(await self._extract_personnel(text, document_id, chunk_id))
        all_entities.extend(await self._extract_failure_modes(text, document_id, chunk_id))
        all_entities.extend(await self._extract_maintenance_actions(text, document_id, chunk_id))
        all_entities.extend(await self._extract_locations(text, document_id, chunk_id))

        resolved = await self.resolve_entities(all_entities)
        self.logger.info(
            "Extracted %d entities (%d after resolution) from chunk %s",
            len(all_entities), len(resolved), chunk_id[:8] if chunk_id else "n/a",
        )
        return resolved

    async def extract_relationships(
        self,
        entities: List[EntityBrief],
        text: str,
        document_id: str = "",
    ) -> List[Dict[str, Any]]:
        """
        Extract relationships between entities using sentence co-occurrence.
        """
        if not entities or not text:
            return []

        sentences = extract_sentences(text)
        relationships: List[Dict[str, Any]] = []
        seen_pairs: set = set()

        # Build entity lookup by name (lowered) for matching in sentences
        entity_map: Dict[str, EntityBrief] = {}
        for e in entities:
            entity_map[e.name.lower()] = e

        # For each sentence, find which entities appear
        for sentence in sentences:
            sent_lower = sentence.lower()
            present: List[EntityBrief] = []
            for name_lower, entity in entity_map.items():
                if name_lower in sent_lower:
                    present.append(entity)

            # Generate relationships for co-occurring entity pairs
            for i, e1 in enumerate(present):
                for e2 in present[i + 1:]:
                    pair_key = tuple(sorted([e1.id, e2.id]))
                    if pair_key in seen_pairs:
                        continue
                    seen_pairs.add(pair_key)

                    rel_type = self._infer_relationship_type(e1, e2)
                    if rel_type:
                        relationships.append({
                            "source_entity_id": e1.id,
                            "target_entity_id": e2.id,
                            "relationship_type": rel_type,
                            "confidence": 0.75,
                            "source_document_id": document_id,
                        })

        self.logger.info("Extracted %d relationships from text", len(relationships))
        return relationships

    # ════════════════════════════════════════════════
    # Individual extractors
    # ════════════════════════════════════════════════

    async def extract_equipment_tags(
        self, text: str, document_id: str = "", chunk_id: str = "",
    ) -> List[EntityBrief]:
        """Extract equipment tags from text."""
        entities: List[EntityBrief] = []
        seen: set = set()

        # Tag patterns (P-1001A)
        for pattern in self.EQUIPMENT_TAG_PATTERNS:
            for match in pattern.finditer(text):
                name = match.group(1) if match.lastindex else match.group(0)
                name = name.strip()
                if name.lower() not in seen:
                    seen.add(name.lower())
                    entities.append(self._make_entity(
                        name, EntityType.EQUIPMENT, 0.92, document_id, chunk_id,
                    ))

        # Keyword patterns (pump, valve, etc.)
        for match in self.EQUIPMENT_KEYWORD_PATTERN.finditer(text):
            name = match.group(1).strip()
            if name.lower() not in seen and len(name) > 2:
                seen.add(name.lower())
                entities.append(self._make_entity(
                    name, EntityType.EQUIPMENT, 0.78, document_id, chunk_id,
                ))

        return entities

    async def extract_dates(
        self, text: str, document_id: str = "", chunk_id: str = "",
    ) -> List[EntityBrief]:
        """Extract dates from text."""
        entities: List[EntityBrief] = []
        seen: set = set()

        for pattern in self.DATE_PATTERNS:
            for match in pattern.finditer(text):
                name = match.group(1).strip()
                if name not in seen:
                    seen.add(name)
                    entities.append(self._make_entity(
                        name, EntityType.PARAMETER, 0.90, document_id, chunk_id,
                        extra_props={"sub_type": "date"},
                    ))
        return entities

    async def extract_regulations(
        self, text: str, document_id: str = "", chunk_id: str = "",
    ) -> List[EntityBrief]:
        """Extract regulatory references."""
        entities: List[EntityBrief] = []
        seen: set = set()

        for pattern in self.REGULATION_PATTERNS:
            for match in pattern.finditer(text):
                name = match.group(1).strip()
                if name.lower() not in seen and len(name) > 2:
                    seen.add(name.lower())
                    entities.append(self._make_entity(
                        name, EntityType.REGULATION, 0.90, document_id, chunk_id,
                    ))
        return entities

    async def resolve_entities(self, entities: List[EntityBrief]) -> List[EntityBrief]:
        """Deduplicate entities by normalised name + type, keeping highest confidence."""
        if not entities:
            return []

        best: Dict[str, EntityBrief] = {}
        for e in entities:
            key = f"{e.entity_type.value}::{e.name.lower().strip()}"
            existing = best.get(key)
            if existing is None:
                best[key] = e
            else:
                # Keep higher confidence; merge properties
                existing_conf = existing.properties.get("confidence", 0)
                new_conf = e.properties.get("confidence", 0)
                if new_conf > existing_conf:
                    best[key] = e

        return list(best.values())

    # ════════════════════════════════════════════════
    # Private extractors
    # ════════════════════════════════════════════════

    async def _extract_standards(
        self, text: str, document_id: str = "", chunk_id: str = "",
    ) -> List[EntityBrief]:
        entities: List[EntityBrief] = []
        seen: set = set()
        for pattern in self.STANDARD_PATTERNS:
            for match in pattern.finditer(text):
                name = match.group(1).strip()
                if name.lower() not in seen and len(name) > 2:
                    seen.add(name.lower())
                    entities.append(self._make_entity(
                        name, EntityType.REGULATION, 0.93, document_id, chunk_id,
                        extra_props={"sub_type": "standard"},
                    ))
        return entities

    async def _extract_parameters(
        self, text: str, document_id: str = "", chunk_id: str = "",
    ) -> List[EntityBrief]:
        entities: List[EntityBrief] = []
        seen: set = set()
        for pattern in self.PARAMETER_PATTERNS:
            for match in pattern.finditer(text):
                name = match.group(1).strip()
                if name not in seen:
                    seen.add(name)
                    entities.append(self._make_entity(
                        name, EntityType.PARAMETER, 0.85, document_id, chunk_id,
                    ))
        return entities

    async def _extract_personnel(
        self, text: str, document_id: str = "", chunk_id: str = "",
    ) -> List[EntityBrief]:
        entities: List[EntityBrief] = []
        seen: set = set()
        for pattern in self.PERSONNEL_PATTERNS:
            for match in pattern.finditer(text):
                name = match.group(1).strip()
                if name.lower() not in seen and len(name) > 3:
                    seen.add(name.lower())
                    entities.append(self._make_entity(
                        name, EntityType.PERSON, 0.80, document_id, chunk_id,
                    ))
        return entities

    async def _extract_failure_modes(
        self, text: str, document_id: str = "", chunk_id: str = "",
    ) -> List[EntityBrief]:
        entities: List[EntityBrief] = []
        seen: set = set()
        text_lower = text.lower()
        for keyword in self.FAILURE_MODE_KEYWORDS:
            if keyword in text_lower:
                # Extract the keyword with surrounding context for better naming
                pattern = re.compile(
                    rf"\b(\w+\s+)?({re.escape(keyword)})(\s+\w+)?\b", re.IGNORECASE,
                )
                for match in pattern.finditer(text):
                    name = match.group(0).strip()
                    if name.lower() not in seen and len(name) > 3:
                        seen.add(name.lower())
                        entities.append(self._make_entity(
                            name, EntityType.FAILURE_EVENT, 0.75, document_id, chunk_id,
                        ))
        return entities

    async def _extract_maintenance_actions(
        self, text: str, document_id: str = "", chunk_id: str = "",
    ) -> List[EntityBrief]:
        entities: List[EntityBrief] = []
        seen: set = set()

        for keyword in self.MAINTENANCE_ACTION_KEYWORDS:
            pattern = re.compile(
                rf"\b({re.escape(keyword)}\s+[^.\n,;]{{3,60}})",
                re.IGNORECASE,
            )
            for match in pattern.finditer(text):
                name = match.group(1).strip()
                # Trim to max ~60 chars
                if len(name) > 60:
                    name = name[:60].rsplit(" ", 1)[0]
                if name.lower() not in seen and len(name) > 5:
                    seen.add(name.lower())
                    entities.append(self._make_entity(
                        name, EntityType.MAINTENANCE_ACTION, 0.78, document_id, chunk_id,
                    ))
        return entities

    async def _extract_locations(
        self, text: str, document_id: str = "", chunk_id: str = "",
    ) -> List[EntityBrief]:
        entities: List[EntityBrief] = []
        seen: set = set()
        for pattern in self.LOCATION_PATTERNS:
            for match in pattern.finditer(text):
                name = match.group(1).strip()
                if name.lower() not in seen and len(name) > 3:
                    seen.add(name.lower())
                    entities.append(self._make_entity(
                        name, EntityType.LOCATION, 0.82, document_id, chunk_id,
                    ))
        return entities

    # ════════════════════════════════════════════════
    # Helpers
    # ════════════════════════════════════════════════

    @staticmethod
    def _make_entity(
        name: str,
        entity_type: EntityType,
        confidence: float,
        document_id: str,
        chunk_id: str,
        extra_props: Optional[Dict[str, Any]] = None,
    ) -> EntityBrief:
        props: Dict[str, Any] = {
            "confidence": confidence,
            "source_document_id": document_id,
            "source_chunk_id": chunk_id,
        }
        if extra_props:
            props.update(extra_props)
        return EntityBrief(
            id=str(uuid.uuid4()),
            entity_type=entity_type,
            name=name,
            properties=props,
        )

    @staticmethod
    def _infer_relationship_type(e1: EntityBrief, e2: EntityBrief) -> Optional[str]:
        """Infer the most likely relationship type between two co-occurring entities."""
        t1, t2 = e1.entity_type, e2.entity_type
        pair = {t1, t2}

        if EntityType.EQUIPMENT in pair and EntityType.FAILURE_EVENT in pair:
            return "AFFECTS"
        if EntityType.FAILURE_EVENT in pair and EntityType.MAINTENANCE_ACTION in pair:
            return "CAUSES"
        if EntityType.EQUIPMENT in pair and EntityType.REGULATION in pair:
            return "REGULATED_BY"
        if EntityType.EQUIPMENT in pair and EntityType.LOCATION in pair:
            return "LOCATED_IN"
        if EntityType.EQUIPMENT in pair and EntityType.MAINTENANCE_ACTION in pair:
            return "MAINTAINED_BY"
        if EntityType.PART in pair and EntityType.EQUIPMENT in pair:
            return "PART_OF"
        if EntityType.EQUIPMENT in pair and EntityType.PARAMETER in pair:
            return "DEPENDS_ON"
        if EntityType.EQUIPMENT in pair and EntityType.PERSON in pair:
            return "MAINTAINED_BY"

        # Default: co-occurrence with no clear semantic => REFERENCES
        return "REFERENCES"
