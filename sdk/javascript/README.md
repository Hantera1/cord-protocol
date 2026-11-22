# CORD JavaScript Core verifier

Dependency-free Node.js reference implementation for CORD Core v0.1.

Run from the repository root:

```bash
node --test sdk/javascript/test/core.test.mjs
```

The implementation independently parses JSON while rejecting duplicate keys, checks UTF-8 and Core field constraints, applies CORD-CJSON-1 to the fixed six-field Bundle, and verifies both receipt hashes.

A PASS has the same deliberately narrow meaning as the Python Core verifier: integrity consistency only. It does not establish signer identity, trusted time, model provenance, truth, or event completeness.
