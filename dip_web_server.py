from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from dip_free.cli import report_to_dict
from dip_free.orchestrator import DIPOrchestrator


ROOT_DIR = Path(__file__).resolve().parent
WEB_DIR = ROOT_DIR / "web"


class DIPWebHandler(BaseHTTPRequestHandler):
    orchestrator = DIPOrchestrator()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/health":
            self._send_json({"ok": True, "service": "dip-free-web"})
            return

        if path == "/" or path == "/index.html":
            self._serve_file(WEB_DIR / "index.html", "text/html; charset=utf-8")
            return

        if path == "/styles.css":
            self._serve_file(WEB_DIR / "styles.css", "text/css; charset=utf-8")
            return

        if path == "/app.js":
            self._serve_file(WEB_DIR / "app.js", "application/javascript; charset=utf-8")
            return

        self.send_error(HTTPStatus.NOT_FOUND, "File not found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/analyze":
            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(raw_body or "{}")
        except (ValueError, json.JSONDecodeError):
            self._send_json({"error": "Invalid JSON payload."}, status=HTTPStatus.BAD_REQUEST)
            return

        query = str(payload.get("query", "")).strip()
        if not query:
            self._send_json({"error": "Query is required."}, status=HTTPStatus.BAD_REQUEST)
            return

        domain = payload.get("domain", "general")
        stakes = payload.get("stakes", "medium")
        constraints = payload.get("constraints", [])
        notes = payload.get("notes", [])

        if not isinstance(constraints, list):
            constraints = [str(constraints)]
        if not isinstance(notes, list):
            notes = [str(notes)]

        context = {
            "stakes": stakes,
            "constraints": constraints,
            "notes": notes,
            "runtime": "local-free-web",
            "free": True,
        }
        report = self.orchestrator.decide(query, domain=domain, context=context)
        report_data = report_to_dict(report)
        report_data["source"] = "local-web"
        self._send_json(report_data)

    def _serve_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(path.read_bytes())

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the free local DIP web frontend.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind the local server to.")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the local server to.")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), DIPWebHandler)
    print(f"DIP web server running at http://{args.host}:{args.port}")
    print("Open the URL in your browser to use the local frontend.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
