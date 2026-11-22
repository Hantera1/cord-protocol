import test from "node:test";
import assert from "node:assert/strict";
import { canonicalCoreJson, sha256, verifyCore, CordValidationError } from "../dist/index.js";

const bundle = {spec_version:"0.1",model_id:"demo-model",timestamp:"2026-03-06T12:00:00Z",policy_id:"cord-output-v0.1",input_hash:"1".repeat(64),output_hash:"2".repeat(64)};
const bytes = new TextEncoder().encode(JSON.stringify(bundle, null, 2) + "\n");
const receipt = {spec_version:"0.1",bundle_hash:sha256(canonicalCoreJson(bundle)),bundle_file_hash:sha256(bytes),created_at:"2026-03-06T12:00:05Z"};

test("verifies Core v0.1 fixture", () => assert.equal(verifyCore(bundle,receipt,bytes).status,"PASS"));
test("rejects tampered file bytes", () => assert.throws(()=>verifyCore(bundle,receipt,new TextEncoder().encode("tampered")),CordValidationError));
test("rejects unknown fields", () => assert.throws(()=>verifyCore({...bundle,extra:"no"},receipt,bytes),CordValidationError));
test("rejects unsupported versions", () => assert.throws(()=>verifyCore({...bundle,spec_version:"0.2"},receipt,bytes),CordValidationError));
