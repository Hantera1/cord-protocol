# Cord License Sales Ledger — Data Model

The registry is a private operational system. It must not be implemented as a public GitHub issue list or public blockchain.

## Entities and IDs
- `organization_id`: legal entity/customer/partner.
- `lead_id`: CRM lead.
- `quote_id`: commercial quote.
- `order_id`: accepted order.
- `agreement_id`: signed license agreement version.
- `license_id`: immutable commercial entitlement ID.
- `invoice_id`: accounting invoice.
- `payment_id`: payment provider/accounting reference.
- `partner_id`: authorized channel partner.
- `commission_id`: partner settlement.
- `audit_event_id`: append-only event identifier.

## Required events
`lead.created`, `lead.qualified`, `quote.issued`, `order.accepted`, `agreement.signed`, `invoice.issued`, `payment.confirmed`, `license.issued`, `license.activated`, `license.entitlement_changed`, `license.suspended`, `license.renewed`, `license.expired`, `license.terminated`, `partner.sale_reported`, `commission.calculated`, `commission.paid`, `refund.issued`.

## Reconciliation rules
- Every ACTIVE license must reference an executed agreement and a confirmed payment or approved credit record.
- Every reseller-issued customer license must reference a valid partner entitlement.
- Partner-reported sales must reconcile to issued license IDs.
- Refund, chargeback and termination events must update entitlements according to the signed agreement.
- Changes are append-only audit events; never overwrite the historic agreement or original license issuance.

## Dashboard metrics
Pipeline value, paid license revenue, ARR/renewal value, active licenses, expired/suspended licenses, partner sales, unpaid invoices, refunds, commission liabilities, country/vertical mix and customer concentration.

## Data minimisation
Keep passport copies, Emirates IDs, bank details and beneficial-owner documents in an appropriately secured compliance system, not in the public license certificate or Git repository. Public lookup reveals only license validity fields and the licensor identity.
