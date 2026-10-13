"""Bounded TypeSafe HTTP transport; one attempt, no redirects, no response-body errors."""

import json
import math
from urllib import request
from urllib.error import HTTPError
from urllib.parse import urlsplit
from .i18n import CATEGORY, SUBJECT, PiiError

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MAX_PAYLOAD = 200_000
MAX_RESPONSE = 1_000_000


def probability(value):
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or not 0 <= value <= 1
    ):
        raise PiiError("response")
    return value


def validate_response(data, model="jev-1.13.0"):
    try:
        if data["model"] != model or set(data["answers"]) != {
            "personal",
            "category",
            "special",
            "subject",
            "free_text",
        }:
            raise PiiError("response")
        answers = data["answers"]
        output = {"model": model}
        for name in ("personal", "special", "free_text"):
            if answers[name]["type"] != "noul":
                raise PiiError("response")
            output[name] = probability(answers[name]["noul"])
        for name, options in (("category", CATEGORY), ("subject", SUBJECT)):
            answer = answers[name]
            probs = answer["probabilities"]
            if (
                answer["type"] != "choice"
                or set(probs) != set(options)
                or answer["choice"] not in options
            ):
                raise PiiError("response")
            probs = {key: probability(value) for key, value in probs.items()}
            if abs(sum(probs.values()) - 1) > 0.001 or probs[answer["choice"]] < max(
                probs.values()
            ):
                raise PiiError("response")
            output[name] = answer["choice"]
            output[name + "_confidence"] = probability(answer["confidence"])
            output[name + "_probabilities"] = probs
        usage = data["usage"]
        output["usage"] = {}
        for name in ("input_tokens", "output_tokens"):
            if (
                isinstance(usage[name], bool)
                or not isinstance(usage[name], int)
                or usage[name] < 0
            ):
                raise PiiError("response")
            output["usage"][name] = usage[name]
        return output
    except (KeyError, TypeError, AttributeError):
        raise PiiError("response") from None


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class TypeSafeTransport:
    def __init__(self, api_key, *, endpoint=ENDPOINT, timeout=15, allow_loopback=False):
        try:
            url = urlsplit(endpoint)
            official = endpoint == ENDPOINT
            loopback = (
                allow_loopback
                and url.scheme == "http"
                and url.hostname in ("127.0.0.1", "::1")
                and url.path == "/v1/systemone"
                and not url.username
                and not url.password
                and not url.query
                and not url.fragment
            )
            if (
                not (official or loopback)
                or isinstance(timeout, bool)
                or not 0 < timeout <= 60
            ):
                raise PiiError("bounds")
        except (ValueError, TypeError):
            raise PiiError("bounds") from None
        if (
            not isinstance(api_key, str)
            or not api_key.strip()
            or "\r" in api_key
            or "\n" in api_key
        ):
            raise PiiError("key")
        self._key = api_key
        self.endpoint = endpoint
        self.timeout = timeout
        self._opener = request.build_opener(request.ProxyHandler({}), NoRedirect())

    def send(self, payload):
        if not isinstance(payload, bytes) or len(payload) > MAX_PAYLOAD:
            raise PiiError("bounds")
        req = request.Request(
            self.endpoint,
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self._key,
            },
        )
        try:
            with self._opener.open(req, timeout=self.timeout) as response:
                if response.status != 200:
                    raise PiiError("network")
                raw = response.read(MAX_RESPONSE + 1)
            if len(raw) > MAX_RESPONSE:
                raise PiiError("response")
            data = json.loads(raw)
        except PiiError:
            raise
        except HTTPError as err:
            err.close()
            raise PiiError("network") from None
        except Exception:
            raise PiiError("network") from None
        return validate_response(data)
