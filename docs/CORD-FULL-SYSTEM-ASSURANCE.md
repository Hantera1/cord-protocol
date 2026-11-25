# CORD Full-System Assurance Agent v0.1

**Status:** Architecture proposal; not implemented  
**Maturity:** Design draft  
**Security posture:** Read-only by default; fail closed  
**Scope:** Repository-wide and system-wide security assessment of CORD

This document defines the proposed CORD Agent capability for continuously inspecting the CORD repository and its implemented components. It is a design contract, not evidence that an agent, scanner, sandbox, or automated remediation service currently exists.

## 1. Objective

CORD Full-System Assurance (FSA) is intended to identify, reproduce, explain, track, and retest security weaknesses across the complete CORD system—not merely review isolated files.

It must inspect the relationship between:
- normative specifications and schemas;
- reference implementations and SDKs;
- tests, fixtures, and cross-language vectors;
- dependency and build configuration;
- CI workflows and release configuration;
- trust inputs, key lifecycle, timestamping, and event checkpoints;
- documented claims, actual behavior, and known limitations.

The agent must distinguish an observed fact from an inference, hypothesis, or unverified concern.

## 2. Non-goals and prohibited claims

FSA is not:
- a proof that CORD is secure;
- a substitute for independent human security review, penetration testing, or formal verification;
- an oracle of factual truth or legal compliance;
- an authority that can approve its own findings or release;
- a mechanism for silently changing protocol behavior.

A clean scan or passing test suite must never be reported as proof that no vulnerabilities exist.

## 3. Security invariants

1. **Read-only default:** repository inspection cannot write to the repository, alter settings, create releases, or access production credentials.
2. **Least privilege:** each capability receives only the minimum read or execution permissions required.
3. **No untrusted execution on the host:** repository code, tests, build scripts, and fixtures are untrusted inputs and must run only in a disposable, isolated environment.
4. **No secrets in the analysis context:** do not expose secret values to the model, logs, reports, prompts, or artifacts. Secret detection should report location and type, with values redacted.
5. **Fail closed:** missing evidence, unavailable tools, timeouts, parser failures, and incomplete scans produce INDETERMINATE or INCOMPLETE—not PASS.
6. **Evidence-linked findings:** every finding must identify the commit, file and line/range where possible, reproduction method, observed output, and confidence.
7. **Independent verification:** the component that proposes a finding cannot be the sole component that validates its severity or closure.
8. **No self-approval:** the agent cannot approve its own pull request, dismiss its own finding, change branch protection, or authorize a release.
9. **Reproducibility:** record tool versions, configuration, commit SHA, test commands, environment constraints, and artifact hashes.
10. **Explicit coverage:** every report lists inspected, excluded, skipped, and failed-to-inspect areas.

## 4. Proposed architecture

### 4.1 Read-only Repository Collector

Collects a snapshot at a pinned commit SHA:
- tracked files and repository tree;
- specs, schemas, source code, SDKs, examples, tests, and test vectors;
- dependency manifests and lockfiles;
- workflow definitions and repository security configuration that the integration is authorized to read;
- PR and release metadata where available.

The collector must not follow symlinks outside the checked-out workspace. It must not fetch arbitrary URLs or execute repository-provided code.

### 4.2 System Mapper

Builds a versioned component inventory and dependency graph. Each node records:
- component identifier and version/status;
- source files and normative specifications;
- direct and transitive dependencies;
- inputs, outputs, trust boundaries, and external services;
- tests and test vectors;
- security properties claimed and properties explicitly not established.

Unmapped or orphaned components are reported as coverage gaps.

### 4.3 Specification-to-Implementation Auditor

Compares normative requirements with implementation and tests. It identifies:
- requirements without implementation;
- implementation behavior not covered by a requirement;
- tests that do not assert the claimed property;
- mismatches between Python/TypeScript or other runtimes;
- inconsistent status names, error handling, canonicalization, and version behavior;
- documentation claims stronger than the code or evidence supports.

The agent must cite the exact requirement and implementation evidence for each discrepancy.

### 4.4 Static Security Analyzer

Runs approved, pinned analysis tools for:
- unsafe parsing and serialization;
- resource exhaustion and unbounded input;
- path traversal and filesystem race conditions;
- unsafe subprocess and shell use;
- cryptographic misuse and weak defaults;
- authorization and trust-boundary mistakes;
- dependency vulnerabilities and license metadata;
- secret exposure, with all discovered values redacted;
- insecure CI permissions and mutable third-party actions.

Tool output is evidence to triage, not automatically a confirmed vulnerability.

### 4.5 Adversarial Test Planner and Runner

Converts threat-model risks into bounded, reproducible tests:
- malformed and ambiguous input;
- oversized and deeply nested data;
- Unicode and canonicalization edge cases;
- tampered, replayed, reordered, omitted, or substituted evidence;
- invalid, expired, revoked, or unauthorized keys;
- timestamp and checkpoint edge cases;
- cross-runtime differential tests;
- fuzz and property-based tests where a bounded harness exists.

All execution occurs in a disposable sandbox with no network by default, no host credentials, read-only source mounts where practical, CPU/memory/time limits, and bounded output. Network access requires a separately approved test profile and explicit allowlist.

### 4.6 Independent Result Verifier

A separate verifier checks:
- whether the reproduction actually demonstrates the claimed behavior;
- whether the evidence belongs to the pinned commit;
- whether the proposed severity follows the documented rubric;
- whether a fix closes the original case without weakening another invariant;
- whether regression tests fail before and pass after the change.

It must not simply repeat the primary model's conclusion. Where practical, use a different implementation, deterministic checks, or independent human review.

### 4.7 Findings and Assurance Ledger

Stores append-only, versioned records. A finding contains:
- stable finding ID;
- affected component and commit SHA;
- severity and confidence as separate fields;
- status: OPEN, CONFIRMED, DISPUTED, ACCEPTED_RISK, FIX_PROPOSED, FIXED_PENDING_RETEST, CLOSED, or INDETERMINATE;
- exact evidence and reproduction steps;
- impact, prerequisites, and affected security properties;
- owner, remediation reference, and retest evidence;
- scan coverage and tool versions.

A finding may be closed only after independent retesting. Accepted risk requires a named human decision-maker, rationale, scope, and review/expiry date.

## 5. Trust and result model

FSA must not collapse different properties into one green check. Report at least:

| Dimension | Question |
|---|---|
| Integrity | Do the observed bytes match the recorded digest? |
| Authenticity | Is the source or signer authenticated? |
| Authorization | Was that signer or actor permitted to make this claim? |
| Freshness | Is the evidence current relative to a trusted state? |
| Trusted time | Is time independently validated? |
| Observation | Was the relevant event actually observed? |
| Coverage | What systems, periods, and events were covered or omitted? |
| Correctness | Does the implementation satisfy the normative requirement? |
| Resilience | Does it withstand the defined adversarial tests? |

A pass in one dimension must never imply a pass in another. Silence or missing data is not proof that no event occurred.

## 6. Severity and reporting

Use a documented severity rubric based on impact, exploitability, prerequisites, scope, and confidence. Keep severity and confidence separate.

Every run produces:
1. executive summary and exact commit SHA;
2. coverage statement, including exclusions and failed checks;
3. component/dependency map;
4. findings grouped by severity and status;
5. confirmed reproductions and raw, redacted evidence;
6. specification-to-code gaps;
7. test and tool results;
8. residual risks and unresolved questions;
9. comparison with the previous run.

Do not use a single overall PASS if any critical area was not inspected. Prefer explicit states such as COMPLETE_WITH_FINDINGS, COMPLETE_NO_FINDINGS_WITHIN_SCOPE, PARTIAL, FAILED, and INDETERMINATE.

## 7. Controlled remediation workflow

Remediation is a separate capability and is disabled by default.

When enabled by an authorized human:
1. FSA creates a proposed patch on an isolated branch.
2. The patch includes regression tests and a security rationale.
3. CI runs against the exact patch commit.
4. Independent Result Verifier evaluates the fix.
5. A human reviews and approves the pull request.
6. The protected default branch enforces required checks and approvals.

The agent must never merge its own patch, change branch protections, rotate production keys, alter trust anchors, or deploy to production.

## 8. Execution phases

### Phase 0 — Inventory and read-only baseline
- Pin the commit SHA.
- Enumerate files, components, specifications, tests, dependencies, and workflows.
- Produce a coverage map and identify missing ownership or documentation.

**Exit:** inventory is reproducible and all exclusions are explicit.

### Phase 1 — Threat and requirements mapping
- Create a threat model for each component and trust boundary.
- Map normative requirements to code and tests.
- Identify untested security claims.

**Exit:** each in-scope component has a reviewed threat model and requirement map.

### Phase 2 — Static analysis and bounded adversarial tests
- Run pinned static analyzers and dependency checks.
- Execute approved tests in an isolated sandbox.
- Add regression tests only through reviewed pull requests.

**Exit:** findings have reproducible evidence or are explicitly marked unconfirmed.

### Phase 3 — Independent validation
- Reproduce high-impact findings independently.
- Verify fixes and regression tests.
- Review coverage gaps and false-positive rates.

**Exit:** independent review is recorded; no agent self-approval.

### Phase 4 — Continuous assurance
- Re-run on every proposed change and scheduled baseline.
- Compare findings and component graph across commits.
- Alert on new regressions, newly exposed dependencies, and coverage loss.

**Exit:** monitoring is reliable, access is controlled, and reports are auditable.

## 9. Initial CORD assessment scope

The first inventory should include at least:
- Core verifier and canonicalization;
- signed receipts and Ed25519 handling;
- Trust Store parsing, pinning, roles, key lifecycle, and revocation;
- RFC 3161 timestamp verification and OpenSSL invocation;
- event-chain construction and external checkpoint assumptions;
- EVC Python and TypeScript implementations and shared vectors;
- Proof of Observation proposals and their implementation status;
- CI workflows, dependency manifests, repository permissions, and release process;
- specifications, schemas, examples, and public claims.

Proposals and documentation-only designs must be labelled as such, not treated as implemented capabilities.

## 10. Initial implementation boundary

The first software milestone should be a local, read-only inventory and report generator—not an autonomous coding agent.

Minimum safe MVP:
- accepts an explicit repository path and commit SHA;
- refuses to run outside the selected workspace;
- inventories files without executing them;
- applies size and traversal limits;
- redacts secret-like values;
- produces deterministic JSON findings and a human-readable report;
- marks unsupported checks as NOT_RUN;
- records hashes of inputs and outputs;
- has tests for symlinks, path traversal, oversized files, malformed encodings, secret redaction, and incomplete scans.

Only after this MVP passes review should isolated static-analysis and test-runner adapters be added.

## 11. Known limitations

This proposal does not implement the agent, sandbox, scanners, ledger, or continuous monitoring. It does not yet define a signed report format, remote multi-tenant execution, model-provider isolation, or an external witness service. Those require separate threat models and specifications before implementation.
