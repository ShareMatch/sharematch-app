-- Migration: Add asset categories for cross-category asset support
-- This allows the same asset name to exist in different categories
-- (e.g., Netherlands in Eurovision vs Netherlands in Cricket)

-- Create enum type for high-level asset categories
CREATE TYPE asset_category AS ENUM (
    'football',
    'cricket',
    'motorsport',
    'eurovision',
    'politics',
    'basketball',
    'american_football',
    'entertainment',
    'music',
    'other'
);

-- Add category column to assets table
ALTER TABLE assets 
ADD COLUMN category asset_category NOT NULL DEFAULT 'other';

-- Create index on category for performance
CREATE INDEX idx_assets_category ON assets(category);

