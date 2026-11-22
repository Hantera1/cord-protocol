# Cord Trade Integration Plan

## Goal
Prove the protocol with local, exportable evidence packages before building hosted infrastructure or handling customer funds/data.

## Adapter contract
Each adapter MUST return a normalized evidence record containing:
- `provider_id`, `provider_reference`, `observed_at`;
- `status` from a provider-specific mapping;
- `raw_evidence_hash` for the original response/document;
- `verification_method` and `trust_class`;
- `limitations` and `provider_signature` where available.

Adapters MUST preserve the original provider status and map uncertainty to pending/unknown, never silently upgrade it to final.

## Integration order

| Priority | Integration | Initial scope | Why |
|---|---|---|---|
| P0 | JSON Schema + Python/TS validators | local Trade manifest | establish deterministic data contract |
| P0 | document hash + evidence packager | contracts, invoices, certificates | broad use without provider dependencies |
| P1 | e-signature provider adapter | signed document + provider receipt | agreement evidence |
| P1 | bank payment reference adapter | reference/status evidence only | avoids custody and money transmission |
| P1 | blockchain read-only adapter | transaction status and confirmations | supports crypto without wallet custody |
| P1 | shipping/tracking adapter | dispatch/delivery status | links physical fulfilment |
| P2 | assay/authentication provider adapter | signed certificate and report hash | valuable-goods trust |
| P2 | POS/ERP/accounting connectors | order/invoice/ledger references | business adoption |
| P3 | hosted verification API | stateless verify/index | only after security/privacy review |

## First pilot
Build two local demo packages:
1. A watch sale: serial/model/condition, seller declaration, authentication report hash, contract hash, payment reference, delivery acknowledgement.
2. A silver lot: lot ID, gross/net weight, unit, purity declaration, assay report hash, invoice hash, payment reference, custody/delivery events.

Use synthetic data only. Never include real identity documents, private keys, customer addresses or live transaction credentials in repository fixtures.

## API boundary (future)
Proposed endpoints, not implemented:
- `POST /v1/evidence/validate`
- `POST /v1/evidence/verify`
- `POST /v1/events`
- `GET /v1/transactions/{transaction_id}/evidence`
- `GET /v1/health`

Hosted API must be stateless with respect to custody: it validates and indexes evidence but never receives seed phrases, private keys or customer funds.

## Acceptance criteria
- Invalid/unknown event types fail closed.
- Every event references a valid Core receipt hash.
- Detached extension data cannot alter Core hashes or PASS semantics.
- Every payment/delivery status includes source, observed time and trust class.
- Reversed/refunded/failed states remain visible as later events.
- Evidence export and offline verification work without API access.
- Tests cover tampering, replay, duplicate IDs, missing prior events, unknown schema versions and misleading status transitions.
