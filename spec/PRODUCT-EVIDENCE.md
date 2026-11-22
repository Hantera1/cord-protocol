# CORD Product Evidence Profile (v0.1)

**Status:** proposed application profile — draft; specification work in progress.  
**Proposed profile ID:** `org.cordprotocol.profile.product-evidence`  
**Initial focus:** batteries and industrial products.  
**Layer:** CORD Application Profile above the unchanged CORD Core.

## 1. Purpose

This profile defines a vendor-neutral evidence package for recording and independently checking integrity and consistency of product-related evidence across manufacture, supply, use, repair, refurbishment, reuse, and end-of-life handling.

It is intended to complement Digital Product Passport (DPP) services, product information systems, battery passport systems, GS1 identifiers and data carriers, conformity-document repositories, and sector-specific standards. It does not replace them.

CORD verifies that the evidence package and its declared commitments match the selected locally trusted profile. It does not establish that product claims are true or that a product complies with law.

## 2. Scope and staged coverage

The profile is designed as a general product evidence model with a battery-focused first implementation.

### Stage A — common product record
- Product, model, batch, and individual-item identifiers, with identifier scheme and issuer namespace.
- Manufacturer, economic-operator, supplier, and responsible-party assertions.
- Product category and versioned product description references.
- Component and material declarations with source references and scope.
- Links to technical documentation, declarations, certificates, test reports, and external product-passport records.
- Evidence issue, correction, supersession, and withdrawal events.

### Stage B — battery and industrial-product evidence
- Battery chemistry and declared technical attributes, with units and source.
- Capacity, voltage, mass, state-of-health, and performance observations where applicable, each with method, unit, time, and issuer.
- Cell, module, pack, and component relationships where applicable.
- Manufacturing and placing-on-market event references.
- Repair, replacement, refurbishment, repurposing, recycling, and dismantling events.
- Relevant conformity and safety document references.
- Carbon-footprint or recycled-content claims only as sourced assertions with methodology and boundary references; no automatic validation of the underlying calculation.

### Stage C — lifecycle and chain-of-custody evidence
- Transfer and handover events between identified organizations or pseudonymous party references.
- Installation, maintenance, inspection, repair, and end-of-life events.
- Evidence of data provenance and corrections.
- Optional sensor and telemetry references, without treating untrusted device readings as ground truth.

The schema MUST distinguish product model, batch, and individual physical item. A batch-level assertion MUST NOT be represented as an individually verified item-level fact.

## 3. Evidence and claim model

Every material claim SHOULD carry:
- a stable claim identifier;
- claim type and subject identifier;
- value and unit where relevant;
- issuer reference and declared issuer role;
- source evidence references;
- method or standard reference where relevant;
- declared event time and time type;
- scope (model, batch, component, or individual item);
- status such as asserted, corrected, superseded, or withdrawn.

An issuer name or role is a declaration until validated through a separate trust mechanism. A source document hash proves only that the referenced bytes match the committed digest.

## 4. Lifecycle event model

Events SHOULD be append-only and uniquely identified. An event SHOULD include:
- event identifier and event type;
- subject and affected component references;
- declared event time and time type;
- actor/organization reference and declared role;
- source evidence references;
- previous-event or sequence reference where ordering is asserted;
- correction or supersession reference where applicable.

The profile MUST distinguish event time, record-creation time, and trusted timestamp. A producer-declared timestamp is not trusted time. Missing events cannot be inferred from a valid hash chain.

## 5. Verification requirements

A conforming profile verifier is expected to:
1. Run the unchanged CORD Core verifier.
2. Resolve the exact profile ID and version from a locally pinned registry.
3. Validate manifest and package integrity according to the CORD Profile Manifest specification.
4. Validate profile evidence against the exact pinned schema.
5. Check identifier uniqueness, reference resolution, scope consistency, event relationships, and valid correction/supersession links.
6. Return separate results for Core integrity, profile package integrity, schema validity, semantic consistency, and any supported trust checks.
7. Report unsupported trust mechanisms as unsupported or indeterminate, never silently as passed.

Profile-level statuses MUST NOT imply that underlying product claims have been independently substantiated.

## 6. Trust model and explicit non-goals

This profile does not, by itself:
- prove manufacturer identity or issuer authorization;
- prove physical product identity, authenticity, safety, quality, or condition;
- prove legal ownership, possession, or custody;
- validate a certificate, test report, laboratory, or conformity assessment;
- validate sensor calibration or telemetry completeness;
- establish trusted time;
- establish regulatory compliance or satisfy every DPP data/access requirement;
- replace an official registry, product passport service, or legally mandated record.

Where stronger assurance is required, deployments need separately specified issuer signatures, trust lists, authorization rules, certificate/key lifecycle, revocation, trusted timestamping, and audit procedures.

## 7. Privacy, security, and access control

- Do not place personal data, trade secrets, security-sensitive technical details, or confidential supplier information in public evidence by default.
- Prefer stable references, controlled-access source repositories, and selective disclosure over embedding complete source documents.
- Public hashes can reveal equality or enable confirmation attacks against predictable documents; assess this risk before publication.
- Access control and lawful disclosure are deployment responsibilities and are not provided by a hash.
- Avoid globally exposing serial numbers or sensitive component identifiers where they create security or privacy risks.
- Corrections MUST be represented as new evidence events; prior commitments must not be silently rewritten.

## 8. Interoperability strategy

The profile SHOULD reuse established identifiers, data models, and sector standards rather than inventing parallel vocabularies. Each external mapping must specify:
- standard name, version, and exact field mapping;
- whether the field is copied, referenced, transformed, or omitted;
- unit and code-list handling;
- provenance and issuer requirements;
- known semantic gaps and loss of information.

A CORD package may commit to an external DPP or battery-passport export. CORD is not the authoritative DPP registry and does not guarantee that an external system accepts the package.

## 9. Initial implementation acceptance criteria

The first reference implementation is not complete until it includes:
- manifest and strict evidence JSON Schema;
- pinned registry entry and profile-engine integration;
- deterministic sample package builder;
- positive, negative, malformed-input, duplicate-ID, broken-reference, scope-mismatch, invalid-unit, and correction/supersession tests;
- explicit result semantics and documented limitations;
- at least one battery-focused sample and one general industrial-product sample;
- mapping documentation for the relevant external standards and DPP ecosystem;
- reproducible CI results.

## 10. Versioning

The profile MUST use an exact SemVer version. Breaking changes to identifiers, claim semantics, required evidence, or verification behavior require a major version increment. Additive optional fields may be considered minor changes only when the manifest/schema compatibility rules permit them. A verifier MUST NOT silently upgrade a package to a newer profile version.

## 11. Draft questions to resolve before schema freeze

1. Which identifier schemes are mandatory for the first battery/industrial pilot, and which remain optional?
2. Which battery data fields belong in the profile evidence versus references to an authoritative DPP system?
3. How should confidential supplier and battery data be selectively disclosed?
4. Which existing standards and vocabularies should be mapped first, and at which versions?
5. Which claims require issuer signatures or qualified trust services in the target deployment?
6. What is the minimal interoperable lifecycle event vocabulary for manufacture, repair, replacement, reuse, and recycling?

These questions are intentional design gates. The schema must not be frozen until mappings and trust assumptions have been reviewed.
