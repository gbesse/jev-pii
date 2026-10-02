"""Local-only before/after PII inventory on synthetic column values."""
import json

from jev_pii import diff, scan_columns

BEFORE = {"contact": ["person@example.test"], "note": ["ordinary note"]}
AFTER = {"contact": ["person@example.test"], "note": ["Call +1 202 555 0142"], "payment": ["4111 1111 1111 1111"]}


def example():
    old = scan_columns(BEFORE, local_only=True)
    new = scan_columns(AFTER, local_only=True)
    return {
        "source": "synthetic fixture; local checks only",
        "changes": diff(old, new),
        "columns": [{"name": row["column"], "detectors": row["detectors"]} for row in new["findings"]],
        "network_payloads": len(old["payloads"]) + len(new["payloads"]),
    }


if __name__ == "__main__":
    print(json.dumps(example(), indent=2, sort_keys=True))
