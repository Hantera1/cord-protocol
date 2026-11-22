# CORD RFC 3161 Trusted Timestamp Profile

**Profile ID:** `org.cordprotocol.profile.rfc3161-timestamp`  
**Version:** 0.1.0  
**Status:** Experimental draft  
**Applies to:** CORD Ed25519 Signed Receipt Extension v0.1 and Trust Store v0.1

## 1. Purpose and security claim

This profile defines how an RFC 3161 Time-Stamp Token (TST) may establish that a specific CORD Ed25519 receipt-signature value existed no later than the TSA's asserted generation time.

The timestamp message imprint MUST cover the exact 64 raw Ed25519 signature octets decoded from the detached Signed Receipt v0.1 envelope's `signature` field. It MUST NOT cover a producer-declared timestamp, a JSON rendering of the envelope, or an unrelated caller-selected digest.

A valid result means the configured TSA accepted a matching message imprint and issued a verifiable token. It does not prove that receipt claims are true, that the signer is a particular person or organization, or that the signer created the signature at the exact generation time. The signature existed no later than that time.

## 2. Trust inputs and validation

The verifier MUST receive its TSA trust anchor through trusted local configuration or an authenticated administrative channel. A CA file, certificate, token, or URI supplied only inside the evidence package MUST NOT establish trust.

The verifier MUST validate the CMS SignedData signature, message imprint, TSTInfo, TSA certificate path, certificate purpose, and timestamping EKU. Implementations MUST NOT disable certificate-purpose checks or accept an arbitrary signer certificate as a trust anchor.

## 3. Result and policy

A verifier MUST report message-imprint validation, CMS signature validation, TSA certificate-path validation, timestamping-EKU validation, generation time, and the configured trust-anchor reference separately.

The timestamp result MUST be combined with, not substituted for:
1. Core bundle/receipt integrity verification;
2. Ed25519 receipt-signature verification;
3. Trust Store key resolution, role authorization, and lifecycle policy.

Only after timestamp validation returns PASS may its generation time be passed to the Trust Store resolver as `trusted_signature_time`. If timestamp verification is absent or fails, `receipt.created_at` MUST NOT be used as a substitute.

## 4. Revocation and historical validation

The initial reference implementation validates the TSA certificate path against an operator-configured CA file but does not perform online OCSP or CRL checks. Deployments MUST document their TSA certificate revocation policy and MUST NOT claim comprehensive historical validation when revocation status has not been checked.

## 5. Reference implementation

The reference implementation accepts DER token bytes, obtains exact signature bytes from a strict Signed Receipt v0.1 envelope, invokes OpenSSL without a shell, bounds token size and execution time, and returns generation time only after successful verification. OpenSSL version and configuration are part of the verifier's operational trust boundary.

## 6. Limitations

This profile does not provide a global TSA directory, select a TSA, prove the TSA's legal status, perform OCSP/CRL checks in the initial implementation, establish civil identity, or prove signed claims true. It is experimental and has not undergone independent security audit or interoperability review.
