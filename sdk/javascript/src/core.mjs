import { createHash } from "node:crypto";

export const SPEC_VERSION = "0.1";
export const MAX_FILE_BYTES = 1_048_576;
const BUNDLE_FIELDS = ["input_hash", "model_id", "output_hash", "policy_id", "spec_version", "timestamp"];
const RECEIPT_FIELDS = ["bundle_file_hash", "bundle_hash", "created_at", "spec_version"];
const HASH_RE = /^[0-9a-f]{64}$/;
const TIMESTAMP_RE = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/;

export class CordValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = "CordValidationError";
  }
}

function parseJsonStrict(text, label) {
  let i = 0;
  const fail = (message) => { throw new CordValidationError(`${label}: ${message} at offset ${i}`); };
  const ws = () => { while (i < text.length && /[\t\n\r ]/.test(text[i])) i++; };

  function string() {
    const start = i++;
    while (i < text.length) {
      const c = text.charCodeAt(i);
      if (c === 0x22) {
        i++;
        try { return JSON.parse(text.slice(start, i)); }
        catch { fail("invalid JSON string"); }
      }
      if (c < 0x20) fail("unescaped control character");
      if (c === 0x5c) {
        i++;
        if (i >= text.length) fail("incomplete escape");
        const e = text[i];
        if (e === "u") {
          if (!/^[0-9a-fA-F]{4}$/.test(text.slice(i + 1, i + 5))) fail("invalid Unicode escape");
          i += 5;
          continue;
        }
        if (!(e === '"' || e === String.fromCharCode(92) || e === "/" || ["b", "f", "n", "r", "t"].includes(e))) fail("invalid escape");
      }
      i++;
    }
    fail("unterminated string");
  }

  function value(depth = 0) {
    if (depth > 64) fail("maximum JSON nesting depth exceeded");
    ws();
    const c = text[i];
    if (c === '"') return string();
    if (c === "{") {
      i++;
      ws();
      const out = Object.create(null);
      const keys = new Set();
      if (text[i] === "}") { i++; return out; }
      while (true) {
        ws();
        if (text[i] !== '"') fail("object key must be a string");
        const key = string();
        if (keys.has(key)) fail(`duplicate object key ${JSON.stringify(key)}`);
        keys.add(key);
        ws();
        if (text[i++] !== ":") fail("expected colon");
        out[key] = value(depth + 1);
        ws();
        if (text[i] === "}") { i++; return out; }
        if (text[i++] !== ",") fail("expected comma or closing brace");
      }
    }
    if (c === "[") {
      i++;
      ws();
      const out = [];
      if (text[i] === "]") { i++; return out; }
      while (true) {
        out.push(value(depth + 1));
        ws();
        if (text[i] === "]") { i++; return out; }
        if (text[i++] !== ",") fail("expected comma or closing bracket");
      }
    }
    const rest = text.slice(i);
    for (const literal of ["true", "false", "null"]) {
      if (rest.startsWith(literal)) { i += literal.length; return JSON.parse(literal); }
    }
    const match = /^-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/.exec(rest);
    if (match) {
      i += match[0].length;
      const n = Number(match[0]);
      if (!Number.isFinite(n)) fail("non-finite number");
      return n;
    }
    fail("invalid JSON value");
  }

  const result = value();
  ws();
  if (i !== text.length) fail("trailing content");
  if (result === null || Array.isArray(result) || typeof result !== "object") {
    throw new CordValidationError(`${label} must be a JSON object`);
  }
  return result;
}

function rejectSurrogates(value, field) {
  for (let i = 0; i < value.length; i++) {
    const code = value.charCodeAt(i);
    if (code >= 0xd800 && code <= 0xdbff) {
      const next = value.charCodeAt(i + 1);
      if (!(next >= 0xdc00 && next <= 0xdfff)) {
        throw new CordValidationError(`${field} contains an unpaired surrogate`);
      }
      i++;
    } else if (code >= 0xdc00 && code <= 0xdfff) {
      throw new CordValidationError(`${field} contains an unpaired surrogate`);
    }
  }
}

function validateFields(obj, expected, label) {
  const actual = Object.keys(obj).sort();
  const wanted = [...expected].sort();
  if (actual.length !== wanted.length || actual.some((key, index) => key !== wanted[index])) {
    throw new CordValidationError(`${label} must contain exactly: ${wanted.join(", ")}`);
  }
  for (const [key, value] of Object.entries(obj)) {
    if (typeof value !== "string") throw new CordValidationError(`${label}.${key} must be a string`);
    rejectSurrogates(value, `${label}.${key}`);
  }
}

function validateTimestamp(value, field) {
  const match = TIMESTAMP_RE.exec(value);
  if (!match) throw new CordValidationError(`${field} must be a valid RFC 3339 UTC timestamp ending in Z`);
  const [year, month, day, hour, minute, second] = match.slice(1, 7).map(Number);
  const date = new Date(0);
  date.setUTCFullYear(year, month - 1, day);
  date.setUTCHours(hour, minute, second, 0);
  if (date.getUTCFullYear() !== year || date.getUTCMonth() !== month - 1 ||
      date.getUTCDate() !== day || date.getUTCHours() !== hour ||
      date.getUTCMinutes() !== minute || date.getUTCSeconds() !== second) {
    throw new CordValidationError(`${field} must be a valid RFC 3339 UTC timestamp ending in Z`);
  }
}

export function validateBundle(bundle) {
  validateFields(bundle, BUNDLE_FIELDS, "bundle");
  if (bundle.spec_version !== SPEC_VERSION) throw new CordValidationError("unsupported bundle spec_version");
  for (const field of ["model_id", "policy_id"]) {
    if (!bundle[field] || bundle[field].trim() !== bundle[field]) {
      throw new CordValidationError(`bundle.${field} must be a non-empty trimmed string`);
    }
  }
  validateTimestamp(bundle.timestamp, "bundle.timestamp");
  for (const field of ["input_hash", "output_hash"]) {
    if (!HASH_RE.test(bundle[field])) throw new CordValidationError(`bundle.${field} must be a lowercase SHA-256 digest`);
  }
}

export function validateReceipt(receipt) {
  validateFields(receipt, RECEIPT_FIELDS, "receipt");
  if (receipt.spec_version !== SPEC_VERSION) throw new CordValidationError("unsupported receipt spec_version");
  for (const field of ["bundle_hash", "bundle_file_hash"]) {
    if (!HASH_RE.test(receipt[field])) throw new CordValidationError(`receipt.${field} must be a lowercase SHA-256 digest`);
  }
  validateTimestamp(receipt.created_at, "receipt.created_at");
}

export function canonicalBundleBytes(bundle) {
  validateBundle(bundle);
  const keys = [...BUNDLE_FIELDS].sort();
  const members = keys.map((key) => `${JSON.stringify(key)}:${JSON.stringify(bundle[key])}`);
  return Buffer.from(`{${members.join(",")}}`, "utf8");
}

export function createReceiptBytes(bundleBytes, createdAt) {
  const raw = Buffer.isBuffer(bundleBytes) ? bundleBytes : Buffer.from(bundleBytes);
  const bundle = decodeFile(raw, "bundle");
  validateBundle(bundle);
  validateTimestamp(createdAt, "created_at");
  const receipt = {
    spec_version: SPEC_VERSION,
    bundle_hash: sha256(canonicalBundleBytes(bundle)),
    bundle_file_hash: sha256(raw),
    created_at: createdAt,
  };
  return Buffer.from(JSON.stringify(receipt, null, 2) + "\\n", "utf8");
}

function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function decodeFile(bytes, label) {
  const data = Buffer.isBuffer(bytes) ? bytes : Buffer.from(bytes);
  if (data.length > MAX_FILE_BYTES) throw new CordValidationError(`${label} exceeds ${MAX_FILE_BYTES} bytes`);
  if (data.subarray(0, 3).equals(Buffer.from([0xef, 0xbb, 0xbf]))) {
    throw new CordValidationError(`${label} MUST NOT contain a UTF-8 BOM`);
  }
  let text;
  try { text = new TextDecoder("utf-8", { fatal: true }).decode(data); }
  catch { throw new CordValidationError(`${label} is not valid UTF-8`); }
  return parseJsonStrict(text, label);
}

export function verifyBytes(bundleBytes, receiptBytes) {
  const bundleRaw = Buffer.isBuffer(bundleBytes) ? bundleBytes : Buffer.from(bundleBytes);
  const receiptRaw = Buffer.isBuffer(receiptBytes) ? receiptBytes : Buffer.from(receiptBytes);
  const bundle = decodeFile(bundleRaw, "bundle");
  const receipt = decodeFile(receiptRaw, "receipt");
  validateBundle(bundle);
  validateReceipt(receipt);
  const checks = {
    bundle_hash: sha256(canonicalBundleBytes(bundle)) === receipt.bundle_hash,
    bundle_file_hash: sha256(bundleRaw) === receipt.bundle_file_hash,
  };
  if (!Object.values(checks).every(Boolean)) {
    throw new CordValidationError("hash mismatch: " + Object.entries(checks).filter(([, ok]) => !ok).map(([key]) => key).join(", "));
  }
  return {
    status: "PASS",
    spec_version: SPEC_VERSION,
    checks,
    meaning: "Bundle and receipt hashes match. This is an integrity check, not proof of identity or trusted time.",
  };
}
