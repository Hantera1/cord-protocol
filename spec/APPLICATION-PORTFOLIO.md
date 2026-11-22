# CORD Application Portfolio and Reserved Use Cases

**Status: architecture portfolio — proposed/reserved scope.** This document records the intended application areas for CORD so that they remain part of the project direction. A listed area is not a claim that a corresponding profile, service, certification, integration, or production implementation already exists.

## 1. Purpose

CORD is intended to be a vendor-neutral protocol and verification infrastructure for creating, exchanging, and independently verifying cryptographic evidence about digital events, data, decisions, physical assets, and transactions.

CORD is not a single industry application. Its Core is intended to support multiple versioned application profiles while preserving one stable verification foundation.

## 2. Architectural layers

1. **CORD Core:** stable versioned bundle/receipt formats, canonicalization, cryptographic commitments, and offline integrity verification.
2. **Trust and evidence extensions:** signatures, trusted timestamps, event chains/checkpoints, identity/key trust, provenance, and policy evidence. Each extension has its own specification and trust model.
3. **Application profiles:** industry- or workflow-specific evidence schemas, validation rules, status semantics, privacy rules, and test vectors.
4. **SDKs and integrations:** reusable libraries, APIs, adapters, and reference implementations.
5. **Optional services:** hosted verification, evidence storage, organization administration, dashboards, and support. Core verification must remain possible without CORD-operated services.

Application profiles MUST NOT silently add fields to Core v0.1, alter Core canonicalization, or redefine the meaning of Core PASS.

## 3. Reserved cross-industry verification capabilities

The following capability areas are part of the intended CORD architecture. They may be implemented as extensions, shared services, or reusable profile components after separate specifications and threat reviews.

| Capability area | Intended verification purpose |
|---|---|
| Clock and Time Verification | Trusted timestamp evidence, clock-source attestations, clock synchronization evidence, event-time claims, and time-ordering limitations |
| Identity and Key Verification | Key-to-identity bindings, issuer identity, roles, authorization, key rotation, expiry, and revocation |
| Data Integrity Verification | Detect changes to evidence and data through cryptographic commitments |
| Data Provenance Verification | Record source, transformations, custody, and lineage of data |
| Event Continuity Verification | Link events, detect broken/reordered records relative to trusted checkpoints, and expose completeness limitations |
| AI Event and Output Verification | Record AI inputs/outputs by digest, model and policy declarations, execution context, and signed attestations where available |
| AI Agent Action Verification | Evidence of agent identity, authority, tool calls, approvals, actions, and outcomes |
| Policy and Compliance Evidence | Record policy versions, control evaluations, approvals, and audit evidence without claiming legal compliance solely from a CORD PASS |
| Document and Record Verification | Verify document integrity, issuer signatures, revisions, and evidence history |
| Asset and Ownership Evidence | Identify physical assets and record authenticity examinations, condition, custody, ownership assertions, service, and transfers |
| Transaction and Settlement Evidence | Record transaction instructions, approvals, timestamps, handoffs, and settlement-related attestations |
| Supply Chain and Logistics Evidence | Record origin claims, custody, shipping events, handovers, condition, and delivery evidence |

## 4. Reserved application domains

The following domains are explicitly in scope for future CORD application profiles. The list is a product and architecture reservation, not a claim of completed implementation.

### 4.1 High-value physical assets and luxury commerce
- Luxury watches, clocks, and collectible timepieces.
- Jewellery, diamonds, gemstones, and precious metals.
- Art, antiques, design objects, and collectibles.
- Luxury, classic, and collectible vehicles.
- Other individually identifiable high-value assets.

Initial profile: [CORD Luxury Asset Verification](LUXURY-ASSET-VERIFICATION.md). Watches are the initial reference use case.

### 4.2 Real estate and built assets
- Property identity and document evidence.
- Inspection, condition, maintenance, and renovation records.
- Building component and equipment histories.
- Property transaction and handover evidence.
- Contractor, surveyor, inspector, and service-provider attestations.

CORD evidence does not replace land registries, legal title records, conveyancing, permits, or professional inspections.

### 4.3 Financial services and high-value transactions
- Transaction evidence and authorization trails.
- Trade and settlement event evidence.
- Asset provenance and supporting-document integrity.
- Audit trails for financial operations.
- Evidence exchange between institutions and counterparties.

CORD does not itself provide banking, custody, payment clearing, investment advice, AML/KYC determinations, or regulatory approval.

### 4.4 Supply chain, trade, and logistics
- Product and batch provenance.
- Custody and handover events.
- Shipping, delivery, and condition evidence.
- Certificates, invoices, and trade-document integrity.
- Cross-organization evidence exchange.

### 4.5 AI, software, and digital infrastructure
- AI model and output evidence.
- AI agent identity, permissions, and actions.
- Software build, release, deployment, and change evidence.
- Data lineage and transformation evidence.
- Operational event and incident evidence.
- Policy evaluation and audit evidence.

### 4.6 Public sector and regulated organizations
- Digital document and record integrity.
- Inter-agency evidence exchange.
- Procurement and approval trails.
- Audit and accountability evidence.
- Time-sensitive decision and event records.

CORD does not itself confer government recognition, legal validity, certification, or regulatory compliance.

## 5. Initial profile register

| Profile | Status in repository | Intended scope |
|---|---|---|
| Luxury Asset Verification | Proposed draft documented | Watches first; jewellery, art, precious metals, vehicles, collectibles |
| Clock Verification | Proposed draft documented separately | Trusted time evidence and event ordering |
| Identity and Key Trust | Reserved; specification pending | Identity, issuer roles, authorization, key lifecycle |
| Data Provenance | Reserved; specification pending | Source, lineage, transformations, custody |
| AI Event and Agent Verification | Reserved; specification pending | AI events, model declarations, agent actions |
| Financial and Transaction Evidence | Reserved; specification pending | Transaction and settlement-related evidence |
| Real Estate Evidence | Reserved; specification pending | Property, inspection, maintenance, transfer documentation |
| Supply Chain Verification | Reserved; specification pending | Origin, custody, logistics, delivery |

This register MUST be updated as profiles are specified, implemented, tested, and independently reviewed. Status labels must distinguish documented, specified, implemented, interoperable, and production-ready work.

## 6. Common profile requirements

Every future CORD application profile MUST define, at minimum:

1. Purpose, scope, terminology, and non-goals.
2. Exact versioned schemas and required/optional fields.
3. How profile evidence is packaged and committed using CORD Core without changing Core semantics.
4. Issuer identity, signature coverage, trust anchors, key rotation, expiry, and revocation.
5. Time semantics and whether timestamps are self-declared or independently trusted.
6. Privacy, data minimization, disclosure, retention, and correction rules.
7. Threat model, abuse cases, and explicit security limitations.
8. PASS/FAIL and claim-status semantics, clearly separated from Core PASS.
9. Positive, negative, boundary, and cross-implementation test vectors.
10. Reference verifier behavior and interoperability requirements.
11. Versioning, compatibility, migration, and deprecation policy.
12. Release status and evidence required before production claims.

## 7. Commercial and deployment principles

- CORD should be usable across jurisdictions and vendors, subject to local law and deployment requirements.
- The protocol should support open independent verification and optional commercial services.
- Application profiles may be licensed, supported, or integrated commercially without making Core verification dependent on a single provider.
- Enterprise deployments may add access control, managed storage, audit dashboards, SLAs, and integration services.
- No profile may claim that cryptographic integrity alone proves physical authenticity, legal ownership, truth, regulatory compliance, or trusted time.
- Market opportunities, including international financial, luxury, real-estate, logistics, and public-sector markets, are strategic targets and not evidence of customer adoption or regulatory acceptance.

## 8. Governance and change control

This portfolio records intended scope. It does not freeze every technical detail permanently. Each profile must be developed through a versioned specification, review, test vectors, and explicit release gates.

Changes to Core require the project's Core change process. Application profiles must remain separate and MUST NOT weaken Core guarantees or introduce incompatible Core semantics.

## 9. Project-wide maturity rule

CORD capabilities MUST be labelled accurately:
- **Reserved:** use case recorded in this portfolio.
- **Documented:** profile draft exists.
- **Specified:** normative schemas and rules are complete.
- **Implemented:** reference implementation exists.
- **Tested:** published test vectors and automated tests pass.
- **Interoperable:** independent implementations agree on vectors and behavior.
- **Production-ready:** security review, operational controls, documentation, and release gates are complete.

A capability MUST NOT be promoted to a later status without the corresponding evidence.

## 10. Relationship to existing specifications

- [CORD Core Formats v0.1](FORMATS.md)
- [CORD Luxury Asset Verification Profile](LUXURY-ASSET-VERIFICATION.md)
- [CORD Clock Verification Profile](CLOCK-VERIFICATION.md)
- [Signed Receipt Extension](SIGNED-RECEIPT.md)
- [Event Chain Extension](EVENT-CHAIN.md)
