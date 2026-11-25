# CORD Food ingestion architecture v0.1

## Pipeline
1. Discover: use only permitted endpoints or datasets.
2. Fetch: obey source rate limits, API keys, User-Agent rules and terms.
3. Land raw: store exact response bytes in controlled object storage; calculate SHA-256; record source, licence, retrieval time and source record key.
4. Parse: validate against source-specific schemas.
5. Normalize: map units, language tags, identifiers, ingredients, nutrients and categories while retaining original label text.
6. Resolve identity: match GTIN/UPC/EAN where valid; otherwise use conservative brand, name, package size and market matching. Never merge on name alone.
7. Quality checks: validate units, impossible values, ingredient order, dates, duplicates and conflicting claims.
8. Quarantine: ambiguous identity, rights or material conflicts go to review.
9. Publish assertions: retain each source claim separately; expose approved fields with provenance.
10. Monitor: re-fetch under source policy and create new assertions rather than overwriting history.

## Adapter contract
Each adapter provides source_key, adapter_version, fetch, parse, map_to_cord, licence_metadata, source_record_key, source_updated_at, retrieved_at and quality_report. AI may suggest mappings or anomalies but must not invent missing data.

## Licence isolation
- Open Food Facts data is under ODbL/DbCL; product images have a separate CC BY-SA licence. Isolate this dataset and its derivatives in a share-alike domain. Do not mix it into an unrestricted proprietary export without legal review.
- USDA FoodData Central is CC0. Preserve attribution as good practice and keep dataset type and FDC IDs.
- FAO/INFOODS is a directory of national and regional food composition tables. Review each dataset's own licence.
- EU regulatory databases require source-specific reuse review and jurisdiction/effective-date handling.
- Manufacturer and laboratory submissions require documented permission and contractual rules for public and confidential fields.
- Product image rights are separate from text-data rights.

## Evidence classes
label_transcribed; manufacturer_declared; government_published; database_reference; laboratory_measured; independently_audited; ai_inferred.
AI-inferred information is never a verified fact.

## Conflict policy
Do not choose the newest or most favourable claim automatically. Preserve all claims and route conflicts for review. If the package label differs from the database, surface the discrepancy and request a current package/batch check.

## Initial adapter order
1. USDA FoodData Central: CC0, keep Foundation, FNDDS, Branded Foods and SR Legacy distinct.
2. Open Food Facts API v3: isolated ODbL/DbCL domain; separate image rights; obey API terms and rate limits.
3. EU additives, allergen and pesticide MRL references: jurisdiction-specific.
4. FAO/INFOODS: discover national datasets and onboard only after individual licence review.
5. Manufacturer and laboratory direct submissions: authenticated and signed.
6. GS1 EPCIS/CBV: supply-chain events, not ingredient truth.

## Operations
Idempotent imports; versioned adapters; retries with backoff; respect HTTP 429 and Retry-After; dead-letter queue; import metrics; audit log; source withdrawal handling. No product is independently verified merely because it appears in an open database.
