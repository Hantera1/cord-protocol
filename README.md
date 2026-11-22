<p align="center">
  <img src="logo.png.PNG" alt="Cord Logo" width="400">
</p>

# CORD

**An open protocol by Hantera · Created by KentPH**

**Cord** is an open, vendor-neutral protocol draft for cryptographically verifiable evidence about AI and digital events.

Cord uses a bundle and a receipt to let an independent verifier check whether the evidence matches its cryptographic commitments. Core verification is intended to work offline.

> **Status: Experimental draft (v0.1).** Cord is not yet a finalized standard or a production security certification. The specification, canonicalization rules, verifier, and test vectors are being developed.

## What Cord can and cannot establish

Cord Core is designed to check evidence integrity: whether the supplied files match the hashes in the receipt.

A passing integrity check does **not** by itself prove who created an event, which model actually generated an output, whether the declared timestamp is trustworthy, or whether the content is true, safe, lawful, or policy-compliant. Those require separate mechanisms and evidence.

## Core evidence package

- `bundle.json` describes the event and includes hashes of the input and output.
- `receipt.json` binds the bundle to cryptographic hashes.

The Core is designed to remain small, implementation-neutral, and independently verifiable. Optional capabilities such as signatures and trusted timestamps will be specified as separate extensions.

## Quick start

The current reference verifier can be run with:

```bash
python verifier/verify.py bundle.json receipt.json
```

The v0.1 implementation and examples are experimental. Check the specification and test vectors before relying on a result. Known inconsistencies are being addressed; do not treat the current repository as a stable production release.

## Project principles

- Open protocol and public specifications.
- Vendor-neutral integrations; no required AI provider or cloud.
- Offline Core verification.
- Strict, deterministic formats with reproducible test vectors.
- Optional hosted services must never be required to verify Core evidence.
- Clear separation between integrity, authenticity, identity, and trusted time.

## Documentation

- [Cord Core Formats](spec/FORMATS.md)
- [Cord Core Specification](spec/cord-core.md)
- [Project Charter](docs/PROJECT-CHARTER.md)
- [Completion Roadmap](docs/ROADMAP.md)
- [Security Model](docs/SECURITY-MODEL.md)
- [Contributing](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)

## How to contribute

We welcome specification reviews, verifier improvements, independent implementations, test vectors, SDKs, and integration examples. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and open an issue before proposing significant protocol changes.

## Sustainability and support

Cord's protocol and core verification are intended to remain open. Voluntary donations may support maintenance and development; donations do not buy protocol privileges, influence verification results, or provide exclusive access.

Current voluntary crypto donation details are listed below. We will add hosted payment or sponsorship options only after the relevant accounts and ownership are configured and verified.

<details>
<summary>Crypto donation addresses</summary>

**Ethereum (ETH)**

`0x3d6344fc57ba0039429bdf78dd7ca734c42195b9`

**Bitcoin (BTC)**

`bc1q8qtrmfmq53smfhzp8s6p9er080z66zvzae9f38`

</details>

## License

Cord is published under the [Apache License 2.0](LICENSE).

## Origin and attribution

**CORD by Hantera — Created by KentPH.**

Cord was initiated and is maintained as an open project by Hantera, founded by KentPH. The protocol is open for everyone to inspect, implement, use, and extend under the project license. Independent implementations and community contributions are welcome; the project's origin and official name should remain clearly attributed when referring to the original Cord project.

Project creator: [KentPH](https://github.com/Hantera1) · Project home: [Hantera on GitHub](https://github.com/Hantera1)
