"""Synthetic HTTP and CLI tests; no secrets and no external services."""

import contextlib
import copy
import io
import json
import os
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from jev_pii import (
    TypeSafeTransport,
    payload_for,
    preview_plan,
    scan_columns,
    validate_response,
)
from jev_pii.cli import main
from jev_pii.i18n import TEXT, PiiError


def response():
    def choice(key, options):
        return {
            "type": "choice",
            "choice": key,
            "confidence": 0.8,
            "probabilities": {x: 1.0 if x == key else 0.0 for x in options},
        }

    return {
        "model": "jev-1.13.0",
        "answers": {
            "personal": {"type": "noul", "noul": 0.8},
            "special": {"type": "noul", "noul": 0.1},
            "free_text": {"type": "noul", "noul": 0.2},
            "category": choice(
                "other", ("identity", "contact", "financial", "health", "other")
            ),
            "subject": choice(
                "other", ("employee", "customer", "prospect", "patient", "other")
            ),
        },
        "usage": {"input_tokens": 123, "output_tokens": 0},
    }


class LiveTests(unittest.TestCase):
    def test_payload_contract_languages_and_user_text(self):
        for lang in TEXT:
            body = json.loads(payload_for("réponse", ["Texto del usuario"], lang=lang))
            self.assertEqual(body["state"]["samples"], ["Texto del usuario"])
            self.assertEqual(set(body["questions"]), set(response()["answers"]))
            for q in body["questions"].values():
                self.assertTrue(q["instructions"])
                if q["type"] == "choice":
                    self.assertIsInstance(q["criteria"], dict)
            self.assertEqual(
                body["questions"]["personal"]["instructions"],
                TEXT[lang]["questions"][0],
            )

    def test_plan_binds_exact_samples_and_questions(self):
        base = {"b": ["synthetic"], "a": [1, 2, 3]}
        plan = preview_plan(base)
        self.assertEqual(plan, preview_plan(dict(reversed(list(base.items())))))
        for kwargs in ({"mask": True}, {"lang": "fr"}, {"sample_size": 1}, {"seed": 9}):
            self.assertNotEqual(
                plan["plan_sha256"], preview_plan(base, **kwargs)["plan_sha256"]
            )
        self.assertNotEqual(
            plan["plan_sha256"],
            preview_plan({"b": ["changed"], "a": [1, 2, 3]})["plan_sha256"],
        )

    def test_validation_rejects_malformed_answers(self):
        alterations = [
            lambda d: d.update(model="unexpected"),
            lambda d: d["answers"].pop("special"),
            lambda d: d["answers"]["personal"].update(noul=True),
            lambda d: d["answers"]["special"].update(noul=float("nan")),
            lambda d: d["answers"]["category"].update(choice="invented"),
            lambda d: d["answers"]["category"]["probabilities"].update(other=0.7),
            lambda d: d["answers"]["subject"].update(confidence=-1),
            lambda d: d["usage"].update(input_tokens=True),
            lambda d: d["answers"]["free_text"].update(type="choice"),
            lambda d: d.update(answers=None),
        ]
        self.assertEqual(validate_response(response())["personal"], 0.8)
        for change in alterations:
            data = response()
            change(data)
            with self.subTest(data=data), self.assertRaises(PiiError):
                validate_response(data)

    def test_untrusted_response_fields_discarded(self):
        data = response()
        data["debug"] = "secret"
        data["usage"]["debug"] = "secret"
        data["answers"]["personal"]["text"] = "sample"
        out = validate_response(data)
        self.assertNotIn("secret", json.dumps(out))
        self.assertNotIn("sample", json.dumps(out))

    def test_bounds_and_endpoint(self):
        for opts in (
            {"endpoint": "http://api.typesafe.ai/v1/systemone"},
            {"endpoint": "https://example.test/v1/systemone"},
            {"timeout": float("nan")},
            {"timeout": True},
            {"endpoint": "http://127.0.0.1/v1/systemone"},
        ):
            with self.assertRaises(PiiError):
                TypeSafeTransport("synthetic", **opts)
        for size in (0, 101, True):
            with self.assertRaises(PiiError):
                payload_for("x", ["a"], size=size)
        with self.assertRaises(PiiError):
            preview_plan({"x": [{"nested": "value"}]})
        with self.assertRaises(PiiError):
            payload_for("x", ["x" * 201_000])

    def test_http_exact_bytes_no_redirect_no_body_leak(self):
        received = []

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                received.append(self.rfile.read(int(self.headers["Content-Length"])))
                self.send_response(self.server.status)
                self.send_header("Location", self.server.endpoint)
                self.end_headers()
                self.wfile.write(
                    json.dumps(response()).encode()
                    if self.server.status == 200
                    else b"SENSITIVE_ERROR"
                )

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        server.status = 200
        server.endpoint = f"http://127.0.0.1:{server.server_port}/v1/systemone"
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            client = TypeSafeTransport(
                "synthetic", endpoint=server.endpoint, allow_loopback=True
            )
            payload = payload_for("notes", ["synthetic note"])
            self.assertEqual(client.send(payload)["category"], "other")
            self.assertEqual(received, [payload])
            for status in (302, 429, 401):
                server.status = status
                with self.assertRaises(PiiError) as err:
                    client.send(payload)
                self.assertNotIn("SENSITIVE_ERROR", str(err.exception))
            self.assertEqual(len(received), 4)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_live_scan_does_not_return_samples(self):
        class Fake:
            def send(self, payload):
                return validate_response(response())

        result = scan_columns(
            {"note": ["synthetic private sentinel"]}, local_only=False, transport=Fake()
        )
        self.assertEqual(result["payloads"], [])
        self.assertNotIn("sentinel", json.dumps(result))
        self.assertEqual(result["request_count"], 1)

    def test_cli_guardrails_and_private_output(self):
        class Fake:
            calls = []

            def __init__(self, key):
                pass

            def send(self, payload):
                self.calls.append(payload)
                return validate_response(response())

        with (
            tempfile.TemporaryDirectory() as folder,
            patch("jev_pii.cli.TypeSafeTransport", Fake),
        ):
            f = Path(folder) / "input.json"
            f.write_text(json.dumps({"notes": ["private sentinel"]}))
            out = Path(folder) / "preview.json"
            self.assertEqual(main(["scan", str(f), "--dry-run", "--out", str(out)]), 0)
            preview = json.loads(out.read_text())
            digest = preview["plan_sha256"]
            self.assertIn("sentinel", out.read_text())
            self.assertEqual(out.stat().st_mode & 0o777, 0o600)
            self.assertEqual(Fake.calls, [])
            for args in (
                ["--live"],
                ["--live", "--approve-plan", "wrong"],
                ["--live", "--approve-plan", digest, "--max-calls", "0"],
                ["--live", "--approve-plan", digest, "--out", str(out)],
            ):
                with (
                    contextlib.redirect_stderr(io.StringIO()),
                    self.assertRaises(SystemExit),
                ):
                    main(["scan", str(f)] + args)
                self.assertEqual(Fake.calls, [])
            live = Path(folder) / "live.json"
            main(
                ["scan", str(f), "--live", "--approve-plan", digest, "--out", str(live)]
            )
            self.assertEqual(Fake.calls, [preview["payloads"][0].encode()])
            self.assertNotIn("sentinel", live.read_text())
            self.assertEqual(live.stat().st_mode & 0o777, 0o600)
            f.write_text(json.dumps({"notes": ["changed"]}))
            with (
                contextlib.redirect_stderr(io.StringIO()),
                self.assertRaises(SystemExit),
            ):
                main(["scan", str(f), "--live", "--approve-plan", digest])
            self.assertEqual(len(Fake.calls), 1)

    def test_local_and_estimate_never_create_transport(self):
        with (
            tempfile.TemporaryDirectory() as folder,
            patch(
                "jev_pii.cli.TypeSafeTransport", side_effect=AssertionError("network")
            ),
        ):
            f = Path(folder) / "input.json"
            f.write_text('{"x":["synthetic"]}')
            for command in ("scan", "estimate"):
                capture = io.StringIO()
                with contextlib.redirect_stdout(capture):
                    main([command, str(f)])
                result = json.loads(capture.getvalue())
                self.assertEqual(result["request_count"], int(command == "estimate"))

    def test_cli_help_and_errors_all_languages(self):
        for lang in TEXT:
            out = io.StringIO()
            with contextlib.redirect_stdout(out), self.assertRaises(SystemExit):
                main(["--lang", lang, "--help"])
            self.assertIn(TEXT[lang]["live"], " ".join(out.getvalue().split()))
            err = io.StringIO()
            with contextlib.redirect_stderr(err), self.assertRaises(SystemExit):
                main(["scan", "absent", "--lang", lang])
            self.assertIn(TEXT[lang]["error"], err.getvalue())
