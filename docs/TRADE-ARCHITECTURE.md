# Cord Trade — Architecture and Product Plan

**Status: architecture proposal.** This document describes an optional business-evidence layer built on Cord Core v0.1. It does not change Core fields, canonicalization, or verification semantics.

## 1. Product direction

Cord should be a vendor-neutral evidence protocol and optional integration platform for business transactions. It is not a marketplace, bank, exchange, custody provider, identity authority, appraiser, or authenticity laboratory.

The same evidence model should support:
- physical goods: watches, jewellery, art, collectibles, machinery, inventory;
- commodities and metals: gold, silver, platinum, industrial metals, lots and assay certificates;
- contracts and services: offers, purchase agreements, delivery terms, acceptance and amendments;
- digital commerce: invoices, orders, refunds, fulfilment and payment references;
- bank and crypto payments: evidence references to external payment systems;
- AI-assisted business events: declarations, model outputs and policy evidence.

## 2. Non-negotiable architecture rules

1. **Core remains immutable and small.** Trade data is an extension package linked to a Core receipt hash. Never add trade-specific fields to the Core Bundle or Receipt.
2. **Evidence, not truth claims.** Cord can verify hashes, signatures, schemas and externally anchored timestamps. It cannot independently prove an item is genuine, ownership is legally valid, a payment is final, or a delivery happened unless a trusted external source attests to that fact.
3. **Offline verification first.** Every evidence package must be exportable and independently verifiable without a Cord account or Cord server.
4. **No sensitive data on public chains.** Do not publish names, addresses, full contracts, serial numbers, identity documents, invoices or private commercial data on-chain. Store encrypted documents off-chain; anchor only commitments where appropriate.
5. **Provider-neutral adapters.** Banks, payment providers, chains, identity providers, e-signature vendors, ERP/POS systems and logistics providers are replaceable adapters.
6. **Explicit trust levels.** Distinguish party-declared, counterparty-acknowledged, provider-attested, and independently audited evidence.
7. **No custody or exchange in v1.** Cord records evidence and references; it does not hold customer money, private keys, crypto-assets or goods.

## 3. Reference architecture

```
Business apps / POS / ERP / Marketplace / Mobile
                 |
          Cord Integration SDKs
                 |
     Trade Event API (optional hosted service)
                 |
   Validation + Schema Registry + Policy Engine
                 |
      Evidence Package / Event Journal
          |                    |
   Cord Core receipt     Detached extensions
          |             /       |        \
     Core verifier   Signatures  Payment  Item/Delivery
                         |       adapters adapters
                    External KMS  Bank/chain APIs
                         |
              Timestamp / trust anchors
```

The hosted API is optional. It may validate, index and relay evidence but must not be the only place where evidence can be verified.

## 4. Trade evidence package

A Trade package is a detached, versioned JSON document with:
- extension identifier and version;
- event identifier and event type;
- references to the Cord Core receipt hash;
- transaction identifier and previous-event reference;
- actor references (pseudonymous IDs, not raw identity documents);
- item or lot descriptors;
- claims and their evidence sources;
- document commitments (hash, media type, encrypted storage reference);
- payment and delivery references;
- signatures and optional timestamp tokens;
- disclosure and retention metadata.

A package is not automatically a legally binding contract. Contract validity and electronic-signature requirements depend on jurisdiction, document type and signing method.

## 5. Event lifecycle

Recommended transaction states:
1. `DRAFT` — one party creates a proposed transaction.
2. `OFFERED` — offer and terms are shared.
3. `ACCEPTED` — required parties sign/accept a defined version.
4. `PAYMENT_PENDING` — payment initiated; not yet treated as settled.
5. `PAYMENT_CONFIRMED` — provider evidence confirms the relevant payment status.
6. `FULFILMENT_PENDING` — goods or services are being delivered.
7. `DELIVERED` — delivery evidence exists.
8. `COMPLETED` — required conditions have evidence and parties acknowledge completion.
9. `DISPUTED` / `CANCELLED` / `REFUNDED` — explicit exception events.

Do not let an integration infer completion from a single payment or shipping status. Keep each state transition as a new append-only event; corrections are compensating events, not silent overwrites.

## 6. Vertical profiles

### A. Watches, jewellery and high-value goods
Record brand, model, serial/reference number, physical attributes, condition, photos, service history, certificates and seller declarations. Serial number is an identifier, not proof of authenticity or title. Optional third-party authentication and ownership evidence must be separately attributed and signed.

### B. Metals and commodities
Record commodity, form, gross/net weight, unit, fineness/purity, assay method, lot/batch ID, refinery/assayer, certificate ID, origin declarations, custody transfers and delivery weights. Distinguish seller-declared data from accredited assay results. Include unit conventions and measurement uncertainty.

### C. Contracts and B2B trade
Commit to exact document bytes; capture document version, parties' signing evidence, signature provider transaction IDs, amendments, delivery milestones, invoice references and acceptance events. Use a qualified or otherwise appropriate e-signature provider where required; Cord itself is not a signature service.

### D. Payments and crypto
Store provider, network, asset, transaction/reference ID, amount, currency/asset unit, status, observed time and confirmation policy. For blockchain payments, record chain ID, transaction hash, asset contract/mint where relevant, destination and confirmation/finality policy. Never treat an unconfirmed transaction as settled. Never store private keys or seed phrases in Cord.

### E. Accounting and ERP/POS
Use external accounting systems as the system of record for ledgers and tax books. Cord links evidence to invoice, receipt, order, settlement and delivery identifiers. It is not a general ledger and does not replace statutory bookkeeping.

## 7. Trust and verification model

Every claim should carry an evidence class:
- `DECLARED`: entered by a party; proves only that the party made the declaration.
- `ACKNOWLEDGED`: acknowledged/signed by another identified party.
- `PROVIDER_ATTESTED`: backed by a verifiable statement from a payment, identity, logistics, e-signature or assay provider.
- `INDEPENDENTLY_AUDITED`: supported by a named independent auditor and an identified report.

Verification output must report exactly which checks passed, which trust anchors were used, and which claims remain unverified. Never collapse all checks into one generic “verified transaction” badge.

## 8. Privacy, security and compliance by design

- Minimise personal data; use pseudonymous actor IDs in public evidence.
- Keep contracts, identity data and commercial records encrypted and access-controlled.
- Define retention, deletion, export, access logs and breach response before hosting customer data.
- Support selective disclosure: share only the document/claims needed for a counterparty or auditor.
- Separate tenant data and keys; use managed KMS/HSM for server-side signing keys.
- Perform sanctions, AML/KYC, consumer, tax, data protection and commodity-specific checks through appropriately licensed/qualified providers where applicable. Cord must not claim to perform these checks merely by recording provider references.
- Obtain jurisdiction-specific legal review before production in Sweden, EU, UAE or other target markets.

## 9. Business model

Recommended staged model:
- **Open protocol + free local verifier:** adoption, trust and independent implementations.
- **Developer tier:** free sandbox, SDKs, schemas and test tools.
- **Business SaaS:** per-organisation subscription for team workflows, API access, audit search, integrations, retention controls and support.
- **Usage pricing:** metered evidence events/API verification/storage, with transparent caps and export.
- **Enterprise:** private deployment, SSO, policy controls, KMS/HSM integration, audit exports, SLA and support.
- **Partner revenue:** integrations with e-signature, assay, authentication, logistics and payment providers. Disclose referral fees and never sell verification outcomes.

Avoid a proprietary token, transaction speculation, custody, spreads on customer assets or pay-to-pass verification.

## 10. Go-to-market: Sweden + Arabic-speaking markets

Build one protocol and localise interfaces/documentation. Start with two design-partner tracks:
- Sweden/Nordics: second-hand and luxury dealers, auctioneers, metal traders, B2B wholesalers, ERP/POS integrators.
- Arabic-speaking markets: begin with UAE and Saudi Arabia discovery, then wider MENA. Use Arabic RTL UI and bilingual Arabic/English contracts and evidence summaries. Validate local commercial, privacy, e-signature, AML and precious-metals requirements before live transactions.

Do not assume one legal framework applies across MENA. Country-by-country launch gates are mandatory.

## 11. Delivery plan

### Phase 1 — Protocol and demo (now)
- Publish Trade extension schema and trust vocabulary.
- Add deterministic test vectors and strict schema validation.
- Create watch and metal sample evidence packages.
- Add SDK helper that creates detached Trade manifests linked to Core receipt hashes.
- Keep all data local; no accounts, payments or custody.

### Phase 2 — Integrations
- Add signature-provider adapter interface.
- Add payment reference adapters (bank reference and one selected chain).
- Add shipping/delivery and assay-provider evidence adapters.
- Add import/export for common invoice/ERP formats.

### Phase 3 — Hosted pilot
- Stateless verification API, tenant authentication, rate limits, encrypted object storage, audit logging, backup/restore, incident response and retention controls.
- Pilot with selected businesses in Sweden and UAE after legal and security review.

### Phase 4 — Scale
- Independent implementations, external protocol review, conformance suite, partner directory and regional deployments.

## 12. Release gates

Cord Trade must not be marketed as production-ready until:
- schema and event semantics are stable and versioned;
- cross-language conformance tests pass;
- signature and timestamp trust policies are implemented and reviewed;
- privacy/security threat model and penetration test are complete;
- provider adapters distinguish pending, failed, reversed and final statuses;
- legal review is complete for each launch jurisdiction;
- incident response, data export/deletion and operational monitoring are tested.
