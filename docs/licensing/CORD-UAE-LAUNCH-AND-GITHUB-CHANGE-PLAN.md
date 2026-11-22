# Cord UAE Launch and GitHub Change Plan

**Status:** Proposed plan. This document does not claim incorporation, trademark registration, completed legal review, production readiness or an executed UAE licence.

## 1. Agreed commercial direction
- Market: United Arab Emirates only.
- Partner model: non-exclusive.
- Proposed royalty: 2% of defined Net Cord-attributable Licence Revenue actually received.
- Attribution: required for separately licensed Cord Commercial products and approved Cord-branded services.
- Core: remains Apache License 2.0. Existing permissions are not restricted.
- Operating model: partner builds, hosts and operates its own customer solution and contracts with its own payment providers. Cord does not receive or hold customer funds or operate a payment gateway under the base licence.

## 2. Important scope boundary
Royalty does not apply to:
- use of Apache-licensed Core alone;
- unrelated partner revenue;
- the value of goods sold;
- payment principal or merchant settlement funds;
- marketplace GMV merely because a Cord evidence event exists.

Royalty applies only to identified, separately licensed Commercial Assets and/or licensed Cord-branded products/services, with revenue streams listed in a signed Product Schedule.

## 3. Public repository additions
Proposed public files:
- docs/licensing/CORD-UAE-ROYALTY-TERM-SHEET.md
- docs/licensing/CORD-ROYALTY-REPORTING-STANDARD.md
- docs/licensing/KENTPH-ATTRIBUTION-AND-BRAND-POLICY.md
- docs/licensing/CORD-UAE-LAUNCH-AND-GITHUB-CHANGE-PLAN.md

Public content must remain high-level and contain no signed contracts, private partner identities, customer data, bank details, private pricing beyond approved public terms, credentials, keys, tax returns or confidential legal advice.

## 4. Private-only materials
Keep outside the public repository:
- signed licence and trademark agreements;
- named partner due diligence and KYC documents;
- invoices, bank account details and tax documentation;
- actual royalty reports and audit evidence;
- confidential pricing, negotiations and partner commissions;
- counsel advice, risk assessments and non-public security reports;
- customer data, personal data, payment information and credentials.

## 5. UAE legal verification
Before signature, UAE counsel should verify:
- owner and registrability of CORD and KENTPH marks in the relevant classes;
- trademark licence drafting, notarisation/authentication, Arabic translation and filing/recordal requirements;
- the legal entity permitted to grant the licence and the Licensee's UAE business activity;
- local commercial, consumer, privacy, payment-services and advertising rules relevant to the actual product;
- enforceability of royalty, audit, quality-control, termination and dispute provisions.

The UAE Ministry of Economy & Tourism currently publishes a trademark-use licensing service and requirements. Confirm current process, fees and formalities at filing; do not rely on this repository document as a substitute for local advice.

## 6. Swedish legal and tax verification
Before signature, Swedish counsel/advisers should verify:
- legal licensor and IP chain-of-title;
- corporate authority and tax treatment of foreign royalty income;
- VAT treatment and invoicing;
- transfer pricing/related-party issues if applicable;
- permanent establishment and place-of-effective-management risks;
- contract law, liability and dispute enforcement.

## 7. Repository implementation sequence
1. Review this proposal against the existing master architecture and legal requirements.
2. Keep all commercial legal documents marked as drafts until counsel approval.
3. Add public README links only after the PR is reviewed.
4. Verify the Apache LICENSE file and NOTICE handling remain unchanged.
5. Do not add a mandatory KentPH notice to Core source files as a new restriction.
6. Do not publish private partner or royalty data.
7. Keep proprietary Commercial code in a separate private repository once entity and rights ownership are established.
8. Add CI checks for secrets, dependencies, schema validity and synthetic-only examples.
9. Do not issue a live licence ID until the licensor, rights and reporting controls are ready.

## 8. Launch gates
- Legal licensor incorporated/identified and authorised.
- Asset-by-asset chain-of-title signed and recorded.
- Trademark clearance and UAE filing strategy approved.
- UAE and Swedish legal/tax reviews complete.
- Definitive agreement and schedules signed.
- Licensee identity and UAE activity verified.
- Royalty report, invoice and audit processes tested.
- Brand quality-control process operational.
- Clear public product claims and responsibility boundaries.

## 9. Acceptance criteria for this PR
- Proposed 2% UAE non-exclusive model is documented consistently.
- Royalty base excludes unrelated sales and payment principal.
- Apache 2.0 Core boundary is explicit.
- KentPH attribution applies only to separately licensed commercial products/marks.
- Partner operational responsibilities and payment-provider boundary are explicit.
- No confidential partner, customer, tax or banking information is published.
- No claim is made that a company, trademark, contract or production service already exists.
