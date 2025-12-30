"""
Video Deployment Script
Copies generated videos from scripts/asset-branding/veo3/ to public/avatars/videos/
Maps asset names to trading asset IDs using the database.
"""

import os
import re
import shutil
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

# --------------------------------------------------
# Setup
# --------------------------------------------------
load_dotenv()

DATABASE_URL = os.getenv("DEV_DB_URL")
if not DATABASE_URL:
    raise RuntimeError("DEV_DB_URL not set")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VEO3_DIR = os.path.join(BASE_DIR, "veo3")
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
OUTPUT_VIDEOS_DIR = os.path.join(PROJECT_ROOT, "public", "avatars", "videos")

os.makedirs(OUTPUT_VIDEOS_DIR, exist_ok=True)


# --------------------------------------------------
# Helpers
# --------------------------------------------------
def normalize_asset_name(filename: str) -> str:
    """
    Extract asset name from video filename.
    Examples:
        'Marseille_Animation.mp4' -> 'Marseille'
        'Liverpool_Animation.mp4' -> 'Liverpool'
        'Lando Norris_Animation.mp4' -> 'Lando Norris'
    """
    # Remove _Animation.mp4 suffix
    name = filename.replace("_Animation.mp4", "").replace(".mp4", "")
    return name.strip()


def get_trading_asset_id_map(conn) -> dict[str, str]:
    """
    Query database to create a mapping: asset_name -> trading_asset_id
    Returns a dictionary for lookup.
    """
    cur = conn.cursor()
    
    cur.execute(
        """
        SELECT
            a.name,
            mita.id as trading_asset_id
        FROM market_index_trading_assets mita
        JOIN assets a ON a.id = mita.asset_id
        WHERE mita.status IN ('active', 'settled')
        ORDER BY a.name;
        """
    )
    
    rows = cur.fetchall()
    name_to_id = {}
    
    for name, trading_asset_id in rows:
        # Normalize name for matching (case-insensitive)
        normalized = name.strip().lower()
        name_to_id[normalized] = trading_asset_id
    
    cur.close()
    return name_to_id


def find_video_files() -> list[Path]:
    """Find all MP4 files in the veo3 directory."""
    veo3_path = Path(VEO3_DIR)
    if not veo3_path.exists():
        print(f"⚠️  VEO3 directory not found: {VEO3_DIR}")
        return []
    
    video_files = list(veo3_path.glob("*.mp4"))
    return video_files


# --------------------------------------------------
# Main
# --------------------------------------------------
def main():
    print("🎬 Video Deployment Script")
    print("=" * 50)
    
    # Connect to database
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Get asset name to trading asset ID mapping
    print("📊 Loading asset mappings from database...")
    name_to_id = get_trading_asset_id_map(conn)
    print(f"✅ Loaded {len(name_to_id)} asset mappings")
    
    # Find video files
    video_files = find_video_files()
    if not video_files:
        print("⚠️  No MP4 files found in veo3/ directory")
        conn.close()
        return
    
    print(f"\n📹 Found {len(video_files)} video file(s) to process")
    print("-" * 50)
    
    copied_count = 0
    skipped_count = 0
    error_count = 0
    
    for video_file in video_files:
        filename = video_file.name
        asset_name = normalize_asset_name(filename)
        
        # Try to find matching trading asset ID
        normalized_name = asset_name.lower()
        trading_asset_id = name_to_id.get(normalized_name)
        
        if not trading_asset_id:
            print(f"⚠️  Skipping {filename} - No matching asset found for '{asset_name}'")
            skipped_count += 1
            continue
        
        # Destination path
        dest_filename = f"{trading_asset_id}.mp4"
        dest_path = os.path.join(OUTPUT_VIDEOS_DIR, dest_filename)
        
        try:
            # Copy file
            shutil.copy2(video_file, dest_path)
            print(f"✅ {asset_name} -> {trading_asset_id}.mp4")
            copied_count += 1
        except Exception as e:
            print(f"❌ Error copying {filename}: {e}")
            error_count += 1
    
    conn.close()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Deployment Summary:")
    print(f"   ✅ Copied: {copied_count}")
    print(f"   ⚠️  Skipped: {skipped_count}")
    print(f"   ❌ Errors: {error_count}")
    print(f"\n📁 Videos deployed to: {OUTPUT_VIDEOS_DIR}")
    
    if copied_count > 0:
        print("\n🎉 Deployment complete! Videos are ready for frontend use.")


# --------------------------------------------------
if __name__ == "__main__":
    main()

