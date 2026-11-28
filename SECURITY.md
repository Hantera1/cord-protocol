# CORD Security Policy

CORD takes security reports seriously. This policy applies to the protocol specifications, reference implementations, test infrastructure, and other security-sensitive code in this repository.

## Reporting a vulnerability

**Please do not publish exploitable vulnerability details in a public issue or pull request.**

Use GitHub's **Report a vulnerability** function for this repository if private vulnerability reporting is enabled. If it is not available, contact the repository maintainer privately through GitHub to arrange a confidential reporting channel. Do not include exploit details in a public message.

A useful report should include, where possible:

- the affected component, file, version, or commit;
- the conditions required to reproduce the issue;
- the security impact and affected trust boundary;
- a minimal reproduction or proof of concept;
- any suggested mitigation.

Please allow the maintainer reasonable time to investigate and coordinate a fix before public disclosure. The appropriate disclosure timeline will depend on severity, exploitability, and the availability of a mitigation.

## Scope

Reports may concern, for example:

- parser or verifier vulnerabilities;
- canonicalization or hash-validation inconsistencies;
- signature verification or key-trust failures;
- timestamp validation or trust-store handling;
- event-chain or checkpoint validation;
- denial-of-service or resource-exhaustion conditions;
- unsafe handling of untrusted evidence packages;
- CI, release, or dependency-supply-chain weaknesses.

## Current security and maturity limitations

CORD Core v0.1 and its extensions are experimental. The repository does not claim that CORD has undergone an independent security audit, formal verification, or comprehensive third-party interoperability review.

A successful CORD Core verification establishes only the integrity-consistency properties defined by the supported Core specification. It does not, by itself, prove identity, authorship, model provenance, trusted time, factual correctness, completeness, safety, or legal/regulatory compliance.

Experimental extensions have their own trust assumptions and limitations. Review the relevant specification and [Security Model](docs/SECURITY-MODEL.md) before relying on them.

## Security response

The maintainer will assess a report, determine affected versions and components, and decide on mitigation, fixes, tests, and coordinated disclosure. Not every report will result in a code change; design limitations and documentation issues may require a specification clarification or an explicit statement of non-goals.

Security fixes should include regression tests where practical. Public advisories should describe affected versions, impact, mitigations, and fixed versions without unnecessarily exposing exploit details.

## Security-related contributions

For proposed security improvements, include the threat model, trust assumptions, expected failure behavior, and relevant positive and negative tests. A passing automated test suite is not a substitute for independent security review.
