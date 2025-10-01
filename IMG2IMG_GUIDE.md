# 🖼️ Img2Img Mode - Quick Guide

**Status:** ✅ **READY TO TEST**
**Added:** 2025-09-30
**Compatible with:** FLUX `unstableEvolution_Fp811GB.safetensors`

---

## What is Img2Img?

Image-to-image (img2img) lets you upload an existing image and modify it with a text prompt, rather than generating from scratch. The AI uses your image as a starting point and transforms it according to your prompt.

---

## How to Use

### 1. Start ComfyUI and the App

```bash
# Terminal 1: Start ComfyUI
./start_comfy.sh

# Terminal 2: Start the app
python app.py
```

### 2. Switch to Generate Mode

Click **🎨 Generate** button in the mode selector.

### 3. Select the Img2Img Workflow

1. Open **🔀 Workflow Selector** accordion
2. Select **"FLUX Img2Img"** from dropdown
3. Workflow info should show: *"Image-to-image generation with FLUX model"*

### 4. Upload Your Image

1. Open **🖼️ Img2Img Settings (Optional)** accordion
2. Click on the image upload area
3. Select your input image (JPG, PNG, etc.)
4. The image will appear in the preview

### 5. Write Your Prompt

Describe how you want to modify the image. Examples:
- `"turn this into a watercolor painting"`
- `"make it look like a cyberpunk cityscape"`
- `"add dramatic sunset lighting"`
- `"convert to anime art style"`

### 6. Adjust Denoise Strength

The **Denoise Strength** slider controls how much the image changes:

| Value | Effect | Use When |
|-------|--------|----------|
| **0.0 - 0.3** | Minimal changes, mostly adds details | You want to keep the image very similar |
| **0.4 - 0.6** | Moderate changes, style variations | Changing art style or lighting |
| **0.7 - 0.9** | Major changes, significant transformation | Complete style transfer or composition changes |
| **1.0** | Complete regeneration (like text2img) | Starting almost from scratch |

**Recommended starting value:** `0.75`

### 7. Generate!

Click **🎨 Generate Image** and wait for the result.

---

## Important Notes

### ⚠️ Workflow Must Support Img2Img

- The workflow **must** have `LoadImage` and `VAEEncode` nodes
- The included `FLUX Img2Img` workflow is pre-configured
- Text2img workflows (like `FLUX Krea Text2Image`) will ignore the input image

### 📐 Image Dimensions

- For img2img, width/height sliders are **ignored**
- The generated image will match your **input image dimensions**
- Make sure your input image isn't too large (recommended: <2048px)

### 🔄 Switching Back to Text2img

1. Simply **don't upload an image**, or
2. Switch to a text2img workflow like "FLUX Krea Text2Image"
3. Leave the Img2Img Settings accordion collapsed

---

## Examples & Tips

### Style Transfer
```
Input: Photo of a cat
Prompt: "oil painting of a majestic cat, renaissance style"
Denoise: 0.75
Result: Cat photo transformed into oil painting
```

### Lighting Changes
```
Input: Daytime photo
Prompt: "dramatic purple sunset lighting, golden hour"
Denoise: 0.6
Result: Same scene with sunset lighting
```

### Detail Enhancement
```
Input: Low-quality photo
Prompt: "ultra detailed, sharp focus, professional photography"
Denoise: 0.4
Result: Enhanced details while keeping composition
```

### Complete Transformation
```
Input: Sketch or rough concept
Prompt: "highly detailed cyberpunk cityscape, neon lights, rainy night"
Denoise: 0.9
Result: Fully realized scene based on sketch
```

---

## Troubleshooting

### "Failed to upload input image"
- Check that ComfyUI is running
- Verify the image file isn't corrupted
- Try a different image format (PNG/JPG)

### Image doesn't change
- Increase denoise strength (try 0.75 or higher)
- Make your prompt more specific and directive
- Check that you selected the Img2Img workflow

### Out of VRAM error
- Use smaller input images
- Reduce number of steps
- Switch to IDLE mode and back to clear VRAM

### Workflow error
- Make sure you selected "FLUX Img2Img" workflow
- The text2img workflow doesn't have LoadImage nodes
- Check ComfyUI terminal for specific errors

---

## Next Steps

Once img2img is working, you can:
1. Combine with **Vision Chat** to iteratively refine images
2. Use **Seed variations** to explore different results
3. Create your own img2img workflows in ComfyUI
4. Try **inpainting** (Phase 3 feature - coming soon!)

---

## Technical Details

### What Happens Behind the Scenes

1. **Upload:** Image is uploaded to ComfyUI via `/upload/image` endpoint
2. **Encode:** `LoadImage` + `VAEEncode` nodes convert image to latent space
3. **Denoise:** `KSampler` processes latents with your denoise strength
4. **Decode:** `VAEDecode` converts back to final image
5. **Save:** Result returned to app and saved to `outputs/`

### Workflow Structure

The img2img workflow uses:
- **LoadImage** - Loads your input image
- **VAEEncode** - Converts image to latent representation
- **KSampler** - Applies denoising with your prompt
- **VAEDecode** - Converts latents back to image
- All other nodes same as text2img (CLIP, UNET, etc.)

### Denoise Math

`denoise=1.0` means 100% noise is added (complete regeneration)
`denoise=0.0` means 0% noise (no changes, original image)

Most useful range: `0.5 - 0.9` for style transfer and modifications.

---

**Happy img2img generation!** 🎨✨
