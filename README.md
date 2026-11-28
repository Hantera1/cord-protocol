<p align="center">
  <img src="logo.png.PNG" alt="CORD logo" width="320">
</p>

<h1 align="center">CORD</h1>

<p align="center">
  <strong>Open evidence formats. Independent verification.</strong>
</p>

<p align="center">
  An open, vendor-neutral protocol draft by Hantera · Created by KentPH
</p>

---

## Overview

CORD is an open protocol project for creating, packaging and independently verifying cryptographic evidence about digital events, including AI-related events.

The project is designed around a small, implementation-neutral Core, with optional extensions and application profiles developed separately. Evidence can be inspected and verified offline; a CORD account or hosted service is not required for Core verification.

**Current release status:** Experimental draft, Core v0.1. The specification and reference implementation are under development and require independent review. CORD is not a production security certification.

## What Core v0.1 verifies

A Core evidence package contains two files:

- `bundle.json` — the evidence bundle.
- `receipt.json` — the receipt containing the expected hashes.

The reference verifier checks the bundle structure, its canonical hash, and the hash of the exact bundle file. Verification is performed offline.

A **PASS** means that the supplied files are internally consistent under the supported Core version. It does not establish:

- who created the files;
- whether a particular AI model actually generated the declared output;
- whether the declared timestamp is trustworthy;
- whether the evidence is complete, truthful, safe or legally compliant.

If an attacker can replace both the bundle and its receipt, they can create a new matching pair. Read the [Security Model](docs/SECURITY-MODEL.md) before relying on a verification result.

## Quick start

**Requirements:** Python 3.10 or later for Core verification. Optional extensions may require additional dependencies listed in `requirements.txt`.

Create a receipt for a valid bundle:

```bash
python verifier/verify.py create bundle.json receipt.json --created-at 2026-03-06T12:00:05Z
```

Verify the package:

```bash
python verifier/verify.py verify bundle.json receipt.json
```

Run the test suite:

```bash
python -m unittest discover -s tests -v
```

Verify the fixed test vector:

```bash
python verifier/verify.py verify test-vectors/bundle_valid.json test-vectors/receipt_valid.json
```

The verifier outputs JSON and returns exit code `0` on success or `1` when input is invalid or a check fails.

## Project structure

| Area | Purpose | Status |
|---|---|---|
| CORD Core v0.1 | Canonical evidence bundle and receipt formats; offline hash verification | Experimental draft |
| Signed Receipt | Ed25519 signatures for receipts | Experimental extension |
| Trust Store | Local, pinned trust configuration and signer-role checks | Experimental extension |
| Trusted Timestamp | RFC 3161 timestamp validation profile | Experimental extension |
| Event Chain | Hash-linked sequence of evidence events | Experimental extension |
| Application Profiles | Domain-specific evidence requirements | Proposed / in development |

Core is intentionally kept separate from extensions. Experimental extensions do not change the meaning or guarantees of Core PASS.

## Specifications and documentation

### Core and security

- [CORD Core Formats v0.1](spec/FORMATS.md)
- [Security Model](docs/SECURITY-MODEL.md)
- [Project Charter](docs/PROJECT-CHARTER.md)
- [Development Roadmap](docs/ROADMAP.md)

### Experimental extensions

- [Ed25519 Signed Receipt](spec/SIGNED-RECEIPT.md)
- [Offline Trust Store v0.1](spec/TRUST-STORE.md)
- [RFC 3161 Trusted Timestamp Profile](spec/RFC3161-TIMESTAMP.md)
- [Receipt Event Chain](spec/EVENT-CHAIN.md)

### Application profiles and schemas

- [Application Portfolio and Reserved Use Cases](spec/APPLICATION-PORTFOLIO.md)
- [Luxury Asset Verification Profile — proposed](spec/LUXURY-ASSET-VERIFICATION.md)
- [Clock Verification Profile — proposed](spec/CLOCK-VERIFICATION.md)
- [Application Profile Manifest — proposed](spec/PROFILE-MANIFEST.md)
- [Profile Manifest JSON Schema 0.1](schemas/profile-manifest-0.1.schema.json)
- [Trust Store JSON Schema](schemas/trust-store-0.1.schema.json)

## Python integration

A minimal Python helper is available at `sdk/python/cord_sdk.py`. See [the Python quick-start example](examples/python_quickstart.py).

The signed-receipt, Trust Store, timestamp and event-chain capabilities are experimental. For example, an event chain requires an independently retained checkpoint to detect replacement of the entire chain.

## Design principles

- **Open and vendor-neutral:** the protocol is designed to be inspectable and implementable by independent parties.
- **Offline Core verification:** no CORD account or hosted service is needed to verify a Core package.
- **Explicit trust boundaries:** a cryptographic match is not presented as proof of identity, truth or real-world origin.
- **Separation of concerns:** the Core remains small; extensions and domain-specific profiles are specified separately.
- **Interoperability:** deterministic formats and test vectors support independent implementations.

## Contributing

Protocol reviews, independent implementations, verifier improvements, test vectors, SDKs and integration examples are welcome.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md). For significant protocol changes, open an issue or discussion before submitting a pull request.

## Origin and attribution

**CORD by Hantera — created by KentPH.**

CORD was initiated by Hantera and KentPH. The project is open for inspection, implementation, use and extension under its published license. Community contributions and independent implementations are welcome.

Project creator: [KentPH / Hantera](https://github.com/Hantera1).

## Support the project

Voluntary donations can support continued development. Donations do not provide protocol privileges and do not influence verification results.

**Ethereum (ETH)**

`0x3d6344fc57ba0039429bdf78dd7ca734c42195b9`

**Bitcoin (BTC)**

`bc1q8qtrmfmq53smfhzp8s6p9er080z66zvzae9f38`

## License

CORD is published under the [Apache License 2.0](LICENSE).
