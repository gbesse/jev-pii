"""Network transport smoke using loopback only; no API key and no paid request."""

import runpy
from pathlib import Path

runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "examples" / "transport_demo.py"),
    run_name="__main__",
)
