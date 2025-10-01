# 📦 AI Image Chat - Deployment Checklist

Follow these steps **in order** to set up everything correctly.

---

## ✅ Pre-Flight Checklist

Before you start, verify these are already installed:

- [ ] **Ollama** is installed and has models
  ```bash
  ollama list
  # Should show: llama3.1:latest, mistral:7b, etc.
  ```

- [ ] **ComfyUI** is installed at `/home/ant/AI/ComfyUI`
  ```bash
  ls /home/ant/AI/ComfyUI/main.py
  # Should exist
  ```

- [ ] **Your FLUX finetune** exists
  ```bash
  ls /home/ant/AI/ComfyUI/models/diffusion_models/unstableEvolution_Fp811GB.safetensors
  # Should exist (11GB file)
  ```

- [ ] **ComfyUI support files** exist
  ```bash
  ls /home/ant/AI/ComfyUI/models/text_encoders/clip_l.safetensors
  ls /home/ant/AI/ComfyUI/models/text_encoders/t5xxl_fp16.safetensors
  ls /home/ant/AI/ComfyUI/models/vae/ae.safetensors
  # All should exist
  ```

- [ ] **Python 3.10+** is installed
  ```bash
  python --version
  # Should show 3.10 or higher
  ```

---

## 📥 Step 1: Get the Files

Copy all these files to your project directory (e.g., `~/ai-image-chat/`):

Required files:
- [ ] `app.py` - Main application
- [ ] `config.py` - Configuration
- [ ] `comfyui_api.py` - ComfyUI integration
- [ ] `requirements.txt` - Dependencies
- [ ] `workflows/text2img/flux_krea_text2img.json` - Default text-to-image workflow
- [ ] `workflows/text2img/flux_krea_text2img_meta.json` - Workflow metadata
- [ ] `workflows/img2img/flux_img2img.json` - Default image-to-image workflow
- [ ] `workflows/img2img/flux_img2img_meta.json` - Workflow metadata
- [ ] `start_comfy.sh` - ComfyUI launcher
- [ ] `start_app.sh` - App launcher

> If you're migrating from an older manual setup that only used `flux1_krea_dev.json`, copy that file into `workflows/text2img/` and rename it to `flux_krea_text2img.json` so the workflow manager can pick it up.

Documentation:
- [ ] `README.md` - Full guide
- [ ] `QUICKSTART.md` - Quick reference
- [ ] `DEPLOYMENT.md` - This file

---

## 🔧 Step 2: Install Dependencies

```bash
cd ~/ai-image-chat  # or wherever you put the files

# Install Python packages
pip install -r requirements.txt

# If PyTorch not installed, install with CUDA support
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

**Verify installation:**
```bash
python -c "import gradio; print('Gradio:', gradio.__version__)"
python -c "import torch; print('PyTorch:', torch.__version__, 'CUDA:', torch.cuda.is_available())"
```

Should show:
- Gradio: 4.x.x or higher
- PyTorch: 2.x.x, CUDA: True

---

## ⚙️ Step 3: Verify Configuration

Check `config.py` has the correct paths:

```bash
cat config.py | grep -E "COMFYUI_PATH|FINETUNE_NAME"
```

Should show:
```
COMFYUI_PATH = "/home/ant/AI/ComfyUI"
FINETUNE_NAME = "unstableEvolution_Fp811GB.safetensors"
```

If different, edit `config.py` with your actual paths.

---

## 🧪 Step 4: Test Services

### Test Ollama:
```bash
ollama list
curl http://localhost:11434/api/tags
```

If not running:
```bash
ollama serve &
```

### Test ComfyUI (Terminal 1):
```bash
./start_comfy.sh
```

Wait for: "To see the GUI go to: http://0.0.0.0:8188"

Then test:
```bash
# In another terminal
curl http://localhost:8188/system_stats
```

Should return JSON with system info.

**Keep ComfyUI running for now.**

---

## 🚀 Step 5: Launch AI Image Chat (Terminal 2)

```bash
./start_app.sh
```

Or directly:
```bash
python app.py
```

Should see:
```
============================================================
AI IMAGE CHAT - Phase 1
============================================================
User: ant
Hostname: nobara-laptop
ComfyUI: http://localhost:8188
Ollama: http://localhost:11434/api
Chat Model: llama3.1:latest
FLUX Finetune: unstableEvolution_Fp811GB.safetensors
============================================================

Access URLs:
• Laptop: http://localhost:7860
• Desktop: http://192.168.1.175:7860
```

---

## 🌐 Step 6: Test in Browser

### From Laptop:
Open: http://localhost:7860

### From Desktop:
Open: http://192.168.1.175:7860

You should see the AI Image Chat interface with:
- Mode selector buttons at the top
- Status showing "IDLE MODE"
- Chat interface on the left
- Generation panel on the right

---

## 🎯 Step 7: Test the Workflow

### Test Chat Mode:

1. Click **[💬 Chat]** button
2. Wait for status to show "💬 CHAT MODE - Active"
3. Type in chat: "Create a photorealistic portrait of a mountain"
4. Click **Send**
5. AI should respond with a refined prompt

**Success indicator:** Status shows ~5GB VRAM usage

### Test Generation Mode:

1. Click **[🔵 Idle]** (if in Chat Mode)
2. Wait 2-3 seconds
3. Make sure ComfyUI is running (Terminal 1)
4. Click **[🎨 Generate]** button
5. Status should show "🎨 GENERATION MODE - Active"

**Success indicator:** Status shows ~12GB VRAM usage

### Test Image Generation:

1. Make sure you're in Generation Mode
2. Enter a prompt in the "Current Prompt" textbox:
   ```
   Photorealistic portrait of a woman, golden hour lighting, 
   shallow depth of field, professional photography
   ```
3. Click **[🎨 Generate Image]**
4. Wait 15-30 seconds
5. Image should appear below!

**Success indicator:** Image appears, status shows "✅ Generated successfully!"

---

## ✅ Verification Checklist

After completing all steps, verify:

- [ ] App starts without errors
- [ ] Can access from browser
- [ ] Chat mode works (can send messages)
- [ ] Generation mode connects to ComfyUI
- [ ] Can generate images
- [ ] Can switch between modes
- [ ] VRAM is properly managed

---

## 🎉 You're Done!

If all checks pass, you're ready to use AI Image Chat!

**Next Steps:**
1. Read `QUICKSTART.md` for common workflows
2. Check `README.md` for detailed usage
3. Experiment with different prompts
4. Have fun creating images!

---

## 🐛 Common Setup Issues

### "ModuleNotFoundError: No module named 'gradio'"
```bash
pip install -r requirements.txt
```

### "Cannot connect to Ollama"
```bash
ollama serve &
```

### "ComfyUI not running"
```bash
./start_comfy.sh
```

### "CUDA not available"
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### Scripts not executable
```bash
chmod +x start_comfy.sh start_app.sh
```

### Wrong file paths in config
Edit `config.py` and update:
- `COMFYUI_PATH`
- `FINETUNE_NAME`

---

## 🆘 Need Help?

If stuck:

1. **Check terminal output** for errors
2. **Verify all files** are in the same directory
3. **Test services individually** (Ollama, ComfyUI)
4. **Check file paths** in `config.py`
5. **Read README.md** for detailed troubleshooting

---

## 📝 Quick Commands Reference

```bash
# Start everything
./start_comfy.sh    # Terminal 1
./start_app.sh      # Terminal 2

# Check services
ollama list
curl http://localhost:11434/api/tags
curl http://localhost:8188/system_stats
nvidia-smi

# Stop everything
# Press Ctrl+C in both terminals
```

---

**Ready to create amazing images! 🎨✨**
