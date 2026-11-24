# EVC v0.1 conformance and development notes

This document describes the experimental reference implementations. It does not expand the normative scope in [EVC.md](../spec/EVC.md).

## Implementations

- Python: `assurance/evc.py`
- TypeScript: `assurance/evc.ts`
- TypeScript CLI: `assurance/evc_cli.ts`
- Shared vectors: `test-vectors/evc-conformance-0.1.json`
- Cross-runtime tests: `tests/test_evc_cross_runtime.py`

Both implementations independently parse and validate the graph, evaluate claim-scoped dependency freshness, normalize unordered arrays, and compute the graph SHA-256. The TypeScript parser rejects duplicate JSON object keys; plain `JSON.parse` alone would not provide that guarantee.

## Run the conformance suite

Requirements: Python 3.11+, Node.js 22+, npm.

Install the TypeScript compiler and Node.js type definitions:

```bash
npm install --no-save --no-package-lock typescript@5.8.3 @types/node@22.15.3
```

Compile the TypeScript implementation:

```bash
npx tsc --strict --target ES2022 --module commonjs --moduleResolution node --esModuleInterop --skipLibCheck --rootDir . --outDir build assurance/evc.ts assurance/evc_cli.ts
```

Run all repository tests, including Python/TypeScript parity checks:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

The GitHub Actions workflow performs these steps. Cross-runtime tests compare complete output objects, including the graph digest, for every shared vector. Additional tests cover array-order invariance and malformed input rejection by the TypeScript CLI.

## CLI

After compilation:

```bash
node build/assurance/evc_cli.js test-vectors/evc-conformance-0.1.json
```

The CLI accepts one graph JSON file and writes one JSON evaluation result to standard output. It exits non-zero for invalid input.

## Scope and limitations

A `VALID` result means only that the declared dependencies match the supplied current-state snapshot and the claim references at least one evidence record. It does not authenticate that snapshot, verify evidence bytes, establish issuer identity or trusted time, prove truth or safety, or establish legal compliance. Dependency completeness remains an assertion by the graph producer.

The shared vectors are a finite compatibility suite, not exhaustive proof that all possible Python and TypeScript inputs behave identically. The implementations and protocol remain experimental and have not received an independent security audit or formal protocol review.
