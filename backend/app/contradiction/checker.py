from __future__ import annotations

import requests
from datetime import datetime
from typing import Any


OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"


def _parse_datetime(
    date_value: str,
    time_value: str,
) -> datetime:
    """Convert date + time strings into a datetime object."""

    return datetime.strptime(
        f"{date_value} {time_value}",
        "%Y-%m-%d %H:%M",
    )


# ============================================================
# 1. TIMELINE CONTRADICTION
# ============================================================

def check_timeline_contradiction(
    police_facts: dict[str, Any],
    medical_facts: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Detect whether medical treatment occurred before
    the reported accident.
    """

    try:
        incident = _parse_datetime(
            police_facts["incident_date"],
            police_facts["incident_time"],
        )

        treatment = _parse_datetime(
            medical_facts["treatment_date"],
            medical_facts["treatment_time"],
        )
    except (KeyError, TypeError, ValueError):
        return None

    # Only flag if treatment happened before the accident
    if treatment < incident:

        difference_hours = (
            incident - treatment
        ).total_seconds() / 3600

        return {
            "type": "timeline_contradiction",
            "severity": "high",
            "description": (
                "Medical treatment occurred before "
                "the reported accident."
            ),
            "evidence": [
                {
                    "source": "police_report",
                    "fact": (
                        f"Accident occurred at "
                        f"{police_facts['incident_time']}"
                    ),
                },
                {
                    "source": "medical_report",
                    "fact": (
                        f"Treatment occurred at "
                        f"{medical_facts['treatment_time']}"
                    ),
                },
            ],
            "difference_hours": round(
                difference_hours,
                2,
            ),
        }

    return None


# ============================================================
# 2. DAMAGE DIRECTION CONTRADICTION
# ============================================================

def check_damage_contradiction(
    police_facts: dict[str, Any],
    repair_facts: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Detect a possible collision-direction/damage-location
    inconsistency.

    If the police report says the vehicle struck another
    vehicle and the repair invoice reports rear damage,
    flag the claim for investigation.
    """

    collision = (
        police_facts.get(
            "collision_description",
            "",
        )
        or ""
    ).lower()

    damage_location = (
        repair_facts.get(
            "damage_location",
            "",
        )
        or ""
    ).lower()

    if (
        "struck another vehicle" in collision
        and "rear" in damage_location
    ):

        return {
            "type": "damage_direction_contradiction",
            "severity": "medium",
            "description": (
                "The collision description indicates that "
                "the vehicle struck another vehicle, while "
                "the repair invoice reports rear damage."
            ),
            "evidence": [
                {
                    "source": "police_report",
                    "fact": (
                        police_facts.get(
                            "collision_description",
                            "",
                        )
                    ),
                },
                {
                    "source": "repair_invoice",
                    "fact": (
                        f"Damage location: "
                        f"{repair_facts.get('damage_location', '')}"
                    ),
                },
            ],
        }

    return None


# ============================================================
# 3. DAMAGE SEVERITY CONTRADICTION
# ============================================================

def check_severity_contradiction(
    police_facts: dict[str, Any],
    repair_facts: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Detect a mismatch between reported accident severity
    and the extent of repair damage.
    """

    police_description = (
        (
            police_facts.get(
                "collision_description",
                "",
            )
            or ""
        )
        + " "
        + (
            police_facts.get(
                "officer_notes",
                "",
            )
            or ""
        )
    ).lower()

    repair_description = (
        (
            repair_facts.get(
                "damage_description",
                "",
            )
            or ""
        )
        + " "
        + (
            repair_facts.get(
                "estimated_cause",
                "",
            )
            or ""
        )
    ).lower()

    minor_terms = [
        "minor",
        "cosmetic",
        "low speed",
        "light contact",
        "no structural damage",
    ]

    major_terms = [
        "extensive",
        "structural",
        "frame",
        "major high-impact",
        "reconstruction",
    ]

    minor_count = sum(
        term in police_description
        for term in minor_terms
    )

    major_count = sum(
        term in repair_description
        for term in major_terms
    )

    if minor_count >= 2 and major_count >= 2:

        return {
            "type": "damage_severity_contradiction",
            "severity": "high",
            "description": (
                "The police report describes a minor "
                "low-speed collision with no structural "
                "damage, while the repair invoice describes "
                "extensive structural damage."
            ),
            "evidence": [
                {
                    "source": "police_report",
                    "fact": (
                        police_facts.get(
                            "officer_notes",
                            "",
                        )
                    ),
                },
                {
                    "source": "repair_invoice",
                    "fact": (
                        repair_facts.get(
                            "damage_description",
                            "",
                        )
                    ),
                },
            ],
        }

    return None


# ============================================================
# 4. WEATHER CONTRADICTION
# ============================================================

def check_weather_consistency(
    police_facts: dict[str, Any],
    lat: float,
    lon: float,
) -> dict[str, Any] | None:
    """
    Cross-check the weather reported by the police report
    against historical precipitation data from Open-Meteo.

    A contradiction is reported when:
      - The police report says clear or sunny weather.
      - Historical Open-Meteo data reports precipitation > 0.

    API/network failures are handled gracefully and return None.
    """

    weather_reported = (
        police_facts.get(
            "weather_reported",
            "",
        )
        or ""
    ).lower()

    # Only investigate clear/sunny reports.
    if (
        "clear" not in weather_reported
        and "sunny" not in weather_reported
    ):
        return None

    incident_date = police_facts.get(
        "incident_date"
    )

    if not incident_date:
        return None

    try:
        response = requests.get(
            OPEN_METEO_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "start_date": incident_date,
                "end_date": incident_date,
                "hourly": "precipitation",
            },
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        precipitation = (
            data
            .get("hourly", {})
            .get("precipitation", [])
        )

    except (
        requests.exceptions.RequestException,
        ValueError,
        TypeError,
    ):
        # External API failure must not crash
        # the InsurGuard pipeline.
        return None

    if not precipitation:
        return None

    total_precipitation = sum(
        value or 0
        for value in precipitation
    )

    if total_precipitation <= 0:
        return None

    return {
        "type": "weather_contradiction",
        "severity": "medium",
        "description": (
            f"Police report states weather was "
            f"'{police_facts.get('weather_reported')}', "
            f"but historical weather data shows "
            f"{total_precipitation:.1f} mm of precipitation "
            f"on {incident_date}."
        ),
        "evidence": [
            {
                "source": "police_report",
                "fact": (
                    f"Weather reported: "
                    f"{police_facts.get('weather_reported')}"
                ),
            },
            {
                "source": "open_meteo",
                "fact": (
                    f"Total precipitation: "
                    f"{total_precipitation:.1f} mm"
                ),
            },
        ],
    }


# ============================================================
# 5. RUN ALL CONTRADICTION CHECKS
# ============================================================

def find_contradictions(
    police_facts: dict[str, Any],
    medical_facts: dict[str, Any],
    repair_facts: dict[str, Any],
    lat: float | None = None,
    lon: float | None = None,
) -> list[dict[str, Any]]:
    """
    Run all contradiction checks for one insurance claim.

    Weather verification is performed only when both latitude
    and longitude are provided.
    """

    contradictions: list[dict[str, Any]] = []

    # --------------------------------------------------------
    # Timeline
    # --------------------------------------------------------

    timeline = check_timeline_contradiction(
        police_facts,
        medical_facts,
    )

    if timeline:
        contradictions.append(timeline)

    # --------------------------------------------------------
    # Damage direction
    # --------------------------------------------------------

    damage = check_damage_contradiction(
        police_facts,
        repair_facts,
    )

    if damage:
        contradictions.append(damage)

    # --------------------------------------------------------
    # Damage severity
    # --------------------------------------------------------

    severity = check_severity_contradiction(
        police_facts,
        repair_facts,
    )

    if severity:
        contradictions.append(severity)

    # --------------------------------------------------------
    # Weather
    # --------------------------------------------------------

    if lat is not None and lon is not None:

        weather = check_weather_consistency(
            police_facts,
            lat,
            lon,
        )

        if weather:
            contradictions.append(weather)

    return contradictions