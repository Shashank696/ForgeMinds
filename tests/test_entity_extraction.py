"""
Tests for entity extraction.
Assigned to: RUDRA
"""

import pytest
import os
import sys
import asyncio

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.entity_extraction import EntityExtractionService


SAMPLE_TEXT = """
MAINTENANCE REPORT - PUMP P-1001A

Date: 15/03/2024
Location: Unit-3, Area B
Equipment: Centrifugal Pump P-1001A
Manufacturer: Flowserve Corporation

INSPECTION FINDINGS:
1. Bearing vibration levels exceeded ISO 10816 threshold at 7.2 mm/s
2. Seal leakage detected at mechanical seal assembly
3. Impeller wear observed - estimated 15% degradation

ROOT CAUSE ANALYSIS:
The primary cause of bearing failure was identified as misalignment
between the motor shaft and pump shaft. Contributing factors include:
- Inadequate lubrication schedule (last service: 01/12/2023)
- Operating temperature exceeded design limit of 85°C

CORRECTIVE ACTIONS:
1. Replace bearing assembly (SKF 6310-2RS)
2. Realign motor-pump coupling per API 686 standards
3. Replace mechanical seal (John Crane Type 2100)
4. Update lubrication schedule to monthly intervals
5. Install vibration monitoring sensor per OISD Standard 117 requirements

REGULATORY COMPLIANCE:
- Factory Act 1948, Section 21 - Safety requirements met
- OISD Standard 117 - Monitoring requirements updated
- ISO 14224 - Failure data recorded

Prepared by: Rajesh Kumar, Senior Maintenance Engineer
Approved by: Anil Sharma, Plant Manager
"""


def _run(coro):
    """Helper to run async functions in sync tests."""
    return asyncio.run(coro)


class TestEntityExtraction:
    """Tests for NER / entity extraction from industrial text."""

    def setup_method(self):
        """Create a fresh service instance for each test."""
        self.service = EntityExtractionService()

    def test_extract_equipment_tags(self):
        """Test extraction of equipment tags (e.g., P-101A, V-2001)."""
        entities = _run(self.service.extract_equipment_tags(SAMPLE_TEXT))

        names = [e.name for e in entities]
        # Should find the equipment tag P-1001A
        assert any("P-1001A" in n for n in names), f"Expected P-1001A in {names}"

        # All entities should have equipment type
        for e in entities:
            assert e.entity_type.value == "equipment"

    def test_extract_dates(self):
        """Test extraction of dates from document text."""
        entities = _run(self.service.extract_dates(SAMPLE_TEXT))

        names = [e.name for e in entities]
        # Should find 15/03/2024
        assert any("15/03/2024" in n for n in names), f"Expected 15/03/2024 in {names}"

    def test_extract_personnel(self):
        """Test extraction of personnel names."""
        entities = _run(self.service._extract_personnel(SAMPLE_TEXT))

        names = [e.name for e in entities]
        # Should find Rajesh Kumar
        assert any("Rajesh Kumar" in n for n in names), f"Expected Rajesh Kumar in {names}"

        # Should have person type
        for e in entities:
            assert e.entity_type.value == "person"

    def test_extract_regulations(self):
        """Test extraction of regulatory references."""
        entities = _run(self.service.extract_regulations(SAMPLE_TEXT))

        names = [e.name.lower() for e in entities]
        # Should find Factory Act and OISD
        has_factory_act = any("factory act" in n for n in names)
        has_oisd = any("oisd" in n for n in names)
        assert has_factory_act or has_oisd, f"Expected Factory Act or OISD in {names}"

    def test_extract_parameters(self):
        """Test extraction of process parameters (pressure, temperature)."""
        entities = _run(self.service._extract_parameters(SAMPLE_TEXT))

        names = [e.name for e in entities]
        # Should find 7.2 mm/s
        assert any("7.2 mm/s" in n for n in names), f"Expected 7.2 mm/s in {names}"

    def test_entity_resolution(self):
        """Test deduplication of extracted entities."""
        from shared.enums import EntityType
        from shared.interfaces import EntityBrief

        # Create duplicates with different confidences
        duplicates = [
            EntityBrief(id="1", entity_type=EntityType.EQUIPMENT, name="P-1001A",
                        properties={"confidence": 0.8}),
            EntityBrief(id="2", entity_type=EntityType.EQUIPMENT, name="P-1001A",
                        properties={"confidence": 0.95}),
            EntityBrief(id="3", entity_type=EntityType.EQUIPMENT, name="P-1001A",
                        properties={"confidence": 0.7}),
            EntityBrief(id="4", entity_type=EntityType.REGULATION, name="OISD 117",
                        properties={"confidence": 0.9}),
        ]

        resolved = _run(self.service.resolve_entities(duplicates))

        # Should deduplicate P-1001A to one entity, keep OISD 117
        equipment_entities = [e for e in resolved if e.entity_type == EntityType.EQUIPMENT]
        assert len(equipment_entities) == 1

        # Should keep the highest confidence one
        assert equipment_entities[0].properties["confidence"] == 0.95

        # Total should be 2 (one equipment + one regulation)
        assert len(resolved) == 2

    def test_extract_all_entities(self):
        """Test the full extract_entities pipeline."""
        entities = _run(self.service.extract_entities(SAMPLE_TEXT, "doc-123", "chunk-1"))

        assert len(entities) > 0

        # Should have multiple entity types
        types = set(e.entity_type.value for e in entities)
        assert len(types) >= 2, f"Expected at least 2 entity types, got {types}"

        # Every entity should have confidence
        for e in entities:
            assert "confidence" in e.properties
            assert 0 <= e.properties["confidence"] <= 1.0

    def test_extract_relationships(self):
        """Test relationship extraction from entities and text."""
        entities = _run(self.service.extract_entities(SAMPLE_TEXT, "doc-123", "chunk-1"))
        relationships = _run(self.service.extract_relationships(entities, SAMPLE_TEXT, "doc-123"))

        # Should have at least some relationships
        assert len(relationships) > 0

        # Each relationship should have required fields
        for rel in relationships:
            assert "source_entity_id" in rel
            assert "target_entity_id" in rel
            assert "relationship_type" in rel
            assert "confidence" in rel

    def test_extract_from_empty_text(self):
        """Test entity extraction from empty text."""
        entities = _run(self.service.extract_entities(""))
        assert entities == []

        entities = _run(self.service.extract_entities("   "))
        assert entities == []

    def test_extract_failure_modes(self):
        """Test extraction of failure modes."""
        entities = _run(self.service._extract_failure_modes(SAMPLE_TEXT))

        names = [e.name.lower() for e in entities]
        # Should find failure-related terms
        has_failure = any("failure" in n for n in names)
        has_leak = any("leak" in n for n in names)
        has_wear = any("wear" in n for n in names)
        has_misalignment = any("misalignment" in n for n in names)
        assert has_failure or has_leak or has_wear or has_misalignment, \
            f"Expected failure mode keywords in {names}"

    def test_extract_maintenance_actions(self):
        """Test extraction of maintenance actions."""
        entities = _run(self.service._extract_maintenance_actions(SAMPLE_TEXT))

        names = [e.name.lower() for e in entities]
        # Should find actions like "replace", "realign", "install", "update"
        has_replace = any("replace" in n for n in names)
        has_install = any("install" in n for n in names)
        assert has_replace or has_install, f"Expected maintenance action keywords in {names}"

    def test_extract_locations(self):
        """Test extraction of locations."""
        entities = _run(self.service._extract_locations(SAMPLE_TEXT))

        names = [e.name for e in entities]
        has_unit = any("Unit" in n for n in names)
        has_area = any("Area" in n for n in names)
        assert has_unit or has_area, f"Expected location in {names}"
