# CORD Food Integrity — Foundation v0.1

Status: architecture draft. Scope: global food products, all food categories. This application profile does not modify CORD Core v0.1.

## Mission
Build an independent, source-aware record of food products, ingredients, nutrition, claims, production and supply-chain evidence. Include all products, not only products marketed as healthy or organic. Do not equate poor nutritional quality with a safety violation, or organic certification with overall healthfulness.

## Non-negotiable rules
1. Every fact has source, source record ID, retrieval time, original payload reference and applicable licence.
2. Preserve source assertions separately; never silently overwrite conflicts.
3. Distinguish label-transcribed, manufacturer-declared, government-published, laboratory-measured, independently audited and AI-inferred information.
4. Missing means unknown, not zero or proof of absence.
5. Product-level facts and batch/lot-level facts are separate.
6. A barcode identifies a trade item; it does not necessarily identify a production lot or prove the physical item matches the record.
7. Consumer summaries show evidence level, date, jurisdiction and uncertainty.
8. Do not create an opaque single good/bad/safe score. Show separate dimensions and evidence.
9. Track database and image licences separately. Do not combine incompatible datasets into unrestricted exports.
10. Corrections are append-only assertions with provenance.

## Architecture
- PostgreSQL: canonical relational store and provenance.
- Object storage: raw source snapshots, label images, certificates and lab reports.
- Import workers: source-specific adapters; raw landing, validation, normalization, entity resolution, review, publish.
- Search: PostgreSQL full-text/trigram initially.
- API: versioned REST API for consumer, business and AI retrieval.
- Traceability: GS1 EPCIS/CBV-compatible events.
- CORD evidence: separate application profile; never change Core formats or imply a valid hash proves a claim is true.

## Entities
Organisations, facilities, brands, products, identifiers, localizations, packaging assets, ingredients, ingredient names, ordered product-ingredient links, nutrients, allergens, claims, certifications, batches/lots, production and traceability events, suppliers, evidence records, source assertions, source registry, licence registry, import runs and retailer offers.

## Import lifecycle
discovered -> fetched -> quarantined -> normalized -> identity_matched -> quality_checked -> reviewed -> published

Ambiguous identity, licence or material conflicts remain quarantined or visibly provisional.

## First implementation sequence
1. Database schema and migrations.
2. Source registry and immutable raw landing.
3. Open Food Facts adapter in an isolated ODbL data domain after licence review.
4. USDA FoodData Central adapter as a separate CC0 source.
5. FAO/INFOODS national and regional source catalogue.
6. EU additives, allergen and pesticide reference data with jurisdiction and effective dates.
7. Product identity matching and conflict review.
8. Read-only product API and AI retrieval endpoint.
9. Manufacturer portal and GS1 EPCIS-compatible lot events.

## Not a certification
CORD Food is an information and evidence-management system. It does not replace statutory food-safety controls, official inspections, laboratory testing or legal compliance review.
