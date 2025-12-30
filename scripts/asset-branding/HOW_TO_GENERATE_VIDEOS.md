# 🎬 How to Generate Videos: Step-by-Step Guide

This is a practical walkthrough for creating animated asset badges using ChatGPT/DALL-E 3 and Veo3.

---

## Prerequisites

- **ChatGPT Plus** subscription (for DALL-E 3 access)
- **Veo3** access (Google's video generation tool)
- An asset SVG file from `public/avatars/`

---

## Step 1: Find Your Asset SVG

1. **Pick an asset** you want to animate (e.g., "Marseille", "Liverpool", "Lando Norris")
2. **Find the SVG file** in `public/avatars/`
   - Files are named by trading asset ID (UUID format)
   - You can open any SVG to see which asset it is
   - Or query the database to find the trading asset ID for a specific asset name

**Example:** Let's say you want to create a video for "Marseille"
- The SVG might be: `public/avatars/0a4cbe88-dc22-414c-b453-0bffa6a91dcc.svg`
- Open it to verify it shows "MAR" and "UCL" (Marseille in Champions League)

---

## Step 2: Extract Asset Details from SVG

Open the SVG file in a text editor or browser to identify:

1. **Primary Color** (outer ring): Look for `fill="#005CB8"` → This is blue (`#005CB8`)
2. **Secondary Color** (text/ring): Look for `fill="#FFFFFF"` → This is white
3. **Initials** (top text): Look for text content → "MAR"
4. **Market Token** (bottom text): Look for text content → "UCL"
5. **Asset Name**: "Marseille" (you know this from the asset)

**From the example SVG:**
- Primary Color: `#005CB8` (blue)
- Secondary Color: `#FFFFFF` (white)
- Initials: "MAR"
- Market Token: "UCL"
- Asset Name: "Marseille"

---

## Step 3: Create Glossy Still Image (ChatGPT/DALL-E 3)

### 3.1 Open ChatGPT

1. Go to [chat.openai.com](https://chat.openai.com)
2. Make sure you're using **GPT-4** (with DALL-E access)
3. Start a new conversation

### 3.2 Upload the SVG

1. Click the **attachment/upload button** (📎 icon) in the chat
2. Select your SVG file (e.g., `0a4cbe88-dc22-414c-b453-0bffa6a91dcc.svg`)
3. Wait for it to upload

### 3.3 Create the Prompt

Use this template, customizing it for your asset:

```
Bring this badge to life as a premium 3D physical token spinning in a dark studio. 
The outer blue circle is glossy, wet-look automotive paint. 
The central green lightning bolt is translucent glowing emerald glass. 
"MAR" and "UCL" are raised, brushed stainless steel letters. 
The coin rotates slowly and smoothly 360 degrees. 
As it turns, a ray of light sweeps across the glossy surface. 
Cinematic, 8k, photorealistic, macro lens.
```

**For Marseille (from our example):**
- Outer color: **blue** (from `#005CB8`)
- Center icon: **green lightning bolt** (the ShareMatch bolt)
- Secondary color: **emerald** (green glow)
- Initials: **"MAR"**
- Market token: **"UCL"**

### 3.4 Generate and Download

1. Send the prompt to ChatGPT
2. Wait for DALL-E 3 to generate the image
3. **Download the high-quality image** (click the image, then download)
4. Save it temporarily (you'll use it in Step 4)

**What you should get:** A photorealistic, glossy 3D rendering of the badge that looks like a physical coin/token.

---

## Step 4: Animate the Still Image (Veo3)

### 4.1 Access Veo3

1. Go to [Veo3](https://veo.google/) (or wherever you access Google's Veo3)
2. Sign in if needed
3. Navigate to the video generation interface

### 4.2 Upload the Glossy Still Image

1. Click **"Upload"** or **"Create Video"**
2. Select the **glossy still image** you downloaded from Step 3
3. Wait for it to upload

### 4.3 Use the Same Prompt

**IMPORTANT:** Use the **exact same prompt** you used in Step 3!

```
Bring this badge to life as a premium 3D physical token spinning in a dark studio. 
The outer blue circle is glossy, wet-look automotive paint. 
The central green lightning bolt is translucent glowing emerald glass. 
"MAR" and "UCL" are raised, brushed stainless steel letters. 
The coin rotates slowly and smoothly 360 degrees. 
As it turns, a ray of light sweeps across the glossy surface. 
Cinematic, 8k, photorealistic, macro lens.
```

**Why the same prompt?** This ensures Veo3 understands what animation to create and maintains consistency with the still image.

### 4.4 Generate the Video

1. Paste the prompt into Veo3
2. Click **"Generate"** or **"Create Video"**
3. Wait for processing (this may take several minutes)
4. The video should show the badge rotating 360 degrees smoothly

### 4.5 Download the Video

1. Once generation is complete, **download the MP4 file**
2. Save it with this exact name format: `{Asset_Name}_Animation.mp4`
   - Example: `Marseille_Animation.mp4`
   - Example: `Liverpool_Animation.mp4`
   - Example: `Lando Norris_Animation.mp4`

---

## Step 5: Save to veo3 Directory

1. **Move or copy** the downloaded video to:
   ```
   scripts/asset-branding/veo3/Marseille_Animation.mp4
   ```

2. **Verify the file is there:**
   ```powershell
   dir scripts\asset-branding\veo3\
   ```

---

## Step 6: Deploy the Video

Run the deployment script to copy the video to the public folder:

```bash
python scripts/asset-branding/copy_videos_to_public.py
```

**What happens:**
- Script finds `Marseille_Animation.mp4` in `veo3/`
- Looks up "Marseille" in the database
- Gets the trading asset ID (e.g., `0a4cbe88-dc22-414c-b453-0bffa6a91dcc`)
- Copies video to `public/avatars/videos/0a4cbe88-dc22-414c-b453-0bffa6a91dcc.mp4`

**Expected output:**
```
🎬 Video Deployment Script
==================================================
✅ Connected to database
📊 Loading asset mappings from database...
✅ Loaded 250 asset mappings

📹 Found 1 video file(s) to process
--------------------------------------------------
✅ Marseille -> 0a4cbe88-dc22-414c-b453-0bffa6a91dcc.mp4

==================================================
📊 Deployment Summary:
   ✅ Copied: 1
   ⚠️  Skipped: 0
   ❌ Errors: 0

📁 Videos deployed to: public/avatars/videos/
🎉 Deployment complete! Videos are ready for frontend use.
```

---

## Complete Example: Marseille

Here's the full workflow for one asset:

### 1. Find SVG
- File: `public/avatars/0a4cbe88-dc22-414c-b453-0bffa6a91dcc.svg`
- Asset: Marseille
- Colors: Blue (#005CB8), White (#FFFFFF)
- Text: "MAR" and "UCL"

### 2. ChatGPT Prompt
```
Bring this badge to life as a premium 3D physical token spinning in a dark studio. 
The outer blue circle is glossy, wet-look automotive paint. 
The central green lightning bolt is translucent glowing emerald glass. 
"MAR" and "UCL" are raised, brushed stainless steel letters. 
The coin rotates slowly and smoothly 360 degrees. 
As it turns, a ray of light sweeps across the glossy surface. 
Cinematic, 8k, photorealistic, macro lens.
```

### 3. Download glossy still image from ChatGPT

### 4. Upload to Veo3 with same prompt

### 5. Download video as `Marseille_Animation.mp4`

### 6. Save to `scripts/asset-branding/veo3/Marseille_Animation.mp4`

### 7. Run deployment script:
```bash
python scripts/asset-branding/copy_videos_to_public.py
```

### 8. Verify:
```powershell
dir public\avatars\videos\0a4cbe88-dc22-414c-b453-0bffa6a91dcc.mp4
```

---

## Tips for Best Results

1. **Color Accuracy**: Match the color descriptions to the actual SVG colors
   - Blue → "blue"
   - Red → "red"
   - Green → "green" or "emerald"

2. **Icon Description**: Describe what's in the center
   - Football badge → "football icon"
   - Lightning bolt → "green lightning bolt"
   - Racing car → "racing car icon"

3. **Consistency**: Always use the same prompt for both ChatGPT and Veo3

4. **File Naming**: Always use `{Asset_Name}_Animation.mp4` format

5. **Quality**: Request "8k" and "photorealistic" in the prompt for best quality

---

## Troubleshooting

### ChatGPT doesn't generate the image
- Make sure you're using GPT-4 (not GPT-3.5)
- Check that you have DALL-E access enabled
- Try rephrasing the prompt slightly

### Veo3 video doesn't rotate
- Make sure you included "rotates slowly and smoothly 360 degrees" in the prompt
- Try regenerating with a clearer prompt

### Video file not found by deployment script
- Check the filename matches exactly: `{Asset_Name}_Animation.mp4`
- Make sure it's in `scripts/asset-branding/veo3/`
- Asset name must match database exactly (case-insensitive)

### "No matching asset found"
- Check the asset name spelling
- Verify the asset exists in the database
- The name must match exactly (e.g., "Marseille" not "Marseille FC")

---

## Next Steps

Once you've generated and deployed your first video:
1. **Phase 2** will add frontend support to display videos in the UI
2. Test with one asset first before generating more
3. Once Phase 2 is complete, videos will automatically show in the frontend!

