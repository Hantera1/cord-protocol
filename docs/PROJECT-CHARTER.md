# CORD Architecture Charter

**Document status:** Governing architecture charter — v1.0 draft  
**Project:** CORD Protocol  
**Origin:** Hantera / KentPH  
**Scope:** Project-wide architecture, product direction, governance, compatibility, and maturity rules.

This charter records the enduring architectural direction of CORD. It is intended to prevent scope drift, protect the stable Core, and give future contributors and implementers a common reference. It does not claim that every capability described here has been specified, implemented, certified, or deployed.

## 1. Mission

CORD is an open, vendor-neutral protocol for creating, packaging, exchanging, and independently verifying cryptographic evidence about digital events, data, decisions, transactions, and physical assets.

CORD's purpose is to make evidence more portable, inspectable, tamper-evident, and independently verifiable across organizations, software systems, industries, and jurisdictions.

CORD is an evidence protocol and verification architecture. It is not itself an oracle of truth, a legal authority, a certification body, an identity provider, a payment network, or an authentication laboratory.

## 2. Long-term vision

CORD is intended to become a reusable verification foundation with:
- a small, stable, openly specified Core;
- separately versioned trust and evidence extensions;
- industry-specific application profiles;
- independent implementations and interoperable test vectors;
- SDKs, APIs, and adapters for common systems;
- optional commercial services that add operational convenience without controlling the protocol.

The same verification foundation should be reusable across AI, software, finance, luxury assets, physical goods, real estate, logistics, documents, and public-sector evidence workflows.

## 3. Foundational principles

1. **Evidence before claims.** Every result must state exactly what evidence was checked and what it does not establish.
2. **Open specification.** Normative formats and verification rules must be publicly inspectable.
3. **Vendor neutrality.** No single cloud, AI provider, database, hardware vendor, or CORD-operated service may be mandatory for Core verification.
4. **Offline verifiability.** A complete evidence package must be independently verifiable without calling a CORD server.
5. **Small stable Core.** Industry-specific requirements belong in versioned profiles, not ad hoc Core changes.
6. **Interoperability first.** Normative behavior requires deterministic test vectors and independent implementation checks.
7. **Cryptographic agility.** Algorithms and trust policies must be explicitly identified and maintainable as security requirements evolve.
8. **Privacy by design.** Evidence should minimize personal and commercially sensitive data and support controlled disclosure.
9. **Explicit trust.** Trust anchors, issuer roles, key status, timestamp authorities, and policy assumptions must be visible and configurable.
10. **No overclaiming.** A cryptographic PASS must never be represented as proof of truth, legality, physical authenticity, ownership, or regulatory compliance unless separate evidence and authority establish that claim.
11. **Backward compatibility.** Published versions, schemas, and test vectors remain identifiable and reproducible.
12. **Sustainable openness.** Commercial services may support the project, but may not buy privileged verification outcomes or exclusive control over the protocol.

## 4. Architecture and layers

### 4.1 CORD Core

The Core defines the minimum interoperable evidence package and deterministic integrity verification. Core responsibilities include:
- version identification;
- strict bundle and receipt formats;
- canonicalization rules;
- cryptographic digest commitments;
- deterministic validation and error behavior;
- offline verification.

Core v0.1 currently has its own narrowly defined semantics. A Core PASS means only that the supported Core format and cryptographic commitments validate as specified. It does not imply trusted identity, trusted time, truth, authorization, provenance, or completeness.

### 4.2 Trust and evidence extensions

Extensions add separately specified evidence or trust mechanisms, potentially including:
- signed receipts and issuer identity;
- key binding, key rotation, expiry, and revocation;
- trusted timestamp tokens and clock evidence;
- event chains and externally retained checkpoints;
- provenance and lineage;
- policy and authorization attestations;
- selective disclosure and privacy mechanisms.

Each extension MUST define its own version, schema, cryptographic coverage, trust model, failure behavior, threat model, and test vectors. Experimental extensions MUST be labelled as experimental.

### 4.3 Application profiles

Application profiles define how CORD is used in a specific industry or workflow. A profile may define:
- domain entities and evidence types;
- required and optional claims;
- issuer roles and qualification requirements;
- profile-specific verification outcomes;
- privacy and disclosure rules;
- mappings to relevant external standards;
- workflow and interoperability requirements.

Profiles MUST build on Core and applicable extensions. They MUST NOT silently change Core fields, canonicalization, digest semantics, or the meaning of Core PASS.

### 4.4 SDKs, adapters, and integrations

SDKs and adapters may support programming languages, AI frameworks, enterprise systems, asset registries, document systems, logistics platforms, and verification workflows.

An SDK is an implementation convenience, not a separate source of protocol truth. Conformance is determined by normative specifications and test vectors.



### 4.6 Profile manifest and common verification model

Every application profile MUST be identified by an immutable profile identifier and an exact version. A machine-readable manifest declares profile identity, version, Core compatibility, normative specification, evidence schema, and verification requirements. Profile-aware verification MUST be layered on top of Core verification and MUST NOT alter Core v0.1 semantics. The proposed manifest and staged verifier model are defined in [CORD Application Profile Manifest and Verification Model](../spec/PROFILE-MANIFEST.md).

### 4.5 Optional services

Optional services may include hosted verification, managed evidence storage, organization administration, dashboards, key-management integrations, audit exports, support, and service-level agreements.

These services MUST remain optional. They MUST NOT be required to verify a complete Core evidence package. Their own security, availability, privacy, retention, and data-export obligations must be documented.

## 5. Reserved application portfolio

The following areas are part of CORD's recorded strategic scope. Reservation means that the use case is included in the architecture direction; it does not mean a production implementation exists.

### 5.1 AI and autonomous systems
- AI input/output and execution evidence.
- Model and policy declarations.
- AI agent identity, authority, tool calls, approvals, and actions.
- Human review and intervention evidence.
- AI system audit and incident records.

### 5.2 Software and digital infrastructure
- Software build and release provenance.
- Deployment, configuration, and change evidence.
- Data integrity and lineage.
- System events, incidents, and operational audit trails.
- Machine-to-machine evidence exchange.

### 5.3 Clock and time verification
- Producer-declared event time.
- Clock source and synchronization observations.
- Trusted timestamp tokens, including RFC 3161 where supported.
- Event ordering, sequence evidence, and external checkpoints.
- Time uncertainty and historical validation.

### 5.4 Identity and key trust
- Issuer and organization identity assertions.
- Key-to-identity bindings.
- Roles, authorization, delegation, and approvals.
- Key lifecycle, rotation, expiry, and revocation.

### 5.5 High-value assets and luxury commerce
- Watches and collectible timepieces.
- Jewellery, diamonds, gemstones, and precious metals.
- Art, antiques, design objects, and collectibles.
- Luxury, classic, and collectible vehicles.
- Authenticity examination, condition, components, service, custody, ownership assertions, transfers, and valuation evidence.

### 5.6 Finance and transactions
- Transaction instructions and approvals.
- Trade and settlement-related evidence.
- Counterparty attestations and audit trails.
- Evidence supporting high-value asset transactions.

CORD does not itself provide banking, payment clearing, custody, investment advice, AML/KYC decisions, or regulatory authorization.

### 5.7 Real estate and built assets
- Property and document identity evidence.
- Inspections, condition, maintenance, and renovation records.
- Building component and equipment histories.
- Contractor and professional attestations.
- Transaction, handover, and lifecycle records.

CORD does not replace land registries, legal title records, permits, conveyancing, or professional inspections.

### 5.8 Supply chain, trade, and logistics
- Product and batch provenance.
- Custody and handover events.
- Shipping, delivery, and condition evidence.
- Certificates, invoices, and trade-document integrity.
- Cross-organization evidence exchange.

### 5.9 Documents, public sector, and regulated workflows
- Document integrity, issuer signatures, and revision history.
- Procurement and approval trails.
- Inter-agency evidence exchange.
- Audit, accountability, and records-management evidence.
- Time-sensitive decisions and event records.

CORD does not itself confer legal validity, government recognition, certification, or regulatory compliance.

The maintained application register is [CORD Application Portfolio and Reserved Use Cases](../spec/APPLICATION-PORTFOLIO.md).

## 6. Evidence semantics and trust boundaries

CORD implementations and profiles MUST distinguish, where relevant:
- integrity from authenticity;
- authenticity claims from independent examination;
- identity from control of a cryptographic key;
- authorization from identity;
- ownership from possession and custody;
- declared event time from independently trusted timestamping;
- event sequence from proof of completeness;
- a source assertion from an independently verified fact;
- technical conformance from legal or regulatory compliance.

A hash proves a relationship between data and a digest under the specified algorithm; it does not prove that the data is true. A signature proves control of a key over signed bytes, subject to key trust; it does not automatically prove the signer's civil identity or authority. A timestamp token proves a TSA's attestation under its policy; it does not prove the underlying real-world event occurred at that time.

Physical identifiers, QR codes, NFC tags, serial numbers, photographs, and certificates may be copied, moved, forged, or misrepresented. Profiles MUST describe how physical-world claims are examined and what evidence supports them.

## 7. Security and privacy requirements

Every normative extension and application profile MUST include:
- a threat model and abuse cases;
- cryptographic algorithms and parameters;
- trust-anchor and key-management assumptions;
- signature coverage and canonicalization rules;
- expiry, revocation, and historical-validation behavior where applicable;
- failure and indeterminate-result semantics;
- data minimization and privacy requirements;
- retention, export, correction, and deletion considerations;
- test vectors for valid, invalid, and boundary cases.

Sensitive personal, financial, location, asset, and business information SHOULD be kept out of public evidence packages unless necessary. Hashing predictable personal data is not sufficient anonymization. Profiles SHOULD support access-controlled evidence and selective disclosure where feasible.

## 8. Verification result model

CORD MUST keep Core integrity results separate from extension and profile results.

A verifier SHOULD report each relevant check independently, for example:
- Core format and integrity;
- signature cryptographic validity;
- signer identity and trust status;
- authorization and issuer qualification;
- timestamp validity and trust policy;
- event-chain continuity and checkpoint match;
- profile schema and claim requirements;
- evidence completeness against the profile's declared scope.

Where evidence or trust configuration is insufficient, the verifier MUST be able to report an indeterminate or unsupported result rather than silently treating missing information as success.

No global green status may conceal a failed or unverified critical check.

## 9. Versioning and compatibility

- Every normative specification MUST have a stable identifier and explicit version.
- Core, extensions, and application profiles MUST be versioned independently.
- Unsupported major versions MUST be rejected or reported as unsupported; implementations MUST NOT guess semantics.
- Minor and patch compatibility rules MUST be stated by each specification.
- Published schemas, test vectors, and release artifacts MUST remain available and immutable by version.
- Breaking changes require a new major version or a clearly documented migration path.
- Deprecation MUST include notice, rationale, affected versions, and a migration recommendation.
- Implementations MUST identify the exact specification versions they support.

## 10. Governance and change control

This charter is the project-wide architectural baseline. It is stable by default, but not immutable.

A proposed change to this charter or to normative Core behavior SHOULD include:
1. problem statement and motivation;
2. scope and affected specifications;
3. alternatives and compatibility impact;
4. security and privacy analysis;
5. proposed normative wording;
6. test-vector and implementation impact;
7. migration and release plan.

Significant changes SHOULD be discussed publicly in the repository before adoption. Accepted changes MUST be committed with a clear rationale and version history. No single application profile may unilaterally redefine the Core.

## 11. Commercial model and ecosystem

CORD is intended to support both open protocol adoption and sustainable commercial activity.

Potential commercial offerings include:
- enterprise integration and deployment;
- managed evidence storage and verification operations;
- organization and issuer administration;
- profile-specific workflows and industry adapters;
- professional support, maintenance, and SLAs;
- audit dashboards and reporting;
- hardware, identity, timestamp, and registry integrations.

Commercial services MUST NOT make Core verification exclusive, conceal protocol rules, manipulate verification results, or imply that payment purchases trust. Open specifications and independent verification remain central.

The project may collaborate with standards bodies, industry groups, manufacturers, laboratories, auditors, service providers, and public institutions. Such relationships MUST be described accurately; no partnership, endorsement, certification, or recognition may be claimed without evidence.

## 12. Maturity and release language

Every CORD capability MUST use accurate maturity labels:

- **Reserved:** use case recorded in the application portfolio.
- **Documented:** explanatory or draft profile document exists.
- **Specified:** normative schemas, rules, and semantics are complete.
- **Implemented:** a reference implementation exists.
- **Tested:** automated tests and published test vectors pass.
- **Interoperable:** independent implementations pass shared conformance vectors.
- **Reviewed:** security and protocol review has been completed and documented.
- **Production-ready:** release gates, operational controls, documentation, support, and risk treatment are complete.

These labels are cumulative only where the required evidence exists. A draft document is not an implementation. A passing local test suite is not independent interoperability. A production deployment is not a certification.

## 13. Roadmap priorities

The intended order of work is:

1. Stabilize and independently validate Core v0.1 before declaring it stable.
2. Maintain precise specifications, reproducible test vectors, and a reliable reference verifier.
3. Complete trust foundations: signatures, key lifecycle, trusted timestamps, and checkpoints.
4. Develop initial application profiles, beginning with Clock Verification and Luxury Asset Verification.
5. Build profile-aware verification and independent interoperability implementations.
6. Expand into identity, provenance, AI agents, finance, real estate, supply chain, and public-sector workflows.
7. Add SDKs, adapters, and optional commercial services without introducing mandatory central dependencies.
8. Complete independent security review and operational readiness before production claims.

The detailed implementation status and exit criteria are maintained in the [CORD Roadmap](ROADMAP.md).

## 14. Relationship to normative documents

This charter sets project direction. Technical conformance is determined by the relevant versioned normative specification, not by this charter alone.

Key documents:
- [CORD Core Formats](../spec/FORMATS.md)
- [CORD Application Portfolio](../spec/APPLICATION-PORTFOLIO.md)
- [CORD Clock Verification Profile](../spec/CLOCK-VERIFICATION.md)
- [CORD Luxury Asset Verification Profile](../spec/LUXURY-ASSET-VERIFICATION.md)
- [Signed Receipt Extension](../spec/SIGNED-RECEIPT.md)
- [Event Chain Extension](../spec/EVENT-CHAIN.md)
- [CORD Security Model](SECURITY-MODEL.md)

## 15. Current status statement

CORD Core v0.1 and several extensions/profiles are at draft or experimental maturity as identified in their individual documents. This charter records the intended long-term architecture; it does not upgrade the implementation status of any component.

**CORD's architectural commitment:** one open, stable verification foundation; separately versioned trust mechanisms and application profiles; independent verification; explicit trust boundaries; and no claims beyond the evidence.
