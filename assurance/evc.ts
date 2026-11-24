import { createHash } from "node:crypto";

export const SCHEMA_VERSION = "cord-evc-0.1";
export const MAX_GRAPH_BYTES = 2 * 1024 * 1024;
export const DEPENDENCY_TYPES = new Set([
  "SUBJECT_VERSION", "MODEL_VERSION", "CONFIGURATION", "TOOL_PERMISSION",
  "DATASET", "TEST_PROFILE", "VERIFIER_BUILD", "TRUST_ANCHOR",
  "SIGNING_KEY", "TIMESTAMP_POLICY", "EVIDENCE_ARTIFACT", "REGULATORY_PROFILE",
]);
const ROOT = ["schema_version", "graph_id", "subject", "current_state", "claims", "evidence", "dependencies"];
const SUBJECT = ["id", "version", "sha256"];
const STATE = ["type", "object_id", "sha256"];
const CLAIM = ["id", "statement", "scope", "evidence_ids"];
const EVIDENCE = ["id", "kind", "sha256"];
const DEPENDENCY = ["claim_id", "type", "object_id", "expected_sha256"];

export class EVCValidationError extends Error {
  constructor(message: string) { super(message); this.name = "EVCValidationError"; }
}
type Dict = Record<string, unknown>;
type Claim = { id: string; statement: string; scope: string; evidence_ids: string[] };
type Dependency = { claim_id: string; type: string; object_id: string; expected_sha256: string };
type Graph = {
  schema_version: string; graph_id: string;
  subject: { id: string; version: string; sha256: string };
  current_state: { type: string; object_id: string; sha256: string }[];
  claims: Claim[];
  evidence: { id: string; kind: string; sha256: string }[];
  dependencies: Dependency[];
};

function fail(message: string): never { throw new EVCValidationError(message); }
function isObject(v: unknown): v is Dict { return v !== null && typeof v === "object" && !Array.isArray(v); }
function nonempty(v: unknown): v is string { return typeof v === "string" && v.length > 0 && v.trim() === v; }
function exactFields(v: unknown, expected: string[], label: string): asserts v is Dict {
  if (!isObject(v) || Object.keys(v).length !== expected.length || expected.some(k => !Object.prototype.hasOwnProperty.call(v, k)))
    fail(label + " must contain exactly: " + [...expected].sort().join(", "));
}
function id(v: unknown, label: string): asserts v is string {
  if (!nonempty(v)) fail(label + " must be a non-empty trimmed string");
}
function digest(v: unknown, label: string): asserts v is string {
  if (typeof v !== "string" || !/^[0-9a-f]{64}$/.test(v)) fail(label + " must be a lowercase SHA-256 hex digest");
}
function scalarString(s: string): boolean {
  for (let i = 0; i < s.length; i++) {
    const c = s.charCodeAt(i);
    if (c >= 0xd800 && c <= 0xdbff) {
      if (i + 1 >= s.length) return false;
      const n = s.charCodeAt(++i);
      if (n < 0xdc00 || n > 0xdfff) return false;
    } else if (c >= 0xdc00 && c <= 0xdfff) return false;
  }
  return true;
}
function validateUnicode(v: unknown): void {
  if (typeof v === "string") { if (!scalarString(v)) fail("Graph contains an invalid Unicode surrogate"); return; }
  if (Array.isArray(v)) { for (const x of v) validateUnicode(x); return; }
  if (isObject(v)) for (const [k, x] of Object.entries(v)) { if (!scalarString(k)) fail("Graph contains an invalid Unicode object key"); validateUnicode(x); }
}

// Small strict JSON parser: unlike JSON.parse alone, it rejects duplicate object keys.
class StrictParser {
  private i = 0;
  constructor(private readonly s: string) {}
  parse(): unknown {
    this.ws(); const v = this.value(); this.ws();
    if (this.i !== this.s.length) fail("Unexpected trailing JSON data");
    return v;
  }
  private ws(): void { while (this.i < this.s.length && /[\u0020\u0009\u000a\u000d]/.test(this.s[this.i])) this.i++; }
  private string(): string {
    const start = this.i++;
    while (this.i < this.s.length) {
      const c = this.s.charCodeAt(this.i++);
      if (c === 0x22) {
        try { return JSON.parse(this.s.slice(start, this.i)) as string; }
        catch { return fail("Invalid JSON string"); }
      }
      if (c < 0x20) fail("Invalid control character in JSON string");
      if (c === 0x5c) {
        if (this.i >= this.s.length) fail("Incomplete JSON escape");
        const e = this.s[this.i++];
        if (e === "u") {
          const h = this.s.slice(this.i, this.i + 4);
          if (!/^[0-9a-fA-F]{4}$/.test(h)) fail("Invalid Unicode escape");
          this.i += 4;
        } else if (!'"\\/bfnrt'.includes(e)) fail("Invalid JSON escape");
      }
    }
    return fail("Unterminated JSON string");
  }
  private value(): unknown {
    this.ws(); const c = this.s[this.i];
    if (c === "{") return this.object();
    if (c === "[") return this.array();
    if (c === '"') return this.string();
    if (c === "t" && this.s.slice(this.i, this.i + 4) === "true") { this.i += 4; return true; }
    if (c === "f" && this.s.slice(this.i, this.i + 5) === "false") { this.i += 5; return false; }
    if (c === "n" && this.s.slice(this.i, this.i + 4) === "null") { this.i += 4; return null; }
    const m = this.s.slice(this.i).match(/^-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/);
    if (m) { this.i += m[0].length; const n = Number(m[0]); if (!Number.isFinite(n)) fail("Invalid JSON number"); return n; }
    return fail("Invalid JSON value");
  }
  private object(): Dict {
    this.i++; this.ws(); const out: Dict = {};
    if (this.s[this.i] === "}") { this.i++; return out; }
    while (true) {
      this.ws(); if (this.s[this.i] !== '"') fail("JSON object key must be a string");
      const k = this.string();
      if (Object.prototype.hasOwnProperty.call(out, k)) fail("Duplicate JSON object key: " + k);
      this.ws(); if (this.s[this.i++] !== ":") fail("Expected colon after JSON object key");
      out[k] = this.value(); this.ws();
      const c = this.s[this.i++]; if (c === "}") return out; if (c !== ",") fail("Expected comma in JSON object");
    }
  }
  private array(): unknown[] {
    this.i++; this.ws(); const out: unknown[] = [];
    if (this.s[this.i] === "]") { this.i++; return out; }
    while (true) {
      out.push(this.value()); this.ws();
      const c = this.s[this.i++]; if (c === "]") return out; if (c !== ",") fail("Expected comma in JSON array");
    }
  }
}
export function loadGraph(raw: Uint8Array): Graph {
  if (!(raw instanceof Uint8Array)) fail("Graph input must be bytes");
  if (raw.byteLength > MAX_GRAPH_BYTES) fail("Graph exceeds the 2 MiB input limit");
  if (raw.length >= 3 && raw[0] === 0xef && raw[1] === 0xbb && raw[2] === 0xbf) fail("UTF-8 BOM is not permitted");
  let decoded: string;
  try { decoded = new TextDecoder("utf-8", { fatal: true }).decode(raw); }
  catch { return fail("Graph must be valid UTF-8 JSON"); }
  const value = new StrictParser(decoded).parse();
  if (!isObject(value)) fail("Graph top level must be an object");
  validateUnicode(value);
  return value as unknown as Graph;
}
function validate(g: Graph) {
  exactFields(g, ROOT, "graph");
  if (g.schema_version !== SCHEMA_VERSION) fail("Unsupported EVC schema_version");
  id(g.graph_id, "graph_id");
  exactFields(g.subject, SUBJECT, "subject");
  id(g.subject.id, "subject.id"); id(g.subject.version, "subject.version"); digest(g.subject.sha256, "subject.sha256");
  if (!Array.isArray(g.evidence)) fail("evidence must be an array");
  const evidence = new Map<string, true>();
  g.evidence.forEach((e, i) => {
    exactFields(e, EVIDENCE, "evidence[" + i + "]");
    id(e.id, "evidence[" + i + "].id"); id(e.kind, "evidence[" + i + "].kind"); digest(e.sha256, "evidence[" + i + "].sha256");
    if (evidence.has(e.id)) fail("Duplicate evidence id: " + e.id); evidence.set(e.id, true);
  });
  if (!Array.isArray(g.claims)) fail("claims must be an array");
  const claims = new Map<string, Claim>();
  g.claims.forEach((c, i) => {
    exactFields(c, CLAIM, "claims[" + i + "]");
    id(c.id, "claims[" + i + "].id"); id(c.statement, "claims[" + i + "].statement"); id(c.scope, "claims[" + i + "].scope");
    if (claims.has(c.id)) fail("Duplicate claim id: " + c.id);
    if (!Array.isArray(c.evidence_ids) || c.evidence_ids.some(x => !nonempty(x))) fail("claims[" + i + "].evidence_ids must be an array of non-empty strings");
    if (new Set(c.evidence_ids).size !== c.evidence_ids.length) fail("claims[" + i + "].evidence_ids contains duplicates");
    const missing = c.evidence_ids.filter(x => !evidence.has(x)).sort(codePointCompare);
    if (missing.length) fail("claims[" + i + "] references unknown evidence: " + missing.join(", "));
    claims.set(c.id, c);
  });
  if (!Array.isArray(g.current_state)) fail("current_state must be an array");
  const current = new Map<string, string>();
  g.current_state.forEach((s, i) => {
    exactFields(s, STATE, "current_state[" + i + "]");
    if (!nonempty(s.type) || !DEPENDENCY_TYPES.has(s.type)) fail("current_state[" + i + "].type is unsupported");
    id(s.object_id, "current_state[" + i + "].object_id"); digest(s.sha256, "current_state[" + i + "].sha256");
    const k = s.type + "\u0000" + s.object_id;
    if (current.has(k)) fail("Duplicate current_state entry: " + s.type + ":" + s.object_id);
    current.set(k, s.sha256);
  });
  const byClaim = new Map<string, Dependency[]>();
  for (const key of claims.keys()) byClaim.set(key, []);
  if (!Array.isArray(g.dependencies)) fail("dependencies must be an array");
  const seen = new Set<string>();
  g.dependencies.forEach((d, i) => {
    exactFields(d, DEPENDENCY, "dependencies[" + i + "]");
    if (!nonempty(d.claim_id) || !claims.has(d.claim_id)) fail("dependencies[" + i + "] references unknown claim");
    if (!nonempty(d.type) || !DEPENDENCY_TYPES.has(d.type)) fail("dependencies[" + i + "].type is unsupported");
    id(d.object_id, "dependencies[" + i + "].object_id"); digest(d.expected_sha256, "dependencies[" + i + "].expected_sha256");
    const k = d.claim_id + "\u0000" + d.type + "\u0000" + d.object_id;
    if (seen.has(k)) fail("Duplicate dependency: " + d.claim_id + ":" + d.type + ":" + d.object_id);
    seen.add(k); byClaim.get(d.claim_id)!.push(d);
  });
  return { claims, current, byClaim };
}
function codePointCompare(a: string, b: string): number {
  const aa = Array.from(a, x => x.codePointAt(0)!); const bb = Array.from(b, x => x.codePointAt(0)!);
  for (let i = 0; i < Math.min(aa.length, bb.length); i++) if (aa[i] !== bb[i]) return aa[i] - bb[i];
  return aa.length - bb.length;
}
function stable(value: unknown): string {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return "[" + value.map(stable).join(",") + "]";
  const o = value as Dict;
  return "{" + Object.keys(o).sort(codePointCompare).map(k => JSON.stringify(k) + ":" + stable(o[k])).join(",") + "}";
}
export function evaluateGraph(g: Graph) {
  const { claims, current, byClaim } = validate(g);
  const results = [...claims.keys()].sort(codePointCompare).map(claimId => {
    const claim = claims.get(claimId)!; const reasons: string[] = [];
    let stale = false; let indeterminate = claim.evidence_ids.length === 0;
    if (indeterminate) reasons.push("NO_EVIDENCE_REFERENCED");
    const deps = [...byClaim.get(claimId)!].sort((a,b) => codePointCompare(a.type,b.type) || codePointCompare(a.object_id,b.object_id));
    if (!deps.length) { indeterminate = true; reasons.push("NO_DEPENDENCIES_DECLARED"); }
    for (const d of deps) {
      const k = d.type + "\u0000" + d.object_id; const observed = current.get(k);
      if (observed === undefined) { indeterminate = true; reasons.push("CURRENT_STATE_MISSING:" + d.type + ":" + d.object_id); }
      else if (observed !== d.expected_sha256) { stale = true; reasons.push("DEPENDENCY_CHANGED:" + d.type + ":" + d.object_id); }
    }
    const status = stale ? "STALE" : indeterminate ? "INDETERMINATE" : "VALID";
    if (status === "VALID") reasons.push("ALL_DECLARED_DEPENDENCIES_MATCH");
    return { claim_id: claimId, status, statement: claim.statement, scope: claim.scope,
      evidence_ids: [...claim.evidence_ids].sort(codePointCompare), dependency_count: deps.length,
      reasons: reasons.sort(codePointCompare) };
  });
  const statuses = new Set(results.map(x => x.status));
  const status = statuses.has("STALE") ? "STALE" : results.length === 0 || statuses.has("INDETERMINATE") ? "INDETERMINATE" : "VALID";
  const normalized: Dict = { ...g,
    claims: [...g.claims].sort((a,b) => codePointCompare(a.id,b.id)),
    evidence: [...g.evidence].sort((a,b) => codePointCompare(a.id,b.id)),
    current_state: [...g.current_state].sort((a,b) => codePointCompare(a.type,b.type) || codePointCompare(a.object_id,b.object_id)),
    dependencies: [...g.dependencies].sort((a,b) => codePointCompare(a.claim_id,b.claim_id) || codePointCompare(a.type,b.type) || codePointCompare(a.object_id,b.object_id)),
  };
  const graphSha = createHash("sha256").update(stable(normalized), "utf8").digest("hex");
  return { evc_version: SCHEMA_VERSION, graph_id: g.graph_id, graph_sha256: graphSha, status,
    claim_count: results.length, claims: results,
    limitations: [
      "This result evaluates declared dependency freshness only.",
      "Evidence digests are identifiers; evidence bytes are not supplied or verified here.",
      "This prototype does not authenticate issuers, signatures, timestamps, or change events.",
      "A VALID result does not establish factual truth, safety, legal compliance, or completeness.",
    ] };
}
