import sys
import json
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

from app.agents.extraction_agent import extract_facts
from app.contradiction.checker import find_contradictions
from app.scoring.fraud_scorer import score_claim


CLAIM_DIR = (
    Path(__file__).resolve().parents[1]
    / "sample_claims"
    / "claim_1"
)


def main():

    print("=" * 70)
    print("INSURGUARD - CLAIM 1 FULL ANALYSIS")
    print("=" * 70)

    # -------------------------------------------------
    # 1. Extract facts
    # -------------------------------------------------

    police_text = (
        CLAIM_DIR / "police_report.txt"
    ).read_text(encoding="utf-8")

    medical_text = (
        CLAIM_DIR / "medical_report.txt"
    ).read_text(encoding="utf-8")

    repair_text = (
        CLAIM_DIR / "repair_invoice.txt"
    ).read_text(encoding="utf-8")

    police_facts = extract_facts(
        police_text,
        "police_report"
    )

    medical_facts = extract_facts(
        medical_text,
        "medical_report"
    )

    repair_facts = extract_facts(
        repair_text,
        "repair_invoice"
    )

    print("\nFACT EXTRACTION COMPLETE")

    # -------------------------------------------------
    # 2. Find contradictions
    # -------------------------------------------------

    contradictions = find_contradictions(
        police_facts,
        medical_facts,
        repair_facts
    )

    print(
        f"\nContradictions found: "
        f"{len(contradictions)}"
    )

    for contradiction in contradictions:

        print(
            f"\n[{contradiction['severity'].upper()}] "
            f"{contradiction['type']}"
        )

        print(
            contradiction["description"]
        )

    # -------------------------------------------------
    # 3. Load claim metadata
    # -------------------------------------------------

    metadata_file = (
        CLAIM_DIR / "claim_metadata.json"
    )

    metadata = json.loads(
        metadata_file.read_text(
            encoding="utf-8"
        )
    )

    # -------------------------------------------------
    # 4. Calculate final fraud score
    # -------------------------------------------------

    score = score_claim(
        metadata,
        contradiction_count=len(contradictions)
    )

    print("\n" + "=" * 70)
    print("FINAL FRAUD SCORE")
    print("=" * 70)

    print(
        json.dumps(
            score,
            indent=2
        )
    )


if __name__ == "__main__":
    main()