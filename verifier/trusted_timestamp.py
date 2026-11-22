"""RFC 3161 timestamp verification bound to CORD Ed25519 receipt signatures.

Trust anchors are supplied out-of-band. OpenSSL performs RFC 3161/CMS,
message-imprint, TSA path, timestamping-purpose and (optionally) CRL checks.
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from verifier.verify import CordValidationError

MAX_TOKEN_BYTES = 1_048_576
TIME_RE = re.compile(r"^Time stamp:\s*(.+ GMT)\s*$", re.MULTILINE)
HASH_RE = re.compile(r"^Hash Algorithm:\s*([A-Za-z0-9-]+)\s*$", re.MULTILINE)
ALLOWED_IMPRINT_HASHES = {"sha256", "sha384", "sha512"}


def _signature_bytes(envelope: dict[str, Any]) -> bytes:
    if not isinstance(envelope, dict):
        raise CordValidationError("signature envelope must be an object")
    if envelope.get("spec_version") != "0.1" or envelope.get("alg") != "Ed25519":
        raise CordValidationError("timestamp profile supports only Signed Receipt v0.1 Ed25519")
    if set(envelope) != {"spec_version", "alg", "key_id", "signature"}:
        raise CordValidationError("signature envelope must contain exactly spec_version, alg, key_id, and signature")
    key_id = envelope.get("key_id")
    if not isinstance(key_id, str) or not key_id or key_id.strip() != key_id:
        raise CordValidationError("signature envelope.key_id must be a non-empty trimmed string")
    encoded = envelope.get("signature")
    if not isinstance(encoded, str) or not encoded or encoded.strip() != encoded:
        raise CordValidationError("signature envelope.signature must be trimmed Base64")
    try:
        signature = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise CordValidationError("signature envelope.signature must be valid Base64") from exc
    if len(signature) != 64 or base64.b64encode(signature).decode("ascii") != encoded:
        raise CordValidationError("Ed25519 signature must be canonical Base64 for exactly 64 bytes")
    return signature


def _run(args: list[str], timeout: int) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update({"LC_ALL": "C", "LANG": "C"})
    try:
        return subprocess.run(
            args, check=False, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout,
            shell=False, env=env,
        )
    except subprocess.TimeoutExpired as exc:
        raise CordValidationError("OpenSSL timestamp validation timed out") from exc
    except OSError as exc:
        raise CordValidationError(f"could not execute OpenSSL: {exc}") from exc


def _openssl_error(result: subprocess.CompletedProcess[str]) -> str:
    return (result.stderr or result.stdout).strip()[-2000:]


def verify_receipt_signature_timestamp(
    token_der: bytes,
    signature_envelope: dict[str, Any],
    ca_file: str | Path,
    untrusted_file: str | Path | None = None,
    *,
    crl_file: str | Path | None = None,
    require_crl: bool = False,
    openssl_binary: str = "openssl",
    timeout_seconds: int = 15,
) -> dict[str, Any]:
    """Verify an RFC 3161 token whose imprint covers exact signature octets.

    The token must be DER/CMS ContentInfo bytes. The TSA CA file is an
    operator-configured trust anchor, never taken from the evidence package.
    If crl_file is supplied, CRLs are loaded alongside the CA certificates and
    OpenSSL checks revocation for the complete verified chain.
    """
    if not isinstance(token_der, bytes) or not token_der:
        raise CordValidationError("timestamp token must be non-empty DER bytes")
    if len(token_der) > MAX_TOKEN_BYTES:
        raise CordValidationError(f"timestamp token exceeds {MAX_TOKEN_BYTES} bytes")
    if not isinstance(timeout_seconds, int) or not 1 <= timeout_seconds <= 120:
        raise CordValidationError("timeout_seconds must be between 1 and 120")
    if require_crl and crl_file is None:
        raise CordValidationError("CRL checking is required but no CRL file was configured")

    signature = _signature_bytes(signature_envelope)
    executable = shutil.which(openssl_binary)
    if executable is None:
        raise CordValidationError("OpenSSL executable was not found")

    ca = Path(ca_file)
    if not ca.is_file():
        raise CordValidationError("configured TSA CA file does not exist")
    chain = Path(untrusted_file) if untrusted_file is not None else None
    if chain is not None and not chain.is_file():
        raise CordValidationError("configured untrusted TSA chain file does not exist")
    crl = Path(crl_file) if crl_file is not None else None
    if crl is not None and not crl.is_file():
        raise CordValidationError("configured TSA CRL file does not exist")

    with tempfile.TemporaryDirectory(prefix="cord-ts-") as directory:
        work = Path(directory)
        token = work / "timestamp.tsr"
        data = work / "signature.bin"
        trusted = work / "tsa-trust.pem"
        token.write_bytes(token_der)
        data.write_bytes(signature)
        trusted.write_bytes(ca.read_bytes() + (b"\n" + crl.read_bytes() if crl else b""))

        # Read the signed TSTInfo generation time first only to select the
        # certificate validation instant. No time is returned as trusted until
        # the subsequent CMS/imprint/path verification succeeds.
        decoded = _run(
            [executable, "ts", "-reply", "-token_in", "-in", str(token), "-text"],
            timeout_seconds,
        )
        if decoded.returncode:
            raise CordValidationError(
                "RFC 3161 token could not be decoded: " + _openssl_error(decoded)
            )
        match = TIME_RE.search(decoded.stdout)
        if not match:
            raise CordValidationError("OpenSSL output did not contain an RFC 3161 generation time")
        hash_match = HASH_RE.search(decoded.stdout)
        if not hash_match or hash_match.group(1).lower() not in ALLOWED_IMPRINT_HASHES:
            raise CordValidationError("RFC 3161 message-imprint hash must be SHA-256, SHA-384, or SHA-512")
        timestamp_text = match.group(1)
        generation_time = None
        for timestamp_format in ("%b %d %H:%M:%S %Y GMT", "%b %d %H:%M:%S.%f %Y GMT"):
            try:
                generation_time = datetime.strptime(timestamp_text, timestamp_format).replace(tzinfo=timezone.utc)
                break
            except ValueError:
                continue
        if generation_time is None:
            raise CordValidationError("OpenSSL returned an unsupported timestamp format")

        verify_args = [
            executable, "ts", "-verify", "-token_in", "-in", str(token),
            "-data", str(data), "-CAfile", str(trusted),
            "-purpose", "timestampsign",
            "-attime", str(int(generation_time.timestamp())),
        ]
        if chain is not None:
            verify_args.extend(["-untrusted", str(chain)])
        if crl is not None:
            verify_args.append("-crl_check_all")
        verified = _run(verify_args, timeout_seconds)
        if verified.returncode:
            raise CordValidationError(
                "RFC 3161 token validation failed: " + _openssl_error(verified)
            )

    return {
        "status": "PASS",
        "timestamp_profile": "CORD-RFC3161-ED25519-0.1",
        "generation_time": generation_time.isoformat(timespec="microseconds" if generation_time.microsecond else "seconds").replace("+00:00", "Z"),
        "message_imprint_hash": hash_match.group(1).lower(),
        "tsa_trust_anchor_sha256": hashlib.sha256(ca.read_bytes()).hexdigest(),
        "tsa_crl_sha256": hashlib.sha256(crl.read_bytes()).hexdigest() if crl else None,
        "message_imprint": "PASS",
        "cms_signature": "PASS",
        "tsa_certificate_path": "PASS",
        "tsa_timestamping_eku": "PASS",
        "tsa_certificate_validity_at_generation_time": "PASS",
        "tsa_revocation": "PASS" if crl else "NOT_CHECKED",
        "trusted_time_source": "configured_ca_file",
        "meaning": (
            "The configured TSA validated an RFC 3161 token whose message "
            "imprint covers these exact Ed25519 signature bytes. The signature "
            "existed no later than the TSA generation time."
        ),
        "limitations": [
            "The CA trust anchor and any CRLs are verifier-operator trust inputs.",
            "OCSP is not implemented; CRL checking occurs only when a CRL file is supplied.",
            "Without CRL checking, TSA certificate revocation status is not established.",
            "This does not prove civil identity, organizational authority, or truth of receipt claims.",
            "The caller must separately verify the Ed25519 receipt signature and apply CORD Trust Store policy.",
        ],
    }

 
def verify_signed_receipt_with_timestamp(
    receipt: dict[str, Any],
    signature_envelope: dict[str, Any],
    trust_store: dict[str, Any],
    token_der: bytes,
    tsa_ca_file: str | Path,
    required_role: str | None = None,
    untrusted_file: str | Path | None = None,
    *,
    crl_file: str | Path | None = None,
    require_crl: bool = False,
    openssl_binary: str = "openssl",
    timeout_seconds: int = 15,
) -> dict[str, Any]:
    """Verify TSA evidence, then apply the pinned CORD Trust Store policy."""
    timestamp_result = verify_receipt_signature_timestamp(
        token_der,
        signature_envelope,
        tsa_ca_file,
        untrusted_file,
        crl_file=crl_file,
        require_crl=require_crl,
        openssl_binary=openssl_binary,
        timeout_seconds=timeout_seconds,
    )
    from verifier.trust_store import verify_signed_receipt_with_store

    trust_result = verify_signed_receipt_with_store(
        receipt,
        signature_envelope,
        trust_store,
        required_role=required_role,
        trusted_signature_time=timestamp_result["generation_time"],
    )
    passed = timestamp_result["status"] == "PASS" and trust_result["status"] == "PASS"
    return {
        "status": "PASS" if passed else "FAIL",
        "timestamp": timestamp_result,
        "trust": trust_result,
        "meaning": (
            "The TSA token and receipt signature both verified, and the signing key passed the configured Trust Store policy."
            if passed else
            "One or more timestamp, signature, key, role, or historical validity checks did not pass."
        ),
    }
