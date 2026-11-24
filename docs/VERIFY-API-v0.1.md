# CORD Verify API v0.1 — Design Proposal

**Status:** Draft proposal. Not a deployed service, stable API, certification, or production security approval.  
**Scope:** Stateless hosted verification of CORD Core v0.1 evidence packages.  
**Compatibility rule:** The API MUST call the same normative verifier behavior as the offline reference implementation. It MUST NOT redefine Core PASS semantics.

## 1. Product objective

CORD Verify API gives applications a simple HTTPS interface to verify CORD evidence without implementing the verifier themselves. It is a convenience and operations service around the open protocol. It is not the exclusive way to verify CORD evidence.

The same evidence MUST remain independently verifiable offline using an implementation that conforms to the published CORD specification and test vectors.

## 2. Non-negotiable principles

1. **Protocol neutrality:** No AI provider, model vendor, cloud provider, or commercial customer receives a privileged verification rule.
2. **Offline parity:** Hosted results MUST be reproducible by a conforming offline verifier using the same evidence and applicable trust inputs.
3. **No truth overclaim:** A Core v0.1 PASS means only that the supplied bundle and receipt satisfy the Core v0.1 structural and hash-integrity checks. It does not establish authorship, model identity, factual truth, legal ownership, trusted time, or real-world authenticity.
4. **Fail closed:** Malformed, unsupported, or incomplete inputs MUST NOT receive PASS.
5. **No hidden trust:** Trust anchors, trust stores, profiles, and policy versions MUST be identified as verifier-side inputs. A trust anchor supplied only inside an untrusted evidence package MUST NOT be trusted.
6. **Privacy by default:** Evidence content is processed transiently and is not retained by default. Operational logs MUST NOT contain submitted evidence, secrets, or full API keys.
7. **Versioned behavior:** API version, Core version, verifier build, and policy inputs MUST be observable in every result.
8. **No AI verdict override:** AI may help explain or triage evidence, but cannot turn a cryptographic or deterministic FAIL/INDETERMINATE into PASS.

## 3. Initial endpoint

### `POST /v1/verify/core`

Verifies one CORD Core v0.1 bundle and receipt.

**Request**

```http
POST /v1/verify/core HTTP/1.1
Authorization: Bearer <api-key>
Content-Type: application/json
```

```json
{
  "spec_version": "0.1",
  "bundle_base64": "<base64 of the exact original bundle.json bytes>",
  "receipt_base64": "<base64 of the exact original receipt.json bytes>"
}
```

The Base64 values represent the exact original file bytes. The service MUST decode them strictly and MUST pass those bytes to the same bounded parser and verifier used by offline verification. It MUST NOT parse and reserialize the bundle before checking `bundle_file_hash`.

Initial request limits:
- Encoded JSON request body: maximum 3 MiB.
- Decoded bundle: maximum 1 MiB.
- Decoded receipt: maximum 1 MiB.
- Exactly the documented request fields; reject unknown fields.
- Strict Base64 decoding; reject malformed or non-canonical encodings.
- Only `spec_version = "0.1"` is supported by this endpoint.

The limits are conservative initial service limits and may be revised only with documented versioning and security review.

## 4. Response contract

A syntactically valid verification request returns HTTP 200 even when the evidence fails verification. The verification outcome is carried in the response body.

**PASS example**

```json
{
  "api_version": "1",
  "request_id": "req_<opaque-id>",
  "result": {
    "status": "PASS",
    "spec_version": "0.1",
    "profile": "cord-core",
    "checks": {
      "bundle_schema": "PASS",
      "receipt_schema": "PASS",
      "canonical_bundle_hash": "PASS",
      "exact_bundle_file_hash": "PASS"
    },
    "meaning": "The supplied bundle and receipt satisfy CORD Core v0.1 integrity checks. This does not prove authorship, model identity, trusted time, or claim truth."
  },
  "verifier": {
    "name": "CORD Reference Verifier",
    "version": "<build-version>",
    "policy_id": "cord-core-v0.1"
  }
}
```

**FAIL example**

```json
{
  "api_version": "1",
  "request_id": "req_<opaque-id>",
  "result": {
    "status": "FAIL",
    "spec_version": "0.1",
    "profile": "cord-core",
    "checks": {
      "bundle_schema": "PASS",
      "receipt_schema": "PASS",
      "canonical_bundle_hash": "FAIL",
      "exact_bundle_file_hash": "FAIL"
    },
    "error_code": "HASH_MISMATCH",
    "meaning": "One or more deterministic CORD Core v0.1 integrity checks failed."
  },
  "verifier": {
    "name": "CORD Reference Verifier",
    "version": "<build-version>",
    "policy_id": "cord-core-v0.1"
  }
}
```

The examples illustrate the intended contract; exact field names and per-check reporting must be reconciled with the verifier's actual structured results before implementation. The service MUST NOT fabricate individual check results that the verifier did not produce.

### HTTP error semantics

- `400`: malformed request JSON, invalid Base64, unknown fields, or invalid request shape.
- `401`: missing or invalid API credential on hosted authenticated deployments.
- `403`: credential lacks required scope or account is disabled.
- `413`: request or decoded evidence exceeds configured size limits.
- `415`: unsupported content type.
- `422`: unsupported Core version or request cannot be evaluated under this endpoint's contract.
- `429`: rate or quota limit exceeded; include `Retry-After` when applicable.
- `500` / `503`: internal or temporary service failure. Never return PASS on infrastructure failure.

Malformed evidence that reaches the verifier and deterministically fails validation should return HTTP 200 with `result.status = "FAIL"`; transport/request-shape errors use HTTP error codes.

## 5. Outcome semantics

The API MUST preserve the distinction between:
- `PASS`: every required check for the declared scope passed.
- `FAIL`: at least one deterministic required check failed.
- `INDETERMINATE`: the evidence could not be fully evaluated under the selected policy or required trust input was unavailable.

Core v0.1 verification currently provides integrity validation only. It MUST NOT imply signature, identity, timestamp, profile, revocation, or issuer validation unless those checks are explicitly implemented and requested through a separately versioned extension endpoint.

A service outage, timeout, unavailable dependency, or unhandled verifier exception is an API error, not a verification PASS.

## 6. Authentication, plans, and fair access

The hosted service may require an API key for account attribution, abuse prevention, quota enforcement, and billing. API credentials are service credentials; they are not CORD signing keys and MUST never be embedded in evidence receipts.

Required controls:
- Store only a one-way hash of API keys where practical; display the secret only at creation.
- Support key rotation, immediate revocation, scopes, and per-key usage accounting.
- Use constant-time credential comparison where applicable.
- Enforce per-key and per-account rate and concurrency limits.
- Never expose whether another customer's key exists.
- Do not put API keys in URLs, logs, analytics events, or error messages.
- Separate free developer quotas from paid capacity; do not change verification rules by plan.
- Billing, quotas, and service availability MUST NOT influence a verification result.

The public protocol and offline verifier remain open under their applicable license. Paid plans charge for hosted availability, throughput, operations, support, dashboards, and contractual service levels—not for a more favorable verdict or exclusive access to Core verification.

No prices are fixed by this technical proposal.

## 7. Privacy and data handling

Default behavior:
- Process submitted evidence in memory or short-lived isolated temporary storage.
- Do not persist evidence content, bundle fields, receipt fields, or Base64 payloads.
- Do not log request bodies.
- Log only operational metadata needed for reliability and abuse prevention: request ID, account/key identifier (non-secret), endpoint, timestamps, byte counts, duration, outcome category, verifier build, and error code.
- Define and publish retention periods for operational logs.
- Provide an explicit, separately consented evidence-retention product only if a later product requirement justifies it.
- Encrypt transport with TLS; production deployments must also protect backups, secrets, and infrastructure credentials.
- Apply deletion, access, and incident-response procedures before launch.

The service MUST NOT fetch user-supplied URLs or remote evidence locations in the initial version. This avoids SSRF and ambiguous evidence-byte retrieval.

## 8. Reliability and operational controls

Before public production:
- Run the API as a separate service layer around the reference verifier; keep protocol logic independent of HTTP framework code.
- Apply request-size limits at the reverse proxy and application layers.
- Use bounded worker concurrency and request timeouts.
- Add health and readiness endpoints that reveal no secrets or internal topology.
- Use structured, redacted logs and trace IDs.
- Pin dependencies and deployment artifacts; scan dependencies and container images.
- Use least-privilege service identities and separate development, staging, and production.
- Define backup/restore only for account, quota, and billing metadata; evidence is not backed up by default.
- Establish incident response, key compromise, credential revocation, and service status procedures.
- Publish service availability and status without representing uptime as protocol validity.

## 9. Planned API surface

Only the Core verification endpoint is in the initial implementation scope.

| Endpoint | Status | Purpose |
|---|---|---|
| `POST /v1/verify/core` | Initial | Verify Core v0.1 bundle + receipt |
| `GET /v1/health` | Initial operations | Basic liveness, no sensitive details |
| `GET /v1/usage` | Later | Customer's quota and usage |
| `POST /v1/verify/signed-receipt` | Later | Signed receipt + externally pinned Trust Store policy |
| `POST /v1/verify/profile` | Later | Profile-aware verification after profile engine and schemas mature |
| `GET /v1/keys` | Not in initial scope | No public key registry until governance and lifecycle are defined |

No endpoint for arbitrary URL fetching, evidence creation, key issuance, or custody is included in v0.1.

## 10. Implementation sequence and release gates

### Phase A — Contract and parity
- Review this API contract against the current Core verifier and canonicalization rules.
- Add an adapter that calls existing verifier functions without duplicating protocol logic.
- Add request/response schemas and strict decoding.
- Add tests proving API and offline verifier agree on the same fixed vectors and adversarial inputs.

### Phase B — Local developer preview
- Add a small HTTP application with no production secrets or persistent evidence storage.
- Provide local run instructions and a sample client.
- Keep authentication configurable for local development; hosted deployments require authentication.
- Add tests for size limits, malformed JSON/Base64, duplicate keys, unknown fields, hash mismatch, timeouts, and error handling.

### Phase C — Hosted pilot
- Add API-key lifecycle, quotas, rate limits, metrics, billing integration, privacy notices, terms, and support process.
- Complete threat modelling, dependency review, penetration testing, and deployment review.
- Begin with invited pilot customers and conservative limits.

### Production release gates
- API/offline conformance tests pass on CI.
- Independent security review completed and findings triaged.
- Privacy and retention policy published.
- Authentication, revocation, quota isolation, and abuse controls tested.
- Operational monitoring and incident response ready.
- No claim of production certification or regulatory compliance without separate evidence.

## 11. Explicit non-goals

The initial API does not:
- prove that a named AI model generated an output;
- prove the factual truth of claims;
- establish civil identity or legal authority;
- authenticate physical goods or legal ownership;
- provide trusted time or revocation status through Core v0.1;
- store or manage signing private keys;
- require blockchain, a token, a CORD account, or a CORD cloud service for offline verification;
- allow an AI model or paying customer to override deterministic verifier outcomes.

## 12. Governance and compatibility

This document is a service API design proposal, not a change to CORD Core v0.1. Core formats, canonicalization, hashes, receipts, and offline verification semantics remain unchanged.

API changes are versioned independently from Core. Breaking request/response changes require a new API major version. A change to Core semantics requires a separate protocol specification revision, test vectors, and compatibility review.

The first implementation should be deliberately small: one endpoint, one verifier adapter, no evidence storage, no AI verdict engine, no payment dependency, and no public key registry.
