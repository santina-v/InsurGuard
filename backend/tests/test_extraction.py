import sys
import json
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

from app.agents.extraction_agent import extract_facts
from app.scoring.fraud_scorer import score_claim


BASE_DIR = Path(__file__).resolve().parents[1]
SAMPLE_DIR = BASE_DIR / "sample_claims"

DOCUMENT_TYPES = {
    "police_report.txt": "police_report",
    "medical_report.txt": "medical_report",
    "repair_invoice.txt": "repair_invoice",
}


def main():
    for claim_dir in sorted(SAMPLE_DIR.iterdir()):

        if not claim_dir.is_dir():
            continue

        print("\n" + "=" * 70)
        print(f"CLAIM: {claim_dir.name}")
        print("=" * 70)

        # Extract all three documents
        for filename, document_type in DOCUMENT_TYPES.items():

            file_path = claim_dir / filename

            print(f"\n--- {filename} ---")

            try:
                text = file_path.read_text(
                    encoding="utf-8"
                )

                result = extract_facts(
                    text,
                    document_type
                )

                print(
                    json.dumps(
                        result,
                        indent=2
                    )
                )

            except Exception as error:
                print(f"ERROR: {error}")

        # Load metadata
        metadata_file = (
            claim_dir / "claim_metadata.json"
        )

        metadata = json.loads(
            metadata_file.read_text(
                encoding="utf-8"
            )
        )

        # Score without contradictions for now
        score = score_claim(
            metadata,
            contradiction_count=0
        )

        print("\n--- Initial Fraud Score ---")
        print(
            json.dumps(
                score,
                indent=2
            )
        )


if __name__ == "__main__":
    main()