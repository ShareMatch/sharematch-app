-- =========================================
-- 1. Add external_lp_ref_code column
-- =========================================
ALTER TABLE liquidity_provider_index_assets
ADD COLUMN IF NOT EXISTS external_lp_ref_code CHAR(10);

-- =========================================
-- 2. Add UNIQUE constraint
-- =========================================
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'uq_lp_index_assets_external_code'
  ) THEN
    ALTER TABLE liquidity_provider_index_assets
    ADD CONSTRAINT uq_lp_index_assets_external_code
    UNIQUE (external_lp_ref_code);
  END IF;
END;
$$;

-- =========================================
-- 3. Base32 (Crockford) generator function
-- =========================================
CREATE OR REPLACE FUNCTION generate_base32_10()
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
  chars TEXT := '0123456789ABCDEFGHJKMNPQRSTVWXYZ';
  result TEXT := '';
  i INT;
BEGIN
  FOR i IN 1..10 LOOP
    result := result || substr(
      chars,
      floor(random() * length(chars) + 1)::int,
      1
    );
  END LOOP;

  RETURN result;
END;
$$;

-- =========================================
-- 4. Trigger function to auto-populate code
-- =========================================
CREATE OR REPLACE FUNCTION set_external_lp_ref_code()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
  generated_code TEXT;
BEGIN
  -- If already set (should not happen normally), respect it
  IF NEW.external_lp_ref_code IS NOT NULL THEN
    RETURN NEW;
  END IF;

  -- Generate until unique (collision-safe)
  LOOP
    generated_code := generate_base32_10();

    EXIT WHEN NOT EXISTS (
      SELECT 1
      FROM liquidity_provider_index_assets
      WHERE external_lp_ref_code = generated_code
    );
  END LOOP;

  NEW.external_lp_ref_code := generated_code;
  RETURN NEW;
END;
$$;

-- =========================================
-- 5. Attach trigger to table
-- =========================================
DROP TRIGGER IF EXISTS trg_set_external_lp_ref_code
ON liquidity_provider_index_assets;

CREATE TRIGGER trg_set_external_lp_ref_code
BEFORE INSERT ON liquidity_provider_index_assets
FOR EACH ROW
EXECUTE FUNCTION set_external_lp_ref_code();

-- =========================================
-- 6. Make column NOT NULL after backfill
-- =========================================
UPDATE liquidity_provider_index_assets
SET external_lp_ref_code = generate_base32_10()
WHERE external_lp_ref_code IS NULL;

ALTER TABLE liquidity_provider_index_assets
ALTER COLUMN external_lp_ref_code SET NOT NULL;

-- =========================================
-- 7. Prevent updates to external_lp_ref_code
-- =========================================
CREATE OR REPLACE FUNCTION prevent_external_lp_ref_code_update()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  IF NEW.external_lp_ref_code <> OLD.external_lp_ref_code THEN
    RAISE EXCEPTION 'external_lp_ref_code is immutable';
  END IF;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_prevent_external_lp_ref_code_update
ON liquidity_provider_index_assets;

CREATE TRIGGER trg_prevent_external_lp_ref_code_update
BEFORE UPDATE ON liquidity_provider_index_assets
FOR EACH ROW
EXECUTE FUNCTION prevent_external_lp_ref_code_update();
