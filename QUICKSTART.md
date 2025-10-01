# 🚀 AI Image Chat - Quick Reference

## 🏃 Quick Start

### 1. Start ComfyUI (Terminal 1)
```bash
./start_comfy.sh
```
Wait for: "To see the GUI go to: http://0.0.0.0:8188"

### 2. Start AI Image Chat (Terminal 2)
```bash
./start_app.sh
```
Or: `python app.py`

### 3. Open in Browser
- Laptop: http://localhost:7860
- Desktop: http://192.168.1.175:7860

---

## 🎯 Typical Workflow

```
1. Click [💬 Chat] → Chat mode activated
2. Chat: "Create a cinematic portrait..."
3. AI refines prompt
4. Click [🔵 Idle] → Unload chat
5. Start ComfyUI if not running
6. Click [🎨 Generate] → Generation mode
7. Click [🎨 Generate Image] → Wait ~20 seconds
8. Done! Iterate or switch back to chat
```

---

## ⌨️ Common Commands

### Check Services
```bash
# Ollama
curl http://localhost:11434/api/tags

# ComfyUI
curl http://localhost:8188/system_stats

# VRAM usage
nvidia-smi
```

### Start/Stop Services
```bash
# Start Ollama (if not running)
ollama serve

# Stop ComfyUI
# Press Ctrl+C in terminal

# Kill if stuck
pkill -f "python main.py"
pkill -f ollama
```

---

## 🔧 Quick Settings

### In `config.py`:

**Faster generation:**
```python
DEFAULT_STEPS = 15
DEFAULT_WIDTH = 768
DEFAULT_HEIGHT = 768
```

**Better quality:**
```python
DEFAULT_STEPS = 30
DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 1024
```

**Different chat model:**
```python
OLLAMA_CHAT_MODEL = "mistral:7b"  # Faster
```

---

## 💡 Quick Tips

### Prompting:
- ✅ "Photorealistic portrait, golden hour lighting, shallow depth of field"
- ❌ "Make a picture of someone"

### VRAM Management:
- Always **[🔵 Idle]** when done
- Lower resolution if OOM
- Don't run other GPU apps

### Speed vs Quality:
- **Fast:** 768x768, 15 steps (~8 seconds)
- **Balanced:** 1024x1024, 20 steps (~15 seconds)
- **Best:** 1024x1024, 30 steps (~25 seconds)

---

## 🐛 Common Issues

### "Cannot connect to Ollama"
```bash
ollama serve  # Start Ollama
```

### "ComfyUI Not Running"
```bash
./start_comfy.sh  # Start ComfyUI
```

### "Out of VRAM"
1. Click [🔵 Idle]
2. Lower resolution
3. Close other apps

### "Timeout waiting for image"
- Check ComfyUI terminal for errors
- Check ComfyUI UI: http://localhost:8188
- Try smaller resolution

---

## 📊 VRAM Cheatsheet

| Mode | Usage | What's Loaded |
|------|-------|---------------|
| **Idle** | ~0 GB | Nothing |
| **Chat** | ~5 GB | llama3.1 |
| **Generate** | ~12 GB | ComfyUI + FLUX |

| Resolution | VRAM | Speed |
|------------|------|-------|
| 512x512 | ~8 GB | Fast |
| 768x768 | ~10 GB | Medium |
| 1024x1024 | ~12 GB | Balanced |
| 1536x1536 | ~14 GB | Slow |

---

## 🎨 Example Prompts

**Photorealistic Portrait:**
```
Photorealistic portrait of a woman, golden hour lighting, 
shallow depth of field, bokeh background, cinematic composition, 
highly detailed skin texture, professional photography
```

**Landscape:**
```
Dramatic mountain landscape at sunset, purple and orange sky, 
misty valleys, volumetric lighting, wide angle shot, 
highly detailed, 8K quality
```

**Cyberpunk:**
```
Cyberpunk cityscape, neon lights reflecting on rain-slicked streets,
futuristic architecture, dramatic perspective, moody atmosphere,
blade runner aesthetic, high contrast lighting
```

**Fantasy:**
```
Epic fantasy castle on a floating island, dramatic clouds, 
magical atmosphere, ethereal lighting, detailed architecture,
concept art style, vibrant colors, cinematic composition
```

---

## 🆘 Emergency Reset

If everything breaks:

```bash
# Kill all processes
pkill -f ollama
pkill -f "python main.py"
pkill -f "python app.py"

# Clear CUDA
python -c "import torch; torch.cuda.empty_cache()"

# Restart fresh
./start_comfy.sh  # Terminal 1
./start_app.sh     # Terminal 2
```

---

## 📱 Bookmarks

Save these in your browser:

- **AI Image Chat:** http://192.168.1.175:7860
- **ComfyUI:** http://192.168.1.175:8188

---

**Need help? Check README.md for detailed troubleshooting!**
