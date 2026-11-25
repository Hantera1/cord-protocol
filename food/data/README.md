# Initial product data loading

The first commit establishes the schema, source registry, licence registry, core nutrient/allergen vocabulary and global category taxonomy.

No branded product has been marked as verified or published yet. Product records should be added only by a source adapter that stores the original payload, source record key, retrieval timestamp, payload hash and applicable licence.

## First ingestion batches
- USDA FoodData Central: begin with reference foods and branded-food records as separate data types.
- Open Food Facts: begin with a small barcode-based validation batch; keep its ODbL/DbCL-derived data isolated and apply separate image rights.
- National datasets: onboard one country at a time after checking each dataset licence.
- Manufacturer submissions: accept only authenticated submissions with clear public/confidential field permissions.

## Release gate
Before records are exposed to consumers, run schema validation, identifier matching, source/licence checks, duplicate detection, ingredient and nutrient unit validation, and conflict review. A source database record is not an independent laboratory test.
