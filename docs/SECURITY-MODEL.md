# Cord Security Model

## Scope

Cord Core verifies cryptographic consistency between a bundle and a receipt according to a specified protocol version. It is an evidence-integrity mechanism.

## Security properties intended by Core

When implemented correctly and supplied with valid inputs, verification can detect changes that cause the checked hashes to differ from the receipt commitments.

## Properties Core does not establish on its own

A passing verification result does not establish:
- authorship or signer identity;
- that the declared model actually generated the output;
- trusted event time;
- truth, quality, safety, legality, or policy compliance of content;
- completeness of an event log;
- absence of omitted events;
- security of the machine that created or stored the evidence.

These require additional controls and must be represented as separate claims.

## Threats to consider

- altered bundle or receipt files;
- malformed JSON and ambiguous parsing;
- duplicate object keys;
- inconsistent canonicalization across languages;
- unsupported or downgraded protocol versions;
- weak or incorrectly encoded hashes;
- parser crashes, resource exhaustion, and oversized input;
- misleading model, policy, identity, or timestamp metadata;
- compromised signing keys in future extensions.

## Implementation requirements

- Reject malformed input rather than silently repairing it.
- Reject duplicate JSON object keys.
- Validate exact required fields and supported versions.
- Validate hash algorithm and encoding before comparison.
- Bound input sizes in hosted services.
- Keep Core verification independent of network services.
- Do not treat a successful hash comparison as proof of identity or trusted time.
- Publish test vectors for both accepted and rejected inputs.

## Future extensions

Signatures and trusted timestamps must have separate specifications covering algorithms, trust anchors, key rotation, revocation, verification time, and failure behavior. They are not implied by a Core PASS result.
