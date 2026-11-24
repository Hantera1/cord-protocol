"""Minimal hosted adapter for CORD Core verification.

This service delegates all evidence semantics to verifier.verify_bytes.
It does not store submitted evidence or establish identity, truth, or trusted time.
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import os
import re
import uuid
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from verifier.verify import (
    MAX_FILE_BYTES,
    SPEC_VERSION,
    CordValidationError,
    _unique_object,
    verify_bytes,
)

API_VERSION = "1"
MAX_REQUEST_BYTES = 3 * 1024 * 1024
KEY_HASH_RE = re.compile(r"^[0-9a-f]{64}$")

app = FastAPI(
    title="CORD Verify API",
    version=API_VERSION,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


def _error(status_code: int, code: str, message: str, request_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "api_version": API_VERSION,
            "request_id": request_id,
            "error": {"code": code, "message": message},
        },
    )


def _authorized(request: Request) -> bool | None:
    """Return True/False; None means server auth is not configured safely."""
    if os.getenv("CORD_API_AUTH_DISABLED") == "true":
        return True
    expected = os.getenv("CORD_API_KEY_SHA256", "")
    if not KEY_HASH_RE.fullmatch(expected):
        return None
    header = request.headers.get("authorization", "")
    scheme, separator, credential = header.partition(" ")
    if not separator or scheme.lower() != "bearer" or not credential:
        return False
    supplied = hashlib.sha256(credential.encode("utf-8")).hexdigest()
    return hmac.compare_digest(supplied, expected)


async def _read_bounded_body(request: Request) -> bytes | None:
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            if int(content_length) > MAX_REQUEST_BYTES:
                return None
        except ValueError:
            return None
    chunks: list[bytes] = []
    total = 0
    async for chunk in request.stream():
        total += len(chunk)
        if total > MAX_REQUEST_BYTES:
            return None
        chunks.append(chunk)
    return b"".join(chunks)


def _parse_request(raw: bytes) -> dict[str, Any]:
    try:
        decoded = raw.decode("utf-8", errors="strict")
        value = json.loads(
            decoded,
            object_pairs_hook=_unique_object,
            parse_constant=lambda token: (_ for _ in ()).throw(
                CordValidationError(f"invalid JSON constant: {token}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Request body must be valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("Request body must be a JSON object")
    expected = {"spec_version", "bundle_base64", "receipt_base64"}
    if set(value) != expected:
        raise ValueError("Request must contain exactly spec_version, bundle_base64, and receipt_base64")
    if value["spec_version"] != SPEC_VERSION:
        raise LookupError("Unsupported CORD Core spec_version")
    if not isinstance(value["bundle_base64"], str) or not isinstance(value["receipt_base64"], str):
        raise ValueError("Evidence values must be Base64 strings")
    return value


def _decode_evidence(value: str) -> bytes:
    try:
        raw = base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Evidence must use valid standard Base64") from exc
    if base64.b64encode(raw).decode("ascii") != value:
        raise ValueError("Evidence Base64 must use canonical padding and alphabet")
    if len(raw) > MAX_FILE_BYTES:
        raise OverflowError("Decoded evidence file exceeds the 1 MiB Core limit")
    return raw


@app.get("/v1/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "api_version": API_VERSION}


@app.post("/v1/verify/core")
async def verify_core(request: Request) -> JSONResponse:
    request_id = "req_" + uuid.uuid4().hex
    content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if content_type != "application/json":
        return _error(415, "UNSUPPORTED_MEDIA_TYPE", "Content-Type must be application/json", request_id)

    auth = _authorized(request)
    if auth is None:
        return _error(503, "AUTH_NOT_CONFIGURED", "Hosted API authentication is not configured", request_id)
    if not auth:
        return _error(401, "UNAUTHORIZED", "A valid Bearer API key is required", request_id)

    raw = await _read_bounded_body(request)
    if raw is None:
        return _error(413, "REQUEST_TOO_LARGE", "Request exceeds the 3 MiB limit", request_id)

    try:
        payload = _parse_request(raw)
        bundle_bytes = _decode_evidence(payload["bundle_base64"])
        receipt_bytes = _decode_evidence(payload["receipt_base64"])
    except LookupError:
        return _error(422, "UNSUPPORTED_SPEC_VERSION", "Only CORD Core spec_version 0.1 is supported", request_id)
    except OverflowError:
        return _error(413, "EVIDENCE_TOO_LARGE", "Each decoded evidence file is limited to 1 MiB", request_id)
    except (ValueError, CordValidationError):
        return _error(400, "INVALID_REQUEST", "Request JSON or Base64 fields are invalid", request_id)

    try:
        result = verify_bytes(bundle_bytes, receipt_bytes)
    except CordValidationError:
        return JSONResponse(
            status_code=200,
            content={
                "api_version": API_VERSION,
                "request_id": request_id,
                "result": {
                    "status": "FAIL",
                    "spec_version": SPEC_VERSION,
                    "profile": "cord-core",
                    "error_code": "INVALID_EVIDENCE",
                    "meaning": "The supplied evidence did not pass CORD Core v0.1 validation and integrity checks.",
                },
                "verifier": {
                    "name": "CORD Reference Verifier",
                    "version": "core-0.1",
                    "policy_id": "cord-core-v0.1",
                },
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "api_version": API_VERSION,
            "request_id": request_id,
            "result": {
                **result,
                "profile": "cord-core",
            },
            "verifier": {
                "name": "CORD Reference Verifier",
                "version": "core-0.1",
                "policy_id": "cord-core-v0.1",
            },
        },
    )
