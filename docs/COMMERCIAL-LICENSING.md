# Cord Trade Commercial Licensing Framework

**Status: commercial design draft — not a signed legal agreement.**

## 1. Product being licensed

The commercial product is the **Cord Trade Commercial Package**, which may include:
- proprietary trade-agreement templates, schedules, clauses, checklists and workflow materials;
- paid Cord Trade software modules, hosted services, API access and integrations;
- Cord Trade brand assets and approved marketing materials;
- training, implementation, support and partner certification.

The customer is buying a defined right to use these commercial materials and services. The customer is not buying Cord Core, ownership of the protocol, or ownership of the Cord brand.

**Important open-source boundary:** Cord Core is published under Apache License 2.0. Rights already granted under that license cannot be withdrawn from recipients simply by introducing a paid commercial license. Commercial licensing must therefore cover clearly separated proprietary materials, paid services, trademarks, hosted features, support and partner rights. Do not describe the Apache-licensed Core itself as locked or exclusively owned.

## 2. Separate rights and deliverables

| Layer | Rights model |
|---|---|
| Cord Core code already under Apache 2.0 | Open-source license; preserve its existing grant and notices |
| Cord Trade extension code | Confirm repository license and ownership before deciding commercial terms |
| Proprietary agreement templates and playbooks | Commercial copyright license, if chain of title is established |
| Cord name/logo and certification marks | Trademark/brand permission; registration strategy required |
| Hosted API, dashboard and integrations | Subscription/service terms |
| Implementation and support | Services agreement / statement of work |
| Signed transaction agreement between buyer and seller | The contracting parties own/control their executed contract subject to their agreement and law; Cord does not claim ownership |

## 3. License products

### A. Business Use License
For one legal entity using the Cord Trade templates and paid workflow in its own business. Define users, locations, annual agreement volume, permitted use and term.

### B. Professional / Group License
For a group of related companies or a larger dealer/auctioneer. Each legal entity and branch must be named or counted.

### C. Authorized Reseller License
For a partner marketing and reselling Cord Trade licenses in a named territory. It must state whether the partner acts as agent or buys/resells in its own name. No authority to amend templates, promise legal outcomes, issue certificates, or appoint sub-resellers unless expressly granted.

### D. Country / Master Distribution License
Only for a proven partner with minimum annual sales, reporting, training, compliance checks and performance milestones. Exclusivity should be conditional, time-limited and territory-specific—not granted merely for interest.

### E. White-label License
A separate premium agreement allowing approved rebranding. Cord ownership notices, protocol attribution and security disclosures must remain where contractually required.

## 4. License controls

Every issued license must have:
- unique immutable `license_id`;
- exact legal licensor and licensee names, registration numbers and addresses;
- product/package and version;
- territory and language rights;
- named permitted legal entities, users, branches and/or annual transaction volume;
- start date, expiry date, renewal date and status;
- fee, currency, payment schedule, tax treatment and royalty if applicable;
- sublicensing/resale rights (default: none);
- authorized domain names and integrations where relevant;
- signed master agreement and evidence hashes;
- issuer, approver and audit history.

Status values: `DRAFT`, `PENDING_PAYMENT`, `ACTIVE`, `SUSPENDED`, `EXPIRED`, `TERMINATED`, `REVOKED`.

Do not activate a license until the agreement is signed, required due diligence is completed, and payment or approved credit terms are recorded.

## 5. Technical enforcement model

Use a hybrid model:
1. A private licensing registry is the commercial system of record.
2. The licensee receives a digitally signed license certificate (JSON/PDF) containing the license ID, product, territory, entitlements, issue time and expiry.
3. Paid cloud/API/template downloads check the live license status and entitlement.
4. Offline-capable tools accept a signed, time-limited license token with explicit expiry and grace period.
5. Revocation and suspension are recorded as new registry events; never silently overwrite history.
6. A public verification page exposes only minimal status: license ID, product, territory, validity and issuer. Do not expose personal data, price, contract or sales figures.
7. Customer-owned completed agreements and evidence packages remain exportable after termination, subject to lawful retention and privacy rules.

Do not rely on hiding source code, minification, or a secret key embedded in a client application. Server-side signing keys belong in KMS/HSM, never in GitHub or a browser/mobile app. The offline verifier must be able to validate the issuer signature against a published public key.

## 6. Sales and royalty control

The license registry must connect each license to:
- lead/source and sales owner;
- reseller/partner code, if any;
- quote and order ID;
- signed contract ID and hash;
- invoice number, payment status and receipt reference;
- license issue/activation event;
- renewals, upgrades, downgrades, cancellations and refunds;
- commission/royalty calculation, reporting period and payment status.

For reseller agreements, require monthly or quarterly reports containing license ID, end customer legal entity, territory, package, sale date, gross sale, discounts, tax, net revenue, refunds and commission due. Include audit rights, record retention, under-reporting remedies and a clear payment timetable.

Use one system as the source of truth. CRM manages pipeline; accounting software manages invoices and ledger; Cord License Registry manages license entitlements and status. Reconcile them using stable IDs—do not treat GitHub as the sales database.

## 7. Recommended sales process

1. Qualify lead and country/sector.
2. Verify the prospective customer's legal entity and beneficial ownership as appropriate.
3. Select license type, territory, use case and volume.
4. Issue a quote with unique quote ID.
5. Sign the correct bilingual agreement version.
6. Invoice and confirm payment/credit approval.
7. Issue signed license certificate and activate entitlements.
8. Record onboarding, training and authorized users.
9. Monitor usage and partner reporting.
10. Renew, expand, suspend or terminate with an auditable event.

## 8. Ownership and chain-of-title gate

Do not state that a company owns Cord IP until evidence supports it. Before selling:
- identify the exact legal entity that will be licensor;
- obtain written IP assignments from every contributor/contractor covering relevant code, documentation, templates, translations, designs and brand assets;
- record pre-existing third-party/open-source components and their licenses;
- preserve Git history, dated releases, source files, contributor agreements and signed assignment documents;
- check the Cord name/logo for conflicts and file trademark applications in relevant classes and territories;
- consider copyright registration for eligible original works and keep the registration receipt;
- have counsel review the ownership chain and commercial license.

The existing public attribution “Cord by Hantera by KentPH” is project attribution, not by itself proof of legal ownership or assignment to a company. The legal licensor remains **TO BE CONFIRMED** until the assignment and entity documents are signed.

## 9. Dubai / UAE channel plan

Start with a non-exclusive UAE pilot partner, not an exclusive country license. The partner should:
- be a properly licensed UAE legal entity;
- have an identified beneficial owner and authorized signatory;
- sign the reseller agreement and confidentiality terms;
- sell only approved products and Arabic/English versions;
- report every license sale and customer;
- use approved claims and never represent Cord as a government-approved trust provider or legal certification unless that status is independently obtained;
- follow applicable UAE and customer-country rules on marketing, data, consumer protection, sanctions and AML/KYC where relevant.

Cord should integrate a qualified/licensed electronic-signature or trust-service provider where required rather than claiming to be one. Validate the exact UAE rules and licensing implications with local counsel before launch.

## 10. Contract terms that counsel must finalise

Governing law and dispute forum; license grant and restrictions; term and renewal; fees, VAT/tax and withholding; reporting and audit; confidentiality; personal-data roles and cross-border transfers; security; warranties and disclaimers; liability cap and exclusions; indemnities; IP infringement process; suspension/termination; export/retention; sanctions/anti-bribery; language precedence; and enforceability in each territory.

## 11. Launch gates

No commercial license is to be issued until:
- the legal licensor is confirmed and chain of title signed;
- product boundary and included materials are inventoried;
- trademark clearance and filing plan are complete;
- English master license and Arabic translation are reviewed by qualified counsel;
- pricing, tax and partner commission rules are approved;
- license registry, signed certificate and audit log are tested;
- privacy, security and customer support procedures are ready.
