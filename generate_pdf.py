from __future__ import annotations

from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT_DIR = Path(__file__).resolve().parent

OUTPUTS = [
    (
        ROOT_DIR / "DIP_Free_Program_Overview.pdf",
        "DIP Free Program Overview",
        "Deliberative Intelligence Protocol - Local Decision Analysis Tool",
        True,
    ),
    (
        ROOT_DIR / "DIP_Arena_Component_Functions_Guide.pdf",
        "DIP Arena Component Functions Guide",
        "Full component-by-component reference for the project",
        False,
    ),
]

COMPONENTS = [
    {
        "file": "dip_workflow.py",
        "role": "Thin convenience entrypoint for command-line launches.",
        "items": [
            ("main()", "Imports and delegates to dip_free.cli.main so `python dip_workflow.py ...` works without extra wiring."),
        ],
    },
    {
        "file": "dip_free/__main__.py",
        "role": "Package entrypoint for `python -m dip_free`.",
        "items": [
            ("main()", "Forwards execution to the CLI layer when the package is launched as a module."),
        ],
    },
    {
        "file": "dip_free/cli.py",
        "role": "Command-line interface and JSON report export.",
        "items": [
            ("report_to_dict(report)", "Serializes a DecisionReport dataclass into a JSON-friendly dictionary."),
            ("save_report(report_data, output_path)", "Writes report JSON to a requested path or a timestamped file in reports/."),
            ("main()", "Parses CLI arguments, runs the orchestrator, prints JSON, and optionally saves the report."),
        ],
    },
    {
        "file": "dip_free/orchestrator.py",
        "role": "Decision workflow controller that routes, critiques, validates, and synthesizes results.",
        "items": [
            ("DIPOrchestrator.__init__", "Builds the default knowledge base and prepares the specialist agent pool."),
            ("decide(query, domain, context)", "Runs the full observe/retrieve/agent/challenge/validate/synthesize pipeline."),
            ("_observe(query, domain, context)", "Normalizes input into a Task object and chooses required agents."),
            ("_retrieve_context(task)", "Collects domain guidance, notes, and task metadata for downstream reasoning."),
            ("_route_agents(domain, query)", "Selects the specialist agents that should participate in the analysis."),
            ("_run_agents(task, context)", "Runs the chosen agents in parallel with a thread pool and sorts their responses."),
            ("_challenge(task, agent_outputs)", "Creates critique objects that question overconfidence and open gaps."),
            ("_validate(task, agent_outputs, context)", "Scores each claim against the retrieved evidence."),
            ("_score_claim(claim, source_pool, agent_confidence)", "Assigns supported, weakly_supported, or unsupported status and a confidence adjustment."),
            ("_synthesize(task, agent_outputs, critiques, validations)", "Merges all signals into the final DecisionReport."),
            ("_recommendation_from_domain(domain, agent_outputs)", "Chooses a domain-specific recommendation or the strongest stance."),
            ("_merge_unique(values)", "Deduplicates lists while preserving order."),
        ],
    },
    {
        "file": "dip_free/agents.py",
        "role": "Specialist reasoning agents with focused perspectives.",
        "items": [
            ("BaseAgent.__init__", "Stores the shared knowledge base for all agents."),
            ("BaseAgent.run", "Abstract interface that each concrete agent overrides."),
            ("BaseAgent._evidence_for_domain(task, fallback)", "Returns domain evidence or a safe fallback string."),
            ("ResearchAgent.run", "Focuses on evidence-first reasoning and missing-fact discovery."),
            ("RiskAgent.run", "Highlights failure modes, uncertainty, and downside exposure."),
            ("EthicsAgent.run", "Checks fairness, harm minimization, and stakeholder impact."),
            ("PolicyAgent.run", "Looks at governance, compliance, auditability, and rollout structure."),
            ("EconomicsAgent.run", "Weighs cost, benefit, externalities, and long-run value."),
            ("StrategyAgent.run", "Checks alignment with objectives, execution capacity, and trust."),
        ],
    },
    {
        "file": "dip_free/models.py",
        "role": "Shared data model layer for tasks, agent responses, critiques, validations, and reports.",
        "items": [
            ("Domain", "Typed literal for supported domains: general, policy, healthcare, business, research, security."),
            ("AgentKind", "Typed literal for the six specialist agent categories."),
            ("ValidationStatus", "Typed literal for claim status values: supported, weakly_supported, unsupported."),
            ("Task", "Captures the query, stakes, constraints, routing, evidence needs, and context."),
            ("AgentResponse", "Stores each agent's stance, claims, evidence, assumptions, confidence, risks, and open questions."),
            ("Critique", "Represents a challenge to an agent's output, including severity and unresolved issue."),
            ("ValidationResult", "Records how a claim was scored and why."),
            ("DecisionReport", "Holds the final recommendation, confidence, supporting claims, dissent, risks, tradeoffs, and diagnostics."),
            ("ReportDict", "Dictionary alias used for serialized report data."),
        ],
    },
    {
        "file": "dip_web_server.py",
        "role": "Local HTTP server that serves the UI and analysis API.",
        "items": [
            ("DIPWebHandler.do_GET", "Serves health, HTML, CSS, and JS responses."),
            ("DIPWebHandler.do_POST", "Accepts analysis requests, normalizes payloads, and returns a report JSON response."),
            ("DIPWebHandler._serve_file", "Reads a static file and returns it with the correct content type."),
            ("DIPWebHandler._send_json", "Serializes Python data to JSON and writes the HTTP response."),
            ("DIPWebHandler.log_message", "Suppresses default HTTP server logging for a cleaner console."),
            ("main()", "Parses host/port arguments and starts the ThreadingHTTPServer."),
        ],
    },
    {
        "file": "web/app.js",
        "role": "Browser-side state, rendering, export, history, comparison, and theme behavior.",
        "items": [
            ("setStatus(message, tone)", "Updates the status banner and stores a tone token."),
            ("getTheme()", "Reads the saved theme from localStorage."),
            ("setTheme(theme)", "Applies the theme to the document and updates the toggle label."),
            ("toggleTheme()", "Switches between the two saved themes."),
            ("clearElement(element, fallbackText)", "Clears a container and optionally marks it as empty state."),
            ("createItem(text)", "Builds a simple list item for summaries and results."),
            ("createChip(text)", "Builds a pill-shaped chip for tradeoffs and triggers."),
            ("toMarkdown(report)", "Exports the active report to a Markdown document."),
            ("escapeHtml(value)", "Escapes user-facing text before HTML insertion."),
            ("getHistory()", "Loads saved reports from localStorage."),
            ("saveHistory(history)", "Persists the latest report history list locally."),
            ("addToHistory(entry)", "Adds the newest analysis to history and refreshes comparison options."),
            ("renderHistory()", "Renders saved queries as clickable history items."),
            ("renderCompareOptions()", "Populates the Report A and Report B selectors."),
            ("populateFormFromInput(input)", "Restores a saved query into the form controls."),
            ("downloadReport(report)", "Downloads the JSON report as a file."),
            ("downloadMarkdown(report)", "Downloads the report as Markdown."),
            ("renderList(element, items, emptyText)", "Renders a simple list or fallback empty state."),
            ("renderChips(element, items, emptyText)", "Renders a chip group or fallback empty state."),
            ("renderAgents(items)", "Builds the agent debate cards."),
            ("findHistoryItem(id)", "Finds a saved report by ID."),
            ("renderComparison(left, right)", "Builds the side-by-side comparison view."),
            ("renderValidations(items)", "Builds validation cards with status badges."),
            ("renderReport(report, enableExport)", "Populates the dashboard with the latest analysis result."),
            ("analyzeQuery(payload)", "Sends the request to /api/analyze and handles success or failure."),
        ],
    },
    {
        "file": "web/index.html",
        "role": "Semantic page structure for the navbar, hero, forms, report area, and support sections.",
        "items": [
            ("No executable functions", "Provides anchors, layout containers, and semantic sections used by app.js and styles.css."),
        ],
    },
    {
        "file": "web/styles.css",
        "role": "Design system, palette, responsive layout, and component styling.",
        "items": [
            ("No executable functions", "Defines the visual behavior of the premium SaaS interface, including layout, cards, spacing, and theme tokens."),
        ],
    },
    {
        "file": "sample_inputs/delhi_policy.json",
        "role": "Ready-to-use example payload for testing the policy flow.",
        "items": [
            ("No functions", "Static input data for a representative policy scenario."),
        ],
    },
    {
        "file": "evaluation/benchmark_queries.json",
        "role": "Benchmark query set for experimentation and regression checks.",
        "items": [
            ("No functions", "Static benchmark data for quality checks and comparisons."),
        ],
    },
    {
        "file": "reports/",
        "role": "Local output directory for saved decision reports.",
        "items": [
            ("No functions", "Stores JSON exports generated from CLI or the browser app."),
        ],
    },
]


styles = getSampleStyleSheet()

TITLE_STYLE = ParagraphStyle(
    "TitleStyle",
    parent=styles["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=23,
    leading=28,
    textColor=colors.HexColor("#1f5e63"),
    alignment=TA_CENTER,
    spaceAfter=8,
)

SUBTITLE_STYLE = ParagraphStyle(
    "SubtitleStyle",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=11,
    leading=14,
    textColor=colors.HexColor("#5f726d"),
    alignment=TA_CENTER,
    spaceAfter=14,
)

SECTION_STYLE = ParagraphStyle(
    "SectionStyle",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=14,
    leading=17,
    textColor=colors.HexColor("#1f5e63"),
    spaceBefore=8,
    spaceAfter=8,
)

SUBSECTION_STYLE = ParagraphStyle(
    "SubsectionStyle",
    parent=styles["Heading3"],
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=14,
    textColor=colors.HexColor("#2f767b"),
    spaceBefore=6,
    spaceAfter=4,
)

BODY_STYLE = ParagraphStyle(
    "BodyStyle",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=9.6,
    leading=12.4,
    alignment=TA_JUSTIFY,
    spaceAfter=6,
)

BULLET_STYLE = ParagraphStyle(
    "BulletStyle",
    parent=BODY_STYLE,
    leftIndent=12,
    firstLineIndent=-10,
    spaceAfter=4,
)

CODE_STYLE = ParagraphStyle(
    "CodeStyle",
    parent=styles["BodyText"],
    fontName="Courier",
    fontSize=8.5,
    leading=11,
    alignment=TA_LEFT,
    textColor=colors.HexColor("#204a57"),
    spaceAfter=6,
)

SMALL_STYLE = ParagraphStyle(
    "SmallStyle",
    parent=styles["BodyText"],
    fontName="Helvetica-Oblique",
    fontSize=8.6,
    leading=11,
    textColor=colors.HexColor("#5f726d"),
    spaceAfter=4,
)


def bullet_paragraph(text: str) -> Paragraph:
    return Paragraph(f"&bull; {text}", BULLET_STYLE)


def code_paragraph(text: str) -> Paragraph:
    return Paragraph(text.replace("\n", "<br/>") , CODE_STYLE)


def section_header(text: str) -> Paragraph:
    return Paragraph(escape(text), SECTION_STYLE)


def subsection_header(text: str) -> Paragraph:
    return Paragraph(escape(text), SUBSECTION_STYLE)


def build_utility_table() -> Table:
    data = [
        ["Layer", "Primary Function"],
        ["CLI", "Accepts a query, runs the orchestrator, prints JSON, and optionally saves a report."],
        ["Web Server", "Serves the SPA and exposes /api/analyze for browser-driven analysis."],
        ["Orchestrator", "Coordinates observe, retrieve, run, challenge, validate, and synthesize steps."],
        ["Agents", "Provide specialized perspectives for research, risk, ethics, policy, economics, and strategy."],
        ["Models", "Define the typed data structures that move through the pipeline."],
        ["Frontend", "Collects input, renders reports, preserves history, and exports artifacts."],
    ]
    table = Table(data, colWidths=[1.25 * inch, 5.6 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f5e63")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f6f2ea")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f7f5")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#b8c7c0")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def build_component_reference(elements: list, detailed: bool) -> None:
    elements.append(section_header("Component and Function Reference"))
    elements.append(Paragraph(
        "This section lists the role of each source component and the function-level behavior it contributes to the product.",
        BODY_STYLE,
    ))

    for component in COMPONENTS:
        elements.append(subsection_header(component["file"]))
        elements.append(Paragraph(escape(component["role"]), BODY_STYLE))
        for name, description in component["items"]:
            elements.append(bullet_paragraph(f"<b>{escape(name)}</b>: {escape(description)}"))
        elements.append(Spacer(1, 0.06 * inch))

        if detailed and component["file"] in {"dip_free/orchestrator.py", "web/app.js", "dip_web_server.py"}:
            elements.append(Paragraph(
                "These are the highest-impact control points in the application and drive most of the user-visible behavior.",
                SMALL_STYLE,
            ))


def build_document(output_path: Path, title: str, subtitle: str, detailed: bool) -> None:
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        topMargin=0.72 * inch,
        bottomMargin=0.68 * inch,
        leftMargin=0.72 * inch,
        rightMargin=0.72 * inch,
    )

    elements: list = []
    elements.append(Paragraph(escape(title), TITLE_STYLE))
    elements.append(Paragraph(escape(subtitle), SUBTITLE_STYLE))
    elements.append(Paragraph(
        "Generated for the local DIP free edition. The document describes the full flow from query intake to report rendering.",
        BODY_STYLE,
    ))

    elements.append(section_header("Project Summary"))
    elements.append(Paragraph(
        "DIP Arena is a local, offline decision intelligence system that routes a question through multiple specialist agents, critiques high-confidence claims, validates evidence against a small built-in knowledge base, and synthesizes a structured report for review.",
        BODY_STYLE,
    ))

    elements.append(section_header("System Flow"))
    flow_data = [
        ["Input", "Query, domain, stakes, constraints, notes"],
        ["Route", "Orchestrator selects research, risk, ethics, policy, economics, and strategy agents"],
        ["Deliberate", "Agents respond in parallel with claims, evidence, assumptions, risks, and confidence"],
        ["Challenge", "Critiques question blind spots and unsupported certainty"],
        ["Validate", "Each claim is scored against the retrieved evidence"],
        ["Synthesize", "The final DecisionReport aggregates recommendation, confidence, claims, dissent, and risks"],
        ["Present", "CLI prints JSON and the web UI renders the report with history and comparison tools"],
    ]
    flow_table = Table(flow_data, colWidths=[1.05 * inch, 5.8 * inch])
    flow_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6f1ec")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bccdc6")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    elements.append(flow_table)
    elements.append(Spacer(1, 0.12 * inch))

    elements.append(section_header("Component Overview"))
    elements.append(build_utility_table())
    elements.append(Spacer(1, 0.1 * inch))

    build_component_reference(elements, detailed)

    if detailed:
        elements.append(PageBreak())
        elements.append(section_header("Agent and Report Outputs"))
        elements.append(Paragraph(
            "The report format is intentionally explicit so the user can inspect what was considered, what was challenged, and what would change the decision.",
            BODY_STYLE,
        ))
        report_fields = [
            "<b>recommendation</b> - The selected path or stance for the query.",
            "<b>confidence_score</b> - Weighted signal combining agent confidence, evidence coverage, and critique penalties.",
            "<b>supporting_claims</b> - Claims that passed validation most strongly.",
            "<b>dissenting_views</b> - Views that were uncertain, risky, or divergent.",
            "<b>risks</b> - Consolidated risks from the specialist outputs and critiques.",
            "<b>tradeoffs</b> - Explicit tension points such as speed versus scrutiny.",
            "<b>what_would_change_the_decision</b> - Conditions that would materially alter the recommendation.",
            "<b>agent_outputs</b> - The full per-agent debate output.",
            "<b>critiques</b> - Challenges raised against overconfident assumptions.",
            "<b>validations</b> - Claim-by-claim evidence scoring.",
        ]
        for field in report_fields:
            elements.append(bullet_paragraph(field))

        elements.append(Spacer(1, 0.08 * inch))
        elements.append(section_header("Runtime Commands"))
        elements.append(subsection_header("CLI"))
        elements.append(code_paragraph('python -m dip_free "Should Delhi prioritize economic growth or pollution control?" --domain policy --stakes high --constraint "must remain auditable" --free --save-report'))
        elements.append(subsection_header("Web"))
        elements.append(code_paragraph("python dip_web_server.py --port 8000<br/>Open http://127.0.0.1:8000 in a browser"))
        elements.append(subsection_header("Browser UI Features"))
        ui_features = [
            "Query entry with local analysis",
            "JSON and Markdown export",
            "Local browser history with restore support",
            "Side-by-side report comparison",
            "Theme toggle and premium dashboard styling",
            "Responsive layout for desktop and mobile",
        ]
        for feature in ui_features:
            elements.append(bullet_paragraph(escape(feature)))

        elements.append(Spacer(1, 0.08 * inch))
        elements.append(section_header("Design Notes"))
        elements.append(Paragraph(
            "The free edition keeps the interface offline, auditable, and deterministic. The browser front end presents the same underlying workflow as a polished SaaS dashboard while the backend stays deliberately small and transparent.",
            BODY_STYLE,
        ))

    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(
        f"<i>Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}</i>",
        SMALL_STYLE,
    ))

    def add_footer(canvas, doc_obj):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#5f726d"))
        canvas.drawString(doc_obj.leftMargin, 0.42 * inch, "DIP Arena documentation")
        canvas.drawRightString(letter[0] - doc_obj.rightMargin, 0.42 * inch, f"Page {canvas.getPageNumber()}")
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
    print(f"PDF created successfully: {output_path}")


def main() -> None:
    for output_path, title, subtitle, detailed in OUTPUTS:
        build_document(output_path, title, subtitle, detailed)


if __name__ == "__main__":
    main()
