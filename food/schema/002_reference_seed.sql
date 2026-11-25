-- Reference seed data for CORD Food v0.1.
-- Review source terms before production ingestion.

INSERT INTO licence_registry (licence_id, licence_name, licence_uri, compatibility_class, obligations, legal_review_status)
VALUES
('CC0-1.0','Creative Commons CC0 1.0','https://creativecommons.org/publicdomain/zero/1.0/','public_domain','{"attribution":"recommended"}','approved_with_conditions'),
('ODbL-1.0','Open Database License 1.0','https://opendatacommons.org/licenses/odbl/1-0/','share_alike','{"attribution":true,"share_alike":true,"legal_review":true}','not_reviewed'),
('DbCL-1.0','Database Contents License 1.0','https://opendatacommons.org/licenses/dbcl/1-0/','share_alike','{"follow_source_terms":true}','not_reviewed'),
('CC-BY-SA','Creative Commons Attribution ShareAlike','https://creativecommons.org/licenses/by-sa/4.0/','share_alike','{"attribution":true,"share_alike":true,"asset_level_review":true}','not_reviewed'),
('CONTRACTUAL','Source-specific contractual terms',NULL,'contractual','{"review_each_source":true}','not_reviewed'),
('UNKNOWN','Unknown or unconfirmed licence',NULL,'unknown','{"publication_blocked":true}','blocked')
ON CONFLICT (licence_id) DO NOTHING;

INSERT INTO source_registry (source_key,source_name,source_type,base_uri,licence_id,terms_uri,reuse_policy,api_access_allowed,image_reuse_policy,notes)
VALUES
('open_food_facts','Open Food Facts','open_database','https://world.openfoodfacts.org/','ODbL-1.0','https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/','isolated_share_alike_domain',true,'CC-BY-SA','Community-contributed data; verify records and follow API, database and image terms separately.'),
('usda_fooddata_central','USDA FoodData Central','government','https://fdc.nal.usda.gov/','CC0-1.0','https://fdc.nal.usda.gov/api-guide/','cc0_domain',true,'separate_review_required','Keep Foundation, FNDDS, Branded Foods and SR Legacy data types distinct.'),
('fao_infoods','FAO INFOODS','intergovernmental','https://www.fao.org/infoods/tables-and-databases','CONTRACTUAL','https://www.fao.org/infoods/','per_dataset_review',false,'separate_review_required','Each linked national/regional dataset requires its own licence review.'),
('eu_food_additives','European Commission Food Additives Database','government','https://food.ec.europa.eu/food-safety/food-improvement-agents/additives/database_en','CONTRACTUAL',NULL,'regulatory_reference_review',false,'not_applicable','EU-specific regulatory reference.'),
('eu_pesticides_mrl','European Commission Pesticides Database','government','https://food.ec.europa.eu/horizontal-topics/eu-food-safety-databases-and-other-online-services_en','CONTRACTUAL',NULL,'regulatory_reference_review',false,'not_applicable','MRLs are legal limits, not test results for a specific product.'),
('gs1_epcis','GS1 EPCIS and CBV','standards_body','https://ref.gs1.org/standards/epcis/','CONTRACTUAL',NULL,'standard_implementation',false,'not_applicable','Supply-chain event interoperability, not ingredient truth.')
ON CONFLICT (source_key) DO NOTHING;

INSERT INTO nutrient_entities (nutrient_code,canonical_name,unit_default) VALUES
('ENERGY_KJ','Energy','kJ'),
('ENERGY_KCAL','Energy','kcal'),
('FAT_TOTAL','Fat, total','g'),
('FAT_SATURATED','Fat, saturated','g'),
('CARBOHYDRATE','Carbohydrate','g'),
('SUGARS_TOTAL','Sugars, total','g'),
('FIBRE','Dietary fibre','g'),
('PROTEIN','Protein','g'),
('SALT','Salt','g'),
('SODIUM','Sodium','mg')
ON CONFLICT (nutrient_code) DO NOTHING;

INSERT INTO allergen_entities (canonical_name,jurisdiction_codes) VALUES
('Gluten-containing cereals',ARRAY['EU']),
('Crustaceans',ARRAY['EU']),
('Eggs',ARRAY['EU']),
('Fish',ARRAY['EU']),
('Peanuts',ARRAY['EU']),
('Soybeans',ARRAY['EU']),
('Milk',ARRAY['EU']),
('Tree nuts',ARRAY['EU']),
('Celery',ARRAY['EU']),
('Mustard',ARRAY['EU']),
('Sesame',ARRAY['EU']),
('Sulphur dioxide and sulphites',ARRAY['EU']),
('Lupin',ARRAY['EU']),
('Molluscs',ARRAY['EU'])
ON CONFLICT (canonical_name) DO NOTHING;
