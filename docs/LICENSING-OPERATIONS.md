# Cord License Registry — Operating Model

## System of record
The private Cord License Registry is the authoritative record for license issuance, entitlements, payments, partner attribution and status. It is not the public Cord evidence chain and must not publish customer commercial data.

## Required records
- Organization: legal name, jurisdiction, registration number, address, beneficial-owner review status, authorized signatory.
- License: license ID, organization ID, product, version, territory, permitted entities, user cap, annual agreement cap, term, status.
- Contract: agreement ID, version/language, signed PDF hash, signing provider reference, signed timestamp.
- Order: quote/order IDs, currency, price, discounts, tax, reseller code.
- Payment: invoice reference, payment provider, received amount, currency, received date, refund/chargeback status.
- Partner settlement: gross sales, permitted deductions, commission rate, net amount, reporting period, paid status.
- Audit event: actor, event type, timestamp, previous event reference, evidence hash.

## Access control
- Sales can create leads, quotes and draft license applications.
- Legal/admin approves legal entity, contract version and license terms.
- Finance confirms payment, refunds, tax and commissions.
- License service alone can activate/suspend/revoke entitlements after authorized approvals.
- Partner accounts see only their own downstream customers and sales.
- Auditor role is read-only and logged.

## Minimum audit events
`lead.created`, `quote.issued`, `license.applied`, `contract.signed`, `invoice.issued`, `payment.confirmed`, `license.activated`, `entitlement.changed`, `usage.recorded`, `partner.reported`, `commission.calculated`, `renewal.completed`, `license.suspended`, `license.terminated`, `refund.issued`.

## Public verification
Public lookup should return only:
- license ID;
- product name and version;
- status (active / expired / suspended / terminated);
- territory at a coarse level;
- validity period;
- issuing licensor name after legal ownership is confirmed.

Never return customer personal data, exact address, pricing, contract files, invoice numbers, payment references, usage volumes or partner commissions.

## Reconciliation
Monthly reconcile:
1. active licenses against signed agreements;
2. active licenses against paid invoices/approved credit;
3. partner-reported sales against license activations;
4. commission calculations against partner invoices;
5. renewals/expiries against access entitlement changes.

Keep an immutable audit trail. Corrections are new events with references to the prior event.
