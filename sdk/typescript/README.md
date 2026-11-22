# Cord TypeScript SDK (experimental)

Requires Node.js 20+ and npm. This package implements the fixed-field Cord Core v0.1 validation and hash checks using Node's built-in cryptography; TypeScript is a development dependency.

```sh
npm install
npm test
```

The caller must supply:
- a parsed bundle object;
- a parsed receipt object;
- the exact original bytes of `bundle.json`.

The SDK deliberately does not parse JSON files: JavaScript's built-in JSON.parse silently accepts duplicate object keys, while Cord Core requires duplicate-key rejection. Use a duplicate-key-rejecting parser at the file boundary before passing objects to this SDK. Never re-serialize the bundle to calculate `bundle_file_hash`; pass the original bytes.

This SDK is an interoperability implementation, not a security certification. Core PASS establishes hash consistency only. See the root security model and `spec/FORMATS.md`.
