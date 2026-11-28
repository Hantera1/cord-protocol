# Contributing to CORD

Thank you for your interest in contributing to CORD.

CORD is an open, vendor-neutral protocol project. The current Core specification and reference implementation are experimental drafts. Contributions are welcome, especially those that improve correctness, security, clarity, and interoperability.

## Ways to contribute

You can help by:

- reviewing the Core and extension specifications;
- identifying ambiguities, inconsistencies, or security assumptions;
- adding positive, negative, and boundary test vectors;
- improving the reference verifier and its tests;
- developing independent implementations and interoperability tests;
- improving SDKs, examples, and developer documentation.

## Before proposing a change

For substantial protocol or architecture changes, open an issue or discussion first. Explain the problem and the intended scope before investing in an implementation.

A useful proposal should include, where relevant:

1. the problem and motivation;
2. the affected specification, implementation, or profile;
3. compatibility and migration considerations;
4. security and privacy implications;
5. test vectors and expected verifier behavior;
6. documentation updates.

## Protocol design expectations

Contributions should preserve the project's core principles:

- Keep Core minimal and implementation-neutral.
- Preserve deterministic verification semantics.
- Keep optional extensions separate from Core.
- State trust assumptions and limitations explicitly.
- Fail closed on unsupported or malformed normative input.
- Avoid platform-specific dependencies in the Core protocol.
- Do not claim that hashes or signatures prove facts beyond their defined cryptographic properties.

Changes to CORD Core v0.1 must not be introduced indirectly through an extension or application profile. Any proposed Core change must be explicitly identified and reviewed as a Core change.

## Code and test contributions

Code contributions should include appropriate automated tests. Protocol changes should include test vectors that cover valid inputs, invalid inputs, boundary conditions, and relevant adversarial cases.

Where more than one implementation exists, shared conformance vectors should be used to compare complete verification results—not merely whether each implementation exits successfully.

Keep changes focused. Avoid adding dependencies or complexity unless they provide a clear, documented benefit.

## Pull request checklist

Before submitting a pull request:

- [ ] Describe the problem and the proposed solution.
- [ ] Identify whether the change affects Core, an extension, a profile, tooling, or documentation.
- [ ] Add or update tests and test vectors where applicable.
- [ ] Update relevant specifications and documentation.
- [ ] State what was tested and where the test results came from.
- [ ] List known limitations and any work that remains incomplete.
- [ ] Avoid production, certification, interoperability, or security-audit claims unless supported by published evidence.

A passing CI run is useful implementation evidence. It is not, by itself, an independent security audit or proof of interoperability.

## Review and acceptance

Submitting a pull request does not mean the change is accepted. Changes may require design discussion, security review, compatibility analysis, or additional test coverage before merge.

Experimental proposals should remain clearly labelled as proposals until their review and implementation requirements have been met.

## License

CORD is published under the Apache License 2.0. By submitting a contribution, you agree that your contribution may be distributed under that license.
