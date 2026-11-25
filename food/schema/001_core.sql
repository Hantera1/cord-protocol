-- CORD Food Integrity schema v0.1; PostgreSQL 15+
-- Application profile only. CORD Core remains unchanged.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE licence_registry (
  licence_id text PRIMARY KEY, licence_name text NOT NULL, licence_uri text,
  compatibility_class text NOT NULL CHECK (compatibility_class IN ('public_domain','permissive','share_alike','restricted','contractual','unknown')),
  obligations jsonb NOT NULL DEFAULT '{}'::jsonb,
  legal_review_status text NOT NULL DEFAULT 'not_reviewed'
    CHECK (legal_review_status IN ('not_reviewed','approved','approved_with_conditions','blocked'))
);

CREATE TABLE source_registry (
  source_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), source_key text NOT NULL UNIQUE,
  source_name text NOT NULL, source_type text NOT NULL,
  base_uri text, jurisdiction_codes text[] NOT NULL DEFAULT '{}',
  licence_id text REFERENCES licence_registry(licence_id), terms_uri text,
  attribution_text text, reuse_policy text NOT NULL DEFAULT 'review_required',
  bulk_import_allowed boolean NOT NULL DEFAULT false, api_access_allowed boolean NOT NULL DEFAULT false,
  image_reuse_policy text NOT NULL DEFAULT 'separate_review_required',
  active boolean NOT NULL DEFAULT true, checked_at timestamptz, notes text
);

CREATE TABLE organisations (
  organisation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), legal_name text NOT NULL,
  trading_names jsonb NOT NULL DEFAULT '[]', organisation_type text NOT NULL,
  country_code char(2), registration_identifiers jsonb NOT NULL DEFAULT '[]',
  website text, verification_status text NOT NULL DEFAULT 'unverified',
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE facilities (
  facility_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id uuid NOT NULL REFERENCES organisations(organisation_id),
  facility_name text NOT NULL, facility_type text NOT NULL, address jsonb,
  country_code char(2), geolocation jsonb, external_identifiers jsonb NOT NULL DEFAULT '[]'
);
CREATE TABLE brands (
  brand_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), brand_name text NOT NULL,
  owner_organisation_id uuid REFERENCES organisations(organisation_id), country_code char(2)
);
CREATE TABLE products (
  product_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), canonical_name text NOT NULL,
  category_code text, food_type text NOT NULL DEFAULT 'packaged',
  brand_id uuid REFERENCES brands(brand_id),
  manufacturer_organisation_id uuid REFERENCES organisations(organisation_id),
  default_market_country char(2), lifecycle_status text NOT NULL DEFAULT 'unknown',
  record_status text NOT NULL DEFAULT 'provisional', created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE product_identifiers (
  product_identifier_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id uuid NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
  scheme text NOT NULL, identifier_value text NOT NULL, market_country char(2),
  valid_from date, valid_to date, UNIQUE(scheme,identifier_value,market_country)
);
CREATE TABLE product_localizations (
  product_localization_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id uuid NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
  language_tag text NOT NULL, market_country char(2), display_name text,
  description text, label_text text, ingredient_statement text,
  UNIQUE(product_id,language_tag,market_country)
);

CREATE TABLE ingredient_entities (
  ingredient_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), canonical_name text NOT NULL,
  ingredient_kind text NOT NULL, parent_ingredient_id uuid REFERENCES ingredient_entities(ingredient_id),
  external_identifiers jsonb NOT NULL DEFAULT '[]'
);
CREATE TABLE ingredient_names (
  ingredient_name_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  ingredient_id uuid NOT NULL REFERENCES ingredient_entities(ingredient_id),
  language_tag text NOT NULL, name text NOT NULL, name_type text NOT NULL DEFAULT 'synonym'
);
CREATE TABLE product_ingredients (
  product_ingredient_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id uuid NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
  ingredient_id uuid REFERENCES ingredient_entities(ingredient_id),
  ingredient_text_original text NOT NULL, position integer,
  percentage numeric(9,4), percentage_basis text,
  declared_as_compound boolean NOT NULL DEFAULT false,
  assertion_id uuid, confidence numeric(4,3) CHECK(confidence BETWEEN 0 AND 1)
);
CREATE TABLE nutrient_entities (
  nutrient_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), nutrient_code text UNIQUE,
  canonical_name text NOT NULL, unit_default text NOT NULL,
  external_identifiers jsonb NOT NULL DEFAULT '[]'
);
CREATE TABLE product_nutrients (
  product_nutrient_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id uuid NOT NULL REFERENCES products(product_id),
  nutrient_id uuid NOT NULL REFERENCES nutrient_entities(nutrient_id),
  value numeric(18,6) NOT NULL, unit text NOT NULL,
  basis text NOT NULL CHECK(basis IN ('per_100g','per_100ml','per_serving','per_package','other')),
  measurement_type text NOT NULL CHECK(measurement_type IN ('label_declared','laboratory_measured','database_reference','calculated','estimated')),
  assertion_id uuid, measured_at timestamptz
);
CREATE TABLE allergen_entities (
  allergen_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), canonical_name text NOT NULL UNIQUE,
  jurisdiction_codes text[] NOT NULL DEFAULT '{}', external_identifiers jsonb NOT NULL DEFAULT '[]'
);
CREATE TABLE product_allergens (
  product_allergen_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id uuid NOT NULL REFERENCES products(product_id),
  allergen_id uuid NOT NULL REFERENCES allergen_entities(allergen_id),
  status text NOT NULL CHECK(status IN ('contains','may_contain','free_from_claim','unknown','cross_contact_risk')),
  statement_original text, assertion_id uuid
);
CREATE TABLE product_claims (
  claim_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), product_id uuid NOT NULL REFERENCES products(product_id),
  claim_type text NOT NULL, claim_text text NOT NULL, jurisdiction_code char(2),
  certification_body text, certificate_reference text, valid_from date, valid_to date,
  verification_status text NOT NULL DEFAULT 'unverified', assertion_id uuid
);

CREATE TABLE evidence_records (
  evidence_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), evidence_type text NOT NULL,
  storage_uri text, sha256_hex char(64), issuer_organisation_id uuid REFERENCES organisations(organisation_id),
  issued_at timestamptz, captured_at timestamptz NOT NULL DEFAULT now(),
  access_class text NOT NULL DEFAULT 'public_summary', licence_id text REFERENCES licence_registry(licence_id),
  metadata jsonb NOT NULL DEFAULT '{}'
);
CREATE TABLE import_runs (
  import_run_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id uuid NOT NULL REFERENCES source_registry(source_id),
  adapter_version text NOT NULL, started_at timestamptz NOT NULL DEFAULT now(),
  finished_at timestamptz, run_status text NOT NULL DEFAULT 'running',
  records_seen integer NOT NULL DEFAULT 0, records_imported integer NOT NULL DEFAULT 0,
  records_quarantined integer NOT NULL DEFAULT 0, error_summary jsonb NOT NULL DEFAULT '{}'
);
CREATE TABLE raw_source_records (
  raw_record_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id uuid NOT NULL REFERENCES source_registry(source_id),
  source_record_key text, fetched_at timestamptz NOT NULL DEFAULT now(),
  payload_sha256 char(64) NOT NULL, payload_storage_uri text NOT NULL,
  licence_id text REFERENCES licence_registry(licence_id),
  import_run_id uuid REFERENCES import_runs(import_run_id),
  processing_status text NOT NULL DEFAULT 'landed', error_details jsonb
);
CREATE TABLE source_assertions (
  assertion_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id uuid NOT NULL REFERENCES source_registry(source_id),
  source_record_key text, subject_type text NOT NULL, subject_id uuid,
  predicate text NOT NULL, value_json jsonb NOT NULL,
  language_tag text, jurisdiction_code char(2), asserted_at timestamptz,
  retrieved_at timestamptz NOT NULL DEFAULT now(), source_updated_at timestamptz,
  evidence_id uuid REFERENCES evidence_records(evidence_id),
  raw_record_id uuid REFERENCES raw_source_records(raw_record_id),
  assertion_status text NOT NULL DEFAULT 'unreviewed',
  supersedes_assertion_id uuid REFERENCES source_assertions(assertion_id), notes text
);

CREATE TABLE product_batches (
  batch_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id uuid NOT NULL REFERENCES products(product_id),
  batch_code text NOT NULL, facility_id uuid REFERENCES facilities(facility_id),
  produced_at timestamptz, best_before date, use_by date,
  quantity numeric(18,4), quantity_unit text, status text NOT NULL DEFAULT 'unknown',
  assertion_id uuid, UNIQUE(product_id,batch_code)
);
CREATE TABLE traceability_events (
  trace_event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), event_type text NOT NULL,
  event_time timestamptz NOT NULL, recorded_at timestamptz NOT NULL DEFAULT now(),
  product_id uuid REFERENCES products(product_id), batch_id uuid REFERENCES product_batches(batch_id),
  organisation_id uuid REFERENCES organisations(organisation_id), facility_id uuid REFERENCES facilities(facility_id),
  source_event_id text, epcis_payload jsonb, evidence_id uuid REFERENCES evidence_records(evidence_id),
  event_status text NOT NULL DEFAULT 'unverified'
);
CREATE TABLE product_offers (
  offer_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), product_id uuid NOT NULL REFERENCES products(product_id),
  retailer_organisation_id uuid REFERENCES organisations(organisation_id), store_external_id text,
  market_country char(2), availability_status text NOT NULL DEFAULT 'unknown',
  price_amount numeric(12,2), price_currency char(3),
  observed_at timestamptz NOT NULL, valid_until timestamptz, assertion_id uuid
);

CREATE INDEX idx_products_name ON products USING gin(to_tsvector('simple',canonical_name));
CREATE INDEX idx_identifiers_value ON product_identifiers(identifier_value);
CREATE INDEX idx_ingredient_names ON ingredient_names(lower(name));
CREATE INDEX idx_assertions_subject ON source_assertions(subject_type,subject_id);
CREATE INDEX idx_batch_code ON product_batches(batch_code);
CREATE INDEX idx_offers_market ON product_offers(product_id,market_country,observed_at DESC);
