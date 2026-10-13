"""Run the real HTTP adapter against a synthetic loopback server; zero paid calls."""

import argparse
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from jev_pii import TypeSafeTransport, preview_plan, scan_columns


def main():
    p = argparse.ArgumentParser(
        description="FR : simulation HTTP locale / EN: local HTTP replay / ES: simulación HTTP local"
    )
    p.add_argument("--lang", choices=("fr", "en", "es"), default="en")
    args = p.parse_args()
    received = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            received.append(self.rfile.read(int(self.headers["Content-Length"])))
            questions = json.loads(received[-1])["questions"]
            answers = {
                key: (
                    {"type": "noul", "noul": 0.2}
                    if q["type"] == "noul"
                    else {
                        "type": "choice",
                        "choice": "other",
                        "confidence": 0.8,
                        "probabilities": {
                            option: float(option == "other") for option in q["criteria"]
                        },
                    }
                )
                for key, q in questions.items()
            }
            self.send_response(200)
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {
                        "model": "jev-1.13.0",
                        "answers": answers,
                        "usage": {"input_tokens": 123, "output_tokens": 0},
                    }
                ).encode()
            )

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        columns = {
            "notes": [
                "FR : exemple fictif. EN: fictional example. ES: ejemplo ficticio."
            ]
        }
        plan = preview_plan(columns, lang=args.lang)
        client = TypeSafeTransport(
            "synthetic-not-a-real-key",
            endpoint=f"http://127.0.0.1:{server.server_port}/v1/systemone",
            allow_loopback=True,
        )
        result = scan_columns(
            columns, local_only=False, transport=client, lang=args.lang
        )
        assert received == plan["payloads"]
        assert result["payloads"] == []
        assert result["findings"][0]["semantic"]["category"] == "other"
        print(
            json.dumps(
                {
                    "simulation": True,
                    "paid_requests": 0,
                    "http_requests": len(received),
                    "inventory": result,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == "__main__":
    main()
