class FraudReasoningAgent:
    """
    Agent 3 - Fraud Reasoning Agent

    Combines:
        - Fraud score
        - Score contributors
        - Contradictions
        - Evidence verification

    Important:
        UNKNOWN != MISMATCH

    UNKNOWN means evidence is unavailable.
    MISMATCH means documents actually conflict.
    """

    def reason(
        self,
        risk_score,
        risk_level,
        score_contributors,
        contradictions,
        verification,
    ):

        reasons = []
        review_items = []

        # =====================================================
        # 1. CONTRADICTIONS
        # =====================================================

        if contradictions:

            reasons.append(
                f"{len(contradictions)} "
                "cross-document contradiction(s) detected."
            )


        # =====================================================
        # 2. IDENTITY
        # =====================================================

        identity_status = verification.get(
            "identity",
            "UNKNOWN"
        )

        if identity_status == "MISMATCH":

            reasons.append(
                "Claimant identity mismatch detected."
            )

        elif identity_status == "UNKNOWN":

            review_items.append(
                "Claimant identity could not be "
                "fully verified from the available documents."
            )


        # =====================================================
        # 3. VEHICLE
        # =====================================================

        vehicle_status = verification.get(
            "vehicle",
            "UNKNOWN"
        )

        if vehicle_status == "MISMATCH":

            reasons.append(
                "Vehicle information mismatch detected."
            )

        elif vehicle_status == "UNKNOWN":

            review_items.append(
                "Claimant vehicle information could not "
                "be fully verified from the available documents."
            )


        # =====================================================
        # 4. DATE
        # =====================================================

        date_status = verification.get(
            "date",
            "UNKNOWN"
        )

        if date_status == "MISMATCH":

            reasons.append(
                "Incident and treatment dates do not match."
            )

        elif date_status == "UNKNOWN":

            review_items.append(
                "Incident/treatment date comparison "
                "could not be completed."
            )


        # =====================================================
        # 5. TIMELINE
        # =====================================================

        timeline_status = verification.get(
            "timeline",
            "UNKNOWN"
        )

        if timeline_status == "MISMATCH":

            reasons.append(
                "Medical timeline inconsistency detected."
            )

        elif timeline_status == "UNKNOWN":

            review_items.append(
                "Medical timeline requires further review."
            )


        # =====================================================
        # 6. DAMAGE
        # =====================================================

        damage_status = verification.get(
            "damage",
            "UNKNOWN"
        )

        if damage_status == "MISMATCH":

            reasons.append(
                "Damage information mismatch detected."
            )

        elif damage_status == "UNKNOWN":

            review_items.append(
                "Damage evidence could not be fully verified."
            )


        # =====================================================
        # 7. SCORE CONTRIBUTORS
        # =====================================================

        for contributor in score_contributors:

            description = contributor.get(
                "description"
            )

            if description:

                reasons.append(
                    description
                )


        # =====================================================
        # 8. BUILD EXPLANATION
        # =====================================================

        if reasons:

            explanation = (
                f"The claim is classified as "
                f"{risk_level} risk based on the available "
                "evidence. "
                + " ".join(reasons)
            )

        else:

            explanation = (
                f"The claim is classified as "
                f"{risk_level} risk. "
                "No direct contradictions or major "
                "fraud indicators were detected."
            )


        # =====================================================
        # 9. RETURN
        # =====================================================

        return {

            "risk_score": risk_score,

            "risk_level": risk_level,

            "reasons": reasons,

            "review_items": review_items,

            "explanation": explanation,
        }