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


BASE_DIR = Path(__file__).resolve().parents[1]
CLAIMS_DIR = BASE_DIR / "sample_claims"


DOCUMENTS = {
    "police_report.txt": "police_report",
    "medical_report.txt": "medical_report",
    "repair_invoice.txt": "repair_invoice",
}


def analyze_claim(claim_dir: Path) -> dict:
    """Extract facts, find contradictions and calculate fraud score."""

    extracted = {}

    # ---------------------------------------
    # 1. Extract facts from all documents
    # ---------------------------------------

    for filename, document_type in DOCUMENTS.items():

        file_path = claim_dir / filename

        text = file_path.read_text(
            encoding="utf-8"
        )

        extracted[document_type] = extract_facts(
            text,
            document_type
        )

    # ---------------------------------------
    # 2. Find contradictions
    # ---------------------------------------

    contradictions = find_contradictions(
        extracted["police_report"],
        extracted["medical_report"],
        extracted["repair_invoice"],
    )

    # ---------------------------------------
    # 3. Load claim metadata
    # ---------------------------------------

    metadata_path = (
        claim_dir / "claim_metadata.json"
    )

    metadata = json.loads(
        metadata_path.read_text(
            encoding="utf-8"
        )
    )

    # ---------------------------------------
    # 4. Calculate final fraud score
    # ---------------------------------------

    score = score_claim(
        metadata,
        contradiction_count=len(contradictions)
    )

    return {
        "claim_id": metadata["claim_id"],
        "contradictions": contradictions,
        "score": score,
    }


def main():

    print("=" * 70)
    print("INSURGUARD - ALL CLAIMS ANALYSIS")
    print("=" * 70)

    claim_dirs = sorted(
        path
        for path in CLAIMS_DIR.iterdir()
        if path.is_dir()
    )

    for claim_dir in claim_dirs:

        print(
            f"\n{'=' * 70}"
        )

        print(
            f"ANALYZING: {claim_dir.name}"
        )

        print(
            f"{'=' * 70}"
        )

        try:

            result = analyze_claim(
                claim_dir
            )

            contradictions = result[
                "contradictions"
            ]

            score = result["score"]

            print(
                f"\nClaim ID: "
                f"{result['claim_id']}"
            )

            print(
                f"Contradictions: "
                f"{len(contradictions)}"
            )

            for contradiction in contradictions:

                print(
                    f"\n[{contradiction['severity'].upper()}]"
                )

                print(
                    contradiction["description"]
                )

            print(
                f"\nFraud Risk Score: "
                f"{score['base_score']:.2f}"
            )

            print("\nScore Contributors:")

            for contributor in score[
                "score_contributors"
            ]:

                print(
                    f"- "
                    f"{contributor['feature']}: "
                    f"{contributor['weight']}"
                )

        except Exception as error:

            print(
                f"\nERROR: {error}"
            )


if __name__ == "__main__":
    main()