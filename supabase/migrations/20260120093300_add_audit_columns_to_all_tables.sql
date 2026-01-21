-- Migration: Add audit columns (created_at, updated_at, created_by, updated_by) to all tables
-- This migration adds tracking for who created/updated records and when

-- Function to safely add columns if they don't exist
DO $$
BEGIN
    -- company_bank_accounts (already has created_at, updated_at - add created_by, updated_by)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='company_bank_accounts' AND column_name='created_by'
    ) THEN
        ALTER TABLE public.company_bank_accounts ADD COLUMN created_by uuid;
        ALTER TABLE public.company_bank_accounts ADD COLUMN updated_by uuid;
    END IF;

    -- news_articles (has created_at - add updated_at, created_by, updated_by)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='news_articles' AND column_name='updated_at'
    ) THEN
        ALTER TABLE public.news_articles ADD COLUMN updated_at timestamptz default now();
        ALTER TABLE public.news_articles ADD COLUMN created_by uuid;
        ALTER TABLE public.news_articles ADD COLUMN updated_by uuid;
    END IF;

    -- news_updates (has last_updated_at - add created_at, created_by, updated_by)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='news_updates' AND column_name='created_at'
    ) THEN
        ALTER TABLE public.news_updates ADD COLUMN created_at timestamptz default now();
        ALTER TABLE public.news_updates ADD COLUMN created_by uuid;
        ALTER TABLE public.news_updates ADD COLUMN updated_by uuid;
    END IF;

    -- positions (already has created_at, updated_at - add created_by, updated_by)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='positions' AND column_name='created_by'
    ) THEN
        ALTER TABLE public.positions ADD COLUMN created_by uuid;
        ALTER TABLE public.positions ADD COLUMN updated_by uuid;
    END IF;

    -- transactions (has created_at - add updated_at, created_by, updated_by)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='transactions' AND column_name='updated_at'
    ) THEN
        ALTER TABLE public.transactions ADD COLUMN updated_at timestamptz default now();
        ALTER TABLE public.transactions ADD COLUMN created_by uuid;
        ALTER TABLE public.transactions ADD COLUMN updated_by uuid;
    END IF;

    -- user_compliance (no audit columns - add all)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_compliance' AND column_name='created_at'
    ) THEN
        ALTER TABLE public.user_compliance ADD COLUMN created_at timestamptz default now();
        ALTER TABLE public.user_compliance ADD COLUMN updated_at timestamptz default now();
        ALTER TABLE public.user_compliance ADD COLUMN created_by uuid;
        ALTER TABLE public.user_compliance ADD COLUMN updated_by uuid;
    END IF;

    -- user_crypto_wallets (no audit columns - add all)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_crypto_wallets' AND column_name='created_at'
    ) THEN
        ALTER TABLE public.user_crypto_wallets ADD COLUMN created_at timestamptz default now();
        ALTER TABLE public.user_crypto_wallets ADD COLUMN updated_at timestamptz default now();
        ALTER TABLE public.user_crypto_wallets ADD COLUMN created_by uuid;
        ALTER TABLE public.user_crypto_wallets ADD COLUMN updated_by uuid;
    END IF;

    -- wallets (already has created_at, updated_at - add created_by, updated_by)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='wallets' AND column_name='created_by'
    ) THEN
        ALTER TABLE public.wallets ADD COLUMN created_by uuid;
        ALTER TABLE public.wallets ADD COLUMN updated_by uuid;
    END IF;

    -- assets (has created_at, updated_at - add created_by, updated_by)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='assets' AND column_name='created_by'
    ) THEN
        ALTER TABLE public.assets ADD COLUMN created_by uuid;
        ALTER TABLE public.assets ADD COLUMN updated_by uuid;
    END IF;

    -- markets (already has created_at, updated_at - add created_by, updated_by)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='markets' AND column_name='created_by'
    ) THEN
        ALTER TABLE public.markets ADD COLUMN created_by uuid;
        ALTER TABLE public.markets ADD COLUMN updated_by uuid;
    END IF;

    -- market_index_seasons (already has created_at, updated_at - add created_by, updated_by)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='market_index_seasons' AND column_name='created_by'
    ) THEN
        ALTER TABLE public.market_index_seasons ADD COLUMN created_by uuid;
        ALTER TABLE public.market_index_seasons ADD COLUMN updated_by uuid;
    END IF;

    -- market_index_trading_assets (has created_at - add updated_at, created_by, updated_by)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='market_index_trading_assets' AND column_name='updated_at'
    ) THEN
        ALTER TABLE public.market_index_trading_assets ADD COLUMN updated_at timestamptz default now();
        ALTER TABLE public.market_index_trading_assets ADD COLUMN created_by uuid;
        ALTER TABLE public.market_index_trading_assets ADD COLUMN updated_by uuid;
    END IF;

    -- asset_ledger (has created_at, recorded_at - add updated_at, created_by, updated_by)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='asset_ledger' AND column_name='updated_at'
    ) THEN
        ALTER TABLE public.asset_ledger ADD COLUMN updated_at timestamptz default now();
        ALTER TABLE public.asset_ledger ADD COLUMN created_by uuid;
        ALTER TABLE public.asset_ledger ADD COLUMN updated_by uuid;
    END IF;

    -- market_indexes (already has created_at, updated_at - add created_by, updated_by)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='market_indexes' AND column_name='created_by'
    ) THEN
        ALTER TABLE public.market_indexes ADD COLUMN created_by uuid;
        ALTER TABLE public.market_indexes ADD COLUMN updated_by uuid;
    END IF;

    -- index_trading_asset_profile (already has created_at, updated_at - add created_by, updated_by)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='index_trading_asset_profile' AND column_name='created_by'
    ) THEN
        ALTER TABLE public.index_trading_asset_profile ADD COLUMN created_by uuid;
        ALTER TABLE public.index_trading_asset_profile ADD COLUMN updated_by uuid;
    END IF;

    -- login_history (has created_at - add updated_at, created_by, updated_by)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='login_history' AND column_name='updated_at'
    ) THEN
        ALTER TABLE public.login_history ADD COLUMN updated_at timestamptz default now();
        ALTER TABLE public.login_history ADD COLUMN created_by uuid;
        ALTER TABLE public.login_history ADD COLUMN updated_by uuid;
    END IF;

    -- user_preferences (already has created_at, updated_at - add created_by, updated_by)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_preferences' AND column_name='created_by'
    ) THEN
        ALTER TABLE public.user_preferences ADD COLUMN created_by uuid;
        ALTER TABLE public.user_preferences ADD COLUMN updated_by uuid;
    END IF;

    -- investor_declarations (already has created_at, updated_at - add created_by, updated_by)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='investor_declarations' AND column_name='created_by'
    ) THEN
        ALTER TABLE public.investor_declarations ADD COLUMN created_by uuid;
        ALTER TABLE public.investor_declarations ADD COLUMN updated_by uuid;
    END IF;

    -- investor_otp_verification (has created_at - add updated_at, created_by, updated_by)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='investor_otp_verification' AND column_name='updated_at'
    ) THEN
        ALTER TABLE public.investor_otp_verification ADD COLUMN updated_at timestamptz default now();
        ALTER TABLE public.investor_otp_verification ADD COLUMN created_by uuid;
        ALTER TABLE public.investor_otp_verification ADD COLUMN updated_by uuid;
    END IF;

    -- liquidity_provider (no audit columns - add all)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='liquidity_provider' AND column_name='created_at'
    ) THEN
        ALTER TABLE public.liquidity_provider ADD COLUMN created_at timestamptz default now();
        ALTER TABLE public.liquidity_provider ADD COLUMN updated_at timestamptz default now();
        ALTER TABLE public.liquidity_provider ADD COLUMN created_by uuid;
        ALTER TABLE public.liquidity_provider ADD COLUMN updated_by uuid;
    END IF;

    -- liquidity_provider_compliance (no audit columns - add all)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='liquidity_provider_compliance' AND column_name='created_at'
    ) THEN
        ALTER TABLE public.liquidity_provider_compliance ADD COLUMN created_at timestamptz default now();
        ALTER TABLE public.liquidity_provider_compliance ADD COLUMN updated_at timestamptz default now();
        ALTER TABLE public.liquidity_provider_compliance ADD COLUMN created_by uuid;
        ALTER TABLE public.liquidity_provider_compliance ADD COLUMN updated_by uuid;
    END IF;

    -- liquidity_provider_index_assets (already has created_at, updated_at - add created_by, updated_by)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='liquidity_provider_index_assets' AND column_name='created_by'
    ) THEN
        ALTER TABLE public.liquidity_provider_index_assets ADD COLUMN created_by uuid;
        ALTER TABLE public.liquidity_provider_index_assets ADD COLUMN updated_by uuid;
    END IF;

END $$;

-- Create indexes for audit columns for better performance
-- Only create indexes if the columns were successfully added
DO $$
BEGIN
    -- company_bank_accounts indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='company_bank_accounts' AND column_name='created_by'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_company_bank_accounts_created_by ON public.company_bank_accounts(created_by);
        CREATE INDEX IF NOT EXISTS idx_company_bank_accounts_updated_by ON public.company_bank_accounts(updated_by);
    END IF;

    -- news_articles indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='news_articles' AND column_name='created_by'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_news_articles_created_by ON public.news_articles(created_by);
        CREATE INDEX IF NOT EXISTS idx_news_articles_updated_by ON public.news_articles(updated_by);
    END IF;

    -- news_updates indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='news_updates' AND column_name='created_by'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_news_updates_created_by ON public.news_updates(created_by);
        CREATE INDEX IF NOT EXISTS idx_news_updates_updated_by ON public.news_updates(updated_by);
    END IF;

    -- positions indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='positions' AND column_name='created_by'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_positions_created_by ON public.positions(created_by);
        CREATE INDEX IF NOT EXISTS idx_positions_updated_by ON public.positions(updated_by);
    END IF;

    -- transactions indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='transactions' AND column_name='created_by'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_transactions_created_by ON public.transactions(created_by);
        CREATE INDEX IF NOT EXISTS idx_transactions_updated_by ON public.transactions(updated_by);
    END IF;

    -- user_compliance indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_compliance' AND column_name='created_by'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_user_compliance_created_by ON public.user_compliance(created_by);
        CREATE INDEX IF NOT EXISTS idx_user_compliance_updated_by ON public.user_compliance(updated_by);
    END IF;

    -- user_crypto_wallets indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_crypto_wallets' AND column_name='created_by'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_user_crypto_wallets_created_by ON public.user_crypto_wallets(created_by);
        CREATE INDEX IF NOT EXISTS idx_user_crypto_wallets_updated_by ON public.user_crypto_wallets(updated_by);
    END IF;

    -- wallets indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='wallets' AND column_name='created_by'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_wallets_created_by ON public.wallets(created_by);
        CREATE INDEX IF NOT EXISTS idx_wallets_updated_by ON public.wallets(updated_by);
    END IF;

    -- assets indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='assets' AND column_name='created_by'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_assets_created_by ON public.assets(created_by);
        CREATE INDEX IF NOT EXISTS idx_assets_updated_by ON public.assets(updated_by);
    END IF;

    -- markets indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='markets' AND column_name='created_by'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_markets_created_by ON public.markets(created_by);
        CREATE INDEX IF NOT EXISTS idx_markets_updated_by ON public.markets(updated_by);
    END IF;

    -- market_index_seasons indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='market_index_seasons' AND column_name='created_by'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_market_index_seasons_created_by ON public.market_index_seasons(created_by);
        CREATE INDEX IF NOT EXISTS idx_market_index_seasons_updated_by ON public.market_index_seasons(updated_by);
    END IF;

    -- market_index_trading_assets indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='market_index_trading_assets' AND column_name='created_by'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_market_index_trading_assets_created_by ON public.market_index_trading_assets(created_by);
        CREATE INDEX IF NOT EXISTS idx_market_index_trading_assets_updated_by ON public.market_index_trading_assets(updated_by);
    END IF;

    -- asset_ledger indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='asset_ledger' AND column_name='created_by'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_asset_ledger_created_by ON public.asset_ledger(created_by);
        CREATE INDEX IF NOT EXISTS idx_asset_ledger_updated_by ON public.asset_ledger(updated_by);
    END IF;

    -- market_indexes indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='market_indexes' AND column_name='created_by'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_market_indexes_created_by ON public.market_indexes(created_by);
        CREATE INDEX IF NOT EXISTS idx_market_indexes_updated_by ON public.market_indexes(updated_by);
    END IF;

    -- index_trading_asset_profile indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='index_trading_asset_profile' AND column_name='created_by'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_index_trading_asset_profile_created_by ON public.index_trading_asset_profile(created_by);
        CREATE INDEX IF NOT EXISTS idx_index_trading_asset_profile_updated_by ON public.index_trading_asset_profile(updated_by);
    END IF;

    -- login_history indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='login_history' AND column_name='created_by'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_login_history_created_by ON public.login_history(created_by);
        CREATE INDEX IF NOT EXISTS idx_login_history_updated_by ON public.login_history(updated_by);
    END IF;

    -- user_preferences indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_preferences' AND column_name='created_by'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_user_preferences_created_by ON public.user_preferences(created_by);
        CREATE INDEX IF NOT EXISTS idx_user_preferences_updated_by ON public.user_preferences(updated_by);
    END IF;

    -- investor_declarations indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='investor_declarations' AND column_name='created_by'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_investor_declarations_created_by ON public.investor_declarations(created_by);
        CREATE INDEX IF NOT EXISTS idx_investor_declarations_updated_by ON public.investor_declarations(updated_by);
    END IF;

    -- investor_otp_verification indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='investor_otp_verification' AND column_name='created_by'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_investor_otp_verification_created_by ON public.investor_otp_verification(created_by);
        CREATE INDEX IF NOT EXISTS idx_investor_otp_verification_updated_by ON public.investor_otp_verification(updated_by);
    END IF;

    -- liquidity_provider indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='liquidity_provider' AND column_name='created_by'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_liquidity_provider_created_by ON public.liquidity_provider(created_by);
        CREATE INDEX IF NOT EXISTS idx_liquidity_provider_updated_by ON public.liquidity_provider(updated_by);
    END IF;

    -- liquidity_provider_compliance indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='liquidity_provider_compliance' AND column_name='created_by'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_liquidity_provider_compliance_created_by ON public.liquidity_provider_compliance(created_by);
        CREATE INDEX IF NOT EXISTS idx_liquidity_provider_compliance_updated_by ON public.liquidity_provider_compliance(updated_by);
    END IF;

    -- liquidity_provider_index_assets indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='liquidity_provider_index_assets' AND column_name='created_by'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_liquidity_provider_index_assets_created_by ON public.liquidity_provider_index_assets(created_by);
        CREATE INDEX IF NOT EXISTS idx_liquidity_provider_index_assets_updated_by ON public.liquidity_provider_index_assets(updated_by);
    END IF;

END $$;
