-- Migration: Create liquidity provider tables
-- This migration creates the infrastructure for managing liquidity providers
-- and their relationships with market index trading assets

-- Create liquidity provider table
CREATE TABLE public.liquidity_provider (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  type text not null,
  status text not null check (status in ('active', 'inactive')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Create liquidity provider compliance table
CREATE TABLE public.liquidity_provider_compliance (
  id uuid primary key default gen_random_uuid(),
  liquidity_provider_id uuid not null
    references public.liquidity_provider(id) on delete cascade,
  kyb_status text not null check (kyb_status in ('pending', 'approved', 'rejected')),
  kyb_started_at timestamptz,
  kyb_approved_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Create liquidity provider index assets table
CREATE TABLE public.liquidity_provider_index_assets (
  id uuid primary key default gen_random_uuid(),

  market_index_trading_asset_id uuid not null
    references public.market_index_trading_assets(id)
    on delete restrict,

  liquidity_provider_id uuid not null
    references public.liquidity_provider(id)
    on delete restrict,

  units numeric not null check (units >= 0),

  external_reference_code text not null,

  created_at timestamptz not null default now(),

  updated_at timestamptz not null default now(),

  unique (market_index_trading_asset_id, liquidity_provider_id),
  unique (external_reference_code)
);

-- Create indexes for performance
CREATE INDEX idx_liquidity_provider_status ON public.liquidity_provider(status);
CREATE INDEX idx_liquidity_provider_compliance_status ON public.liquidity_provider_compliance(kyb_status);
CREATE INDEX idx_liquidity_provider_compliance_provider_id ON public.liquidity_provider_compliance(liquidity_provider_id);
CREATE INDEX idx_liquidity_provider_index_assets_provider_id ON public.liquidity_provider_index_assets(liquidity_provider_id);
CREATE INDEX idx_liquidity_provider_index_assets_trading_asset_id ON public.liquidity_provider_index_assets(market_index_trading_asset_id);

