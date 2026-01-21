-- Migration: Alter market_index_trading_assets table
-- This migration adds new columns and renames existing columns for better clarity

-- Add new columns if they don't exist
ALTER TABLE public.market_index_trading_assets
ADD COLUMN IF NOT EXISTS external_reference_code text unique,
ADD COLUMN IF NOT EXISTS subscription_price numeric,
ADD COLUMN IF NOT EXISTS subscribed_at timestamptz,
ADD COLUMN IF NOT EXISTS settled_at timestamptz;

-- Rename existing columns for better clarity
-- Note: PostgreSQL doesn't support IF NOT EXISTS for column renames, 
-- so we need to check if the new column name exists first

-- Rename buy to buy_price
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name='market_index_trading_assets' 
        AND column_name='buy_price'
    ) THEN
        ALTER TABLE public.market_index_trading_assets 
        RENAME COLUMN buy TO buy_price;
    END IF;
END $$;

-- Rename sell to sell_price  
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name='market_index_trading_assets' 
        AND column_name='sell_price'
    ) THEN
        ALTER TABLE public.market_index_trading_assets 
        RENAME COLUMN sell TO sell_price;
    END IF;
END $$;

-- Rename units to total_trading_units
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name='market_index_trading_assets' 
        AND column_name='total_trading_units'
    ) THEN
        ALTER TABLE public.market_index_trading_assets 
        RENAME COLUMN units TO total_trading_units;
    END IF;
END $$;

-- Create indexes for the new columns
CREATE INDEX IF NOT EXISTS idx_market_index_trading_assets_external_ref_code 
ON public.market_index_trading_assets(external_reference_code);

CREATE INDEX IF NOT EXISTS idx_market_index_trading_assets_subscribed_at 
ON public.market_index_trading_assets(subscribed_at);

CREATE INDEX IF NOT EXISTS idx_market_index_trading_assets_settled_at 
ON public.market_index_trading_assets(settled_at);


