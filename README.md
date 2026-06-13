# DIP Free Version

This project is a free, local-only implementation of the Deliberative Intelligence Protocol (DIP).

It does not require an API key, paid model, or external service.

## Run

```powershell
C:/Python314/python.exe dip_workflow.py "Should Delhi prioritize economic growth or aggressive pollution control?" --domain policy --stakes high --constraint "must remain auditable" --free
```

You can also run the package directly:

```powershell
C:/Python314/python.exe -m dip_free "Should Delhi prioritize economic growth or aggressive pollution control?" --domain policy --stakes high --constraint "must remain auditable" --free
```

To save a report locally:

```powershell
C:/Python314/python.exe -m dip_free "Should Delhi prioritize economic growth or aggressive pollution control?" --domain policy --stakes high --constraint "must remain auditable" --free --save-report
```

To launch the web frontend:

```powershell
C:/Python314/python.exe dip_web_server.py --port 8000
```

Then open `http://127.0.0.1:8000` in your browser.

The browser app includes:

- query entry and local analysis
- export of the current report as JSON
- export of the current report as Markdown
- browser-local query history with restore support
- side-by-side comparison of saved reports
- theme toggle with a presentation-matched default palette
- responsive layout for desktop and mobile

## Project Layout

- `dip_workflow.py` - thin entrypoint for convenience
- `dip_free/models.py` - data models
- `dip_free/agents.py` - specialist agents
- `dip_free/orchestrator.py` - routing, critique, validation, synthesis
- `dip_free/cli.py` - command-line interface and JSON output
- `dip_free/__main__.py` - package entrypoint
- `dip_web_server.py` - local HTTP server for the browser UI
- `web/index.html` - frontend markup
- `web/styles.css` - frontend styling
- `web/app.js` - frontend logic
- `sample_inputs/` - example queries and contexts
- `evaluation/` - benchmark query sets for testing
- `reports/` - saved decision reports

## What it does

- routes a query to specialist agents
- creates a debate and critique layer
- validates claims against built-in knowledge snippets
- synthesizes a final decision report with confidence and dissent

## Notes

- This version is fully offline and deterministic.
- You can expand the built-in knowledge base inside `dip_free/orchestrator.py`.
- If you later want real LLM support, add it as an optional mode instead of replacing the free path.

## Sample Files

- `sample_inputs/delhi_policy.json` shows a ready-to-run query payload.
- `evaluation/benchmark_queries.json` contains a small evaluation set.