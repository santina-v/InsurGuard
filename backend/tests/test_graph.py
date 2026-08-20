import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

from app.agents.extraction_agent import extract_facts
from app.graph.graph_builder import build_claim_graph


CLAIM_DIR = (
    Path(__file__).resolve().parents[1]
    / "sample_claims"
    / "claim_1"
)


def main():

    police_text = (
        CLAIM_DIR / "police_report.txt"
    ).read_text(encoding="utf-8")

    medical_text = (
        CLAIM_DIR / "medical_report.txt"
    ).read_text(encoding="utf-8")

    repair_text = (
        CLAIM_DIR / "repair_invoice.txt"
    ).read_text(encoding="utf-8")

    police = extract_facts(
        police_text,
        "police_report",
    )

    medical = extract_facts(
        medical_text,
        "medical_report",
    )

    repair = extract_facts(
        repair_text,
        "repair_invoice",
    )

    graph = build_claim_graph(
        police,
        medical,
        repair,
    )

    print("=" * 70)
    print("INSURGUARD KNOWLEDGE GRAPH")
    print("=" * 70)

    print(
        f"\nNodes: {graph.number_of_nodes()}"
    )

    print(
        f"Edges: {graph.number_of_edges()}"
    )

    print("\nNodes:")

    for node, data in graph.nodes(data=True):
        print(
            f"- {node} "
            f"({data.get('type')})"
        )

    print("\nEdges:")

    for source, target, data in graph.edges(data=True):
        print(
            f"- {source} "
            f"--[{data.get('relation')}]--> "
            f"{target}"
        )


if __name__ == "__main__":
    main()