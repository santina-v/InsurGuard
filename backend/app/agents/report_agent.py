class InvestigationReportAgent:
    """
    Agent 4 - Investigation Report Agent

    Converts the outputs of the verification and
    fraud reasoning agents into an investigator-friendly
    final report.

    UNKNOWN evidence is treated as a review item,
    not as a fraud indicator.
    """

    def generate(
        self,
        reasoning,
        contradictions,
        verification,
        extracted_facts,
    ):

        risk_level = reasoning.get(
            "risk_level",
            "LOW"
        )

        risk_score = reasoning.get(
            "risk_score",
            0
        )

        reasons = reasoning.get(
            "reasons",
            []
        )

        review_items = reasoning.get(
            "review_items",
            []
        )

        # =====================================================
        # RECOMMENDATIONS
        # =====================================================

        recommendations = []

        # HIGH RISK
        if risk_level == "HIGH":

            recommendations.extend([
                "Perform manual investigation.",
                "Verify original supporting documents.",
                "Review claimant and vehicle history.",
                "Validate the reported incident circumstances.",
            ])

        # MEDIUM RISK
        elif risk_level == "MEDIUM":

            recommendations.extend([
                "Review the identified risk indicators.",
                "Verify supporting evidence before settlement.",
                "Request additional documentation if required.",
            ])

        # LOW RISK
        else:

            recommendations.append(
                "No major fraud indicators were detected."
            )

            if review_items:

                recommendations.append(
                    "Complete the following verification "
                    "checks before final claim approval."
                )

                recommendations.extend(
                    review_items
                )

            else:

                recommendations.append(
                    "Proceed with normal claim verification."
                )


        # =====================================================
        # CONTRADICTION RECOMMENDATION
        # =====================================================

        if contradictions:

            recommendations.append(
                "Review all detected cross-document "
                "contradictions."
            )


        # =====================================================
        # FINAL SUMMARY
        # =====================================================

        summary_parts = [
            f"The claim is classified as "
            f"{risk_level} risk "
            f"with a risk score of "
            f"{round(risk_score * 100)}%."
        ]

        if reasons:

            summary_parts.append(
                "Key risk factors: "
                + " ".join(reasons)
            )

        if review_items:

            summary_parts.append(
                "Additional verification is required "
                "for incomplete evidence."
            )

        summary = " ".join(
            summary_parts
        )


        # =====================================================
        # KEY FINDINGS
        # =====================================================

        key_findings = list(reasons)

        if review_items:

            key_findings.append(
                "Additional verification required:"
            )

            key_findings.extend(
                review_items
            )


        # =====================================================
        # RETURN REPORT
        # =====================================================

        return {

            "summary": summary,

            "risk_score": risk_score,

            "risk_percentage": round(
                risk_score * 100
            ),

            "risk_level": risk_level,

            "key_findings": key_findings,

            "contradictions": contradictions,

            "verification": verification,

            "review_items": review_items,

            "recommendations": recommendations,

            "evidence": extracted_facts,
        }