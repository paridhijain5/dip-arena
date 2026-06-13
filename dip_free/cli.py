from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from .models import DecisionReport
from .orchestrator import DIPOrchestrator


def report_to_dict(report: DecisionReport):
    return {
        "query_id": report.query_id,
        "recommendation": report.recommendation,
        "confidence_score": report.confidence_score,
        "supporting_claims": report.supporting_claims,
        "dissenting_views": report.dissenting_views,
        "risks": report.risks,
        "tradeoffs": report.tradeoffs,
        "what_would_change_the_decision": report.what_would_change_the_decision,
        "agent_outputs": [agent_response.__dict__ for agent_response in report.agent_outputs],
        "critiques": [critique.__dict__ for critique in report.critiques],
        "validations": [validation.__dict__ for validation in report.validations],
    }


def save_report(report_data: dict, output_path: str | None) -> Path:
    if output_path:
        destination = Path(output_path)
    else:
        reports_dir = Path("reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        destination = reports_dir / f"dip-report-{report_data['query_id']}-{timestamp}.json"

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report_data, indent=2), encoding="utf-8")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the free, local-only DIP deliberative workflow. No API key required.")
    parser.add_argument("query", help="Decision query to analyze.")
    parser.add_argument("--domain", default="general", choices=["general", "policy", "healthcare", "business", "research", "security"])
    parser.add_argument("--stakes", default="medium", help="Decision stakes, for example low, medium, high.")
    parser.add_argument("--constraint", action="append", default=[], help="Constraint to include in the task context.")
    parser.add_argument("--free", action="store_true", help="Use the built-in local deliberation engine.")
    parser.add_argument("--save-report", action="store_true", help="Save the decision report to the reports folder.")
    parser.add_argument("--output", help="Write the decision report to a specific JSON file.")
    args = parser.parse_args()

    orchestrator = DIPOrchestrator()
    context = {
        "stakes": args.stakes,
        "constraints": args.constraint,
        "notes": [],
        "runtime": "local-free",
        "free": args.free,
    }
    report = orchestrator.decide(args.query, domain=args.domain, context=context)
    report_data = report_to_dict(report)
    print(json.dumps(report_data, indent=2))

    if args.save_report or args.output:
        saved_path = save_report(report_data, args.output)
        print(f"\nSaved report to {saved_path}")