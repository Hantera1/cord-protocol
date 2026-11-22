import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { canonicalBundleBytes, verifyBytes, CordValidationError } from "../src/core.mjs";

const root = new URL("../../../", import.meta.url);
const bundleBytes = await readFile(new URL("test-vectors/bundle_valid.json", root));
const receiptBytes = await readFile(new URL("test-vectors/receipt_valid.json", root));

test("published Core v0.1 vector verifies independently", () => {
  const result = verifyBytes(bundleBytes, receiptBytes);
  assert.equal(result.status, "PASS");
  assert.deepEqual(result.checks, { bundle_hash: true, bundle_file_hash: true });
});

test("canonical bytes match the fixed Core field order", () => {
  const bundle = JSON.parse(bundleBytes.toString("utf8"));
  assert.equal(
    canonicalBundleBytes(bundle).toString("utf8"),
    '{"input_hash":"' + "1".repeat(64) + '","model_id":"demo-model","output_hash":"' + "2".repeat(64) + '","policy_id":"cord-output-v0.1","spec_version":"0.1","timestamp":"2026-03-06T12:00:00Z"}',
  );
});

test("single-byte bundle mutation fails", () => {
  const changed = Buffer.from(bundleBytes);
  changed[changed.length - 2] ^= 1;
  assert.throws(() => verifyBytes(changed, receiptBytes), CordValidationError);
});

test("receipt hash mutation fails", () => {
  const receipt = JSON.parse(receiptBytes.toString("utf8"));
  receipt.bundle_hash = "0".repeat(64);
  assert.throws(() => verifyBytes(bundleBytes, Buffer.from(JSON.stringify(receipt))), CordValidationError);
});

test("duplicate JSON keys fail closed", () => {
  const duplicate = Buffer.from('{"spec_version":"0.1","spec_version":"0.1"}');
  assert.throws(() => verifyBytes(duplicate, receiptBytes), /duplicate object key/);
});

test("UTF-8 BOM is rejected", () => {
  assert.throws(() => verifyBytes(Buffer.concat([Buffer.from([0xef, 0xbb, 0xbf]), bundleBytes]), receiptBytes), /BOM/);
});

test("invalid UTF-8 is rejected", () => {
  assert.throws(() => verifyBytes(Buffer.from([0xff]), receiptBytes), /UTF-8/);
});

test("unpaired Unicode surrogate is rejected", () => {
  const invalid = Buffer.from('{"spec_version":"0.1","model_id":"\\ud800"}');
  assert.throws(() => verifyBytes(invalid, receiptBytes), /surrogate/);
});

test("unknown Core fields are rejected", () => {
  const bundle = JSON.parse(bundleBytes.toString("utf8"));
  bundle.extra = "not allowed";
  assert.throws(() => verifyBytes(Buffer.from(JSON.stringify(bundle)), receiptBytes), /exactly/);
});

test("files above 1 MiB are rejected", () => {
  assert.throws(() => verifyBytes(Buffer.alloc(1_048_577), receiptBytes), /exceeds/);
});
