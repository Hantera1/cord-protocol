import { createHash } from "node:crypto";

export interface CordBundle {
  spec_version: string;
  model_id: string;
  timestamp: string;
  policy_id: string;
  input_hash: string;
  output_hash: string;
}
export interface CordReceipt {
  spec_version: string;
  bundle_hash: string;
  bundle_file_hash: string;
  created_at: string;
}
const BUNDLE_FIELDS = ["input_hash","model_id","output_hash","policy_id","spec_version","timestamp"];
const RECEIPT_FIELDS = ["bundle_file_hash","bundle_hash","created_at","spec_version"];
const HASH = /^[0-9a-f]{64}$/;
const TIMESTAMP = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?Z$/;

export class CordValidationError extends Error {
  constructor(message: string) { super(message); this.name = "CordValidationError"; }
}
export function sha256(data: Uint8Array): string {
  return createHash("sha256").update(data).digest("hex");
}
function exactStringObject(value: unknown, fields: string[], label: string): asserts value is Record<string,string> {
  if (value === null || typeof value !== "object" || Array.isArray(value))
    throw new CordValidationError(label + " must be an object");
  const obj = value as Record<string, unknown>;
  const expected = [...fields].sort();
  const actual = Object.keys(obj).sort();
  if (actual.length !== expected.length || actual.some((key, i) => key !== expected[i]))
    throw new CordValidationError(label + " has missing or unexpected fields");
  for (const key of fields) if (typeof obj[key] !== "string")
    throw new CordValidationError(label + "." + key + " must be a string");
}
function timestamp(value: string, field: string): void {
  const match = TIMESTAMP.exec(value);
  if (!match) throw new CordValidationError(field + " must be a valid RFC 3339 UTC timestamp ending in Z");
  const [, ys, mos, ds, hs, mis, ss] = match;
  const year = Number(ys), month = Number(mos), day = Number(ds);
  const hour = Number(hs), minute = Number(mis), second = Number(ss);
  const leap = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
  const days = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  if (month < 1 || month > 12 || day < 1 || day > days[month - 1] ||
      hour > 23 || minute > 59 || second > 59)
    throw new CordValidationError(field + " is not a valid RFC 3339 UTC calendar time");
}
export function validateBundle(bundle: unknown): asserts bundle is CordBundle {
  exactStringObject(bundle, BUNDLE_FIELDS, "bundle");
  const b = bundle as CordBundle;
  if (b.spec_version !== "0.1") throw new CordValidationError("unsupported bundle spec_version");
  for (const field of ["model_id","policy_id"] as const)
    if (!b[field] || b[field].trim() !== b[field]) throw new CordValidationError("bundle." + field + " must be non-empty and trimmed");
  timestamp(b.timestamp, "bundle.timestamp");
  for (const field of ["input_hash","output_hash"] as const)
    if (!HASH.test(b[field])) throw new CordValidationError("bundle." + field + " must be lowercase SHA-256 hex");
}
export function validateReceipt(receipt: unknown): asserts receipt is CordReceipt {
  exactStringObject(receipt, RECEIPT_FIELDS, "receipt");
  const r = receipt as CordReceipt;
  if (r.spec_version !== "0.1") throw new CordValidationError("unsupported receipt spec_version");
  for (const field of ["bundle_hash","bundle_file_hash"] as const)
    if (!HASH.test(r[field])) throw new CordValidationError("receipt." + field + " must be lowercase SHA-256 hex");
  timestamp(r.created_at, "receipt.created_at");
}
/** CORD-CJSON-1 for Core v0.1 fixed string-only objects. */
export function canonicalCoreJson(value: Record<string,string>): Uint8Array {
  return new TextEncoder().encode(JSON.stringify(Object.fromEntries(Object.keys(value).sort().map(k => [k,value[k]]))));
}
/** Verify already-parsed JSON plus the exact original bundle file bytes. */
export function verifyCore(bundle: unknown, receipt: unknown, bundleFileBytes: Uint8Array) {
  validateBundle(bundle);
  validateReceipt(receipt);
  const bundleHash = sha256(canonicalCoreJson(bundle));
  const fileHash = sha256(bundleFileBytes);
  const checks = { bundle_hash: bundleHash === receipt.bundle_hash, bundle_file_hash: fileHash === receipt.bundle_file_hash };
  if (!checks.bundle_hash || !checks.bundle_file_hash) throw new CordValidationError("hash mismatch");
  return { status: "PASS" as const, spec_version: "0.1", checks,
    meaning: "Hash consistency only; no identity, trusted-time, model-origin, truth, or policy-compliance claim." };
}
