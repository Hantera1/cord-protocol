# Cord Core Specification v0.1

## Deterministic Verification

Given:
- input
- policy
- previous state hash

The system MUST deterministically output:

PASS | FAIL

No probabilistic acceptance is allowed.

## Policy Identity

Each policy MUST be bound to:

policy_hash = SHA256(policy_definition)

The policy hash is immutable.

## State Transition Rule

new_state_hash = SHA256(
    previous_state_hash +
    input_hash +
    policy_hash +
    result
)

If verification fails:
- state transition is rejected
- system remains unchanged