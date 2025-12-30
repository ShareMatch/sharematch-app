#!/usr/bin/env python3
"""
🧪 Test PoC Pipeline Setup

Validates that all dependencies and configurations are ready for the SVG to 3D pipeline.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_environment():
    """Test environment variables"""
    print("🔍 Testing environment variables...")

    load_dotenv()

    # Required for generation
    hf_key = os.getenv("HUGGINGFACE_API_KEY")
    if hf_key:
        print("✅ HUGGINGFACE_API_KEY is set")
    else:
        print("❌ HUGGINGFACE_API_KEY not found")
        return False

    # Optional for upload
    r2_vars = [
        "CLOUDFLARE_R2_ACCESS_KEY_ID",
        "CLOUDFLARE_R2_SECRET_ACCESS_KEY",
        "CLOUDFLARE_R2_ACCOUNT_ID",
        "CLOUDFLARE_R2_BUCKET_NAME"
    ]

    r2_set = all(os.getenv(var) for var in r2_vars)
    if r2_set:
        print("✅ Cloudflare R2 credentials configured")
    else:
        print("⚠️  Cloudflare R2 credentials not found (optional for local testing)")

    return True

def test_dependencies():
    """Test Python dependencies"""
    print("\n🔍 Testing Python dependencies...")

    deps = [
        ("requests", "requests"),
        ("PIL", "Pillow"),
        ("boto3", "boto3"),
        ("dotenv", "python-dotenv"),
    ]

    all_good = True
    for import_name, package_name in deps:
        try:
            __import__(import_name)
            print(f"✅ {package_name} available")
        except ImportError:
            print(f"❌ {package_name} not installed")
            print(f"   Install with: pip install {package_name}")
            all_good = False

    return all_good

def test_svg_files():
    """Test SVG file access"""
    print("\n🔍 Testing SVG file access...")

    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    svg_dir = project_root / "public" / "avatars"

    if not svg_dir.exists():
        print(f"❌ SVG directory not found: {svg_dir}")
        return False

    svg_files = list(svg_dir.glob("*.svg"))
    print(f"✅ Found {len(svg_files)} SVG files in {svg_dir}")

    if svg_files:
        # Test parsing one file
        try:
            import xml.etree.ElementTree as ET
            test_file = svg_files[0]
            ET.parse(test_file)
            print(f"✅ SVG parsing works: {test_file.name}")
        except Exception as e:
            print(f"❌ SVG parsing failed: {e}")
            return False

    return True

def test_directories():
    """Test output directories"""
    print("\n🔍 Testing output directories...")

    script_dir = Path(__file__).parent
    output_dir = script_dir / "poc_output"
    images_dir = output_dir / "images"
    optimized_dir = output_dir / "optimized"

    # Create directories if they don't exist
    output_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)
    optimized_dir.mkdir(exist_ok=True)

    dirs_to_check = [output_dir, images_dir, optimized_dir]
    for dir_path in dirs_to_check:
        if dir_path.exists():
            print(f"✅ Directory ready: {dir_path.relative_to(script_dir)}")
        else:
            print(f"❌ Directory missing: {dir_path}")
            return False

    return True

def main():
    """Run all tests"""
    print("🧪 PoC Pipeline Setup Test")
    print("=" * 40)

    tests = [
        ("Environment Variables", test_environment),
        ("Python Dependencies", test_dependencies),
        ("SVG File Access", test_svg_files),
        ("Output Directories", test_directories),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 Testing: {test_name}")
        print("-" * 30)
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name}: FAILED")

    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! You're ready to run the PoC pipeline.")
        print("\n🚀 Try running:")
        print("   python scripts/asset-branding/poc_svg_to_3d.py --batch 1")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\n🔧 Common fixes:")
        print("   - Install missing dependencies: pip install -r scripts/asset-branding/requirements-poc.txt")
        print("   - Set HUGGINGFACE_API_KEY in your .env file")
        print("   - Check that SVG files exist in public/avatars/")

    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
