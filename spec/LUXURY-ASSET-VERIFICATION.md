# CORD Luxury Asset Verification Profile (v0.1)

**Status: draft application profile; initial reference schema and validator are implemented on PR #13. Not production-ready.**

This profile defines how CORD may be applied to the creation, exchange, and independent verification of evidence about valuable physical assets. It is an application profile above CORD Core. It MUST NOT change Core v0.1 bundle fields, receipt fields, canonicalization, hash semantics, or PASS/FAIL meaning.

## 1. Purpose and scope

The profile is intended for assets that may be authenticated, documented, serviced, transferred, insured, appraised, or resold across organizations and jurisdictions.

Initial use case: luxury watches and collectible timepieces.

The same profile model is intended to support:
- watches and clocks;
- jewellery, diamonds, and gemstones;
- precious metals;
- art, antiques, and collectible objects;
- luxury and collectible vehicles;
- other individually identifiable high-value physical assets.

The profile records verifiable evidence and claims about an asset. CORD is not itself an authentication laboratory, title registry, appraisal service, manufacturer database, or legal authority.

## 2. Design principles

1. **Core remains small and stable.** Profile data is carried as application evidence and committed to using existing CORD mechanisms. No profile-specific fields are added to the Core v0.1 schemas.
2. **Evidence is not truth.** A valid hash or signature proves integrity or signer control under the applicable trust model; it does not prove that a physical-world claim is true.
3. **Claims identify their source.** Every material claim SHOULD identify the issuer, method, time, scope, and supporting evidence.
4. **Independent verification.** A verifier SHOULD be able to validate the evidence package without depending on the original marketplace or seller, subject to required trust material.
5. **Privacy by design.** Public verification MUST NOT disclose personal data or confidential transaction details by default.
6. **Append-only history.** Corrections and later findings SHOULD be added as new evidence events. Existing evidence MUST NOT be silently overwritten.
7. **Interoperability.** Identifiers, evidence types, issuer roles, and status values require documented schemas and test vectors before implementation.

## 3. Asset identity

The profile introduces the conceptual identifier `AssetID`.

An AssetID identifies a record for an individual asset within an issuing namespace. It is not, by itself, proof that the physical object is genuine, unique, or lawfully owned.

An asset record MAY include:
- profile identifier and version;
- AssetID and issuer namespace;
- asset category and descriptive attributes;
- manufacturer, brand, model, reference/model number, and approximate production period where known;
- manufacturer serial number or other physical identifiers, with access restrictions where appropriate;
- photographs and media evidence, represented by cryptographic digests and separately stored content;
- identifier method and confidence/limitations;
- links to predecessor, replacement, or corrected records where an identifier is disputed or changed.

Serial numbers and other sensitive identifiers SHOULD be access-controlled. A public QR code SHOULD resolve to a privacy-safe verification view, not expose the full record.

## 4. Evidence types

The profile defines the following logical evidence types. These names are profile concepts; concrete JSON schemas and normative validation rules are future implementation work.

| Evidence type | Intended purpose |
|---|---|
| `AssetRegistrationEvidence` | Establish that an issuer created an asset record and what observations were recorded |
| `AuthenticityEvidence` | Record an examination or manufacturer/authorized-source confirmation |
| `ConditionEvidence` | Record condition, defects, completeness, and inspection scope |
| `ComponentEvidence` | Record observed components, replacements, and originality claims |
| `ServiceEvidence` | Record service, repair, parts, and service-provider assertions |
| `OwnershipEvidence` | Record a party's signed assertion of ownership or authority |
| `TransferEvidence` | Record a proposed or completed transfer and its participants' attestations |
| `ValuationEvidence` | Record an appraisal, valuation method, date, currency, and appraiser |
| `CustodyEvidence` | Record custody or possession events without equating custody with ownership |
| `ClockEvidence` | Reference independently verifiable time evidence for an event |
| `DisputeEvidence` | Record a challenge, correction, withdrawal, or unresolved conflict |

Evidence SHOULD reference the asset record and any prior evidence it relies on. Evidence SHOULD include an issuer identity/key reference, evidence type and version, creation time, method, scope, and digest(s) of supporting material.

## 5. Authenticity and examination

Authenticity is an assertion made by an identified source using a stated method. The profile MUST distinguish at least:
- manufacturer or brand confirmation;
- examination by a manufacturer-authorized service provider;
- examination by an independent qualified specialist;
- documentary or provenance-based assessment;
- seller-declared or unverified assertion.

A verifier MUST display who made the claim and its scope. A CORD PASS MUST NOT be rendered as “CORD guarantees authentic”. A signature can authenticate the source of a statement relative to a trusted key; it cannot independently authenticate the physical object.

For watches, examination evidence MAY describe the case, movement, dial, hands, bracelet, serial/reference markings, replaced components, and whether the examination was invasive. It SHOULD state which parts were not inspected and whether the watch was opened.

## 6. Ownership, custody, and transfer

The profile MUST keep these concepts separate:
- **ownership assertion:** a party asserts that it owns or is authorized to transfer the asset;
- **custody:** a party physically holds or stores the asset;
- **possession:** a party has practical control of the asset;
- **transfer record:** parties attest to a transaction or handover.

A TransferEvidence record SHOULD identify the asset, transfer event, relevant parties or privacy-preserving party references, each party's signed consent/attestation, event status, and references to supporting documents where appropriate.

CORD records evidence of assertions and attestations. It does not determine legal title, resolve competing claims, verify sanctions/KYC status, or replace applicable contracts, registries, or law. A transfer MUST NOT be represented as legally conclusive merely because its CORD evidence verifies.

The design SHOULD support private or selectively disclosed identity information. Public records SHOULD use pseudonymous references or disclose only the minimum needed to verify a particular claim.

## 7. Time, ordering, and history

The profile MAY reference:
- a producer-declared event time;
- a signed receipt time;
- an independently trusted timestamp token;
- an event-chain sequence and externally retained checkpoint.

These are distinct assurances and MUST be labelled separately. A producer-declared timestamp is not trusted time. An event hash chain can detect changes or reordering relative to a trusted checkpoint, but cannot by itself prevent full-chain replacement.

Trusted timestamping is a separate CORD extension. Implementations MUST NOT claim RFC 3161 trusted time unless the timestamp token, certificate path, trust policy, and validation time have actually been checked against configured trust anchors.

## 8. Verification result and user presentation

A profile-aware verifier SHOULD report separate outcomes rather than a single ambiguous authenticity badge:
- evidence package integrity;
- signature validity and signer trust status;
- timestamp validity and trust status;
- chain continuity/checkpoint status;
- issuer role/qualification status, if configured;
- claim status (asserted, corroborated, disputed, withdrawn, expired, unknown);
- missing evidence and scope limitations.

Core PASS retains its existing meaning: the supplied Core bundle and receipt satisfy the Core checks. Profile checks MUST be reported separately. A profile-level result MUST NOT silently redefine Core PASS.

User interfaces SHOULD avoid binary “genuine” claims unless a named, trusted authority has made that exact determination and the verifier explains the basis and limits.

## 9. Trust, keys, and issuer governance

Deployments need an explicit trust policy defining:
- accepted issuer identities and roles;
- how public keys are provisioned and bound to organizations or individuals;
- key rotation, expiry, compromise, and revocation;
- examiner qualification and authorization criteria;
- accepted timestamp authorities and trust anchors;
- dispute, correction, and withdrawal handling.

A `key_id` supplied in an evidence package is only a lookup hint. A key supplied by the same untrusted source as the evidence MUST NOT become trusted solely because it verifies a signature.

## 10. Data protection and security

Implementations SHOULD minimize personal data, separate public and private views, encrypt sensitive evidence at rest and in transit, enforce role-based access, log access to restricted records, and define retention/deletion policies.

Hashes of predictable personal data or serial numbers can enable guessing attacks. Sensitive fields SHOULD use access-controlled evidence or appropriately designed commitments rather than publishing raw values or unsalted hashes.

Physical labels, QR codes, NFC tags, and embedded identifiers can be copied or moved. They are pointers or identifiers, not tamper-proof proof of the object's identity. High-assurance deployments SHOULD bind records to physical inspection and appropriate anti-tamper or secure-tag processes, while documenting their limitations.

## 11. Initial watch workflow

A reference deployment may follow this sequence:

1. An authorized registrar creates an asset record and AssetID.
2. A qualified examiner inspects the watch and records the examination scope and findings.
3. The examiner issues signed AuthenticityEvidence, or records a clearly labelled inconclusive result.
4. Condition, components, and available service records are added as separate evidence.
5. CORD commitments, signatures, and (when available) trusted timestamp evidence protect the evidence package.
6. A seller and buyer complete a transfer workflow with appropriate identity, consent, and legal checks outside the protocol.
7. A TransferEvidence record is added; prior evidence remains available subject to privacy and retention policy.
8. A later service, inspection, dispute, or resale adds new evidence rather than silently rewriting history.

## 12. Relationship to existing CORD components

This profile is designed to build on, not replace:
- CORD Core bundle and receipt formats;
- CORD canonicalization and hashing;
- the experimental signed-receipt extension;
- the experimental event-chain extension;
- future trusted timestamp, identity, provenance, and policy extensions.

The profile does not assume that experimental extensions are production-ready. Implementers MUST check the status and limitations of each extension they use.

## 13. Implementation roadmap and release gates

This document reserves and describes the application area. It does not claim that the profile is implemented.

Before a profile implementation is declared interoperable, the project MUST:
1. define normative schemas and versioning for each evidence type;
2. define a profile manifest and the exact relationship between profile payloads and Core evidence packages;
3. define signature coverage, issuer trust policy, revocation, and key lifecycle;
4. define trusted-time integration and failure behavior;
5. define privacy-preserving identifiers and disclosure rules;
6. publish positive and negative test vectors;
7. implement a reference verifier and independent interoperability tests;
8. complete threat modelling and independent security review.

**Current status:** draft profile schema and reference consistency validator are implemented on PR #13. No production asset registry, authentication network, trusted timestamp service, legal-title service, or independent interoperable watch-verification implementation is implied.
