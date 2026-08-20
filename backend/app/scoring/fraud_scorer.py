from __future__ import annotations

from typing import Any


AMOUNT_THRESHOLD = 1.3
AMOUNT_WEIGHT = 0.31

PRIOR_CLAIMS_THRESHOLD = 2
PRIOR_CLAIMS_WEIGHT = 0.24

POLICY_TENURE_THRESHOLD = 6
POLICY_TENURE_WEIGHT = 0.15

CONTRADICTION_WEIGHT = 0.15
MAX_CONTRADICTION_COUNT = 2


def score_claim(
    claim_metadata: dict[str, Any],
    contradiction_count: int,
) -> dict[str, Any]:
    """
    Calculate an explainable rule-based fraud score.

    The score is intentionally rule-based because the hackathon
    does not have historical fraud-labelled training data.
    """

    claim_amount = float(
        claim_metadata["claim_amount"]
    )

    region_average = float(
        claim_metadata["region_avg_claim_amount"]
    )

    prior_claims = int(
        claim_metadata["claimant_prior_claims_18mo"]
    )

    policy_tenure = int(
        claim_metadata["policy_tenure_months"]
    )

    contributors: list[dict[str, Any]] = []

    # 1. High claim amount
    if claim_amount > region_average * AMOUNT_THRESHOLD:

        percentage = (
            (claim_amount - region_average)
            / region_average
            * 100
        )

        contributors.append({
            "feature": "claim_amount_above_regional_average",
            "weight": AMOUNT_WEIGHT,
            "description": (
                f"Claim amount is "
                f"{percentage:.0f}% above regional average"
            ),
        })

    # 2. Previous claims
    if prior_claims >= PRIOR_CLAIMS_THRESHOLD:

        contributors.append({
            "feature": "frequent_prior_claims",
            "weight": PRIOR_CLAIMS_WEIGHT,
            "description": (
                f"Claimant filed {prior_claims} "
                "prior claims in the last 18 months"
            ),
        })

    # 3. New policy
    if policy_tenure < POLICY_TENURE_THRESHOLD:

        contributors.append({
            "feature": "new_policy",
            "weight": POLICY_TENURE_WEIGHT,
            "description": (
                "Policy is less than 6 months old"
            ),
        })

    # 4. Contradictions
    if contradiction_count > 0:

        contradiction_weight = (
            CONTRADICTION_WEIGHT
            * min(
                contradiction_count,
                MAX_CONTRADICTION_COUNT,
            )
        )

        contributors.append({
            "feature": "cross_document_contradictions",
            "weight": contradiction_weight,
            "description": (
                "Cross-document "
                "contradiction(s) detected"
            ),
        })

    # Calculate final score.
    base_score = min(
        sum(
            item["weight"]
            for item in contributors
        ),
        1.0,
    )

    # Highest contribution first.
    contributors.sort(
        key=lambda item: item["weight"],
        reverse=True,
    )

    return {
        "base_score": round(base_score, 4),
        "score_contributors": contributors,
    }