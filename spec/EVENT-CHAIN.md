# Cord Event Chain Extension (experimental)

## Purpose and limits

This extension links receipt references into an ordered hash chain. It detects
modified records, broken links, and reordering relative to a trusted chain
head. It does NOT prevent an attacker from rewriting the entire chain. A
consumer that needs tamper evidence MUST retain or externally publish a trusted
checkpoint (the final `event_hash`) and protect that checkpoint independently.

## Event record

Each record is a JSON object with exactly these string fields:

- `spec_version`: `0.1`
- `sequence`: zero-based decimal integer encoded as a string
- `previous_hash`: previous event hash; all-zero SHA-256 value for genesis
- `receipt_hash`: SHA-256 digest of the exact receipt file bytes
- `created_at`: producer-declared RFC 3339 UTC time ending in `Z`
- `event_hash`: SHA-256 of the canonical event body excluding event_hash

Canonical event body: UTF-8 JSON, keys sorted by Unicode code point, compact
separators, non-ASCII characters unescaped, no trailing newline. The
`event_hash` is lowercase hexadecimal.

## Verification

A verifier checks exact fields/types, version, sequence continuity, previous
hash linkage, timestamp syntax, receipt hash syntax, recomputed event hashes,
and (when supplied) equality with an externally trusted expected chain head.

A PASS without an external checkpoint proves internal consistency only. It
does not prove completeness, trusted time, event truth, or resistance to full
chain replacement. For stronger audit guarantees, combine signed receipts,
externally anchored checkpoints, and independently trusted timestamp evidence.
