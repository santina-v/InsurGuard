from __future__ import annotations

from typing import Dict, Any

import networkx as nx


def _add_fact_node(
    graph: nx.DiGraph,
    source_doc_node: str,
    field_name: str,
    value: Any,
    relation: str,
) -> None:
    """Add a fact node and connect it to its source document."""

    if value is None or value == "":
        return

    node_id = f"{field_name}:{value}"

    graph.add_node(
        node_id,
        type="fact",
        field=field_name,
        value=value,
    )

    graph.add_edge(
        source_doc_node,
        node_id,
        relation=relation,
    )


def build_claim_graph(
    police_facts: Dict[str, Any],
    medical_facts: Dict[str, Any],
    invoice_facts: Dict[str, Any],
) -> nx.DiGraph:
    """Build the EchoClaim knowledge graph."""

    graph = nx.DiGraph()

    # Central claim node
    graph.add_node(
        "claim",
        type="claim",
    )

    # Document nodes
    documents = [
        "police_report",
        "medical_report",
        "repair_invoice",
    ]

    for document in documents:
        graph.add_node(
            document,
            type="document",
        )

        graph.add_edge(
            "claim",
            document,
            relation="documented_by",
        )

    # Police report
    _add_fact_node(
        graph,
        "police_report",
        "date",
        police_facts.get("incident_date"),
        "occurred_on",
    )

    _add_fact_node(
        graph,
        "police_report",
        "time",
        police_facts.get("incident_time"),
        "occurred_at",
    )

    _add_fact_node(
        graph,
        "police_report",
        "location",
        police_facts.get("location"),
        "occurred_in",
    )

    _add_fact_node(
        graph,
        "police_report",
        "weather",
        police_facts.get("weather_reported"),
        "reported_weather",
    )

    _add_fact_node(
        graph,
        "police_report",
        "collision",
        police_facts.get("collision_description"),
        "describes_collision_as",
    )

    _add_fact_node(
        graph,
        "police_report",
        "at_fault",
        police_facts.get("at_fault_party"),
        "names_at_fault",
    )

    # Medical report
    _add_fact_node(
        graph,
        "medical_report",
        "patient",
        medical_facts.get("patient_name"),
        "treats_patient",
    )

    _add_fact_node(
        graph,
        "medical_report",
        "treatment_date",
        medical_facts.get("treatment_date"),
        "treated_on",
    )

    _add_fact_node(
        graph,
        "medical_report",
        "treatment_time",
        medical_facts.get("treatment_time"),
        "treated_at",
    )

    _add_fact_node(
        graph,
        "medical_report",
        "complaint",
        medical_facts.get("chief_complaint"),
        "reports_complaint",
    )

    _add_fact_node(
        graph,
        "medical_report",
        "onset",
        medical_facts.get("reported_onset"),
        "describes_onset",
    )

    # Repair invoice
    _add_fact_node(
        graph,
        "repair_invoice",
        "vehicle",
        invoice_facts.get("vehicle"),
        "identifies_vehicle",
    )

    _add_fact_node(
        graph,
        "repair_invoice",
        "service_date",
        invoice_facts.get("service_date"),
        "serviced_on",
    )

    _add_fact_node(
        graph,
        "repair_invoice",
        "damage",
        invoice_facts.get("damage_description"),
        "describes_damage",
    )

    _add_fact_node(
        graph,
        "repair_invoice",
        "damage_location",
        invoice_facts.get("damage_location"),
        "locates_damage_at",
    )

    _add_fact_node(
        graph,
        "repair_invoice",
        "cause",
        invoice_facts.get("estimated_cause"),
        "estimates_cause",
    )

    _add_fact_node(
        graph,
        "repair_invoice",
        "total_cost",
        invoice_facts.get("total_cost"),
        "costs",
    )

    return graph