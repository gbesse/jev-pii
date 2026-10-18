# Purpose: Local detectors, seeded column sampling, payload controls and inventory diff.
import hashlib, json, random, re, math
from copy import deepcopy
from .i18n import TEXT, PiiError, questions
from .client import MAX_PAYLOAD

PATTERNS = {
    "email": re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?!\w)"),
    "phone": re.compile(r"(?<!\d)(?:\+?\d[ .-]?){8,15}(?!\d)"),
    "uuid": re.compile(
        r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b",
        re.I,
    ),
}


def luhn(value):
    digits = [int(x) for x in re.sub(r"\D", "", value)]
    return (
        len(digits) >= 12
        and sum(
            (n * 2 - 9 if n * 2 > 9 else n * 2) if (len(digits) - i) % 2 == 0 else n
            for i, n in enumerate(digits)
        )
        % 10
        == 0
    )


def iban(value):
    value = re.sub(r"\s", "", value).upper()
    if not re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]{10,30}", value):
        return False
    rearranged = value[4:] + value[:4]
    number = "".join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged)
    return int(number) % 97 == 1


def detect(value):
    text = str(value)
    found = [name for name, pattern in PATTERNS.items() if pattern.search(text)]
    for match in re.findall(r"(?:\d[ -]?){12,19}", text):
        if luhn(match):
            found.append("payment_card")
    for match in re.findall(r"\b[A-Z]{2}\d{2}[A-Z0-9 ]{10,34}\b", text.upper()):
        if iban(match):
            found.append("iban")
    return sorted(set(found))


def assert_read_only(connection):
    if not getattr(connection, "read_only", False):
        raise PermissionError(
            "Database connection is writable; read-only mode is required"
        )


def sample_column(values, size=20, seed=7):
    values = [str(v) for v in values if v not in (None, "")]
    return random.Random(seed).sample(values, min(size, len(values)))


def mask_value(value):
    value = PATTERNS["email"].sub(
        lambda m: m.group(0)[0] + "***@" + m.group(0).split("@")[1], str(value)
    )
    return re.sub(r"\d", "#", value)


def validate_columns(columns):
    if not isinstance(columns, dict) or len(columns) > 200:
        raise PiiError("input_error")
    for name, values in columns.items():
        if not isinstance(name, str) or not name or not isinstance(values, list):
            raise PiiError("input_error")
        for value in values:
            if (
                not isinstance(value, (str, int, float, bool, type(None)))
                or isinstance(value, float)
                and not math.isfinite(value)
            ):
                raise PiiError("input_error")


def payload_for(column, values, size=20, seed=7, mask=False, lang="en"):
    if isinstance(size, bool) or not isinstance(size, int) or not 1 <= size <= 100:
        raise PiiError("bounds")
    samples = sample_column(values, size, seed)
    samples = [mask_value(x) for x in samples] if mask else samples
    payload = json.dumps(
        {
            "model": "jev-1.13.0",
            "state": {"column": column, "samples": samples},
            "questions": questions(lang),
        },
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()
    if len(payload) > MAX_PAYLOAD:
        raise PiiError("bounds")
    return payload


def preview_plan(columns, *, mask=False, sample_size=20, seed=7, lang="en"):
    validate_columns(columns)
    payloads = [
        payload_for(name, columns[name], sample_size, seed, mask, lang)
        for name in sorted(columns)
    ]
    encoded = json.dumps(
        [p.decode() for p in payloads], separators=(",", ":"), ensure_ascii=True
    ).encode()
    return {
        "plan_sha256": hashlib.sha256(encoded).hexdigest(),
        "request_count": len(payloads),
        "payloads": payloads,
        "payload_sha256": [hashlib.sha256(p).hexdigest() for p in payloads],
    }


class FakeJev:
    def __init__(self, answer=None):
        self.answer = answer or {
            "personal": 0.8,
            "category": "contact",
            "special": 0.1,
            "subject": "customer",
            "free_text": 0.2,
        }
        self.calls = []

    def send(self, payload):
        self.calls.append(payload)
        return self.answer


def scan_columns(
    columns,
    *,
    local_only=True,
    dry_run=False,
    mask=False,
    sample_size=20,
    seed=7,
    transport=None,
    row_counts=None,
    lang="en",
):
    validate_columns(columns)
    if lang not in TEXT:
        raise PiiError("bounds")
    if isinstance(sample_size, bool) or not isinstance(sample_size, int) or not 1 <= sample_size <= 100:
        raise PiiError("bounds")
    if row_counts is not None:
        if not isinstance(row_counts, dict) or any(
            name not in columns or isinstance(count, bool) or not isinstance(count, int) or count < len(columns[name])
            for name, count in row_counts.items()
        ):
            raise PiiError("input_error")
    # A transport may call back into caller code; keep local evidence bound to the preview.
    columns = {name: list(values) for name, values in columns.items()}
    row_counts = dict(row_counts) if row_counts is not None else None
    plan = (
        preview_plan(columns, mask=mask, sample_size=sample_size, seed=seed, lang=lang)
        if not local_only
        else None
    )
    findings = []
    payloads = []
    for name in sorted(columns):
        values = columns[name]
        nonempty = [value for value in values if value is not None and str(value).strip()]
        matches = [detect(value) for value in nonempty]
        local = sorted({kind for row in matches for kind in row})
        entry = {
            "column": name,
            "layers": ["local"] if local else [],
            "detectors": local,
            "row_count": (row_counts or {}).get(name, len(values)),
            "confidence": 1 if local else 0,
            "coverage": {
                "provided_rows": len(values),
                "nonempty_rows": len(nonempty),
                "matched_rows": sum(bool(row) for row in matches),
                "detector_counts": {kind: sum(kind in row for row in matches) for kind in local},
                "semantic_sample_count": 0,
            },
        }
        if not local_only:
            payload = plan["payloads"][len(findings)]
            entry["coverage"]["semantic_sample_count"] = len(json.loads(payload)["state"]["samples"])
            if dry_run:
                payloads.append(payload)
            if not dry_run:
                answer = deepcopy(transport.send(payload))
                entry.update(
                    {"semantic": answer, "confidence": answer.get("personal", 0)}
                )
                entry["layers"].append("semantic")
        findings.append(entry)
    return {
        "findings": findings,
        "payloads": payloads,
        "processing_record": [
            {
                "column": x["column"],
                "purpose": "",
                "retention": "",
                "row_count": x["row_count"],
            }
            for x in findings
        ],
        "remediation": TEXT[lang]["remediation"],
        "plan_sha256": plan["plan_sha256"] if plan else None,
        "request_count": plan["request_count"] if plan else 0,
    }


def diff(previous, current):
    old = {x["column"]: x for x in previous["findings"]}
    new = {x["column"]: x for x in current["findings"]}
    return {
        "added": sorted(new.keys() - old.keys()),
        "removed": sorted(old.keys() - new.keys()),
        "recategorized": sorted(
            k
            for k in old.keys() & new.keys()
            if old[k].get("detectors") != new[k].get("detectors")
            or old[k].get("semantic") != new[k].get("semantic")
        ),
    }


def html_report(result, lang="en"):
    title = TEXT[lang]["title"]
    return (
        '<!doctype html><html lang="'
        + lang
        + '"><meta charset=utf-8><title>'
        + title
        + "</title><style>body{font:16px system-ui;max-width:70rem;margin:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style><h1>"
        + title
        + "</h1><pre>"
        + json.dumps(result, indent=2, ensure_ascii=False)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        + "</pre></html>"
    )
