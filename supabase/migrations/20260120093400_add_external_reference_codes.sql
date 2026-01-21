-- Migration: Add external reference codes with immutable triggers
-- Uses Crockford-style Base32-like format (e.g. G4XTC7V2J6)
-- Secure, opaque, LP-safe

-- Enable crypto (safe if already enabled)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================================
-- MITA: market_index_trading_assets
-- ============================================================

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'market_index_trading_assets'
      AND column_name = 'external_reference_code'
  ) THEN
    ALTER TABLE market_index_trading_assets
    ADD COLUMN external_reference_code TEXT;
  END IF;
END $$;

-- Set correct DEFAULT (Postgres-safe, no base32)
ALTER TABLE market_index_trading_assets
ALTER COLUMN external_reference_code
SET DEFAULT
LEFT(
  translate(
    encode(gen_random_bytes(8), 'hex'),
    '0123456789abcdef',
    '0123456789ABCDEFGHJKMNPQRSTVW'
  ),
  10
);

-- Enforce NOT NULL after default exists
ALTER TABLE market_index_trading_assets
ALTER COLUMN external_reference_code
SET NOT NULL;

-- Uniqueness
CREATE UNIQUE INDEX IF NOT EXISTS
idx_mita_external_reference_code
ON market_index_trading_assets (external_reference_code);

-- Prevent updates (immutability)
CREATE OR REPLACE FUNCTION mita_prevent_reference_code_update()
RETURNS trigger AS $$
BEGIN
  IF NEW.external_reference_code <> OLD.external_reference_code THEN
    RAISE EXCEPTION 'external_reference_code is immutable';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_mita_prevent_reference_code_update
ON market_index_trading_assets;

CREATE TRIGGER trg_mita_prevent_reference_code_update
BEFORE UPDATE ON market_index_trading_assets
FOR EACH ROW
EXECUTE FUNCTION mita_prevent_reference_code_update();

-- ============================================================
-- LPIA: liquidity_provider_index_assets
-- ============================================================

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'liquidity_provider_index_assets'
      AND column_name = 'external_reference_code'
  ) THEN
    ALTER TABLE liquidity_provider_index_assets
    ADD COLUMN external_reference_code TEXT;
  END IF;
END $$;

ALTER TABLE liquidity_provider_index_assets
ALTER COLUMN external_reference_code
SET DEFAULT
LEFT(
  translate(
    encode(gen_random_bytes(8), 'hex'),
    '0123456789abcdef',
    '0123456789ABCDEFGHJKMNPQRSTVW'
  ),
  10
);

ALTER TABLE liquidity_provider_index_assets
ALTER COLUMN external_reference_code
SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS
idx_lpia_external_reference_code
ON liquidity_provider_index_assets (external_reference_code);

CREATE OR REPLACE FUNCTION lpia_prevent_reference_code_update()
RETURNS trigger AS $$
BEGIN
  IF NEW.external_reference_code <> OLD.external_reference_code THEN
    RAISE EXCEPTION 'external_reference_code is immutable';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_lpia_prevent_reference_code_update
ON liquidity_provider_index_assets;

CREATE TRIGGER trg_lpia_prevent_reference_code_update
BEFORE UPDATE ON liquidity_provider_index_assets
FOR EACH ROW
EXECUTE FUNCTION lpia_prevent_reference_code_update();
