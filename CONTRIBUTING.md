# Contributing to Cord

Thank you for your interest in contributing to Cord.

Cord is an experimental protocol exploring deterministic verification of AI events. Contributions that improve clarity, correctness, and interoperability are welcome.

---

## Ways to Contribute

You can contribute to Cord in several ways:

- improving the protocol specification
- proposing improvements to the bundle or receipt formats
- adding verification test vectors
- improving the reference verifier
- clarifying documentation

---

## Reporting Issues

If you find a problem in the specification, verifier, or documentation, please open a GitHub issue describing:

- what you observed
- why it appears incorrect
- a possible improvement if known

Clear and minimal examples are very helpful.

---

## Proposing Changes

When proposing changes to the Cord specification:

1. keep the protocol minimal
2. maintain deterministic verification
3. avoid introducing platform dependencies
4. preserve backward compatibility whenever possible

Large changes should be discussed in an issue before submitting a pull request.

---

## Test Vectors

When contributing new features to the specification, corresponding test vectors should be included when possible.

Test vectors help ensure independent implementations behave consistently.

---

## Code Contributions

Code contributions to the verifier should aim to:

- remain simple
- remain deterministic
- avoid unnecessary dependencies

The reference verifier exists to demonstrate protocol behavior, not to become a complex framework.

---

## Project Philosophy

Cord prioritizes:

- minimal design
- deterministic verification
- offline reproducibility
- independent implementation

Changes that increase complexity without improving verification guarantees may be declined.

---

## License

By contributing to this repository, you agree that your contributions will be licensed under the same license as the project.