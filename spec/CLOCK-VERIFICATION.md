# CORD Clock Verification Profile (v0.1)

**Status: proposed application profile — draft; not an implemented or production-ready trusted time service.**

This profile defines how CORD evidence packages may carry and verify evidence about time sources, timestamp claims, clock synchronization, and event ordering. It is designed for use across CORD application profiles, including luxury asset records, financial transactions, AI events, supply chains, real estate records, and digital operations.

This profile MUST NOT change CORD Core v0.1 fields, canonicalization, hashing, or PASS/FAIL semantics.

## 1. The problem

Distributed systems may have clocks that drift, are misconfigured, are manipulated, or rely on different time sources. A timestamp written by an application is only a claim unless its source and trust basis are independently established.

CORD MUST distinguish:
- producer-declared event time;
- local system clock observation;
- clock synchronization status and uncertainty;
- signed receipt creation time;
- independently trusted timestamp evidence;
- logical event ordering.

These are different assertions and MUST NOT be presented as interchangeable.

## 2. Intended capabilities

A profile-aware implementation MAY record and verify:
1. A declared event time and the system that produced it.
2. A clock source identity and its trust policy.
3. Clock synchronization observations, offset, estimated uncertainty, and observation interval.
4. A cryptographically signed timestamp token from a configured Time-Stamping Authority (TSA).
5. Event ordering using sequence numbers, monotonic-clock observations, and/or a CORD event chain.
6. The validation result, trust anchor, certificate path, policy, and validation time used for timestamp verification.

## 3. Evidence concepts

The following logical evidence objects are proposed. Their exact normative schemas and test vectors are future implementation work.

| Evidence type | Purpose |
|---|---|
| `ClockObservation` | Reports a clock reading, source, host/device context, offset, uncertainty, and observation interval |
| `TimeClaim` | Records a producer-declared event time and its source |
| `TimestampTokenEvidence` | Carries or references a signed timestamp token and its message imprint |
| `ClockSyncEvidence` | Records synchronization status and relevant NTP/PTP measurements |
| `EventOrderEvidence` | Records sequence, monotonic counter/clock observations, and ordering assertions |
| `ClockVerificationReceipt` | Summarizes which time checks were performed, their inputs, trust policy, and results |

These are profile-level concepts, not additions to the Core Receipt.

## 4. Trusted timestamping

Where RFC 3161 timestamping is used, a verifier MUST validate at least:
- the timestamp token signature;
- the TSA certificate path to explicitly configured trust anchors;
- certificate validity and applicable revocation policy at the relevant validation time;
- the message imprint algorithm and digest against the exact committed data;
- the token's policy identifier and required accuracy, where policy requires them;
- nonce matching when a nonce was requested;
- token structure and critical extensions;
- algorithm acceptability under the deployment's current security policy.

A timestamp token establishes that the TSA attested to the existence of the specified message imprint by the time stated in the token, subject to the TSA's trustworthiness and policy. It does not prove that the underlying physical-world event occurred at that time.

CORD MUST NOT label a timestamp as trusted merely because a timestamp string ends in `Z`, because a server uses NTP/PTP, or because a timestamp field is signed by the event producer.

## 5. NTP and PTP clock evidence

NTP/PTP synchronization measurements can provide operational evidence about clock synchronization. They are not automatically equivalent to an independent cryptographic timestamp.

A ClockObservation or ClockSyncEvidence SHOULD record:
- protocol and version;
- source identity and source authentication mode, if any;
- observation time and measurement interval;
- measured offset and uncertainty/error bounds with units;
- synchronization state, stratum or grandmaster information where applicable;
- host/device identity or pseudonymous identifier;
- software/configuration version;
- relevant alerts, holdover state, and known limitations.

A verifier MUST report these as clock-source or synchronization assertions under a stated trust policy, not as universal proof of event time.

## 6. Event ordering

Wall-clock timestamps alone MUST NOT be relied upon to establish strict ordering across distributed systems.

Implementations SHOULD use:
- monotonic clock values for local duration/order observations;
- per-source sequence numbers;
- causality or correlation identifiers where needed;
- the CORD Event Chain extension for linked event commitments;
- externally retained or published trusted checkpoints when resistance to full-chain replacement is required.

A monotonic clock value is generally meaningful only within its originating clock domain and boot/session context. It MUST NOT be compared as a global timestamp across unrelated machines.

A hash chain without an independently retained checkpoint proves internal consistency only. It does not prove completeness or prevent replacement of the entire chain.

## 7. Verification result

A profile-aware verifier SHOULD report separate checks, including:
- Core bundle/receipt integrity;
- receipt signature validity and signer trust;
- timestamp token validity;
- TSA trust path and policy result;
- clock synchronization evidence status;
- sequence and event-chain continuity;
- external checkpoint match;
- time uncertainty and stated limitations.

The verifier MUST distinguish `PASS`, `FAIL`, and `INDETERMINATE` for profile checks where the evidence or trust configuration is insufficient. An absent trust anchor, unavailable revocation data, unsupported algorithm, missing checkpoint, or unverifiable TSA certificate MUST NOT be silently treated as success.

Core PASS retains its existing meaning and MUST NOT be upgraded to mean trusted time.

## 8. Security and operational requirements

Deployments MUST define:
- trusted TSA roots and certificate policies;
- acceptable algorithms and transition policy;
- revocation checking and historical validation policy;
- clock-source authentication and monitoring requirements;
- key custody and access controls;
- checkpoint publication/retention strategy;
- behavior during network outage, clock drift, holdover, or trust-service unavailability;
- audit retention and evidence export.

Timestamp tokens and clock evidence SHOULD be retained with sufficient context for later offline verification. Long-term validation may require archived certificates, revocation evidence, policy versions, and algorithm migration records.

## 9. Privacy

Clock evidence SHOULD avoid unnecessary personal data and precise location disclosure. Host identifiers, IP addresses, device identifiers, and operational metadata SHOULD be minimized or access-controlled.

## 10. Relationship to other CORD components

This profile is intended to work with:
- CORD Core v0.1 commitments and offline verification;
- Signed Receipt extension for signer authentication relative to a trusted key;
- Event Chain extension for event linkage and checkpoint comparison;
- application profiles such as Luxury Asset Verification.

The signed-receipt and event-chain extensions are currently experimental. Their existence does not mean trusted time verification is implemented.

## 11. Implementation roadmap and release gates

Before this profile is declared implemented or interoperable, the project MUST:
1. define normative schemas and exact timestamp-token packaging;
2. implement RFC 3161 validation with explicit trust anchors and policy;
3. define certificate path, revocation, historical validation, and algorithm policy;
4. define NTP/PTP observation schemas and semantics;
5. define clock uncertainty and failure behavior;
6. define event-order and checkpoint rules;
7. publish valid, invalid, expired, revoked, unsupported, and boundary test vectors;
8. implement a reference verifier and independent interoperability tests;
9. complete threat modelling and independent security review.

**Current status:** proposed profile draft only. No trusted timestamp authority, NTP/PTP monitoring service, global clock oracle, or production time-certification service is implied by this document.
