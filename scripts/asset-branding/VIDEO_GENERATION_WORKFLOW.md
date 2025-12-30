# 🎥 Workflow: Creating Animated Asset Badges (AI Pipeline)

This document outlines the proven workflow for converting 2D asset SVGs into premium 3D 8K video assets using a 2-step GenAI pipeline.

**Input:** Flat SVG/PNG avatar from `scripts/asset-branding/output` or `public/avatars`.

**Output:** 8K MP4 video file in `scripts/asset-branding/veo3`.

---

## The Pipeline

### Step 1: Image Enhancement (ChatGPT/DALL-E 3)

**Goal:** Convert the flat vector graphic into a photorealistic, "glossy" still image to guide the video model.

1. **Locate the Source SVG:**
   - Find the asset's SVG file in `public/avatars/{trading_asset_id}.svg`
   - Or check `scripts/asset-branding/output/{category}/{trading_asset_id}.svg`
   - The filename is the trading asset ID (UUID format)

2. **Extract Asset Details:**
   - Open the SVG file to identify:
     - **Primary Color**: The outer ring color (e.g., `#FF0000` for red)
     - **Secondary Color**: The inner ring and text color (usually white `#FFFFFF`)
     - **Initials**: The 3-letter code at the top (e.g., "MAR" for Marseille)
     - **Market Token**: The index code at the bottom (e.g., "UCL" for Champions League)
     - **Asset Name**: The full name of the asset (e.g., "Marseille")

3. **Upload to ChatGPT:**
   - Go to ChatGPT (Model 4o with DALL-E access)
   - Upload the SVG file
   - Use the **Standard Animation Prompt** (below) customized for this asset

4. **Download the Result:**
   - Save the generated high-fidelity image
   - This will be the input for Step 2

### Step 2: Video Generation (Veo3)

**Goal:** Animate the still image into a spinning video loop.

1. **Upload the Glossy Still Image:**
   - Take the image from Step 1
   - Upload it to Veo3

2. **Use the Same Prompt:**
   - Use the **exact same prompt** from Step 1
   - This ensures consistency between the still and the animation

3. **Generate the Video:**
   - Let Veo3 process the animation
   - The video should show a smooth 360-degree rotation

4. **Save the MP4:**
   - Download the generated video
   - Save it to: `scripts/asset-branding/veo3/{Asset_Name}_Animation.mp4`
   - Example: `scripts/asset-branding/veo3/Marseille_Animation.mp4`

5. **Deploy to Public Folder:**
   - Run the deployment script: `python scripts/asset-branding/copy_videos_to_public.py`
   - This will automatically:
     - Map the asset name to the trading asset ID
     - Copy the video to `public/avatars/videos/{trading_asset_id}.mp4`
     - Ensure correct naming for frontend lookup

---

## 📝 The Standard Prompt Template

Use this exact prompt structure for both steps, customizing the placeholders:

```
Bring this badge to life as a premium 3D physical token spinning in a dark studio. 
The outer [PRIMARY_COLOR_NAME] circle is glossy, wet-look automotive paint. 
The central [ICON_DESCRIPTION] is translucent glowing [SECONDARY_COLOR_NAME] glass. 
"[INITIALS]" and "[MARKET_TOKEN]" are raised, brushed stainless steel letters. 
The coin rotates slowly and smoothly 360 degrees. 
As it turns, a ray of light sweeps across the glossy surface. 
Cinematic, 8k, photorealistic, macro lens.
```

### Customization Guide

Replace the placeholders based on the asset:

- **`[PRIMARY_COLOR_NAME]`**: Describe the outer ring color (e.g., "blue", "red", "green")
- **`[ICON_DESCRIPTION]`**: Describe the center icon (e.g., "green lightning bolt", "football", "racing car")
- **`[SECONDARY_COLOR_NAME]`**: Usually "emerald" or "white" depending on the design
- **`[INITIALS]`**: The 3-letter code from the top of the badge (e.g., "MAR", "LIV", "MCI")
- **`[MARKET_TOKEN]`**: The index code from the bottom (e.g., "UCL", "EPL", "F1")

### Example: Marseille (UCL)

```
Bring this badge to life as a premium 3D physical token spinning in a dark studio. 
The outer blue circle is glossy, wet-look automotive paint. 
The central green lightning bolt is translucent glowing emerald glass. 
"MAR" and "UCL" are raised, brushed stainless steel letters. 
The coin rotates slowly and smoothly 360 degrees. 
As it turns, a ray of light sweeps across the glossy surface. 
Cinematic, 8k, photorealistic, macro lens.
```

### Example: Liverpool (EPL)

```
Bring this badge to life as a premium 3D physical token spinning in a dark studio. 
The outer red circle is glossy, wet-look automotive paint. 
The central football icon is translucent glowing white glass. 
"LIV" and "EPL" are raised, brushed stainless steel letters. 
The coin rotates slowly and smoothly 360 degrees. 
As it turns, a ray of light sweeps across the glossy surface. 
Cinematic, 8k, photorealistic, macro lens.
```

---

## Directory Structure

```
scripts/asset-branding/
├── veo3/                          # Generated videos (manual workflow)
│   ├── Marseille_Animation.mp4
│   ├── Liverpool_Animation.mp4
│   └── ...
├── output/                        # Source SVGs (if needed)
│   └── {category}/
│       └── {trading_asset_id}.svg
└── VIDEO_GENERATION_WORKFLOW.md   # This file

public/avatars/
├── {trading_asset_id}.svg         # Static avatars
└── videos/                        # Deployed videos (auto-generated)
    └── {trading_asset_id}.mp4
```

---

## Quick Reference: Finding Asset Details

### From Database Query

If you need to look up asset details, you can query:

```sql
SELECT 
    mita.id as trading_asset_id,
    a.name,
    mita.primary_asset_color,
    mita.secondary_asset_color,
    m.market_token
FROM market_index_trading_assets mita
JOIN assets a ON a.id = mita.asset_id
JOIN market_index_seasons mis ON mis.id = mita.market_index_season_id
JOIN market_indexes mi ON mi.id = mis.market_index_id
JOIN markets m ON m.id = mi.market_id
WHERE a.name = 'Marseille';  -- Replace with your asset name
```

### From SVG File

Open the SVG in a text editor and look for:
- `fill="{{PRIMARY_COLOR}}"` → Primary color
- `fill="{{SECONDARY_COLOR}}"` → Secondary color  
- `{{INITIALS}}` → The initials text
- `{{INDEX_CODE}}` → The market token

Or check the generated SVG in `public/avatars/{trading_asset_id}.svg` where these placeholders are replaced with actual values.

---

## Tips & Best Practices

1. **Consistency is Key**: Use the exact same prompt for both ChatGPT and Veo3
2. **Color Accuracy**: Match the color descriptions to the actual SVG colors
3. **File Naming**: Always use `{Asset_Name}_Animation.mp4` format in `veo3/` folder
4. **Deployment**: Always run the copy script after generating videos
5. **Testing**: Verify the video displays correctly in the frontend before generating more

---

## Troubleshooting

**Video not displaying in frontend?**
- Check that the video was copied to `public/avatars/videos/` with the correct trading asset ID
- Verify the filename matches exactly: `{trading_asset_id}.mp4`
- Check browser console for 404 errors

**Can't find the asset SVG?**
- Check `public/avatars/{trading_asset_id}.svg`
- Or run the avatar generation script to create it

**Video quality issues?**
- Ensure you're requesting 8K resolution in the prompt
- Use "photorealistic" and "macro lens" keywords for best quality

