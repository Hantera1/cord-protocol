<p align="center">
  <img src="logo.png.PNG" alt="Cord Logo" width="400">
</p>

# CORD

**An open protocol by Hantera · Created by KentPH**

Cord is an open, vendor-neutral protocol draft for creating and independently verifying cryptographic evidence about AI events.

## What Core v0.1 does

Cord Core uses a `bundle.json` and a `receipt.json`. The verifier checks the bundle schema, canonical bundle hash, and exact bundle-file hash. Verification is offline.

A PASS means the supplied bundle is valid under the supported Core version and its hashes match the supplied receipt. It does **not** prove who created the files, that the declared AI model generated the output, or that the timestamp is trusted. An attacker who can replace both files can create a new matching pair. See the [Security Model](docs/SECURITY-MODEL.md).

> **Status: Experimental draft (v0.1).** Do not use as a production security certification. The specification and reference implementation are being developed and need independent review.

## Quick start

Python 3.10 or later; no third-party packages are required.

Create a receipt for a valid bundle:

```bash
python verifier/verify.py create bundle.json receipt.json --created-at 2026-03-06T12:00:05Z
```

Verify the evidence package:

```bash
python verifier/verify.py verify bundle.json receipt.json
```

The verifier prints JSON. It exits with code `0` on success and `1` on invalid input or a failed check.

Run the automated tests:

```bash
python -m unittest discover -s tests -v
```

Try the fixed test vector:

```bash
python verifier/verify.py verify test-vectors/bundle_valid.json test-vectors/receipt_valid.json
```

## Core formats

- [Cord Core Formats v0.1](spec/FORMATS.md)
- [Project Charter](docs/PROJECT-CHARTER.md)
- [Completion Roadmap](docs/ROADMAP.md)
- [Security Model](docs/SECURITY-MODEL.md)
- [Contributing](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)

## Design principles

- Open and implementation-neutral.
- Offline verification; no Cord account or server required.
- Strict schemas and deterministic test vectors.
- Vendor-neutral integrations.
- Signatures and trusted timestamps are separate future extensions, not implied by Core PASS.

## Contributing

We welcome protocol reviews, independent implementations, verifier improvements, test vectors, SDKs, and integration examples. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and open an issue before proposing significant protocol changes.

## Support

Voluntary donations support development and do not buy protocol privileges or influence verification results.

**Ethereum (ETH)**

`0x3d6344fc57ba0039429bdf78dd7ca734c42195b9`

**Bitcoin (BTC)**

`bc1q8qtrmfmq53smfhzp8s6p9er080z66zvzae9f38`

## License

Cord is published under the [Apache License 2.0](LICENSE).

## Origin and attribution

**CORD by Hantera — Created by KentPH.**

Cord was initiated by Hantera and KentPH. The protocol is open for everyone to inspect, implement, use, and extend under the project license. Independent implementations and community contributions are welcome.

Project creator: [KentPH / Hantera](https://github.com/Hantera1).
