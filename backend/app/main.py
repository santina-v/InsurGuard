from __future__ import annotations

import re

import networkx as nx

from fastapi import (
    FastAPI,
    File,
    UploadFile,
    HTTPException,
    Form,
)

from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# DOCUMENT EXTRACTION
# ============================================================

from app.services.pdf_extractor import (
    extract_text_from_document
)


# ============================================================
# EXISTING MODULES
# ============================================================

from app.agents.extraction_agent import (
    extract_facts
)

from app.contradiction.checker import (
    find_contradictions
)

from app.scoring.fraud_scorer import (
    score_claim
)

from app.graph.graph_builder import (
    build_claim_graph
)


# ============================================================
# MULTI-AGENT MODULES
# ============================================================

from app.agents.verification_agent import (
    EvidenceVerificationAgent
)

from app.agents.fraud_reasoning_agent import (
    FraudReasoningAgent
)

from app.agents.report_agent import (
    InvestigationReportAgent
)


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="InsurGuard API",
    description=(
        "AI-powered insurance fraud detection system "
        "with multi-agent document analysis"
    ),
    version="1.0.0",
)


# ============================================================
# INITIALIZE AGENTS
# ============================================================

verification_agent = EvidenceVerificationAgent()

fraud_reasoning_agent = FraudReasoningAgent()

report_agent = InvestigationReportAgent()


# ============================================================
# SUPPORTED DOCUMENT FORMATS
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".doc",
    ".jpg",
    ".jpeg",
    ".png",
    ".txt",
    ".xlsx",
    ".xls",
    ".csv",
}


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "application": "InsurGuard",
        "status": "running",
        "message": (
            "Insurance fraud detection API"
        ),
        "supported_documents": sorted(
            SUPPORTED_EXTENSIONS
        ),
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "InsurGuard Backend",
        "multi_agent": True,
    }


# ============================================================
# HELPER — VALIDATE DOCUMENT
# ============================================================

def validate_document(
    uploaded_file: UploadFile,
    document_name: str,
):
    """
    Validate that a document exists and has a
    supported file extension.
    """

    filename = uploaded_file.filename or ""

    if not filename:
        raise HTTPException(
            status_code=400,
            detail=(
                f"{document_name} was not uploaded "
                "or has no filename."
            ),
        )

    filename_lower = filename.lower()

    extension = ""

    if "." in filename_lower:
        extension = (
            "."
            + filename_lower.rsplit(".", 1)[1]
        )

    if extension not in SUPPORTED_EXTENSIONS:

        supported = ", ".join(
            sorted(SUPPORTED_EXTENSIONS)
        )

        raise HTTPException(
            status_code=400,
            detail=(
                f"{document_name} has unsupported "
                f"file format '{extension}'. "
                f"Supported formats: {supported}"
            ),
        )

    return filename


# ============================================================
# HELPER — EXTRACT DOCUMENT
# ============================================================

async def read_and_extract_document(
    uploaded_file: UploadFile,
    document_name: str,
) -> str:

    filename = validate_document(
        uploaded_file,
        document_name,
    )

    try:

        file_bytes = await uploaded_file.read()

        if not file_bytes:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"{document_name} is empty."
                ),
            )

        extracted_text = (
            extract_text_from_document(
                file_bytes,
                filename,
            )
        )

        if not extracted_text or not extracted_text.strip():

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Could not extract readable "
                    f"text from {document_name}."
                ),
            )

        return extracted_text.strip()

    except HTTPException:
        raise

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=(
                f"{document_name}: {str(exc)}"
            ),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to process {document_name}: "
                f"{str(exc)}"
            ),
        ) from exc


# ============================================================
# HELPER — NORMALIZE VALUES
# ============================================================

def _text(value) -> str:
    """Return a normalized string for safe comparisons."""
    if value is None:
        return ""
    return str(value).strip().lower()


def _minutes(value):
    """Convert an HH:MM value embedded in text to minutes."""
    if value is None:
        return None

    match = re.search(
        r"\b([01]?\d|2[0-3]):([0-5]\d)\b",
        str(value),
    )

    if not match:
        return None

    return int(match.group(1)) * 60 + int(match.group(2))


def _contains_any(value, terms) -> bool:
    value = _text(value)
    return any(term in value for term in terms)


# ============================================================
# HELPER — DETERMINISTIC EVIDENCE VERIFICATION
# ============================================================

def build_evidence_verification(extracted_facts: dict) -> dict:
    """
    Verify facts that can be compared directly from Agent 1 output.

    The AI verification agent remains available as a secondary source,
    but deterministic checks are used for dates, times and damage so an
    LLM cannot incorrectly turn an obvious mismatch into MATCH/UNKNOWN.
    """

    police = extracted_facts.get("police_report") or {}
    medical = extracted_facts.get("medical_report") or {}
    repair = extracted_facts.get("repair_invoice") or {}

    evidence = []

    # ------------------------------------------------------------
    # IDENTITY
    # ------------------------------------------------------------
    # The current extraction schema only guarantees patient_name in the
    # medical report. Do not invent identity data that was not extracted.
    patient_name = medical.get("patient_name")

    identity_status = "UNKNOWN"
    identity_description = (
        "Claimant identity cannot be fully verified because the current "
        "police and repair extraction schemas do not provide a comparable "
        "claimant identity field."
    )

    if patient_name:
        identity_description = (
            "Patient identity was extracted from the medical report, "
            "but a second comparable identity value is not available."
        )

    evidence.append({
        "type": "identity_verification",
        "status": identity_status,
        "description": identity_description,
    })

    # ------------------------------------------------------------
    # VEHICLE
    # ------------------------------------------------------------
    # The current extraction schema guarantees vehicle only in the repair
    # invoice, so a cross-document vehicle MATCH cannot be claimed.
    vehicle = repair.get("vehicle")

    vehicle_status = "UNKNOWN"
    vehicle_description = (
        "Vehicle information was extracted from the repair invoice, "
        "but the current police-report extraction schema does not provide "
        "a comparable claimant vehicle field."
    )

    if not vehicle:
        vehicle_description = (
            "Vehicle information is incomplete in the available extracted facts."
        )

    evidence.append({
        "type": "vehicle_verification",
        "status": vehicle_status,
        "description": vehicle_description,
    })

    # ------------------------------------------------------------
    # DATE
    # ------------------------------------------------------------
    incident_date = police.get("incident_date")
    treatment_date = medical.get("treatment_date")

    if incident_date and treatment_date:
        date_match = _text(incident_date) == _text(treatment_date)
        date_status = "MATCH" if date_match else "MISMATCH"
        date_description = (
            "The medical treatment date matches the reported incident date."
            if date_match
            else
            "The medical treatment date differs from the reported incident date."
        )
    else:
        date_match = False
        date_status = "UNKNOWN"
        date_description = (
            "Insufficient date information was extracted for comparison."
        )

    evidence.append({
        "type": "date_verification",
        "status": date_status,
        "incident_date": incident_date,
        "treatment_date": treatment_date,
        "description": date_description,
    })

    # ------------------------------------------------------------
    # TIMELINE
    # ------------------------------------------------------------
    incident_time = police.get("incident_time")
    treatment_time = medical.get("treatment_time")
    reported_onset = medical.get("reported_onset")

    incident_minutes = _minutes(incident_time)
    treatment_minutes = _minutes(treatment_time)

    if incident_minutes is not None and treatment_minutes is not None:
        if treatment_minutes < incident_minutes:
            timeline_status = "MISMATCH"
            timeline_match = False
            timeline_description = (
                f"Medical treatment began at {treatment_time}, before the "
                f"reported accident time of {incident_time}."
            )
        else:
            timeline_status = "MATCH"
            timeline_match = True
            timeline_description = (
                f"Medical treatment at {treatment_time} occurred after the "
                f"reported accident time of {incident_time}."
            )
    else:
        # A phrase such as "this morning's accident" is not enough to prove
        # a precise time mismatch, so keep the result UNKNOWN rather than guess.
        timeline_status = "UNKNOWN"
        timeline_match = False
        timeline_description = (
            "Insufficient time information was extracted for a reliable "
            "timeline comparison."
        )

    evidence.append({
        "type": "timeline_verification",
        "status": timeline_status,
        "incident_time": incident_time,
        "medical_treatment_time": treatment_time,
        "medical_onset": reported_onset,
        "description": timeline_description,
    })

    # ------------------------------------------------------------
    # DAMAGE
    # ------------------------------------------------------------
    damage_location = repair.get("damage_location")
    damage_description = repair.get("damage_description")
    collision_description = police.get("collision_description")
    officer_notes = police.get("officer_notes")

    police_damage_text = " ".join(
        value for value in [collision_description, officer_notes]
        if value
    )

    repair_damage_text = " ".join(
        value for value in [damage_location, damage_description]
        if value
    )

    if police_damage_text and repair_damage_text:
        police_text = _text(police_damage_text)
        repair_text = _text(repair_damage_text)

        front_police = _contains_any(
            police_text,
            ["front", "front-left", "front-right"],
        )
        rear_police = _contains_any(
            police_text,
            ["rear", "rear-left", "rear-right", "back"],
        )
        side_police = _contains_any(
            police_text,
            ["side", "left door", "right door", "left side", "right side"],
        )

        front_repair = _contains_any(
            repair_text,
            ["front", "front-left", "front-right"],
        )
        rear_repair = _contains_any(
            repair_text,
            ["rear", "rear-left", "rear-right", "back"],
        )
        side_repair = _contains_any(
            repair_text,
            ["side", "left door", "right door", "left side", "right side"],
        )

        if (
            (front_police and rear_repair)
            or (rear_police and front_repair)
            or (side_police and (front_repair or rear_repair))
            or (side_repair and (front_police or rear_police))
        ):
            damage_status = "MISMATCH"
            damage_consistent = False
            damage_description_result = (
                "The reported collision/damage location conflicts with the "
                "repair invoice damage location."
            )
        elif (
            (front_police and front_repair)
            or (rear_police and rear_repair)
            or (side_police and side_repair)
        ):
            damage_status = "MATCH"
            damage_consistent = True
            damage_description_result = (
                "The reported damage location is consistent with the repair invoice."
            )
        else:
            damage_status = "UNKNOWN"
            damage_consistent = False
            damage_description_result = (
                "Damage information is available, but the locations could not "
                "be reliably compared."
            )
    else:
        damage_status = "UNKNOWN"
        damage_consistent = False
        damage_description_result = (
            "Insufficient damage information was extracted for comparison."
        )

    evidence.append({
        "type": "damage_verification",
        "status": damage_status,
        "description": damage_description_result,
        "damage_location": damage_location,
        "damage_description": damage_description,
    })

    statuses = [item["status"] for item in evidence]

    if "MISMATCH" in statuses:
        overall_status = "MISMATCH"
    elif all(status == "MATCH" for status in statuses):
        overall_status = "MATCH"
    else:
        overall_status = "PARTIAL"

    return {
        "overall_status": overall_status,
        "identity": identity_status,
        "vehicle": vehicle_status,
        "date": date_status,
        "timeline": timeline_status,
        "damage": damage_status,
        "identity_match": identity_status == "MATCH",
        "vehicle_match": vehicle_status == "MATCH",
        "date_match": date_status == "MATCH",
        "timeline_match": timeline_status == "MATCH",
        "damage_consistent": damage_consistent,
        "evidence": evidence,
    }


# ============================================================
# HELPER — MERGE AI + DETERMINISTIC VERIFICATION
# ============================================================

def merge_verification(ai_result, deterministic_result):
    """Use deterministic checks as the source of truth when available."""

    merged = dict(ai_result) if isinstance(ai_result, dict) else {}

    # Deterministic results are authoritative for fields we can calculate.
    for key in (
        "overall_status",
        "identity",
        "vehicle",
        "date",
        "timeline",
        "damage",
        "identity_match",
        "vehicle_match",
        "date_match",
        "timeline_match",
        "damage_consistent",
        "evidence",
    ):
        if key in deterministic_result:
            merged[key] = deterministic_result[key]

    # Keep AI output separately for transparency/debugging.
    if isinstance(ai_result, dict):
        merged["ai_verification"] = ai_result

    return merged


# ============================================================
# HELPER — CLEAN REPORT
# ============================================================

def clean_report(report, reasoning, contradictions, verification):
    """Normalize Agent 4 output and remove duplicate list items."""

    report = dict(report) if isinstance(report, dict) else {}

    def unique(items):
        output = []
        seen = set()

        for item in items or []:
            text = str(item).strip()
            if not text:
                continue

            key = text.lower()
            if key not in seen:
                seen.add(key)
                output.append(text)

        return output

    risk_score = float(
        reasoning.get("risk_score", 0) or 0
    )
    risk_score = max(0.0, min(1.0, risk_score))
    risk_percentage = round(risk_score * 100)
    risk_level = reasoning.get("risk_level", "LOW")

    reasons = unique(reasoning.get("reasons", []))
    review_items = unique(reasoning.get("review_items", []))

    contradiction_items = []
    for contradiction in contradictions or []:
        if not isinstance(contradiction, dict):
            continue
        text = (
            contradiction.get("explanation")
            or contradiction.get("description")
        )
        if text:
            contradiction_items.append(text)

    key_findings = unique(
        reasons + contradiction_items
    )

    if not key_findings:
        key_findings = [
            "No significant risk contributors were identified."
        ]

    recommendations = unique(
        report.get("recommendations", [])
    )

    if not recommendations:
        if contradictions:
            recommendations = [
                "Review each identified contradiction against the original source documents.",
                "Complete investigator verification before final claim approval.",
            ]
        else:
            recommendations = [
                "Proceed with normal claim verification and review the available evidence."
            ]

    summary = (
        f"The claim is classified as {risk_level} risk with a risk score "
        f"of {risk_percentage}%."
    )

    if key_findings:
        summary += " Key findings: " + "; ".join(key_findings[:5]) + "."

    report.update({
        "summary": summary,
        "risk_score": risk_score,
        "risk_percentage": risk_percentage,
        "risk_level": risk_level,
        "key_findings": key_findings,
        "recommendations": recommendations,
        "contradictions": contradictions or [],
        "verification": verification,
        "review_items": review_items,
    })

    return report


# ============================================================
# HELPER — RUN MULTI-AGENT PIPELINE
# ============================================================

def run_claim_pipeline(
    police_text: str,
    medical_text: str,
    repair_text: str,
    claim_amount: float,
    region_avg_claim_amount: float,
    claimant_prior_claims_18mo: int,
    policy_tenure_months: int,
    location_lat: float | None,
    location_lon: float | None,
):
    """
    Complete InsurGuard multi-agent pipeline.

    Pipeline:

        Documents
             ↓
        Agent 1 - Extraction
             ↓
        Agent 2 - Verification
             ↓
        Contradiction Detection
             ↓
        Knowledge Graph
             ↓
        Fraud Scoring
             ↓
        Agent 3 - Fraud Reasoning
             ↓
        Agent 4 - Investigation Report
             ↓
        Final Assessment
    """

    # ========================================================
    # AGENT 1 — DOCUMENT EXTRACTION
    # ========================================================

    police_facts = extract_facts(
        police_text,
        "police_report",
    )

    medical_facts = extract_facts(
        medical_text,
        "medical_report",
    )

    repair_facts = extract_facts(
        repair_text,
        "repair_invoice",
    )

    extracted_facts = {
        "police_report": police_facts,
        "medical_report": medical_facts,
        "repair_invoice": repair_facts,
    }


    # ========================================================
    # AGENT 2 — EVIDENCE VERIFICATION
    # ========================================================

    # Run the AI verifier, but never allow it to overwrite facts that
    # can be deterministically compared from the extracted schema.
    try:
        ai_verification = verification_agent.verify(
            extracted_facts
        )
    except Exception as exc:
        ai_verification = {
            "status": "unavailable",
            "error": str(exc),
        }

    deterministic_verification = build_evidence_verification(
        extracted_facts
    )

    verification = merge_verification(
        ai_verification,
        deterministic_verification,
    )


    # ========================================================
    # CROSS-DOCUMENT CONTRADICTION DETECTION
    # ========================================================

    contradictions = find_contradictions(
        police_facts,
        medical_facts,
        repair_facts,
        location_lat,
        location_lon,
    )


    # ========================================================
    # KNOWLEDGE GRAPH
    # ========================================================

    claim_graph = build_claim_graph(
        police_facts,
        medical_facts,
        repair_facts,
    )

    graph_data = nx.node_link_data(
        claim_graph
    )


    # ========================================================
    # CLAIM METADATA
    # ========================================================

    metadata = {
        "claim_amount": claim_amount,
        "region_avg_claim_amount": (
            region_avg_claim_amount
        ),
        "claimant_prior_claims_18mo": (
            claimant_prior_claims_18mo
        ),
        "policy_tenure_months": (
            policy_tenure_months
        ),
        "location_lat": location_lat,
        "location_lon": location_lon,
    }


    # ========================================================
    # FRAUD SCORING ENGINE
    # ========================================================

    score = score_claim(
        metadata,
        contradiction_count=len(
            contradictions
        ),
    )

    # Keep the score bounded even if a custom scorer returns an unexpected value.
    risk_score = float(score.get("base_score", 0) or 0)
    risk_score = max(0.0, min(1.0, risk_score))


    # ========================================================
    # RISK LEVEL
    # ========================================================

    if risk_score >= 0.70:

        risk_level = "HIGH"

    elif risk_score >= 0.40:

        risk_level = "MEDIUM"

    else:

        risk_level = "LOW"


    # ========================================================
    # AGENT 3 — FRAUD REASONING
    # ========================================================

    reasoning = fraud_reasoning_agent.reason(
        risk_score=risk_score,
        risk_level=risk_level,
        score_contributors=score[
            "score_contributors"
        ],
        contradictions=contradictions,
        verification=verification,
    )


    # ========================================================
    # AGENT 4 — INVESTIGATION REPORT
    # ========================================================

    try:
        investigation_report = report_agent.generate(
            reasoning=reasoning,
            contradictions=contradictions,
            verification=verification,
            extracted_facts=extracted_facts,
        )
    except Exception:
        # The final API must still return a useful investigation report
        # if the optional LLM report agent is temporarily unavailable.
        investigation_report = {}

    investigation_report = clean_report(
        report=investigation_report,
        reasoning=reasoning,
        contradictions=contradictions,
        verification=verification,
    )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {
        "status": "success",

        "message": (
            "Documents analyzed successfully "
            "using the InsurGuard multi-agent pipeline."
        ),

        # ----------------------------------------------------
        # SCORE
        # ----------------------------------------------------

        "risk_score": risk_score,

        "risk_percentage": round(
            risk_score * 100
        ),
        "risk_score_display": f"{round(risk_score * 100)}%",

        "risk_level": risk_level,

        # ----------------------------------------------------
        # CONTRADICTIONS
        # ----------------------------------------------------

        "contradiction_count": len(
            contradictions
        ),

        "contradictions": contradictions,

        # ----------------------------------------------------
        # SCORE CONTRIBUTORS
        # ----------------------------------------------------

        "score_contributors": score[
            "score_contributors"
        ],

        # ----------------------------------------------------
        # CLAIM METADATA
        # ----------------------------------------------------

        "claim_metadata": metadata,

        # ----------------------------------------------------
        # AGENT 2
        # ----------------------------------------------------

        "verification": verification,

        # ----------------------------------------------------
        # AGENT 3
        # ----------------------------------------------------

        "reasoning": reasoning,

        # ----------------------------------------------------
        # AGENT 4
        # ----------------------------------------------------

        "investigation_report": (
            investigation_report
        ),

        # ----------------------------------------------------
        # KNOWLEDGE GRAPH
        # ----------------------------------------------------

        "graph": graph_data,

        # ----------------------------------------------------
        # AGENT 1
        # ----------------------------------------------------

        "extracted_facts": extracted_facts,
    }


# ============================================================
# LEGACY / TEXT CLAIM ANALYSIS
# ============================================================

@app.post("/api/claims/analyze")
async def analyze_claim(

    police_report: UploadFile = File(...),

    medical_report: UploadFile = File(...),

    repair_invoice: UploadFile = File(...),

    claim_amount: float = Form(...),

    region_avg_claim_amount: float = Form(...),

    claimant_prior_claims_18mo: int = Form(...),

    policy_tenure_months: int = Form(...),

    location_lat: float | None = Form(None),

    location_lon: float | None = Form(None),
):

    """
    Analyze uploaded insurance documents.

    This endpoint now uses the same universal document
    extraction and multi-agent pipeline.
    """

    try:

        # ====================================================
        # READ AND EXTRACT DOCUMENTS
        # ====================================================

        police_text = (
            await read_and_extract_document(
                police_report,
                "Police Report",
            )
        )

        medical_text = (
            await read_and_extract_document(
                medical_report,
                "Medical Report",
            )
        )

        repair_text = (
            await read_and_extract_document(
                repair_invoice,
                "Repair Invoice",
            )
        )


        # ====================================================
        # RUN PIPELINE
        # ====================================================

        return run_claim_pipeline(
            police_text=police_text,
            medical_text=medical_text,
            repair_text=repair_text,
            claim_amount=claim_amount,
            region_avg_claim_amount=(
                region_avg_claim_amount
            ),
            claimant_prior_claims_18mo=(
                claimant_prior_claims_18mo
            ),
            policy_tenure_months=(
                policy_tenure_months
            ),
            location_lat=location_lat,
            location_lon=location_lon,
        )


    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


# ============================================================
# UNIVERSAL DOCUMENT CLAIM ANALYSIS
# ============================================================

@app.post("/api/claims/analyze-pdfs")
async def analyze_claim_pdfs(

    police_report: UploadFile = File(...),

    medical_report: UploadFile = File(...),

    repair_invoice: UploadFile = File(...),

    claim_amount: float = Form(...),

    region_avg_claim_amount: float = Form(...),

    claimant_prior_claims_18mo: int = Form(...),

    policy_tenure_months: int = Form(...),

    location_lat: float | None = Form(None),

    location_lon: float | None = Form(None),
):

    """
    Analyze insurance claim documents.

    IMPORTANT:
    The endpoint name is kept as /analyze-pdfs so that
    the existing React frontend continues to work.

    However, the endpoint now accepts:

        PDF
        DOCX
        DOC
        JPG
        JPEG
        PNG
        TXT
        XLSX
        XLS
        CSV

    Multi-Agent Pipeline:

        Uploaded Documents
                 ↓
        Agent 1 — Extraction
                 ↓
        Structured Facts
                 ↓
        Agent 2 — Verification
                 ↓
        Verified Evidence
                 ↓
        Contradiction Detection
                 ↓
        Knowledge Graph
                 ↓
        Fraud Scoring
                 ↓
        Agent 3 — Fraud Reasoning
                 ↓
        Agent 4 — Investigation Report
                 ↓
        Final Explainable Assessment
    """

    try:

        # ====================================================
        # DOCUMENTS
        # ====================================================

        documents = {
            "police_report": police_report,
            "medical_report": medical_report,
            "repair_invoice": repair_invoice,
        }


        # ====================================================
        # VALIDATE DOCUMENTS
        # ====================================================

        for document_name, uploaded_file in (
            documents.items()
        ):

            validate_document(
                uploaded_file,
                document_name.replace(
                    "_",
                    " "
                ).title(),
            )


        # ====================================================
        # EXTRACT POLICE REPORT
        # ====================================================

        police_text = (
            await read_and_extract_document(
                police_report,
                "Police Report",
            )
        )


        # ====================================================
        # EXTRACT MEDICAL REPORT
        # ====================================================

        medical_text = (
            await read_and_extract_document(
                medical_report,
                "Medical Report",
            )
        )


        # ====================================================
        # EXTRACT REPAIR INVOICE
        # ====================================================

        repair_text = (
            await read_and_extract_document(
                repair_invoice,
                "Repair Invoice",
            )
        )


        # ====================================================
        # RUN COMPLETE MULTI-AGENT PIPELINE
        # ====================================================

        result = run_claim_pipeline(

            police_text=police_text,

            medical_text=medical_text,

            repair_text=repair_text,

            claim_amount=claim_amount,

            region_avg_claim_amount=(
                region_avg_claim_amount
            ),

            claimant_prior_claims_18mo=(
                claimant_prior_claims_18mo
            ),

            policy_tenure_months=(
                policy_tenure_months
            ),

            location_lat=location_lat,

            location_lon=location_lon,
        )


        # ====================================================
        # RETURN RESULT
        # ====================================================

        return result


    except HTTPException:
        raise


    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Document analysis failed: {str(exc)}"
            ),
        ) from exc