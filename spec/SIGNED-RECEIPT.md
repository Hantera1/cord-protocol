# Cord Signed Receipt Extension (experimental)

This extension adds an Ed25519 signature over a canonicalized Core v0.1
receipt. It does not alter Core bundle or receipt fields or hash semantics.

## Trust model

The verifier MUST obtain the trusted Ed25519 public key from an out-of-band
trust store, authenticated configuration, or an explicitly pinned key. The
envelope's `key_id` is only a lookup hint. A public key supplied by the same
untrusted party as the bundle and envelope MUST NOT be treated as trusted.

The signature proves that the holder of the corresponding private key signed
the exact receipt bytes represented by the canonical receipt profile. It does
not prove that the signer is a particular person or organization unless the
key-to-identity binding is independently trusted. Key rotation, revocation,
certificate validation, and hardware-backed key custody are outside this
initial extension and MUST be defined by deployments.

## Envelope

The detached JSON envelope contains exactly:

- `spec_version`: `0.1`
- `alg`: `Ed25519`
- `key_id`: non-empty trimmed key identifier
- `signature`: Base64-encoded 64-byte Ed25519 signature

The signature input is UTF-8 JSON of the validated receipt with sorted keys,
compact separators, no ASCII-only escaping, and no trailing newline. The
receipt itself remains unchanged.

## Python reference

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Use `verifier.signatures.sign_receipt` to create an envelope and
`verify_signed_receipt` to verify it with a trusted public key and expected
key ID. PEM helpers are provided for loading Ed25519 keys.

A successful signature check authenticates the receipt relative to the
externally trusted key. It does not provide trusted time or prove that the
declared model actually generated the output.
