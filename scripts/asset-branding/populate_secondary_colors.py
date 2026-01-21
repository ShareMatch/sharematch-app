import os
import json
import re
import time
import psycopg2
from dotenv import load_dotenv
from google import genai
from google.genai import types

# --------------------------------------------------
# Setup
# --------------------------------------------------
load_dotenv()

DEV_DB_URL = os.getenv("DEV_DB_URL")
API_KEY = os.getenv("API_KEY")

if not DEV_DB_URL:
    raise RuntimeError("DEV_DB_URL not found in environment")
if not API_KEY:
    raise RuntimeError("API_KEY (Gemini) not found in environment")

# Initialize Gemini Client
client = genai.Client(api_key=API_KEY)


# --------------------------------------------------
# Helpers
# --------------------------------------------------
def is_valid_hex(hex_code):
    return bool(re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", hex_code))


def fetch_secondary_color_only(asset_name, asset_class, primary_color):
    """
    Uses Gemini-3-Flash to retrieve only secondary brand color given a primary color.
    """
    prompt = f"""
    Find the OFFICIAL secondary brand HEX color code for the following asset:
    
    Name: {asset_name}
    Asset Class: {asset_class}
    Primary Color: {primary_color}

    INSTRUCTIONS:
    - Identify the specific entity based on name and class (e.g., F1 team, football club).
    - Find the official secondary/accent color that complements their primary brand color.
    - This should be the main supporting color used in their branding (not the primary).
    - Return data in strict JSON format with key "secondary" only.
    - Ensure valid HEX code including '#' symbol.
    """

    max_retries = 5
    base_delay = 10  # Seconds

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                ),
            )

            # Parse JSON from response
            color_data = json.loads(response.text)
            s = color_data.get("secondary", "").upper()

            # Validate format
            if is_valid_hex(s):
                return s
            return None

        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                wait_time = base_delay * (2**attempt)  # Exponential backoff
                print(
                    f"⚠️ Rate limit hit for {asset_name}. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}..."
                )
                time.sleep(wait_time)
            else:
                print(f"⚠️ API Error for {asset_name}: {e}")
                return None

    print(f"❌ Failed to fetch secondary color for {asset_name} after {max_retries} retries.")
    return None


def fetch_official_colors(asset_name, category, asset_class):
    """
    Uses Gemini-3-Flash to retrieve verified brand colors with context.
    Handles rate limiting (429) with retries.
    """
    prompt = f"""
    Find the OFFICIAL primary and secondary brand HEX color codes for the following asset:
    
    Name: {asset_name}
    Category: {category}
    Asset Class: {asset_class}

    INSTRUCTIONS:
    - Identify the specific entity based on the name and category/class (e.g., a football club, an F1 team, a company).
    - Find the official colors used in their main branding representation (e.g., official logo, home kit, main livery).
    - Return the data in a strict JSON format with keys "primary" and "secondary".
    - "primary": The dominant color most associated with the brand (e.g., Red for Man Utd, Ferrari Red for Ferrari).
    - "secondary": The main accent or supporting color.
    - Ensure valid HEX codes including the '#' symbol.
    """

    max_retries = 5
    base_delay = 10  # Seconds

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                ),
            )

            # Parse JSON from response
            color_data = json.loads(response.text)

            p = color_data.get("primary", "").upper()
            s = color_data.get("secondary", "").upper()

            # Validate format
            if is_valid_hex(p) and is_valid_hex(s):
                return p, s
            return None, None

        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                wait_time = base_delay * (2**attempt)  # Exponential backoff
                print(
                    f"⚠️ Rate limit hit for {asset_name}. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}..."
                )
                time.sleep(wait_time)
            else:
                print(f"⚠️ API Error for {asset_name}: {e}")
                return None, None

    print(f"❌ Failed to fetch colors for {asset_name} after {max_retries} retries.")
    return None, None


# --------------------------------------------------
# Main Execution
# --------------------------------------------------
def main():
    conn = psycopg2.connect(DEV_DB_URL)
    cur = conn.cursor()

    # Step 1: Copy color field to primary_color for assets that have color but no primary_color
    print("🎨 Step 1: Copying color to primary_color where needed...")
    cur.execute(
        """
        UPDATE assets 
        SET primary_color = color, updated_at = now()
        WHERE color IS NOT NULL 
        AND primary_color IS NULL
        """
    )
    copied_count = cur.rowcount
    conn.commit()
    print(f"✅ Copied color to primary_color for {copied_count} assets")

    # Step 2: Select all assets that have a MITA record, getting MITA ID as well
    print("🔍 Step 2: Fetching assets for secondary color generation...")
    cur.execute(
        """
        SELECT DISTINCT
            a.id,
            a.name,
            a.primary_color,
            a.secondary_color,
            COALESCE(
                mita.avatar_class,
                CASE
                    WHEN m.market_token = 'F1' THEN 'motorsport'
                    WHEN m.market_token = 'NBA' THEN 'basketball'
                    WHEN m.market_token = 'NFL' THEN 'american_football'
                    WHEN m.market_token = 'EUROVISION' THEN 'music'
                    ELSE 'football'
                END
            ) AS asset_class,
            mita.id AS mita_id
        FROM assets a
        JOIN market_index_trading_assets mita
          ON mita.asset_id = a.id
        JOIN market_index_seasons mis
          ON mis.id = mita.market_index_season_id
        JOIN market_indexes mi
          ON mi.id = mis.market_index_id
        JOIN markets m
          ON m.id = mi.market_id
        WHERE a.secondary_color IS NULL
        """
    )

    assets = cur.fetchall()
    print(f"🔍 Found {len(assets)} assets that need secondary colors.")

    # iterate
    for asset_id, name, primary_color, secondary_color, asset_class, mita_id in assets:
        # Skip if we already have both colors
        if primary_color and secondary_color:
            print(f"✅ {name} already has both colors - skipping")
            continue
            
        # Use asset_class as primary category context for prompt
        print(f"→ Querying Gemini for: {name} (Class: {asset_class})...")

        # Use existing primary_color if available, otherwise fetch both
        if primary_color:
            # Only fetch secondary color
            secondary = fetch_secondary_color_only(name, asset_class, primary_color)
            if secondary:
                # Update ASSETS table
                cur.execute(
                    """
                    UPDATE assets 
                    SET secondary_color = %s, 
                        updated_at = now() 
                    WHERE id = %s
                    """,
                    (secondary, asset_id),
                )

                # Update MITA table
                cur.execute(
                    """
                    UPDATE market_index_trading_assets
                    SET primary_color = %s,
                        secondary_color = %s,
                        updated_at = now()
                    WHERE id = %s
                    """,
                    (primary_color, secondary, mita_id),
                )

                conn.commit()
                print(f"✅ [UPDATED] {name} | Primary: {primary_color} | Secondary: {secondary}")
            else:
                print(f"❌ Could not get secondary color for {name}")
        else:
            # Fetch both colors
            primary, secondary = fetch_official_colors(
                name, "Sports/Entertainment Asset", asset_class
            )

            if primary and secondary:
                # Update ASSETS table
                cur.execute(
                    """
                    UPDATE assets 
                    SET primary_color = %s, 
                        secondary_color = %s, 
                        updated_at = now() 
                    WHERE id = %s
                    """,
                    (primary, secondary, asset_id),
                )

                # Update MITA table
                cur.execute(
                    """
                    UPDATE market_index_trading_assets
                    SET primary_color = %s,
                        secondary_color = %s,
                        updated_at = now()
                    WHERE id = %s
                    """,
                    (primary, secondary, mita_id),
                )

                conn.commit()
                print(f"✅ [UPDATED] {name} | Primary: {primary} | Secondary: {secondary}")
            else:
                print(f"❌ Could not verify colors for {name}")

        # Throttle to respect rate limits (10 RPM = 60s/10 = 6s delay minimum)
        time.sleep(7.0)

    cur.close()
    conn.close()
    print("🎉 Update complete.")


if __name__ == "__main__":
    main()
