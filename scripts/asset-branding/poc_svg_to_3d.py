#!/usr/bin/env python3
"""
PoC Pipeline: Convert SVG Avatars to Premium 3D Images

This script processes SVG avatar files and converts them into premium 3D-style images
using Hugging Face Stable Diffusion XL inference.

PoC Features:
- Processes 1-2 SVG files for testing
- Extracts asset metadata from SVG structure
- Generates premium 3D badge images
- Optimizes images for web delivery
- Uploads to Cloudflare R2
- Generates frontend manifest

Usage:
    python poc_svg_to_3d.py [--svg-path path/to/file.svg] [--batch]

Requirements:
- HUGGINGFACE_API_KEY environment variable
- CLOUDFLARE_R2_ACCESS_KEY_ID
- CLOUDFLARE_R2_SECRET_ACCESS_KEY
- CLOUDFLARE_R2_ACCOUNT_ID
- CLOUDFLARE_R2_BUCKET_NAME
"""

import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import requests
from PIL import Image
import boto3
from botocore.client import Config
from dotenv import load_dotenv
import argparse
import re

# --------------------------------------------------
# Configuration
# --------------------------------------------------
load_dotenv()

# API Keys
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
if not HUGGINGFACE_API_KEY:
    raise RuntimeError("HUGGINGFACE_API_KEY not set")

# Cloudflare R2 Configuration
R2_ACCESS_KEY = os.getenv("CLOUDFLARE_R2_ACCESS_KEY_ID")
R2_SECRET_KEY = os.getenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY")
R2_ACCOUNT_ID = os.getenv("CLOUDFLARE_R2_ACCOUNT_ID")
R2_BUCKET_NAME = os.getenv("CLOUDFLARE_R2_BUCKET_NAME")

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
SVG_DIR = PROJECT_ROOT / "public" / "avatars"
INPUT_DIR = SCRIPT_DIR / "input"
OUTPUT_DIR = SCRIPT_DIR / "poc_output"
IMAGES_DIR = OUTPUT_DIR / "images"
OPTIMIZED_DIR = OUTPUT_DIR / "optimized"

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)
OPTIMIZED_DIR.mkdir(exist_ok=True)

# Stable Diffusion XL Model
SDXL_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
HF_INFERENCE_URL = f"https://api-inference.huggingface.co/models/{SDXL_MODEL}"

# Asset class mapping (icon detection)
ASSET_CLASS_MAP = {
    "football": ["football", "soccer"],
    "basketball": ["basketball"],
    "cricket": ["cricket"],
    "motorsport": ["racing"],
    "american_football": ["american", "football"],
    "music": ["music", "note"],
}


# --------------------------------------------------
# SVG Parsing Functions
# --------------------------------------------------
def parse_svg_metadata(svg_path: Path) -> dict:
    """
    Extract asset metadata from SVG file

    Args:
        svg_path: Path to SVG file

    Returns:
        Dictionary with asset metadata
    """
    # Extract asset ID from filename (UUID)
    asset_id = svg_path.stem

    # Ensure SVG path is absolute or relative to project root
    if not svg_path.is_absolute():
        # If running from scripts/asset-branding/, go up two levels to project root
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent
        svg_path = project_root / svg_path

    try:
        # Parse SVG XML
        tree = ET.parse(svg_path)
        root = tree.getroot()

        # Remove namespace for easier parsing
        for elem in root.iter():
            if "}" in elem.tag:
                elem.tag = elem.tag.split("}", 1)[1]

        metadata = {
            "asset_id": asset_id,
            "name": "",
            "initials": "",
            "market_token": "",
            "primary_color": "",
            "secondary_color": "",
            "asset_class": "football",  # default
        }

        # Extract colors from circles
        circles = root.findall(".//circle")
        for circle in circles:
            fill = circle.get("fill", "")
            stroke = circle.get("stroke", "")

            # Primary color (outer ring)
            if (
                fill
                and fill != "none"
                and fill != "url(#badgeReflect)"
                and not metadata["primary_color"]
            ):
                metadata["primary_color"] = fill

            # Secondary color (inner ring stroke)
            if stroke and stroke != "none":
                metadata["secondary_color"] = stroke

        # Extract text from textPath elements (inside text elements)
        text_paths = root.findall(".//textPath")
        for text_path in text_paths:
            text_content = text_path.text.strip() if text_path.text else ""

            if text_content and len(text_content) <= 4:  # Likely initials or token
                if not metadata["initials"]:
                    metadata["initials"] = text_content
                elif not metadata["market_token"]:
                    metadata["market_token"] = text_content

        # Try to determine asset class from SVG content
        svg_content = svg_path.read_text().lower()

        for asset_class, keywords in ASSET_CLASS_MAP.items():
            if any(keyword in svg_content for keyword in keywords):
                metadata["asset_class"] = asset_class
                break

        # Set name to initials if we don't have better info
        metadata["name"] = metadata["initials"]

        return metadata

    except Exception as e:
        print(f"Error parsing {svg_path}: {e}")
        return {
            "asset_id": asset_id,
            "name": asset_id[:8],  # fallback
            "initials": asset_id[:3].upper(),
            "market_token": "UNK",
            "primary_color": "#FF0000",
            "secondary_color": "#FFFFFF",
            "asset_class": "football",
        }


# --------------------------------------------------
# Stable Diffusion XL Inference
# --------------------------------------------------
def generate_3d_badge_image(asset_data: dict, svg_path: str = None) -> str:
    """
    Generate premium 3D badge image using Stable Diffusion XL image-to-image

    Args:
        asset_data: Asset metadata dictionary
        svg_path: Path to the source SVG file

    Returns:
        Path to generated image file
    """
    asset_id = asset_data["asset_id"]
    name = asset_data["name"]
    initials = asset_data["initials"]
    market_token = asset_data["market_token"]
    primary_color = asset_data["primary_color"]
    secondary_color = asset_data["secondary_color"]
    asset_class = asset_data["asset_class"]

    # Convert hex colors to descriptive names
    color_names = {
        "#FF0000": "red",
        "#0000FF": "blue",
        "#00FF00": "green",
        "#FFFF00": "yellow",
        "#FF6600": "orange",
        "#800080": "purple",
        "#FFC0CB": "pink",
        "#000000": "black",
        "#FFFFFF": "white",
        "#808080": "gray",
        "#006B3F": "green",
        "#FFCD00": "gold",
    }

    # Use the user-provided PNG file directly
    svg_png_path = INPUT_DIR / f"{asset_id}.png"

    if not svg_png_path.exists():
        print(f"ERROR PNG file not found: {svg_png_path}")
        print("Please ensure the PNG file exists in input/")
        return None

    print(f"SUCCESS Using input PNG file: {svg_png_path}")
    # PNG is ready - proceed to image-to-image generation

    try:
        print(f" Making API call to Hugging Face Inference...")
        # Prepare image-to-image API request using base64
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json",
        }

        # Read the PNG image and convert to base64
        import base64

        with open(svg_png_path, "rb") as f:
            image_bytes = f.read()
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        # 3D badge prompt adapted from video generation workflow (static version)
        # Extract colors for dynamic prompt

        prompt = f"""
A premium 3D physical badge that keeps the exact same shape, layout, and typography as the reference image.

Materials:
- Outer ring: glossy wet-look automotive paint
- Inner surface: polished dark enamel
- Lightning bolt: translucent emerald glass
- "{initials}" and "{market_token}": raised brushed stainless steel letters

Studio lighting, dark background, strong rim light.
Photorealistic, macro lens.

Do not change layout, proportions, geometry, or text.
"""

        # Negative prompt to prevent unwanted changes while forcing 3D transformation
        negative_prompt = """
flat, 2d, illustration, cartoon, anime, painting,
redesign, altered logo, changed layout,
incorrect text, wrong letters, extra symbols,
thin geometry, melted shapes,
motion, spinning, rotation, animation
"""

        print(f" Generating 3D badge for {name} ({asset_id})")
        print(f" Using input image: {svg_png_path}")
        print(f" Strength: 0.3 (retain original design, add 3D materials)")
        print(f" Prompt: {prompt[:150]}...")
        print(f" Processing with Stable Diffusion XL image-to-image...")

        # Create JSON payload for image-to-image
        payload = {
            "inputs": {
                "image": f"data:image/png;base64,{image_b64}",
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "strength": 0.15,  # Retain original design while adding 3D effects
                "guidance_scale": 7.0,  # Higher guidance for stronger prompt adherence
                "num_inference_steps": 50,
                "seed": 42,  # For reproducible results in PoC
            }
        }

        response = requests.post(
            HF_INFERENCE_URL, headers=headers, json=payload, timeout=120
        )

        if response.status_code == 200:
            # Save the image (force overwrite existing)
            image_path = IMAGES_DIR / f"{asset_id}.png"
            with open(image_path, "wb") as f:
                f.write(response.content)

            print(f"SUCCESS 3D Image generated: {image_path}")
            return str(image_path)
        else:
            print(f"ERROR Generation failed: {response.status_code}")
            print(f"Response: {response.text[:500]}...")  # First 500 chars of response
            return None

    except Exception as e:
        print(f"ERROR API Error: {e}")
        return None


# --------------------------------------------------
# Image Optimization
# --------------------------------------------------
def optimize_image(image_path: str, asset_id: str) -> dict:
    """
    Optimize image for web delivery

    Args:
        image_path: Path to input image
        asset_id: Asset ID for naming

    Returns:
        Dictionary with paths to optimized images
    """
    try:
        # Open image
        img = Image.open(image_path)

        # Convert to RGB if necessary
        if img.mode != "RGB":
            img = img.convert("RGB")

        optimized_paths = {}

        # Generate 512px and 256px versions
        for size in [512, 256]:
            # Resize with high quality
            resized = img.resize((size, size), Image.Resampling.LANCZOS)

            # Save as WebP with optimization
            webp_path = OPTIMIZED_DIR / f"{asset_id}_{size}px.webp"
            resized.save(
                webp_path,
                "WebP",
                quality=85,  # Good balance of quality/size
                method=6,  # Best compression
                lossless=False,
            )

            optimized_paths[f"{size}px"] = str(webp_path)
            print(f"SUCCESS Optimized {size}px: {webp_path}")

        return optimized_paths

    except Exception as e:
        print(f"ERROR Optimization error: {e}")
        return {}


# --------------------------------------------------
# Cloudflare R2 Upload
# --------------------------------------------------
def upload_to_r2(local_paths: dict, asset_id: str) -> dict:
    """
    Upload optimized images to Cloudflare R2

    Args:
        local_paths: Dictionary of local file paths
        asset_id: Asset ID for R2 path structure

    Returns:
        Dictionary with R2 URLs
    """
    if not all([R2_ACCESS_KEY, R2_SECRET_KEY, R2_ACCOUNT_ID, R2_BUCKET_NAME]):
        print("WARNING R2 credentials not configured, skipping upload")
        return {size: f"local://{path}" for size, path in local_paths.items()}

    try:
        # Configure R2 client
        r2_client = boto3.client(
            "s3",
            endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
            aws_access_key_id=R2_ACCESS_KEY,
            aws_secret_access_key=R2_SECRET_KEY,
            config=Config(signature_version="s3v4"),
        )

        uploaded_urls = {}

        for size, local_path in local_paths.items():
            r2_key = f"avatars/{asset_id}/{size}.webp"

            # Upload file
            with open(local_path, "rb") as f:
                r2_client.upload_fileobj(f, R2_BUCKET_NAME, r2_key)

            # Generate public URL
            r2_url = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com/{R2_BUCKET_NAME}/{r2_key}"
            uploaded_urls[size] = r2_url

            print(f"SUCCESS Uploaded {size}: {r2_url}")

        return uploaded_urls

    except Exception as e:
        print(f"ERROR R2 upload error: {e}")
        return {size: f"error://{e}" for size in local_paths.keys()}


# --------------------------------------------------
# Manifest Generation
# --------------------------------------------------
def generate_manifest(assets_data: list) -> str:
    """
    Generate JSON manifest for frontend consumption

    Args:
        assets_data: List of processed asset dictionaries

    Returns:
        Path to generated manifest file
    """
    manifest = {
        "version": "1.0",
        "description": "Premium 3D avatar images manifest",
        "generated_at": "2024-01-01T00:00:00Z",  # Would use datetime in production
        "assets": {},
    }

    for asset in assets_data:
        manifest["assets"][asset["asset_id"]] = {
            "name": asset["name"],
            "initials": asset["initials"],
            "market_token": asset["market_token"],
            "asset_class": asset["asset_class"],
            "colors": {
                "primary": asset["primary_color"],
                "secondary": asset["secondary_color"],
            },
            "images": asset["r2_urls"],
        }

    # Save manifest
    manifest_path = OUTPUT_DIR / "avatar_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"SUCCESS Manifest generated: {manifest_path}")
    return str(manifest_path)


# --------------------------------------------------
# Main Processing
# --------------------------------------------------
def process_png_file(asset_id: str) -> dict:
    """
    Process a PNG file from poc_output/images/ through the image-to-image pipeline

    Args:
        asset_id: Asset ID (filename without extension)

    Returns:
        Processed asset data dictionary
    """
    print(f"\n Processing asset: {asset_id}")

    # Create basic asset data (we'll get metadata from the asset ID)
    asset_data = {
        "asset_id": asset_id,
        "name": asset_id[:3].upper(),  # Extract initials from asset ID
        "initials": asset_id[:3].upper(),
        "market_token": "TBD",  # Will be determined from context
        "primary_color": "#005CB8",  # Default blue
        "secondary_color": "#FFFFFF",  # Default white
        "asset_class": "football",
    }

    # Try to extract better metadata from the asset ID or context
    # For Marseille (MAR), we know it's UCL
    if asset_id.startswith("0a4cbe88"):  # Marseille asset
        asset_data.update(
            {
                "name": "MAR",
                "initials": "MAR",
                "market_token": "UCL",
                "primary_color": "#005CB8",  # Marseille blue
                "secondary_color": "#FFFFFF",
            }
        )

    print(
        f"    Using PNG file for: {asset_data['name']} ({asset_data['initials']}) - {asset_data['market_token']}"
    )

    # Step 1: Generate 3D image from PNG
    print("    Step 1: Generating 3D badge image from PNG...")
    image_path = generate_3d_badge_image(asset_data)
    if not image_path:
        return None

    # Step 2: Optimize images
    print("    Step 2: Optimizing images...")
    optimized_paths = optimize_image(image_path, asset_id)
    if not optimized_paths:
        return None

    # Step 3: Upload to R2 (skipped if --skip-upload used)
    print("   Step 3: Uploading to R2...")
    r2_urls = upload_to_r2(optimized_paths, asset_id)

    # Combine all data
    asset_data.update(
        {
            "local_image": image_path,
            "optimized_images": optimized_paths,
            "r2_urls": r2_urls,
        }
    )

    print(f"   SUCCESS Processing complete for {asset_id}")
    return asset_data


# --------------------------------------------------
# Main Function
# --------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="PoC: Convert PNG avatars to premium 3D images"
    )
    parser.add_argument(
        "--png-id", help="Asset ID of PNG file in poc_output/images/ to process"
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=1,
        help="Number of PNGs to process in batch mode (default: 1)",
    )
    parser.add_argument(
        "--skip-upload", action="store_true", help="Skip R2 upload for local testing"
    )

    args = parser.parse_args()

    print("Starting PoC: SVG to 3D Premium Images Pipeline")
    print("=" * 60)

    # Find PNG files in input folder
    if args.png_id:
        png_files = [args.png_id]
        print(f" Processing specific PNG: {args.png_id}")
    else:
        # Look for PNG files in input folder
        png_files = []
        for png_file in INPUT_DIR.glob("*.png"):
            png_files.append(png_file.stem)  # Just the filename without extension

        png_files = png_files[: args.batch]
        print(f" Processing {len(png_files)} PNG files from {INPUT_DIR}")

    if not png_files:
        print("ERROR No PNG files found in poc_output/images/")
        print("Please place PNG files in scripts/asset-branding/poc_output/images/")
        return 1

    # Process each PNG
    processed_assets = []

    for png_id in png_files:
        asset_data = process_png_file(png_id)
        if asset_data:
            processed_assets.append(asset_data)

    if not processed_assets:
        print("ERROR No assets were successfully processed!")
        return 1

    # Generate manifest
    print("\n Generating manifest...")
    manifest_path = generate_manifest(processed_assets)

    # Summary
    print("\n PoC Pipeline Complete!")
    print(f"SUCCESS Processed assets: {len(processed_assets)}")
    print(f" Output directory: {OUTPUT_DIR}")
    print(f" Manifest: {manifest_path}")

    print("\n Next steps for production:")
    print("   1. Scale up batch processing")
    print("   2. Implement error handling and retries")
    print("   3. Add progress tracking for large batches")
    print("   4. Set up monitoring and cost tracking")
    print("   5. Integrate with CI/CD pipeline")

    return 0


if __name__ == "__main__":
    exit(main())
