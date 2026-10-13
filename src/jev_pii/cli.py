"""Local by default; exact plan acknowledgement and budget precede all HTTP calls."""

import argparse
import json
import os
import sys
from pathlib import Path
from .core import scan_columns, preview_plan, diff, html_report
from .client import TypeSafeTransport
from .i18n import TEXT, PiiError


class LocalFormatter(argparse.HelpFormatter):
    def __init__(self, prog, lang):
        super().__init__(prog, width=100)
        self.lang = lang

    def add_usage(self, usage, actions, groups, prefix=None):
        super().add_usage(
            usage, actions, groups, prefix=TEXT[self.lang]["usage"] + ": "
        )


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise PiiError("error")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    lang_parser = Parser(add_help=False)
    lang_parser.add_argument("--lang", choices=tuple(TEXT), default="en")
    output = None
    t = TEXT["en"]
    try:
        lang = lang_parser.parse_known_args(argv)[0].lang
        t = TEXT[lang]
        p = Parser(
            prog="jev-pii",
            description=t["description"],
            add_help=False,
            usage="%(prog)s {scan,estimate,report,diff} INPUT [OTHER] [OPTIONS]",
            formatter_class=lambda prog: argparse.HelpFormatter(prog, width=100),
        )
        p._get_formatter = lambda: LocalFormatter(p.prog, lang)
        p._positionals.title = t["positional"]
        p._optionals.title = t["options"]
        p.add_argument("-h", "--help", action="help", help=t["help"])
        p.add_argument("command", choices=["scan", "estimate", "report", "diff"])
        p.add_argument("input", help=t["input"])
        p.add_argument("other", nargs="?", help=t["input"])
        p.add_argument("--lang", choices=tuple(TEXT), default="en", help="FR / EN / ES")
        p.add_argument("--out", help=t["out"])
        modes = p.add_mutually_exclusive_group()
        modes.add_argument("--local-only", action="store_true", help=t["local"])
        modes.add_argument("--dry-run", action="store_true", help=t["dry"])
        modes.add_argument("--live", action="store_true", help=t["live"])
        p.add_argument("--mask", action="store_true", help=t["mask"])
        p.add_argument("--approve-plan", help=t["approve"])
        p.add_argument("--max-calls", type=int, default=10, help=t["budget"])
        p.add_argument("--sample-size", type=int, default=20, help=t["size"])
        p.add_argument("--seed", type=int, default=7, help=t["seed"])
        a = p.parse_args(argv)
        if (
            a.command not in ("scan", "estimate")
            and (a.live or a.dry_run or a.approve_plan)
        ) or (a.command == "estimate" and (a.live or a.local_only)):
            raise PiiError("error")
        if a.command == "diff" and not a.other or a.command == "report" and not a.out:
            raise PiiError("error")
        if a.approve_plan and not a.live:
            raise PiiError("error")
        if Path(a.input).stat().st_size > 10_000_000:
            raise PiiError("bounds")
        first = json.loads(Path(a.input).read_text(encoding="utf-8"))
        kwargs = {
            "mask": a.mask,
            "sample_size": a.sample_size,
            "seed": a.seed,
            "lang": a.lang,
        }
        transport = None
        if a.live:
            plan = preview_plan(first, **kwargs)
            if a.approve_plan != plan["plan_sha256"]:
                raise PiiError("plan")
            if a.max_calls < 0 or plan["request_count"] > a.max_calls:
                raise PiiError("budget_error")
            transport = TypeSafeTransport(os.environ.get("TYPESAFE_API_KEY"))
        if a.out:
            # O_EXCL also rejects symlinks. Reserve before making any paid request.
            output = os.fdopen(
                os.open(a.out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600),
                "w",
                encoding="utf-8",
            )
        if a.command == "diff":
            result = diff(first, json.loads(Path(a.other).read_text(encoding="utf-8")))
        elif a.command == "report":
            result = None
            text = html_report(first, a.lang)
        else:
            dry = a.dry_run or a.command == "estimate"
            result = scan_columns(
                first,
                local_only=not (dry or a.live),
                dry_run=dry,
                transport=transport,
                **kwargs,
            )
            result["payloads"] = [x.decode() for x in result["payloads"]]
        if result is not None:
            text = json.dumps(result, indent=2, ensure_ascii=False)
        if output:
            output.write(text + "\n")
            output.close()
            output = None
        else:
            print(text)
        return 0
    except Exception as err:
        if output is not None:
            output.close()
            Path(a.out).unlink(missing_ok=True)
        code = err.code if isinstance(err, PiiError) else "error"
        print("jev-pii: " + t[code], file=sys.stderr)
        raise SystemExit(1) from None
