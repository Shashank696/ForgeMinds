"""
ForgeMinds — Database Seeding Script.

Populates the database with sample data for development and demo.
Run from project root: python scripts/seed_db.py
"""

import json
import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "seed_data")


def load_json(filename: str) -> list:
    """Load a JSON seed file."""
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


async def seed_users():
    """Seed user accounts."""
    users = load_json("seed_users.json")
    print(f"  → Seeding {len(users)} users...")
    # TODO: Implement — insert users into PostgreSQL
    # Use auth_service.register() or direct SQL insert
    for user in users:
        print(f"    • {user['full_name']} ({user['role']})")
    print("  ✓ Users seeded (placeholder)")


async def seed_equipment():
    """Seed equipment records."""
    equipment = load_json("seed_equipment.json")
    print(f"  → Seeding {len(equipment)} equipment records...")
    # TODO: Implement — insert equipment into PostgreSQL + Neo4j
    for eq in equipment:
        print(f"    • {eq['tag']} — {eq['name']}")
    print("  ✓ Equipment seeded (placeholder)")


async def seed_regulations():
    """Seed regulatory records."""
    regulations = load_json("seed_regulations.json")
    print(f"  → Seeding {len(regulations)} regulations...")
    # TODO: Implement — insert regulations into PostgreSQL + Neo4j
    for reg in regulations:
        print(f"    • {reg['code']} — {reg['name']}")
    print("  ✓ Regulations seeded (placeholder)")


async def seed_knowledge_graph():
    """Seed initial knowledge graph relationships."""
    print("  → Building initial knowledge graph relationships...")
    # TODO: Implement — create Neo4j nodes and edges
    # Link equipment to regulations, locations, etc.
    print("  ✓ Knowledge graph seeded (placeholder)")


async def main():
    """Run all seed functions."""
    print("=" * 60)
    print("  ForgeMinds — Database Seeder")
    print("=" * 60)
    print()

    # TODO: Initialize database connections
    # from backend.db.database import db
    # from backend.db.neo4j_client import neo4j_db
    # await db.connect(...)
    # await neo4j_db.connect(...)

    await seed_users()
    print()
    await seed_equipment()
    print()
    await seed_regulations()
    print()
    await seed_knowledge_graph()

    print()
    print("=" * 60)
    print("  ✓ Seeding complete!")
    print("=" * 60)

    # TODO: Close database connections
    # await db.disconnect()
    # await neo4j_db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
