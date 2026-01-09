/**
 * Helper functions for team/driver logos
 */

/**
 * Team logo mappings to reliable sources
 * Using a combination of sources for best coverage
 */
/**
 * Helper to convert decimal odds to Buy/Sell prices
 */
const isLikelyUuid = (value: string): boolean => {
    // Accept UUID v4 style ids; also used for "settled-..." composite IDs (handled upstream)
    return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value);
};

const TEAM_LOGOS: Record<string, string> = {
    // EPL Teams - Using official club domains for logo.dev
    'Arsenal': 'https://logo.clearbit.com/arsenal.com',
    'Man City': 'https://logo.clearbit.com/mancity.com',
    'Liverpool': 'https://logo.clearbit.com/liverpoolfc.com',
    'Chelsea': 'https://logo.clearbit.com/chelseafc.com',
    'Man Utd': 'https://logo.clearbit.com/manutd.com',
    'Tottenham': 'https://logo.clearbit.com/tottenhamhotspur.com',
    'Newcastle': 'https://logo.clearbit.com/nufc.co.uk',
    'Aston Villa': 'https://logo.clearbit.com/avfc.co.uk',
    'Brighton': 'https://logo.clearbit.com/brightonandhovealbion.com',
    'West Ham': 'https://logo.clearbit.com/whufc.com',
    'Everton': 'https://logo.clearbit.com/evertonfc.com',
    'Wolves': 'https://logo.clearbit.com/wolves.co.uk',
    'Fulham': 'https://logo.clearbit.com/fulhamfc.com',
    'Brentford': 'https://logo.clearbit.com/brentfordfc.com',
    'Crystal Palace': 'https://logo.clearbit.com/cpfc.co.uk',
    'Bournemouth': 'https://logo.clearbit.com/afcb.co.uk',
    'Nottm Forest': 'https://logo.clearbit.com/nottinghamforest.co.uk',
    'Leeds': 'https://logo.clearbit.com/leedsunited.com',

    // F1 Teams
    'Lando Norris': 'https://logo.clearbit.com/mclaren.com',
    'Oscar Piastri': 'https://logo.clearbit.com/mclaren.com',
    'Max Verstappen': 'https://logo.clearbit.com/redbull.com',
    'Sergio Perez': 'https://logo.clearbit.com/redbull.com',
    'Charles Leclerc': 'https://logo.clearbit.com/ferrari.com',
    'Carlos Sainz': 'https://logo.clearbit.com/ferrari.com',
    'Lewis Hamilton': 'https://logo.clearbit.com/mercedesamgf1.com',
    'George Russell': 'https://logo.clearbit.com/mercedesamgf1.com',
    'Fernando Alonso': 'https://logo.clearbit.com/astonmartinf1.com',
    'Lance Stroll': 'https://logo.clearbit.com/astonmartinf1.com',
};

/**
 * Generate avatar URL for assets using local files
 * @param tradingAssetId - The trading asset ID (UUID from market_index_trading_assets table)
 * @param market - Market type to determine file extension (optional)
 * @param teamName - Team name for fallback lookup (optional)
 * @returns Avatar URL or null if not available
 */
export const getAvatarUrl = (tradingAssetId: string | undefined, market?: string, teamName?: string): string | null => {
    if (!tradingAssetId && !teamName) return null;

    // Use PNG files for EPL assets, SVG for others
    const extension = market === 'EPL' ? 'png' : 'svg';

    // First try UUID-based lookup (if available)
    if (tradingAssetId) {
        // Handle settled asset IDs by extracting the original trading asset ID
        let actualId = tradingAssetId;
        if (tradingAssetId.startsWith('settled-')) {
            // Extract the trading asset ID from the end of the composite ID
            const parts = tradingAssetId.split('-');
            if (parts.length >= 6) { // settled-{season_id}-{trading_asset_id}
                // The trading asset ID is the last 5 parts (UUID format)
                actualId = parts.slice(-5).join('-');
            }
        }

        // Only attempt UUID lookup for real UUIDs
        if (isLikelyUuid(actualId)) {
            const filename = `${actualId}.${extension}`;
            return `/avatars/${filename}`;
        }
    }

    // Fallback to team name-based lookup
    if (teamName) {
        // Normalize team name for filename: lowercase, replace spaces/special chars with underscores
        const normalizedName = teamName
            .toLowerCase()
            .replace(/[^a-z0-9]/g, '_') // Replace any non-alphanumeric with underscore
            .replace(/_+/g, '_') // Replace multiple underscores with single
            .replace(/^_|_$/g, ''); // Remove leading/trailing underscores

        const filename = `${normalizedName}.${extension}`;
        return `/avatars/${filename}`;
    }

    return null;
};

/**
 * Generate logo URL for a team/driver
 * @param name - Team or driver name
 * @param market - Market type (EPL, F1, etc.)
 * @param tradingAssetId - Trading asset ID for avatars (optional)
 * @returns Logo URL or null if not available
 */
export const getLogoUrl = (name: string, market: string, tradingAssetId?: string): string | null => {
    // Defensive programming - ensure we have valid inputs
    if (!name || !market) return null;

    // Try to use the generated avatar first (with both UUID and name fallback)
    const avatarUrl = getAvatarUrl(tradingAssetId, market, name);
    if (avatarUrl) return avatarUrl;

    // Fallback to traditional logo mappings
    if (TEAM_LOGOS[name]) {
        return TEAM_LOGOS[name];
    }

    // For teams not in our mapping, return null to show fallback
    return null;
};

/**
 * Get video URL for assets using local MP4 files
 * @param tradingAssetId - The trading asset ID (UUID from market_index_trading_assets table)
 * @returns Video URL or null if not available
 */
export const getVideoUrl = (tradingAssetId: string | undefined): string | null => {
    if (!tradingAssetId) return null;

    // Handle settled asset IDs by extracting the original trading asset ID
    let actualId = tradingAssetId;
    if (tradingAssetId.startsWith('settled-')) {
        // Extract the trading asset ID from the end of the composite ID
        const parts = tradingAssetId.split('-');
        if (parts.length >= 6) { // settled-{season_id}-{trading_asset_id}
            // The trading asset ID is the last 5 parts (UUID format)
            actualId = parts.slice(-5).join('-');
        }
    }

    const filename = `${actualId}.mp4`;
    return `/avatars/videos/${filename}`;
};

/**
 * Get 3D premium image URL for assets
 * @param tradingAssetId - The trading asset ID (UUID from market_index_trading_assets table)
 * @returns 3D image URL or null if not available
 */
export const get3DImageUrl = (tradingAssetId: string | undefined): string | null => {
    if (!tradingAssetId) return null;

    // Handle settled asset IDs by extracting the original trading asset ID
    let actualId = tradingAssetId;
    if (tradingAssetId.startsWith('settled-')) {
        // Extract the trading asset ID from the end of the composite ID
        const parts = tradingAssetId.split('-');
        if (parts.length >= 6) { // settled-{season_id}-{trading_asset_id}
            // The trading asset ID is the last 5 parts (UUID format)
            actualId = parts.slice(-5).join('-');
        }
    }

    // Look for the optimized WebP image
    const filename = `${actualId}.webp`;
    const imagePath = `/3d_images/${filename}`;

    // This assumes images are served from the public/3d_images directory
    return imagePath;
};

/**
 * Get fallback color for a team (from existing color field)
 */
export const getFallbackColor = (color?: string): string => {
    return color || '#6B7280';
};
