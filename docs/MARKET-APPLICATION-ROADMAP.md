# CORD Market Application Roadmap

**Status:** Strategy and requirements baseline; not an implementation or compliance claim.  
**Target architecture:** unchanged CORD Core + versioned Application Profiles + independent local verification.

## 1. Purpose

Develop CORD as a vendor-neutral evidence integrity and verification protocol that can be adopted across industries. CORD should complement existing systems and standards rather than replace product-passport platforms, AI governance systems, SIEM/forensic tools, C2PA, SBOM formats, construction information systems, asset registries, or logistics platforms.

The protocol records and verifies evidence commitments and defined consistency rules. A CORD PASS must never be presented as proof that an underlying claim is true, that a physical object is authentic, that a party legally owns an asset, or that a timestamp is trusted unless a separate, explicitly specified trust mechanism establishes that property.

## 2. Shared architecture

1. **CORD Core:** minimal, deterministic, stable, offline-verifiable. No industry-specific fields are added to Core.
2. **Application Profile Manifest:** identifies a profile, version, Core compatibility, schemas, required package files, and verification requirements.
3. **Profile Engine:** resolves only locally pinned profiles; validates package structure, raw-byte integrity commitments, schemas, and profile-specific consistency rules.
4. **Trust adapters:** separately specified mechanisms for signatures, issuer authorization, trusted timestamps, revocation, external checkpoints, and key lifecycle. A profile must state which are required, optional, or unsupported.
5. **SDK / CLI / API:** reusable interfaces that produce machine-readable results and human-readable verification reports.
6. **Interoperability suite:** deterministic test vectors, negative cases, cross-implementation fixtures, version compatibility tests, and documented limitations.
7. **Privacy boundary:** minimize personal and commercially sensitive data. Prefer references and selective disclosure; do not publish secrets or confidential source evidence in public metadata.

## 3. Market application areas

### A. Product and Battery Evidence
**Profile ID proposal:** `org.cordprotocol.profile.product-evidence`

Evidence scope: product identity references, manufacturer and supplier assertions, component/material declarations, battery attributes, lifecycle events, repair/replacement, recycling/reuse, conformity-document references, and custody/transfer events.

Boundary: CORD is not a Digital Product Passport registry, data carrier, regulatory filing system, or proof of regulatory compliance. It can commit to and verify evidence packages associated with an external product passport.

Initial vertical: batteries and industrial products. Design for extension to other product categories without creating a separate Core format.

### B. AI Governance Evidence
**Profile ID proposal:** `org.cordprotocol.profile.ai-evidence`

Evidence scope: model and deployment references, input/output commitments, policy/version references, event sequence, human oversight events, evaluation results, incident references, and log retention/export evidence.

Boundary: a valid evidence package does not prove that a model is safe, fair, lawful, or correctly operated. Avoid placing raw prompts, personal data, secrets, or proprietary model content in public packages.

### C. Cyber Incident Evidence
**Profile ID proposal:** `org.cordprotocol.profile.incident-evidence`

Evidence scope: incident identifiers, evidence item hashes, acquisition method, collector/tool versions, event chronology, custody transfers, analysis references, containment/recovery actions, and export manifests.

Boundary: CORD does not determine whether an incident occurred, attribute an attacker, validate forensic methodology, or replace chain-of-custody procedures and expert testimony.

### D. Media Provenance Evidence
**Profile ID proposal:** `org.cordprotocol.profile.media-provenance`

Evidence scope: media asset commitments, source/capture assertions, editing/transcoding events, tool/version references, publication and transfer events, and links to established provenance credentials where available.

Boundary: CORD does not identify depicted people, establish that a scene is real, or replace C2PA/content credentials. Integration should preserve and reference existing provenance standards.

### E. Software Supply Chain Evidence
**Profile ID proposal:** `org.cordprotocol.profile.software-supply-chain`

Evidence scope: source revision references, build inputs, build environment, builder identity assertions, SBOM references, artifact digests, test results, signing/attestation references, release and deployment events.

Boundary: a matching digest does not prove that source code is safe, dependencies are non-malicious, or a build process is trustworthy. Integrate with established SBOM and build-provenance formats rather than redefining them.

### F. Construction and Property Evidence
**Profile ID proposal:** `org.cordprotocol.profile.built-environment`

Evidence scope: product/material batches, declarations and certificates, inspections, installation events, design/revision references, maintenance, defects, remediation, and handover packages.

Boundary: CORD does not certify building-code compliance, engineering adequacy, title, condition, or valuation. Sensitive building/security information must be access-controlled.

### G. Luxury Asset Evidence
**Profile ID:** existing draft `org.cordprotocol.profile.luxury-asset`

Evidence scope: asset identity references, condition, components, service, examination, custody, transfers, valuation assertions, and disputes.

Boundary: cryptographic integrity is not physical authentication, legal ownership, custody, or a valuation guarantee. Keep this profile aligned with its existing draft and Profile Engine implementation.

### H. Logistics and Cold Chain Evidence
**Profile ID proposal:** `org.cordprotocol.profile.logistics-evidence`

Evidence scope: shipment and consignment references, handovers, route milestones, sensor/device references, temperature/humidity observations, excursions, calibration evidence, delivery and exception records.

Boundary: CORD does not prove sensor accuracy, physical presence, completeness of telemetry, or delivery unless the relevant devices, issuers, and trust sources are separately validated.

## 4. Delivery sequence

### Foundation — current
- Complete review of Profile Engine v0.1 PR and its security boundaries.
- Establish common profile authoring rules and conformance test requirements.
- Define a common evidence envelope and verification report contract without changing Core.
- Define trust-adapter interfaces and explicit unsupported/indeterminate outcomes.

### Wave 1 — first implementation profiles
1. Product & Battery Evidence.
2. AI Governance Evidence.
3. Cyber Incident Evidence.

These have strong regulatory or operational drivers and reuse the common evidence, event, and integrity model.

### Wave 2 — interoperability-led profiles
4. Software Supply Chain Evidence.
5. Media Provenance Evidence.
6. Logistics & Cold Chain Evidence.

Prioritize standards mapping and adapters over duplicating established formats.

### Wave 3 — domain expansion
7. Construction & Property Evidence.
8. Extend Luxury Asset Evidence from its existing draft and implementation based on pilot feedback.

The order is a proposed engineering sequence, not a claim about measured total addressable market.

## 5. Definition of done for each profile

A profile is not considered implemented merely because a specification or JSON Schema exists. Each profile must have:

- A versioned specification and manifest with a stable profile ID.
- Strict JSON Schemas and documented canonical/raw-byte rules.
- Positive, negative, boundary, malformed-input, and size-limit test vectors.
- A reproducible example package and CLI verification.
- Explicit semantics for PASS, FAIL, UNSUPPORTED, and INDETERMINATE.
- A threat model, privacy classification, trust assumptions, and known limitations.
- Mapping to relevant external standards and clear non-replacement boundaries.
- At least two independent implementations or an interoperability test plan before claiming interoperability.
- Review of backwards compatibility and profile versioning.
- No unsupported claims of legal, regulatory, authenticity, safety, or compliance certification.

## 6. Shared platform milestones

1. Profile Engine v0.1 review and stabilization.
2. Common verification result/report schema.
3. Profile authoring and conformance test harness.
4. Product Evidence v0.1 draft and fixtures.
5. SDK packaging and stable CLI interface.
6. Trust-adapter design for issuer signatures, trusted timestamps, revocation, and key lifecycle.
7. Independent second implementation and interoperability testing.
8. Pilot integrations with existing systems; no central CORD registry required for offline verification.

## 7. Commercial direction

Keep the protocol and verification format vendor-neutral. Potential commercial layers include hosted verification, enterprise policy and profile management, SDK/API support, integrations, managed trust services, and industry-specific workflow products. Do not make the public Core dependent on a CORD-hosted service.

## 8. Release and security gates

No profile or platform release may claim production readiness solely because unit tests pass. Production claims require threat modelling, security review, key management and revocation design, privacy review, independent interoperability evidence, operational monitoring, incident response, documented support policy, and versioned release artifacts.

## 9. Current repository status

- CORD Core v0.1 remains the stable minimal layer.
- Application Profile Manifest and draft Luxury Asset / Clock profiles are documented.
- Profile Engine v0.1 is proposed in PR #13 and remains separate from `main` until reviewed and merged.
- This roadmap is a planning baseline only. It does not implement the eight profiles or certify compliance with any regulation or external standard.
