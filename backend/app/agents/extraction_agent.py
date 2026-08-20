from __future__ import annotations

import json
import os
import re
from typing import Any

import requests


OLLAMA_HOST = os.environ.get(
    "OLLAMA_HOST",
    "http://localhost:11434"
)

OLLAMA_MODEL = os.environ.get(
    "OLLAMA_MODEL",
    "llama3.1"
)


SCHEMAS: dict[str, dict[str, str]] = {
    "police_report": {
        "incident_date": "YYYY-MM-DD",
        "incident_time": "HH:MM",
        "location": "city and state",
        "weather_reported": "weather conditions stated in the report",
        "collision_description": "brief description of the collision",
        "at_fault_party": "party reported as at fault, or null",
        "officer_notes": "additional officer observations, or null",
    },
    "medical_report": {
        "patient_name": "patient name, or null",
        "treatment_date": "YYYY-MM-DD",
        "treatment_time": "HH:MM",
        "chief_complaint": "primary complaint",
        "reported_onset": "verbatim quote describing when symptoms started",
    },
    "repair_invoice": {
        "vehicle": "vehicle make, model and year",
        "service_date": "YYYY-MM-DD",
        "damage_description": "description of the damage",
        "damage_location": "front, rear, or side",
        "estimated_cause": "estimated cause, or null",
        "total_cost": "numeric total cost",
    },
}


def _build_prompt(document_text: str, document_type: str) -> str:
    """Build a strict JSON extraction prompt."""

    fields = SCHEMAS[document_type]

    schema = "\n".join(
        f'    "{field}": "{description}"'
        for field, description in fields.items()
    )

    return f"""
You are an insurance document extraction system.

Document type:
{document_type}

Extract facts ONLY from the document below.

Return ONLY one valid JSON object.

Rules:
1. Use exactly the requested fields.
2. Do not add extra fields.
3. Do not invent information.
4. If a field is not present, return null.
5. Dates must use YYYY-MM-DD.
6. Times must use 24-hour HH:MM.
7. reported_onset must preserve the original wording as a verbatim quote.

Required JSON structure:

{{
{schema}
}}

Document:
--------------------
{document_text}
--------------------

Return only JSON.
""".strip()


def _clean_response(text: str) -> str:
    """Remove markdown fences and surrounding whitespace."""

    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    return text.strip()


def _parse_json(text: str) -> dict[str, Any]:
    """Parse JSON returned by the local model."""

    cleaned = _clean_response(text)

    try:
        result = json.loads(cleaned)

        if not isinstance(result, dict):
            raise ValueError("Model response is not a JSON object.")

        return result

    except json.JSONDecodeError:

        # Try to find a JSON object inside additional model text.
        match = re.search(
            r"\{.*\}",
            cleaned,
            flags=re.DOTALL,
        )

        if not match:
            raise ValueError(
                f"Could not find JSON in model response:\n{cleaned}"
            )

        try:
            result = json.loads(match.group(0))

            if not isinstance(result, dict):
                raise ValueError(
                    "Extracted JSON is not an object."
                )

            return result

        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON returned by Ollama:\n{cleaned}"
            ) from exc


def _validate_result(
    result: dict[str, Any],
    document_type: str,
) -> dict[str, Any]:
    """Ensure the model returned the expected fields."""

    expected_fields = SCHEMAS[document_type]

    # Add missing fields as None.
    for field in expected_fields:
        if field not in result:
            result[field] = None

    # Remove unexpected fields.
    result = {
        field: result[field]
        for field in expected_fields
    }

    return result


def extract_facts(
    document_text: str,
    document_type: str,
) -> dict[str, Any]:
    """
    Extract structured facts from an insurance document.

    Args:
        document_text: Raw document text.
        document_type:
            police_report
            medical_report
            repair_invoice

    Returns:
        Dictionary containing the extracted structured facts.

    Raises:
        ValueError: Invalid document type or invalid model output.
        RuntimeError: Ollama cannot be reached.
    """

    if document_type not in SCHEMAS:
        raise ValueError(
            f"Unsupported document type: {document_type}"
        )

    if not document_text.strip():
        raise ValueError(
            "document_text cannot be empty."
        )

    prompt = _build_prompt(
        document_text,
        document_type,
    )

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0
                },
            },
            timeout=120,
        )

        response.raise_for_status()

    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            f"Cannot connect to Ollama at {OLLAMA_HOST}. "
            "Make sure Ollama is running."
        ) from exc

    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            "Ollama request timed out."
        ) from exc

    raw_response = response.json()

    if "response" not in raw_response:
        raise RuntimeError(
            f"Unexpected Ollama response: {raw_response}"
        )

    result = _parse_json(
        raw_response["response"]
    )

    return _validate_result(
        result,
        document_type,
    )