# 🎨 AI Image Chat - Setup & Usage Guide

**Phase 1: Chat-based prompt refinement + ComfyUI image generation**

---

## 📋 System Info

- **Laptop:** nobara-laptop (192.168.1.175)
- **GPU:** RTX 4090M (16GB VRAM)
- **User:** ant
- **OS:** Nobara Linux

**Installed:**
- ✅ ComfyUI: `/home/ant/AI/ComfyUI`
- ✅ Ollama with models: llama3.1:latest (4.9GB), mistral:7b (4.4GB), gpt-oss:latest (13GB), mistral-small3.2:latest (15GB)
- ✅ FLUX Finetune: `unstableEvolution_Fp811GB.safetensors` (Krea-based)

---

## 🚀 Quick Start (5 Steps)

### 1. Install Dependencies

```bash
cd ~/ai-image-chat  # or wherever you put these files
pip install -r requirements.txt
```

### 2. Make Start Script Executable

```bash
chmod +x start_comfy.sh
```

### 3. Copy Workflow File

Make sure `flux1_krea_dev.json` is in the same directory as `app.py`

### 4. Verify Configuration

Check `config.py` - everything should be pre-configured for your setup:
- ComfyUI path: `/home/ant/AI/ComfyUI`
- Finetune: `unstableEvolution_Fp811GB.safetensors`
- Chat model: `llama3.1:latest`

### 5. Run the App

```bash
python app.py
```

**Access from:**
- Laptop: http://localhost:7860
- Desktop: http://192.168.1.175:7860

---

## ⌨️ Keyboard Shortcuts (TEMPORARILY DISABLED)

⚠️ **Note:** Keyboard shortcuts are currently disabled due to a conflict with button clicks. See [Troubleshooting](#-troubleshooting) for details.

**When re-enabled**, the app will include these keyboard shortcuts:

### Mode Switching
- `Alt+I` - Switch to Idle mode
- `Alt+C` - Switch to Text Chat mode
- `Alt+V` - Switch to Vision Chat mode
- `Alt+G` - Switch to Generate mode

### Actions
- `Ctrl+Enter` - Send chat message (when focused on message box)
- `Ctrl+G` - Generate image
- `Ctrl+K` - Copy prompt to clipboard
- `Ctrl+L` - Use last seed
- `Ctrl+Shift+C` - Clear chat

### Generation Presets
- `Ctrl+1` - Fast Draft preset
- `Ctrl+2` - Balanced preset
- `Ctrl+3` - High Quality preset
- `Ctrl+4` - Ultra Detail preset

### Help
- `?` or `Shift+/` - Toggle shortcuts help panel

**Implementation Status:** Code exists in app.py but is commented out. To re-enable properly, the JavaScript needs to be refactored to not interfere with button clicks. See `TROUBLESHOOTING.md` Issue #1.

---

## 📊 New in Phase 2.5: Power Features

### Live VRAM Monitoring
The app now shows real-time GPU VRAM usage with status indicators:
- 🔵 **Idle** - Nothing loaded
- 🟡 **Loading** - Switching modes
- 🟢 **Active** - Model loaded and ready

### Session Statistics
Track your generation performance with automatic statistics:
- Total images generated
- Average generation time
- Fastest and slowest generations
- Total compute time
- Session duration

Access stats via the **📊 Session Statistics** accordion below the generated image.

### Smart Mode Suggestions
The app intelligently suggests when to switch modes:
- After crafting a prompt → "Switch to Generate?"
- After generating an image → "Switch to Vision Chat?"
- After vision refinement → "Switch to Generate?"

Toggle smart suggestions on/off in the mode selector panel.

### Enhanced Seed Management
Powerful seed control for exploring variations:
- **Variation Buttons** - Fine-tune seeds with +/- 1, 10, or 100
- **Lock Seed** - Keep using the same seed for consistent iterations
- **Seed History** - Dropdown with your last 10 seeds for quick access
- **Random Seed** - Generate a random seed instantly
- Seeds are locked visually with a 🔒 indicator in the status

---

## 📖 How to Use

### The 3-Mode System

The app has **3 modes** to manage VRAM properly:

#### 🔵 **IDLE Mode**
- Nothing loaded, VRAM free
- Starting state
- Switch here when you're done

#### 💬 **CHAT Mode**
- llama3.1 loaded on GPU (~5GB VRAM)
- Fast AI chat for prompt refinement
- Iterative prompt development

#### 🎨 **GENERATE Mode**
- ComfyUI + FLUX finetune on GPU (~12GB VRAM)
- Image generation (text2img or img2img)
- Fast iterations on generated images
- Multiple workflow support

---

## 🖼️ New in Phase 3: Img2Img Mode

Transform existing images with AI! Upload an image and modify it with text prompts.

**Quick Start:**
1. Switch to Generate mode
2. Select "FLUX Img2Img" workflow
3. Upload an image in the Img2Img Settings accordion
4. Write a transformation prompt (e.g., "oil painting style")
5. Set denoise strength (0.75 recommended)
6. Generate!

**Denoise Strength Guide:**
- **0.3** = Minimal changes (add details only)
- **0.75** = Moderate transformation (recommended)
- **0.9** = Major changes (complete style transfer)

📚 **See [IMG2IMG_GUIDE.md](./IMG2IMG_GUIDE.md) for detailed instructions and examples**

---

## 🎯 Complete Workflow

### Step 1: Start in IDLE
```
App starts → Everything unloaded → Choose mode
```

### Step 2: Switch to CHAT Mode

1. Click **💬 Chat** button
2. Wait ~5 seconds for llama3.1 to load
3. Status shows: "💬 CHAT MODE - Active"

### Step 3: Refine Your Prompt

**Example conversation:**

```
You: Create a photorealistic portrait of a woman in a cyberpunk setting

AI: I'll help you create a detailed prompt for that. Here's a refined version:

"Photorealistic portrait of a young woman with neon-lit cyberpunk aesthetic, 
sharp focus on face, dramatic purple and blue neon lighting from nearby 
signs, rain-slicked urban background with bokeh effect, shallow depth of 
field, cinematic composition, highly detailed skin texture, futuristic 
fashion with tech implants, moody atmosphere, 4K quality"

You: Make the lighting more warm and add golden hour tones

AI: Here's the updated prompt with warmer tones:

"Photorealistic portrait of a young woman in cyberpunk setting, 
golden hour lighting with warm amber and orange tones mixing with 
cool neon blues, dramatic side lighting, rain-slicked urban background..."
```

The prompt appears in the **"Current Prompt"** textbox on the right.

### Step 4: Switch to GENERATE Mode

1. Click **🔵 Idle** (unloads Ollama)
2. Wait 2-3 seconds
3. **Start ComfyUI** in a separate terminal:
   ```bash
   ./start_comfy.sh
   ```
   Or manually:
   ```bash
   cd /home/ant/AI/ComfyUI
   conda activate comfy-env
   python main.py --listen --cuda-malloc --force-channels-last --use-sage-attention --dont-upcast-attention --fast
   ```

4. Wait for ComfyUI to fully load (~30 seconds)
5. Click **🎨 Generate** button in the app
6. Status should show: "🎨 GENERATION MODE - Active"

### Step 5: Generate Image

1. Review/edit prompt in the textbox
2. Adjust settings if needed (steps, resolution, seed)
3. Click **🎨 Generate Image**
4. Wait 10-30 seconds (depending on resolution and steps)
5. Image appears below!

### Step 6: Iterate

**Option A: Iterate in GENERATE Mode**
- Edit prompt directly
- Change generation settings
- Generate again (fast, ComfyUI stays loaded)

**Option B: Iterate via CHAT**
1. Click **🔵 Idle**
2. Click **💬 Chat**
3. Continue conversation: "Make the sky more dramatic"
4. Get refined prompt
5. Switch back to GENERATE mode
6. Generate again

---

## ⚙️ Generation Settings

### Recommended for Krea-based finetune:

| Setting | Default | Range | Notes |
|---------|---------|-------|-------|
| **Steps** | 20 | 4-50 | 20 is good quality, 30+ for best |
| **Width** | 1024 | 512-2048 | Must be multiple of 64 |
| **Height** | 1024 | 512-2048 | Must be multiple of 64 |
| **CFG** | 1.0 | N/A | Fixed in workflow (Krea optimal) |
| **Seed** | Random | Any number | Set for reproducibility |

### VRAM Usage by Resolution:

- 512x512: ~8GB
- 768x768: ~10GB
- 1024x1024: ~12GB
- 1536x1536: ~14GB (tight fit!)
- 2048x2048: May OOM!

---

## 💡 Tips & Best Practices

### Chat Tips:
- Start with simple descriptions
- Let the AI expand with details
- Be specific about what you want: style, mood, lighting, composition
- Ask for specific changes: "make it more dramatic", "add sunset lighting"

### Prompt Engineering:
- Include technical terms: "shallow depth of field", "bokeh", "cinematic"
- Specify quality: "highly detailed", "photorealistic", "4K quality"
- Describe lighting: "golden hour", "dramatic side lighting", "soft diffused light"
- Add style references: "in the style of...", "like a movie poster"

### Generation Strategy:
- **Fast iteration:** Stay in GENERATE mode, tweak prompt directly
- **Major changes:** Switch to CHAT mode for AI assistance
- **Reproduce results:** Copy the seed from a good generation

### VRAM Management:
- Always switch to IDLE when done
- Don't run other GPU apps during generation
- Lower resolution if you get OOM errors
- ComfyUI can stay running between app sessions

---

## 🐛 Troubleshooting

### ⚠️ Buttons Not Working (MOST COMMON ISSUE)

**Problem:** Clicking buttons does nothing, app stays in Idle mode

**Cause:** Keyboard shortcuts JavaScript interferes with button clicks

**Fix:** Edit `app.py` line ~381 and comment out the `js=` parameter:
```python
with gr.Blocks(
    theme=gr.themes.Soft(primary_hue="blue"),
    title="AI Image Chat",
    # js=keyboard_js,  # DISABLE THIS LINE
```

Then restart the app. Buttons will work immediately.

**See:** `BUTTON_DEBUG_CHECKLIST.md` for quick fix guide
**Details:** `TROUBLESHOOTING.md` Issue #1

---

### "Cannot connect to Ollama"

**Check if Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

**Start Ollama if needed:**
```bash
ollama serve
```

### "ComfyUI Not Running"

**Manually start ComfyUI:**
```bash
./start_comfy.sh
```

**Check if it's accessible:**
```bash
curl http://localhost:8188/system_stats
```

**Or open in browser:** http://localhost:8188

### "Out of VRAM / CUDA out of memory"

**Solutions:**
1. Switch to IDLE mode and back
2. Lower resolution (try 768x768)
3. Reduce steps (try 15)
4. Close other GPU applications
5. Restart both ComfyUI and the app

**Check VRAM usage:**
```bash
nvidia-smi
```

### "Timeout waiting for image"

**Possible causes:**
- ComfyUI is still processing (check ComfyUI UI)
- Workflow error (check ComfyUI terminal for errors)
- Image too large (reduce resolution)

**Solutions:**
- Check ComfyUI at http://localhost:8188
- Look for errors in ComfyUI terminal
- Reduce resolution and try again

### "Failed to queue prompt"

**Check:**
1. ComfyUI is running
2. Workflow file `flux1_krea_dev.json` exists
3. Finetune file exists: `ls ~/AI/ComfyUI/models/diffusion_models/unstableEvolution_Fp811GB.safetensors`

### "Model not found in ComfyUI"

Edit `config.py` and check `FINETUNE_NAME` matches your actual file:
```python
FINETUNE_NAME = "unstableEvolution_Fp811GB.safetensors"
```

### Chat is slow

**Solutions:**
- Make sure you're in CHAT mode (llama3.1 on GPU)
- Try mistral:7b instead (slightly faster)
- Avoid using mistral-small3.2:latest (15GB, may cause issues)

---

## 📊 System Monitoring

### Watch VRAM usage:
```bash
watch -n 1 nvidia-smi
```

### Check what's using GPU:
```bash
fuser -v /dev/nvidia0
```

### Kill stuck processes:
```bash
pkill -f "ollama"
pkill -f "python main.py"  # ComfyUI
```

---

## 🔧 Configuration

All settings are in `config.py`:

### Change chat model:
```python
OLLAMA_CHAT_MODEL = "mistral:7b"  # Faster, slightly less capable
```

### Change default generation settings:
```python
DEFAULT_WIDTH = 768
DEFAULT_HEIGHT = 768
DEFAULT_STEPS = 15  # Faster
```

### Use different finetune:
```python
FINETUNE_NAME = "your_other_model.safetensors"
```

---

## 🚧 Phase 2 & 3 Plans

### Phase 2: Vision Model Integration
- Add `llava:13b` or `llava:7b`
- See generated images and iterate intelligently
- "Make the sky more dramatic" while looking at the image

### Phase 3: Advanced ComfyUI Integration
- Custom workflow support
- ControlNet integration
- Img2img refinement
- Batch generation

**Want these features? Let me know!**

---

## 📝 File Structure

```
ai-image-chat/
├── app.py                    # Main application
├── config.py                 # Configuration
├── comfyui_api.py           # ComfyUI integration
├── requirements.txt          # Python dependencies
├── start_comfy.sh           # ComfyUI launcher script
├── flux1_krea_dev.json      # Workflow file
└── README.md                 # This file
```

---

## 🎯 Access URLs

### From Laptop:
- AI Image Chat: http://localhost:7860
- ComfyUI: http://localhost:8188
- Ollama API: http://localhost:11434

### From Desktop:
- AI Image Chat: http://192.168.1.175:7860
- ComfyUI: http://192.168.1.175:8188

---

## 🆘 Getting Help

If you encounter issues:

1. **Check the terminal output** for error messages
2. **Check ComfyUI terminal** for generation errors
3. **Run nvidia-smi** to check VRAM usage
4. **Verify all services are running:**
   - Ollama: `curl http://localhost:11434/api/tags`
   - ComfyUI: `curl http://localhost:8188/system_stats`

5. **Share error messages** with context:
   - What mode were you in?
   - What were you trying to do?
   - Full error message from terminal

---

## 🎉 You're Ready!

Start the app and begin creating!

```bash
python app.py
```

Then open: http://localhost:7860 (laptop) or http://192.168.1.175:7860 (desktop)

**Enjoy creating amazing images!** 🚀✨
