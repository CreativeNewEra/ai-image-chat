# 🎨 AI Image Chat

AI-powered image generation application combining ComfyUI + FLUX for image generation, Ollama for chat-based prompt refinement, and a Gradio web interface.

[![Phase 3](https://img.shields.io/badge/Phase-3%20Complete-brightgreen)]()
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)]()
[![License](https://img.shields.io/badge/License-MIT-yellow)]()
[![Tests](https://github.com/CreativeNewEra/ai-image-chat/workflows/Tests%20and%20Linting/badge.svg)](https://github.com/CreativeNewEra/ai-image-chat/actions/workflows/test.yml)
[![Documentation](https://github.com/CreativeNewEra/ai-image-chat/workflows/Documentation%20Check/badge.svg)](https://github.com/CreativeNewEra/ai-image-chat/actions/workflows/docs.yml)

## ✨ Features

- **💬 Text Chat** - AI-powered prompt refinement with Ollama
- **👁️ Vision Chat** - Image-aware refinement with qwen2.5vl
- **🎨 Text-to-Image** - Generate images from text with FLUX workflows
- **🖼️ Image-to-Image** - Transform existing images with AI
- **📦 Batch Generation** - Queue multiple generation jobs
- **🗂️ Enhanced Gallery** - Filter, sort, favorite, and manage images
- **🧠 Smart Mode Switching** - Intelligent VRAM management
- **📊 Real-time Monitoring** - Live VRAM usage and statistics
- **🎯 Multiple Workflows** - Support for various ComfyUI workflows

## 🚀 Quick Start

### Prerequisites

- **GPU:** NVIDIA GPU with 16GB+ VRAM (tested on RTX 4090M)
- **OS:** Linux (tested on Nobara Linux)
- **Python:** 3.10+
- **ComfyUI:** Installed and configured
- **Ollama:** Running with desired models

### Installation

```bash
# Clone repository
git clone https://github.com/CreativeNewEra/ai-image-chat.git
cd ai-image-chat

# Install dependencies
pip install -r requirements.txt

# Configure paths in config.py
# Edit COMFYUI_PATH and FINETUNE_NAME as needed

# Start ComfyUI (in separate terminal)
./start_comfy.sh

# Start the application
python app.py
```

**Access the app:**
- Local: http://localhost:7860
- Network: http://YOUR_IP:7860

## 📖 Documentation

- **[QUICKSTART.md](./QUICKSTART.md)** - Quick setup guide
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Commands and shortcuts
- **[IMG2IMG_GUIDE.md](./IMG2IMG_GUIDE.md)** - Image-to-image tutorial
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common issues and solutions
- **[CLAUDE.md](./CLAUDE.md)** - Developer documentation
- **[ROADMAP.md](./ROADMAP.md)** - Feature roadmap

## 🏗️ Architecture

### Mode System

The application operates in one mode at a time to manage VRAM:

```
IDLE (0 GB) ←→ CHAT (~5 GB) ←→ VISION (~7 GB) ←→ GENERATE (~12 GB)
```

- **IDLE** - Nothing loaded, VRAM free
- **CHAT** - Text LLM for prompt refinement
- **VISION** - Vision LLM for image-aware refinement
- **GENERATE** - ComfyUI + FLUX for image generation

### Project Structure

```
ai-image-chat/
├── app.py                      # Main Gradio application entrypoint
├── config.py                   # Runtime configuration values
├── comfyui_api.py              # ComfyUI integration helpers
├── core/                       # Core business logic modules
│   ├── generation_queue.py     # Batch processing pipeline
│   ├── image_gallery.py        # Gallery management utilities
│   ├── mode_manager.py         # Mode switching state machine
│   ├── workflow_manager.py     # Workflow discovery helpers
│   └── ...                     # Additional VRAM + session helpers
├── ui/                         # Placeholder package for UI components
├── utils/                      # Shared utility helpers
│   └── image_utils.py          # Image conversion helpers
├── workflows/                  # ComfyUI workflow JSONs
│   ├── img2img/
│   └── text2img/
├── test_buttons.py             # Targeted UI regression checks
├── test_comprehensive.py       # End-to-end smoke tests
├── test_new_features.py        # Feature-specific unit tests
├── test_phase25_completion.py  # Phase 2.5 regression coverage
└── test_workflow_manager.py    # Workflow manager unit tests
```

## 🎯 Usage Workflow

1. **Start in IDLE mode**
2. **Switch to CHAT** to refine your prompt with AI
3. **Switch to GENERATE** to create images
4. **Use Vision Chat** to iterate on generated images
5. **Batch generate** variations with the queue system

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Paths
COMFYUI_PATH = "/home/ant/AI/ComfyUI"
FINETUNE_NAME = "unstableEvolution_Fp811GB.safetensors"

# Models
OLLAMA_CHAT_MODEL = "llama3.1:latest"
OLLAMA_VISION_MODEL = "qwen2.5vl:latest"

# Defaults
DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 1024
DEFAULT_STEPS = 20
```

## 🧪 Testing

```bash
# Run all tests
python test_comprehensive.py

# Test specific modules
python test_workflow_manager.py
python test_new_features.py
python test_phase25_completion.py
```

## 🐛 Troubleshooting

**Common Issues:**

- **Cannot connect to Ollama** - Ensure `ollama serve` is running
- **ComfyUI not running** - Start with `./start_comfy.sh`
- **Out of VRAM** - Switch to IDLE and back, or lower resolution
- **Workflow errors** - Check ComfyUI terminal for Python errors

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for detailed solutions.

## 🛣️ Roadmap

**Phase 3 Complete:** ✅
- Multiple workflow support
- Img2img mode
- Batch generation queue
- Enhanced gallery features

**Phase 3 Advanced (In Progress):**
- ControlNet integration
- Inpainting support
- LoRA selector
- Upscaling pipeline
- Animation support

See [ROADMAP.md](./ROADMAP.md) for full feature timeline.

## 📊 Current Status

**Production Ready** ✅
- ~3,700+ lines of code
- 10 modular core classes
- Comprehensive test coverage
- Full documentation
- Phase 3 foundation complete

## 🤝 Contributing

Contributions welcome! This is a personal project but feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **ComfyUI** - Powerful node-based UI for Stable Diffusion
- **Ollama** - Local LLM runtime
- **FLUX** - State-of-the-art image generation model
- **Gradio** - Easy web UI framework

---

**Built with ❤️ using Claude Code**
