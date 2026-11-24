# CORD Verify API — local development

The first API implementation is a stateless HTTP adapter around the existing
CORD Core v0.1 reference verifier. It does not change Core formats or PASS
semantics and does not retain submitted evidence.

## Install

```bash
python -m pip install -r requirements.txt
```

## Run locally

For local-only development, explicitly disable API-key authentication:

```bash
CORD_API_AUTH_DISABLED=true uvicorn api.app:app --host 127.0.0.1 --port 8000
```

Do not use `CORD_API_AUTH_DISABLED=true` on a public or shared deployment.

For an authenticated local test, configure the SHA-256 digest of a long,
random API key (never commit the raw key):

```bash
python -c "import hashlib; print(hashlib.sha256(b'REPLACE-WITH-A-LONG-RANDOM-SECRET').hexdigest())"
export CORD_API_KEY_SHA256="<printed-sha256>"
uvicorn api.app:app --host 127.0.0.1 --port 8000
```

The service returns HTTP 503 if neither explicit local bypass nor a valid
configured key digest is present. This initial single-key mechanism is a
development gate, not a production customer key-management system.

## Verify a package

Send the exact original bytes of `bundle.json` and `receipt.json`, Base64
encoded. Do not parse and reserialize the bundle: Core checks the exact file
hash as well as the canonical bundle hash.

```bash
python - <<'PY'
import base64, json
from pathlib import Path
payload = {
    "spec_version": "0.1",
    "bundle_base64": base64.b64encode(Path("bundle.json").read_bytes()).decode("ascii"),
    "receipt_base64": base64.b64encode(Path("receipt.json").read_bytes()).decode("ascii"),
}
Path("request.json").write_text(json.dumps(payload), encoding="utf-8")
PY
curl -sS http://127.0.0.1:8000/v1/verify/core \
  -H 'Content-Type: application/json' \
  --data-binary @request.json
```

With authentication enabled, add `-H 'Authorization: Bearer YOUR_API_KEY'`.

## Endpoints

- `GET /v1/health`: minimal liveness response.
- `POST /v1/verify/core`: verify one Core v0.1 bundle and receipt.

Swagger/OpenAPI routes are disabled in this initial service. The endpoint is
not a production deployment, service-level agreement, identity service,
trusted timestamp service, or factual-truth oracle.

## Limits and security

- Request body: 3 MiB maximum.
- Each decoded evidence file: 1 MiB maximum (same limit as Core verifier).
- Exact field set and strict UTF-8 JSON / duplicate-key rejection.
- Strict canonical standard Base64.
- No remote URL fetching and no evidence persistence.
- Authentication uses a configured SHA-256 API-key digest and constant-time
  digest comparison. Multi-customer key lifecycle, quotas, billing, durable
  audit controls, production proxy limits, and independent security review
  remain future release gates.

Run tests:

```bash
python -m unittest discover -s tests -v
```
