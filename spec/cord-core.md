# Cord Core Specification v0.1

## Overview

Cord is a minimal verification layer for AI events.

Cord proves that a specific AI event has not been altered after creation.

A Cord event is defined by:

- model_id
- timestamp
- policy_id
- input_hash
- output_hash

The Cord bundle is hashed deterministically and bound to a receipt.

---

## Cord Event Model

A valid Cord event MUST include:

- `spec_version`
- `model_id`
- `timestamp`
- `policy_id`
- `input_hash`
- `output_hash`

Example:

```json
{
  "spec_version": "0.1",
  "model_id": "demo-model",
  "timestamp": "2026-03-06T12:00:00Z",
  "policy_id": "cord-output-v0.1",
  "input_hash": "1111111111111111111111111111111111111111111111111111111111111111",
  "output_hash": "2222222222222222222222222222222222222222222222222222222222222222"
}