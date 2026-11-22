<p align="center">
  <img src="logo.png.PNG" alt="Cord Logo" width="400">
</p>

# CORD

**An open protocol by Hantera · Created by KentPH**

Cord is an open, vendor-neutral protocol draft for creating and independently verifying cryptographic evidence about AI events.

## What Core v0.1 does

Cord Core uses a `bundle.json` and a `receipt.json`. The verifier checks the bundle schema, canonical bundle hash, and exact bundle-file hash. Verification is offline.

A PASS means the supplied bundle is valid under the supported Core version and its hashes match the supplied receipt. It does **not** prove who created the files, that the declared AI model generated the output, or that the timestamp is trusted. An attacker who can replace both files can create a new matching pair. See the [Security Model](docs/SECURITY-MODEL.md).

> **Status: Experimental draft (v0.1).** Do not use as a production security certification. Independent implementations and external security review are still required.

## Quick start

Python 3.10 or later; no third-party packages are required for Core verification.

```bash
python verifier/verify.py create bundle.json receipt.json --created-at 2026-03-06T12:00:05Z
python verifier/verify.py verify bundle.json receipt.json
python -m unittest discover -s tests -v
```

The verifier prints JSON. It exits with code `0` on success and `1` on invalid input or a failed check.

Try the fixed test vector:

```bash
python verifier/verify.py verify test-vectors/bundle_valid.json test-vectors/receipt_valid.json
```

## Languages

- [العربية — التوثيق باللغة العربية](README.ar.md)
- [English — original documentation](README.md)

## Core formats and governance

- [Cord Core Formats v0.1](spec/FORMATS.md)
- [Project Charter](docs/PROJECT-CHARTER.md)
- [Completion Roadmap](docs/ROADMAP.md)
- [Security Model](docs/SECURITY-MODEL.md)
- [Contributing](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)

## Design principles

- Open, vendor-neutral, and independently implementable.
- Offline verification; no Cord account or server required.
- Strict schemas and deterministic test vectors.
- Optional trust extensions never redefine Core hash semantics.
- No claim that hashes alone prove identity, trusted time, truth, or compliance.

## Python integration

A minimal helper is available at `sdk/python/cord_sdk.py`; see `examples/python_quickstart.py`. Install the Ed25519 extension dependency with `python -m pip install -r requirements.txt`.

## TypeScript integration (experimental)

A Node.js 20+ SDK is available in `sdk/typescript`. It verifies parsed Core objects against the exact original bundle bytes. The SDK deliberately requires a duplicate-key-rejecting JSON parser at the file boundary; JavaScript's built-in JSON.parse does not reject duplicate keys.

```bash
cd sdk/typescript
npm install
npm test
```

## Cord Trade (experimental business-evidence extension)

Cord Trade adds detached evidence manifests for physical goods, metals, contracts, payments, delivery and digital commerce without changing Cord Core v0.1.

- [Trade architecture and business model](docs/TRADE-ARCHITECTURE.md)
- [Integration plan](docs/INTEGRATION-PLAN.md)
- [Trade Evidence 0.1 JSON Schema](spec/TRADE-EVIDENCE-0.1.schema.json)
- [Python Trade validator](sdk/python/cord_trade.py)
- [Synthetic watch sale example](examples/trade_watch_sale.json)
- [Synthetic silver lot example](examples/trade_silver_lot.json)

Cord Trade is an experimental extension. Its declarations do not prove authenticity, ownership, payment finality, delivery or legal validity without suitable external evidence and trust anchors.

## Cord Trade Commercial Licensing (working draft)

Commercial licensing separates the open Cord Core protocol from proprietary Trade agreement materials, paid services, hosted features, partner rights and support. The licensing framework is a design draft, not a signed legal contract.

- [Commercial licensing framework](docs/COMMERCIAL-LICENSING.md)
- [License registry operating model](docs/LICENSING-OPERATIONS.md)
- [License Record 0.1 schema](spec/LICENSE-RECORD-0.1.schema.json)
- [Arabic market launch brief](docs/ARABIC-MARKET-LAUNCH.md)

**Ownership gate:** the legal licensor is not confirmed until the IP chain of title and legal entity are documented. Existing Cord Core code is published under Apache 2.0; commercial licensing must not purport to withdraw those rights.

## Cord Trade License v1 — commercial workstream

The selected commercial direction is a new, separate Cord Trade licensing company, selling both trade-agreement template packs and Cord Trade software/workflows, with the UAE as the first target market.

- [Cord Trade License product definition](docs/CORD-TRADE-LICENSE-PRODUCT.md)
- [New company and ownership setup decision](docs/NEWCO-OWNERSHIP-AND-SETUP.md)
- [Commercial license agreement term sheet](docs/CORD-TRADE-LICENSE-AGREEMENT-TERM-SHEET.md)
- [UAE go-to-market checklist](docs/UAE-GO-TO-MARKET-CHECKLIST.md)
- [License sales ledger model](docs/LICENSE-SALES-LEDGER.md)
- [Public license certificate schema](spec/LICENSE-CERTIFICATE-PUBLIC-0.1.schema.json)

These are planning and implementation specifications, not legal advice or executed contracts. The new legal entity, jurisdiction, IP assignments, trademarks, licensing permissions and customer agreements remain to be completed.

## Swedish Cord Trade Licensing AB — establishment pack

The current planning direction is a lean Swedish private limited company, with the Cord Trade brand and UAE as the first export market. The proposed shareholder is Means Zero Holding AB at 100%, subject to confirmation that the holding company is registered and able to subscribe.

- [Swedish establishment plan](docs/SWEDISH-NEWCO-ESTABLISHMENT-PLAN.md)
- [Proposed ownership resolution](docs/PROPOSED-OWNERSHIP-RESOLUTION.md)
- [Formation document data sheet](docs/FORMATION-DOCUMENTS-DRAFT.md)
- [Lean startup budget](docs/LEAN-STARTUP-BUDGET.md)
- [IP asset register template](docs/IP-ASSET-REGISTER-TEMPLATE.md)

These are preparation documents, not filed incorporation papers or executed IP assignments. Company name, shareholder authority, registered office, directors and IP chain of title must be verified before filing or sale.

## Experimental extensions

- [Ed25519 signed receipt](spec/SIGNED-RECEIPT.md)
- [Receipt event chain](spec/EVENT-CHAIN.md)

The signed-receipt and event-chain extensions require externally trusted keys/checkpoints. They do not make Cord a production security certification.

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
