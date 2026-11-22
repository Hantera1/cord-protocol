# Cord Legal, Privacy and Security Requirements

Status: checklist for qualified legal counsel and security review. This is not a legal opinion, certification or guarantee of compliance.

## Mandatory release gate
No commercial launch, customer-data onboarding or paid license issuance until the responsible legal entity, rights chain, contracts, data flows, security controls and country-specific reviews are approved and documented.

## Data protection
For each processing activity document controller, processor and subprocessors; purposes; data categories; lawful basis and notices; data minimization; retention, deletion and backup expiry; data-subject request workflow; processor agreements; international transfer mechanisms and transfer-risk assessment where required; and security measures.

Complete a DPIA where processing is likely to result in high risk. Do not place personal data in public evidence bundles or public GitHub examples. Pseudonymized data remains personal data where re-identification is possible.

## Security controls
- MFA for privileged accounts; least privilege and periodic access review.
- Separate development, test, staging and production environments.
- Secret manager for credentials; no secrets in source, issues, logs or CI artifacts.
- Encryption in transit and at rest; documented key ownership, rotation, revocation and recovery.
- Signed/authenticated webhooks, replay protection, idempotency and request validation.
- Dependency, container, static-code and secret scanning; push protection where available.
- Branch protection, required review and controlled release process.
- Centralized security logs with restricted access and retention policy.
- Tested backups, restore procedures, incident response and vulnerability disclosure.
- Threat modelling and independent security review before production.

## Contracts and commercial licensing
Prepare and review customer terms, service description, commercial license agreement, order form, acceptable-use/security terms, SLA/support terms if offered, data processing agreement, subprocessor terms, confidentiality, partner/reseller agreement, IP assignments and contributor agreements, verification limitations, liability, indemnity, insurance and dispute resolution.

Reseller, master distribution, white-label and sublicensing rights must be explicit. No license certificate until the issuer has verified authority to license the relevant asset and the license is active.

## Payment and financial-services boundary
Initial scope: Cord records provider-generated payment references and status evidence. A regulated payment provider processes and holds funds. Cord does not store card security codes, payment credentials, wallet seed phrases or customer funds.

Before adding payment initiation, acquiring, money remittance, custody, exchange, stored value or crypto-asset services, obtain a jurisdiction-specific regulatory perimeter analysis and any required authorization. Actual product behavior controls the legal analysis.

## Electronic signatures and trust services
Use a suitable established provider for identity verification, signing and trusted timestamps. Describe signature level and provider role accurately. Do not claim Cord is a qualified trust service provider or that a signature is qualified unless the relevant service and provider status are verified.

## Market data and AI analysis
Before ingestion verify lawful access and API permission; database rights, copyright and website terms; rights to store, normalize, derive, display and redistribute data; provenance, timestamps, source reliability and corrections; personal data in listings; and model evaluation and human oversight.

Display asking prices separately from completed sale prices. Disclose sample size, date range, geography, currency, condition assumptions, fees, data gaps and uncertainty. Do not promise investment returns or present an estimate as an appraisal or authentication certificate.

## Watches and physical assets
Cord may preserve evidence and attestations supplied by qualified parties. It must not independently claim physical authenticity, title, condition, provenance or valuation unless supported by an identified competent source and scope. Avoid public full serial numbers, owner names, home addresses, insurance documents and precise storage locations.

## Jurisdictional review
Sweden/EU review should cover GDPR, ePrivacy/cookies where relevant, consumer and e-commerce law, marketing rules, electronic signatures/eIDAS, payment-services perimeter, IP/database rights, tax/accounting and AI Act applicability by actual intended use.

UAE review should cover federal and any applicable free-zone data-protection rules, cross-border transfers, e-commerce/consumer rules, electronic transactions/signatures, payment and financial-services perimeter, IP, tax and local licensing. DIFC and ADGM regimes must be assessed separately if used.

## Evidence of approval
Maintain a private compliance register with requirement ID, product/version, jurisdiction, responsible reviewer, evidence, approval date, review date and unresolved exceptions. Do not publish counsel advice, personal data, customer contracts or security-sensitive findings in the public repository.
