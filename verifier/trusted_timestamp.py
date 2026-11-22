"""RFC 3161 timestamp-token validation for CORD Ed25519 receipt signatures."""
from __future__ import annotations
import base64, binascii, re, shutil, subprocess, tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from verifier.verify import CordValidationError

MAX_TOKEN_BYTES = 1_048_576
TIME_RE = re.compile(r"^Time stamp:\s*(.+ GMT)\s*$", re.MULTILINE)

def _signature_bytes(envelope: dict[str, Any]) -> bytes:
    if not isinstance(envelope, dict) or envelope.get("spec_version") != "0.1" or envelope.get("alg") != "Ed25519":
        raise CordValidationError("timestamp profile supports only Signed Receipt v0.1 Ed25519")
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
    try:
        return subprocess.run(args, check=False, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=timeout, shell=False)
    except subprocess.TimeoutExpired as exc:
        raise CordValidationError("OpenSSL timestamp validation timed out") from exc
    except OSError as exc:
        raise CordValidationError(f"could not execute OpenSSL: {exc}") from exc

def verify_receipt_signature_timestamp(token_der: bytes, signature_envelope: dict[str, Any],
        ca_file: str | Path, untrusted_file: str | Path | None = None, *,
        openssl_binary: str = "openssl", timeout_seconds: int = 15) -> dict[str, Any]:
    """Verify a TST whose message imprint covers the exact raw Ed25519 signature bytes.

    CA trust is supplied out-of-band by the verifier operator. OpenSSL validates
    CMS signature, imprint, TSA chain and timestamping certificate purpose.
    Online OCSP/CRL checking is not performed.
    """
    if not isinstance(token_der, bytes) or not token_der:
        raise CordValidationError("timestamp token must be non-empty DER bytes")
    if len(token_der) > MAX_TOKEN_BYTES:
        raise CordValidationError(f"timestamp token exceeds {MAX_TOKEN_BYTES} bytes")
    if not isinstance(timeout_seconds, int) or not 1 <= timeout_seconds <= 120:
        raise CordValidationError("timeout_seconds must be between 1 and 120")
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
    with tempfile.TemporaryDirectory(prefix="cord-ts-") as directory:
        token = Path(directory) / "timestamp.tsr"
        data = Path(directory) / "signature.bin"
        token.write_bytes(token_der)
        data.write_bytes(signature)
        args = [executable, "ts", "-verify", "-token_in", "-in", str(token),
                "-data", str(data), "-CAfile", str(ca)]
        if chain is not None:
            args.extend(["-untrusted", str(chain)])
        verified = _run(args, timeout_seconds)
        if verified.returncode:
            detail = (verified.stderr or verified.stdout).strip()[-2000:]
            raise CordValidationError("RFC 3161 token validation failed" + (f": {detail}" if detail else ""))
        decoded = _run([executable, "ts", "-reply", "-token_in", "-in", str(token), "-text"], timeout_seconds)
        if decoded.returncode:
            detail = (decoded.stderr or decoded.stdout).strip()[-2000:]
            raise CordValidationError("validated timestamp token could not be decoded" + (f": {detail}" if detail else ""))
        match = TIME_RE.search(decoded.stdout)
        if not match:
            raise CordValidationError("OpenSSL output did not contain an RFC 3161 generation time")
        try:
            gen_time = datetime.strptime(match.group(1), "%b %d %H:%M:%S %Y GMT").replace(tzinfo=timezone.utc)
        except ValueError as exc:
            raise CordValidationError("OpenSSL returned an unsupported timestamp format") from exc
    return {
        "status": "PASS",
        "timestamp_profile": "CORD-RFC3161-ED25519-0.1",
        "generation_time": gen_time.isoformat().replace("+00:00", "Z"),
        "message_imprint": "PASS", "cms_signature": "PASS",
        "tsa_certificate_path": "PASS", "tsa_timestamping_eku": "PASS",
        "trusted_time_source": "configured_ca_file",
        "meaning": "The configured TSA validated a token covering these exact Ed25519 signature bytes; the signature existed no later than generation_time.",
        "limitations": [
            "The CA trust anchor is an operator-supplied trust input.",
            "Online OCSP or CRL revocation checking is not performed.",
            "This does not prove civil identity, organizational authority, or truth of receipt claims.",
            "The caller must separately verify the receipt signature and apply CORD Trust Store policy."
        ]
    }
