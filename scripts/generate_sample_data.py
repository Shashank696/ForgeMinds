"""
ForgeMinds — Synthetic Sample Data Generator.

Generates realistic industrial documents (PDFs) for demo purposes.
Run from project root: python scripts/generate_sample_data.py

Since we don't have real industrial documents, this script creates
synthetic but realistic-looking documents for demonstration:
- Maintenance work orders
- Inspection reports
- Operating procedures
- Incident reports
"""

import os
import json
import random
from datetime import datetime, timedelta

# Add project root to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "sample_documents"
)

# ─── Templates ──────────────────────────────────────────

EQUIPMENT_TAGS = ["P-101A", "P-101B", "V-2001", "FCV-1234", "C-301", "E-1501", "TK-4001", "MOT-101A"]
TECHNICIANS = ["Rajesh Kumar", "Suresh Yadav", "Mohammed Iqbal", "Vikram Singh", "Anand Deshmukh"]
FAILURE_MODES = [
    "Seal leak", "Bearing failure", "Vibration high", "Overheating",
    "Corrosion", "Erosion", "Cavitation", "Impeller wear",
    "Valve stuck", "Instrument drift", "Insulation damage"
]
ACTIONS = [
    "Replaced mechanical seal", "Replaced bearings DE and NDE",
    "Balanced impeller", "Cleaned strainer", "Replaced gasket",
    "Recalibrated instrument", "Applied corrosion inhibitor",
    "Replaced valve internals", "Tightened flange bolts",
    "Replaced coupling", "Realigned pump-motor"
]


def generate_maintenance_record(index: int) -> dict:
    """Generate a synthetic maintenance work order."""
    base_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 730))
    equipment = random.choice(EQUIPMENT_TAGS)
    work_type = random.choice(["preventive", "corrective", "predictive", "emergency"])

    record = {
        "work_order_number": f"WO-2024-{index:04d}",
        "equipment_tag": equipment,
        "title": f"{random.choice(FAILURE_MODES)} on {equipment}",
        "work_type": work_type,
        "priority": random.choice(["critical", "high", "medium", "low"]),
        "description": f"Work order for {work_type} maintenance on {equipment}. "
                       f"Reported issue: {random.choice(FAILURE_MODES)}.",
        "assigned_to": random.choice(TECHNICIANS),
        "findings": f"Upon inspection, found {random.choice(FAILURE_MODES).lower()}. "
                    f"Component showed signs of wear after {random.randint(6, 36)} months of operation.",
        "actions_taken": random.choice(ACTIONS),
        "root_cause": random.choice([
            "Normal wear and tear",
            "Operating outside design parameters",
            "Inadequate lubrication",
            "Material degradation",
            "Installation error",
            "Manufacturing defect"
        ]),
        "parts_replaced": [
            {"part_name": random.choice(["Seal", "Bearing", "Gasket", "O-ring", "Coupling"]),
             "part_number": f"SP-{random.randint(1000, 9999)}",
             "quantity": random.randint(1, 4)}
        ],
        "downtime_hours": round(random.uniform(2, 72), 1),
        "date": base_date.strftime("%Y-%m-%d"),
        "completed_date": (base_date + timedelta(hours=random.randint(4, 96))).strftime("%Y-%m-%d")
    }
    return record


def generate_inspection_report(index: int) -> dict:
    """Generate a synthetic inspection report."""
    base_date = datetime(2023, 6, 1) + timedelta(days=random.randint(0, 365))
    equipment = random.choice(EQUIPMENT_TAGS)

    report = {
        "inspection_id": f"INS-2024-{index:04d}",
        "equipment_tag": equipment,
        "inspection_type": random.choice([
            "Visual inspection", "Thickness measurement",
            "Vibration analysis", "Thermographic survey",
            "NDT — Ultrasonic", "NDT — Radiographic",
            "Pressure test", "Functional test"
        ]),
        "inspector": random.choice(TECHNICIANS),
        "date": base_date.strftime("%Y-%m-%d"),
        "result": random.choice(["Satisfactory", "Marginal", "Unsatisfactory", "Requires attention"]),
        "findings": [
            f"Wall thickness at location {random.choice(['A', 'B', 'C', 'D'])}: "
            f"{round(random.uniform(5.0, 15.0), 1)} mm (minimum required: 6.0 mm)",
            f"Corrosion rate: {round(random.uniform(0.05, 0.5), 2)} mm/year",
            f"Next inspection due: {(base_date + timedelta(days=365)).strftime('%Y-%m-%d')}"
        ],
        "recommendations": random.choice([
            "Continue monitoring at current frequency",
            "Increase inspection frequency to 6 months",
            "Schedule repair at next shutdown",
            "Immediate attention required",
            "Replace component before next turnaround"
        ])
    }
    return report


def generate_text_content(record: dict, doc_type: str) -> str:
    """Convert a record dict to a plain text document content."""
    lines = []
    lines.append("=" * 70)
    lines.append(f"  FORGEMINDS REFINERY COMPLEX — {doc_type.upper()}")
    lines.append("=" * 70)
    lines.append("")

    for key, value in record.items():
        label = key.replace("_", " ").title()
        if isinstance(value, list):
            lines.append(f"{label}:")
            for item in value:
                if isinstance(item, dict):
                    lines.append(f"  - {json.dumps(item)}")
                else:
                    lines.append(f"  - {item}")
        else:
            lines.append(f"{label}: {value}")

    lines.append("")
    lines.append("-" * 70)
    lines.append("This is a synthetically generated document for demonstration purposes.")
    lines.append("Generated by ForgeMinds Sample Data Generator.")
    lines.append("-" * 70)
    return "\n".join(lines)


def main():
    """Generate all sample documents."""
    print("=" * 60)
    print("  ForgeMinds — Sample Data Generator")
    print("=" * 60)
    print()

    os.makedirs(os.path.join(OUTPUT_DIR, "maintenance_records"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "inspection_reports"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "operating_procedures"), exist_ok=True)

    # Generate maintenance records
    print("Generating maintenance records...")
    for i in range(1, 16):
        record = generate_maintenance_record(i)
        content = generate_text_content(record, "Maintenance Work Order")
        filepath = os.path.join(OUTPUT_DIR, "maintenance_records", f"WO-2024-{i:04d}.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ {filepath}")

    print()

    # Generate inspection reports
    print("Generating inspection reports...")
    for i in range(1, 11):
        report = generate_inspection_report(i)
        content = generate_text_content(report, "Inspection Report")
        filepath = os.path.join(OUTPUT_DIR, "inspection_reports", f"INS-2024-{i:04d}.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ {filepath}")

    print()
    print("=" * 60)
    print(f"  ✓ Generated {15 + 10} sample documents")
    print("=" * 60)


if __name__ == "__main__":
    main()
