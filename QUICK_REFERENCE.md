# ⚡ Quick Reference Card

Essential commands and info for AI Image Chat development.

---

## 🚀 Starting the App

```bash
# Start ComfyUI (Terminal 1)
./start_comfy.sh

# Start the app (Terminal 2)
python app.py

# Or both in one script
./start_app.sh
```

**Access URLs:**
- Local: http://localhost:7860
- Network: http://192.168.1.175:7860

---

## 🔧 Development Commands

```bash
# Check code quality
./check_code.sh

# Test core features
python test_new_features.py

# Test button functionality
python test_buttons.py

# Check Python syntax
python -m py_compile app.py

# Install dependencies
pip install -r requirements.txt
```

---

## 🐛 Debug Commands

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Check ComfyUI status
curl http://localhost:8188/system_stats

# Monitor GPU
nvidia-smi
watch -n 1 nvidia-smi

# View logs (when logging is implemented)
tail -f ai_image_chat.log
```

---

## 📁 File Structure

```
ai-image-chat/
├── app.py                      # Main Gradio application
├── config.py                   # Configuration settings
├── comfyui_api.py             # ComfyUI API bridge
├── requirements.txt           # Python dependencies
├── workflows/
│   ├── text2img/
│   │   ├── flux_krea_text2img.json        # Default text-to-image workflow
│   │   └── flux_krea_text2img_meta.json   # Metadata for workflow manager
│   └── img2img/
│       ├── flux_img2img.json              # Default image-to-image workflow
│       └── flux_img2img_meta.json         # Metadata for workflow manager
├── outputs/                   # Generated images (auto-created)
├── prompt_history.json        # Saved prompts
├── README.md                  # User documentation
├── CLAUDE.md                  # Developer guide
├── TROUBLESHOOTING.md         # Issue resolution
├── BEST_PRACTICES.md          # Code quality guide
├── ROADMAP.md                 # Feature roadmap
└── QUICK_REFERENCE.md         # This file
```

> **Note:** The repository ships with the workflow manager structure under `workflows/`. The legacy single-file workflow `flux1_krea_dev.json` is only needed if you're migrating an older manual setup and must copy it in yourself.

---

## ⌨️ Keyboard Shortcuts

*(When enabled in app)*

**Mode Switching:**
- `Alt+I` - Idle mode
- `Alt+C` - Text Chat mode
- `Alt+V` - Vision Chat mode
- `Alt+G` - Generate mode

**Actions:**
- `Ctrl+Enter` - Send chat message
- `Ctrl+G` - Generate image
- `Ctrl+K` - Copy prompt
- `Ctrl+L` - Use last seed
- `Ctrl+Shift+C` - Clear chat
- `?` or `Shift+/` - Show shortcuts

**Presets:**
- `Ctrl+1` - Fast Draft
- `Ctrl+2` - Balanced
- `Ctrl+3` - High Quality
- `Ctrl+4` - Ultra Detail

---

## 🎯 Common Tasks

### Change Chat Model
```python
# Edit config.py
OLLAMA_CHAT_MODEL = "mistral:7b"
```

### Change Generation Defaults
```python
# Edit config.py
DEFAULT_WIDTH = 768
DEFAULT_HEIGHT = 768
DEFAULT_STEPS = 15
```

### Use Different Finetune
```python
# Edit config.py
FINETUNE_NAME = "your_model.safetensors"
```

### Export Prompt History
1. Open app → Generation tab
2. Expand "📚 Prompt History"
3. Click "💾 Export History"
4. File saved as `prompt_export_YYYYMMDD_HHMMSS.json`

---

## 🏗️ Architecture Quick Reference

### Core Classes

| Class | Purpose | Location |
|-------|---------|----------|
| `ModeManager` | Mode switching & VRAM management | app.py:322-641 |
| `VRAMMonitor` | GPU VRAM tracking | app.py:25-70 |
| `SessionStats` | Generation statistics | app.py:76-128 |
| `VRAMEstimator` | VRAM usage estimation | app.py:134-221 |
| `SeedManager` | Seed history & locking | app.py:227-263 |
| `PromptHistory` | Prompt storage & search | app.py:269-407 |
| `ImageGallery` | Session image gallery | app.py:403-470 |
| `SmartSwitchManager` | Auto-switch suggestions | app.py:413-456 |
| `ComfyUIBridge` | ComfyUI API communication | comfyui_api.py:14-264 |

### Key Functions

| Function | Purpose | Returns |
|----------|---------|---------|
| `generate_image()` | Generate image via ComfyUI | (image, status, seed, stats) |
| `chat_with_ollama()` | Text chat with Ollama | response_text |
| `vision_chat_with_ollama()` | Vision chat with image | response_text |
| `check_vram_warnings()` | Get VRAM warnings | (text, visible) |

---

## 🔢 Configuration Reference

### VRAM Estimates
- Idle: 0 GB
- Chat: ~5 GB (llama3.1)
- Vision: ~7 GB (qwen2.5vl)
- Generate: ~12 GB (ComfyUI + FLUX)

### Generation Presets
- Fast Draft: 768x768 @ 15 steps (~4.3 GB)
- Balanced: 1024x1024 @ 20 steps (~8 GB)
- High Quality: 1024x1024 @ 30 steps (~9 GB)
- Ultra Detail: 1536x1536 @ 35 steps (~20 GB) ⚠️

### Timeouts
- Ollama warm-up: 30s
- ComfyUI generation: 300s (5 min)
- VRAM monitor cache: 2s

---

## 🚨 Quick Troubleshooting

| Issue | Quick Fix |
|-------|-----------|
| Buttons not working | Restart app, check terminal for errors |
| Can't switch modes | Check Ollama/ComfyUI status |
| Out of VRAM | Lower resolution or switch to Idle first |
| Generation timeout | Check ComfyUI terminal, verify workflow exists |
| Import errors | Run `pip install -r requirements.txt` |

**Full guide:** See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

---

## 📊 Phase Status

### ✅ Completed
- Phase 1: Core functionality
- Phase 2: Vision Chat + QOL features
- Phase 2.5 (Partial):
  - Keyboard shortcuts
  - Model status indicators
  - Generation statistics
  - Smart mode switching
  - Enhanced seed management
  - Generation warnings
  - Prompt history

### 🚧 Remaining Phase 2.5
- Batch generation queue
- Enhanced gallery features (filter, sort, favorite)

### 🔮 Phase 3 (Planned)
- Multiple workflow support
- ControlNet integration
- Img2img & inpainting
- LoRA selector
- Advanced comparison tools

**Full roadmap:** See [ROADMAP.md](./ROADMAP.md)

---

## 📚 Documentation Index

| Document | Purpose |
|----------|---------|
| `README.md` | User guide & setup instructions |
| `QUICKSTART.md` | Fast setup for first-time users |
| `DEPLOYMENT.md` | Production deployment guide |
| `CLAUDE.md` | Developer guide for AI assistants |
| `TROUBLESHOOTING.md` | Issue tracking & solutions |
| `BEST_PRACTICES.md` | Code quality recommendations |
| `ROADMAP.md` | Feature planning & timeline |
| `QUICK_REFERENCE.md` | This cheat sheet |

---

## 💡 Pro Tips

1. **Keep ComfyUI running** - Faster generation times
2. **Use seed locking** - Iterate on same composition
3. **Start with Fast Draft** - Test prompts quickly
4. **Check VRAM warnings** - Avoid OOM crashes
5. **Export prompt history** - Back up your best prompts
6. **Use Vision Chat** - Iterative refinement works great
7. **Monitor terminal output** - Catch issues early
8. **Run ./check_code.sh** - Before committing changes

---

## 🆘 Getting Help

1. Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for known issues
2. Review terminal output for error messages
3. Verify services are running (Ollama + ComfyUI)
4. Check GPU status with `nvidia-smi`
5. Review [CLAUDE.md](./CLAUDE.md) for architecture details

---

**Last Updated:** 2025-09-30
**Version:** Phase 2.5 (Partial)
