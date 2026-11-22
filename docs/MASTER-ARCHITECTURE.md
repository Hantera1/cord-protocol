# Cord Master Architecture

Status: architecture proposal, not a production specification.

## Product boundary
Cord is a vendor-neutral evidence integrity and verification platform. A valid hash or receipt proves only that supplied bytes match a recorded commitment under a specified format. It does not independently prove truth, identity, legal title, physical authenticity, payment finality, delivery, condition or trusted time.

## Product layers
### Cord Core — open protocol
- Versioned evidence bundles and receipts, canonicalization, hashing and deterministic offline verification.
- Public specifications, SDK interfaces, synthetic test vectors and reference implementations.
- No mandatory account, hosted service, payment rail, identity provider or blockchain.
- Existing Apache 2.0 grants remain in force.

### Cord Extensions — versioned profiles
- Detached signatures and trust-anchor references.
- Trusted timestamp evidence and event-chain/checkpoint profiles.
- Trade, commerce, asset and supply-chain evidence profiles.
- Every extension defines claim semantics, trust assumptions, privacy impact, failure behavior, schema, test vectors and compatibility policy.

### Cord Commercial Services — private
- Hosted API, organization workspace and managed evidence operations.
- Commercial connectors, proprietary workflow orchestration, templates and support.
- License issuance, entitlements, billing references and partner management.
- Customer data, credentials, pricing and trade secrets remain outside public repositories.

### Cord Analysis — separate analytical product
- Lawfully sourced market-data ingestion, provenance, normalization and deduplication.
- Trend detection, comparable-sales analysis, price ranges and alerts.
- Model/version traceability, evaluation and human review.
- Analysis is informational and must not be presented as guaranteed returns or verified facts.

## Shared platform domains
1. Trade: orders, agreements, milestones, handovers and disputes.
2. Commerce: storefront orders, returns, refunds and marketplace events.
3. Payment evidence: provider references, status callbacks and reconciliation; no custody or movement of customer funds in the initial product.
4. Assets: persistent object identifiers, descriptions, evidence references, service events and ownership-claim events.
5. Supply: batches, shipments, custody-transfer claims and delivery evidence.
6. Compliance: policy versions, attestations, audit exports and retention records.
7. Identity and authorization: external identity-provider references, organization roles and scoped access. Core does not assert real-world identity.
8. Analysis: market intelligence and decision support with source and uncertainty disclosures.

## First vertical: watches
Cord Watch Record is an asset profile, not a claim that Cord authenticates watches. It may store an opaque object ID, model/reference metadata, private serial-number reference, dated photographs, condition reports, service records, provenance documents, third-party inspection attestations, and sale/transfer/valuation events.

Private identity, exact owner details, full serial numbers, invoices and location data must be stored in a protected service, not public Core records. Public verification discloses only the minimum status and evidence commitments authorized by the data controller.

Cord Analysis Watch may analyze completed auction results and licensed sale prices, asking prices separately, model supply, sales velocity, demand proxies, condition, completeness, service, provenance, geography, currency and time effects. Show uncertainty intervals, sample size, source freshness and liquidity/risk indicators.

It must not label a watch authentic, owned, investment-grade or undervalued solely from model output. Human expert review and source-specific attestations are required for those claims.

## Webshop and payment integration
1. Merchant system creates an order.
2. Payment service provider processes payment.
3. Provider webhook or signed API response supplies a status claim and provider reference.
4. Cord validates the integration signature and records a minimal evidence event.
5. Fulfilment provider supplies dispatch/delivery events.
6. Cord produces a verifiable evidence package and controlled disclosure link.

Cord does not receive card data, payment credentials or customer funds in the initial architecture. A payment status event is not a guarantee of settlement or immunity from chargeback. Integrations must respect provider terms and applicable payment-services law.

## Trust and data classification
- Public: protocol specs, synthetic fixtures, public test vectors, non-sensitive SDK code.
- Internal: non-public release planning and design notes.
- Confidential: customer contracts, business plans, pricing and security assessments.
- Restricted: personal data, credentials, private keys, payment data, identity documents, full serial numbers linked to owners.

Public GitHub repositories may contain only Public-class information. Confidential and Restricted data belong in approved private systems with least-privilege access, encryption, retention controls and audit logs.

## Licensing and intellectual property
The open Core license is not a commercial entitlement gate. Paid licenses apply only to separately owned or lawfully licensed assets: hosted services, proprietary modules, templates, support, data products, trademarks and partner rights. Chain-of-title must be documented before licensing any asset. No retroactive restriction of existing Apache 2.0 permissions.

## Non-functional requirements
Offline verification; tenant isolation; least privilege; encryption in transit and at rest; managed key lifecycle; authenticated webhooks; replay protection; idempotency; rate limits; data minimization; retention and deletion workflows; restricted audit logs; backups and restore tests; incident response; versioned APIs and schemas; independent security and interoperability review before production claims.

## Release maturity
Draft → reviewed specification → interoperable implementation → security-reviewed beta → production release. A feature is not production-ready merely because a schema or prototype exists.
