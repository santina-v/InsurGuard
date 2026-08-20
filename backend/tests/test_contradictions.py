import sys

from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

from app.contradiction.checker import (
    find_contradictions,
)


claim_1_police = {
    "incident_date": "2026-03-15",
    "incident_time": "15:00",
    "location": "Chicago, Illinois",
    "weather_reported": "Clear, sunny skies.",
    "collision_description": (
        "Vehicle struck another vehicle at intersection."
    ),
    "at_fault_party": "Daniel Carter",
    "officer_notes": (
        "The claimant stated that he was traveling "
        "through the intersection when the collision "
        "occurred."
    ),
}


claim_1_medical = {
    "patient_name": "Daniel Carter",
    "treatment_date": "2026-03-15",
    "treatment_time": "09:00",
    "chief_complaint": (
        "neck pain, back pain, and dizziness"
    ),
    "reported_onset": (
        "Immediately after this morning's accident."
    ),
}


claim_1_repair = {
    "vehicle": "2020 Toyota Camry",
    "service_date": "2026-03-16",
    "damage_description": (
        "The rear bumper, rear trunk panel, "
        "and rear body structure were damaged."
    ),
    "damage_location": "Rear",
    "estimated_cause": (
        "Collision with another vehicle."
    ),
    "total_cost": 5070.0,
}


contradictions = find_contradictions(
    claim_1_police,
    claim_1_medical,
    claim_1_repair,
)


print("\nCONTRADICTIONS FOUND:")
print("=" * 60)

for contradiction in contradictions:
    print(
        f"\nType: {contradiction['type']}"
    )

    print(
        f"Severity: {contradiction['severity']}"
    )

    print(
        f"Description: "
        f"{contradiction['description']}"
    )

print(
    f"\nTotal contradictions: "
    f"{len(contradictions)}"
)