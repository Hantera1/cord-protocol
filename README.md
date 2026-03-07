# Cord

**Cord** is a minimal protocol for cryptographically verifiable AI events.

It provides a simple and deterministic way to verify that an AI-generated output has not been modified after generation.

Cord allows any independent system to verify AI outputs using a small evidence package consisting of a **bundle** and a **receipt**.

Verification can be performed **offline**, without trusting the system that originally produced the output.

---

## Why Cord

AI systems are increasingly used in environments where **verification, transparency, and auditability** are important.

However, most AI outputs today cannot be independently verified after generation.

Typical problems include:

- modified logs
- unverifiable outputs
- platform-dependent audit systems
- lack of standard formats for AI event verification

Cord introduces a minimal, deterministic format that enables **independent verification of AI-generated outputs**.

---

## Core Idea

Cord represents an AI event using two files:

- `bundle.json`
- `receipt.json`

```
AI event
   ↓
bundle.json
   ↓
receipt.json
   ↓
verification
```

The bundle describes the AI event.

The receipt binds the bundle to cryptographic hashes.

A verifier can then independently confirm the integrity of the event.

Verification returns a deterministic result:

PASS

or

FAIL

---

## Example Bundle

```json
{
  "spec_version": "0.1",
  "model_id": "demo-model",
  "timestamp": "2026-03-06T12:00:00Z",
  "policy_id": "cord-output-v0.1",
  "input_hash": "1111111111111111111111111111111111111111111111111111111111111111",
  "output_hash": "2222222222222222222222222222222222222222222222222222222222222222"
}
```

---

## Verification

Verification checks that:

1. the bundle structure is valid  
2. the bundle hash matches the receipt  
3. the bundle contents have not been modified  

If any verification step fails, the event is considered invalid.

Cord verification is designed to be:

- deterministic
- reproducible
- independent of any platform

---

## Repository Structure

```
spec/          Cord protocol specification
test-vectors/  deterministic verification examples
verifier/      reference verifier implementation
reference/     supporting documentation
```

---

## Design Goals

Cord is designed to be:

- minimal
- deterministic
- implementation-neutral
- verifiable offline

The protocol intentionally keeps the core format small to reduce ambiguity and improve cross-implementation compatibility.

---

## Status

Cord is currently an **experimental protocol draft (v0.1)**.

The specification may evolve as implementations and verification tools mature.

---

## License

See the `LICENSE` file for details.
---

## Creator

Cord was originally created by:

GitHub: https://github.com/Hantera1

This repository serves as the original reference implementation and specification of the Cord protocol.
---

## Support

If you find Cord useful and want to support its development, you may send a voluntary contribution.

ETH: 0x3d6344fc57ba0039429bdf78dd7ca734c42195b9

BTC: bc1q8qtrmfmq53smfhzp8s6p9er080z66zvzae9f38

Contributions are optional and help support continued research and development of the Cord protocol.