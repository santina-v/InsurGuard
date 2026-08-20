class EvidenceVerificationAgent:
    """
    Agent 2 - Evidence Verification Agent

    Compares structured facts extracted from:
        - Police Report
        - Medical Report
        - Repair Invoice

    Important:
    The agent never assumes a match when information is missing.

    Status values:
        MATCH
        MISMATCH
        UNKNOWN
    """

    def verify(self, extracted_facts):

        police = extracted_facts.get(
            "police_report", {}
        )

        medical = extracted_facts.get(
            "medical_report", {}
        )

        repair = extracted_facts.get(
            "repair_invoice", {}
        )

        evidence = []

        # =====================================================
        # 1. IDENTITY VERIFICATION
        # =====================================================

        patient_name = self._clean(
            medical.get("patient_name")
        )

        police_claimant = self._clean(
            police.get("claimant_name")
        )

        repair_customer = self._clean(
            repair.get("customer")
        )

        identity_values = [
            value
            for value in [
                patient_name,
                police_claimant,
                repair_customer,
            ]
            if value
        ]

        if len(identity_values) < 2:

            identity_status = "UNKNOWN"

            evidence.append({
                "type": "identity_verification",
                "status": "UNKNOWN",
                "description": (
                    "There is not enough claimant identity "
                    "information across the documents to "
                    "perform a complete comparison."
                ),
            })

        else:

            normalized_names = {
                value.lower()
                for value in identity_values
            }

            if len(normalized_names) == 1:

                identity_status = "MATCH"

                evidence.append({
                    "type": "identity_verification",
                    "status": "MATCH",
                    "description": (
                        "Claimant identity is consistent "
                        "across the available documents."
                    ),
                })

            else:

                identity_status = "MISMATCH"

                evidence.append({
                    "type": "identity_verification",
                    "status": "MISMATCH",
                    "description": (
                        "Different claimant identities were "
                        "found across the documents."
                    ),
                })


        # =====================================================
        # 2. VEHICLE VERIFICATION
        # =====================================================

        police_vehicle = self._clean(
            police.get("claimant_vehicle")
        )

        repair_vehicle = self._clean(
            repair.get("vehicle")
        )

        if not police_vehicle or not repair_vehicle:

            vehicle_status = "UNKNOWN"

            missing_sources = []

            if not police_vehicle:
                missing_sources.append(
                    "police report"
                )

            if not repair_vehicle:
                missing_sources.append(
                    "repair invoice"
                )

            evidence.append({
                "type": "vehicle_verification",
                "status": "UNKNOWN",
                "description": (
                    "Vehicle information is incomplete. "
                    "Claimant vehicle information was not "
                    "available from "
                    + " and ".join(missing_sources)
                    + "."
                ),
            })

        else:

            if self._normalize_vehicle(
                police_vehicle
            ) == self._normalize_vehicle(
                repair_vehicle
            ):

                vehicle_status = "MATCH"

                evidence.append({
                    "type": "vehicle_verification",
                    "status": "MATCH",
                    "police_vehicle": police_vehicle,
                    "repair_vehicle": repair_vehicle,
                    "description": (
                        "Claimant vehicle information "
                        "matches across the available documents."
                    ),
                })

            else:

                vehicle_status = "MISMATCH"

                evidence.append({
                    "type": "vehicle_verification",
                    "status": "MISMATCH",
                    "police_vehicle": police_vehicle,
                    "repair_vehicle": repair_vehicle,
                    "description": (
                        "Claimant vehicle information differs "
                        "between the police report and repair invoice."
                    ),
                })


        # =====================================================
        # 3. INCIDENT / TREATMENT DATE
        # =====================================================

        incident_date = self._clean(
            police.get("incident_date")
        )

        treatment_date = self._clean(
            medical.get("treatment_date")
        )

        if not incident_date or not treatment_date:

            date_status = "UNKNOWN"

            evidence.append({
                "type": "date_verification",
                "status": "UNKNOWN",
                "description": (
                    "Incident date or treatment date "
                    "is missing."
                ),
            })

        elif incident_date == treatment_date:

            date_status = "MATCH"

            evidence.append({
                "type": "date_verification",
                "status": "MATCH",
                "incident_date": incident_date,
                "treatment_date": treatment_date,
                "description": (
                    "The medical treatment date matches "
                    "the reported incident date."
                ),
            })

        else:

            date_status = "MISMATCH"

            evidence.append({
                "type": "date_verification",
                "status": "MISMATCH",
                "incident_date": incident_date,
                "treatment_date": treatment_date,
                "description": (
                    "The medical treatment date differs "
                    "from the reported incident date."
                ),
            })


        # =====================================================
        # 4. MEDICAL TIMELINE
        # =====================================================

        incident_time = self._clean(
            police.get("incident_time")
        )

        medical_onset = self._clean(
            medical.get("reported_onset")
        )

        if not incident_time or not medical_onset:

            timeline_status = "UNKNOWN"

            evidence.append({
                "type": "timeline_verification",
                "status": "UNKNOWN",
                "description": (
                    "Incident time or medical symptom "
                    "onset information is missing."
                ),
            })

        else:

            # We currently have textual onset information.
            # A more advanced version can normalize natural
            # language times using an LLM/time parser.

            normalized_incident = (
                incident_time.replace(" ", "")
            )

            normalized_onset = (
                medical_onset.replace(" ", "")
            )

            if normalized_incident in normalized_onset:

                timeline_status = "MATCH"

                evidence.append({
                    "type": "timeline_verification",
                    "status": "MATCH",
                    "incident_time": incident_time,
                    "medical_onset": medical_onset,
                    "description": (
                        "The reported medical symptom onset "
                        "is consistent with the incident time."
                    ),
                })

            else:

                timeline_status = "UNKNOWN"

                evidence.append({
                    "type": "timeline_verification",
                    "status": "UNKNOWN",
                    "incident_time": incident_time,
                    "medical_onset": medical_onset,
                    "description": (
                        "The available timeline information "
                        "requires further temporal analysis."
                    ),
                })


        # =====================================================
        # 5. DAMAGE VERIFICATION
        # =====================================================

        police_notes = self._clean(
            police.get("officer_notes")
        )

        police_collision = self._clean(
            police.get("collision_description")
        )

        repair_damage = self._clean(
            repair.get("damage_description")
        )

        repair_location = self._clean(
            repair.get("damage_location")
        )

        police_damage_text = " ".join(
            value
            for value in [
                police_notes,
                police_collision,
            ]
            if value
        )

        if not police_damage_text or not repair_damage:

            damage_status = "UNKNOWN"

            evidence.append({
                "type": "damage_verification",
                "status": "UNKNOWN",
                "description": (
                    "Insufficient damage information is "
                    "available for comparison."
                ),
            })

        else:

            police_front_left = (
                "front-left" in
                police_damage_text.lower()
                or "front left" in
                police_damage_text.lower()
            )

            repair_front = (
                "front" in
                repair_damage.lower()
                or (
                    repair_location
                    and "front" in repair_location.lower()
                )
            )

            if police_front_left and repair_front:

                damage_status = "MATCH"

                evidence.append({
                    "type": "damage_verification",
                    "status": "MATCH",
                    "description": (
                        "The reported front/front-left "
                        "damage is consistent between "
                        "the police report and repair invoice."
                    ),
                    "police_report": police_damage_text,
                    "repair_invoice": repair_damage,
                })

            else:

                damage_status = "UNKNOWN"

                evidence.append({
                    "type": "damage_verification",
                    "status": "UNKNOWN",
                    "description": (
                        "Damage information is available, "
                        "but a reliable semantic comparison "
                        "requires deeper analysis."
                    ),
                    "police_report": police_damage_text,
                    "repair_invoice": repair_damage,
                })


        # =====================================================
        # 6. OVERALL VERIFICATION STATUS
        # =====================================================

        statuses = [
            identity_status,
            vehicle_status,
            date_status,
            timeline_status,
            damage_status,
        ]

        if "MISMATCH" in statuses:

            overall_status = "MISMATCH"

        elif all(
            status == "MATCH"
            for status in statuses
        ):

            overall_status = "MATCH"

        else:

            overall_status = "PARTIAL"


        # =====================================================
        # 7. RETURN RESULT
        # =====================================================

        return {

            "overall_status": overall_status,

            "identity": identity_status,

            "vehicle": vehicle_status,

            "date": date_status,

            "timeline": timeline_status,

            "damage": damage_status,

            # Backward-compatible fields
            "identity_match": (
                identity_status == "MATCH"
            ),

            "vehicle_match": (
                vehicle_status == "MATCH"
            ),

            "date_match": (
                date_status == "MATCH"
            ),

            "timeline_match": (
                timeline_status == "MATCH"
            ),

            "damage_consistent": (
                damage_status == "MATCH"
            ),

            "evidence": evidence,
        }


    # =========================================================
    # HELPER: CLEAN TEXT
    # =========================================================

    @staticmethod
    def _clean(value):

        if value is None:
            return None

        if not isinstance(value, str):
            return str(value).strip()

        value = value.strip()

        return value if value else None


    # =========================================================
    # HELPER: NORMALIZE VEHICLE
    # =========================================================

    @staticmethod
    def _normalize_vehicle(value):

        if not value:
            return ""

        return (
            value
            .lower()
            .replace("-", "")
            .replace(" ", "")
            .replace("_", "")
        )