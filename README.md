# 🎨 AI Image Chat

AI-powered image generation application combining ComfyUI + FLUX for image generation, Ollama for chat-based prompt refinement, and a Gradio web interface.

[![Phase 3](https://img.shields.io/badge/Phase-3%20Complete-brightgreen)]()
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)]()
[![License](https://img.shields.io/badge/License-MIT-yellow)]()
[![Tests](https://github.com/CreativeNewEra/ai-image-chat/workflows/Tests%20and%20Linting/badge.svg)](https://github.com/CreativeNewEra/ai-image-chat/actions/workflows/test.yml)
[![Documentation](https://github.com/CreativeNewEra/ai-image-chat/workflows/Documentation%20Check/badge.svg)](https://github.com/CreativeNewEra/ai-image-chat/actions/workflows/docs.yml)

## ✨ Features

### Core Functionality
- **💬 Combined Chat Mode** - Text and Vision chat in unified tabbed interface
- **🎨 Text-to-Image** - Generate images from text with FLUX workflows
- **🖼️ Image-to-Image** - Transform existing images with AI
- **📦 Batch Generation** - Queue multiple generation jobs with variations

### UI/UX (October 2025)
- **🎯 Image Action Buttons** - Quick actions on every image (Variations, Refine, Favorite, Copy Seed)
- **📁 Modal Gallery** - Overlay gallery accessible from any mode
- **🔵 Visual Mode Indicators** - Color-coded banners with real-time VRAM display
- **⚡ Auto-Mode Switching** - Seamless transitions with toast notifications
- **✨ CSS Animations** - Smooth transitions and visual feedback

### UI/UX Polish (October 2025 - Latest)
- **🎨 Theme System** - Dark/Light/Auto modes with 5 color schemes and 3 layout densities
- **📝 Prompt Composer** - 60+ curated tags in 7 categories, template library, smart ordering
- **🔔 Enhanced Toasts** - Rich notifications with progress bars and titles
- **⏳ Loading States** - Skeleton loaders and progress indicators with time estimates
- **📋 Smart Organization** - Accordion consolidation with tabbed interface

### Gallery & Management
- **🗂️ Enhanced Gallery** - Filter, sort, favorite, and manage images
- **📊 Real-time Monitoring** - Live VRAM usage and statistics
- **🎯 Multiple Workflows** - Support for various ComfyUI workflows
- **🧠 Smart Mode Switching** - Intelligent VRAM management

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

### Getting Started
- **[QUICKSTART.md](./QUICKSTART.md)** - Quick setup guide
- **[QUICK_REFERENCE.md](./docs/QUICK_REFERENCE.md)** - Commands and shortcuts
- **[IMG2IMG_GUIDE.md](./docs/IMG2IMG_GUIDE.md)** - Image-to-image tutorial
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common issues and solutions

### UI/UX Features (October 2025)
- **[COMBINED_CHAT_MODE.md](./COMBINED_CHAT_MODE.md)** - Combined Text + Vision chat mode
- **[MODAL_GALLERY.md](./MODAL_GALLERY.md)** - Modal gallery implementation
- **[VISUAL_MODE_INDICATORS.md](./VISUAL_MODE_INDICATORS.md)** - Visual mode feedback
- **[IMAGE_ACTION_BUTTONS.md](./IMAGE_ACTION_BUTTONS.md)** - Quick action buttons

### UI/UX Polish Documentation (October 2025 - Latest)
- **[docs/PHASE1_UI_IMPROVEMENTS.md](./docs/PHASE1_UI_IMPROVEMENTS.md)** - Toast notifications, loading states, accordion organization
- **[docs/PHASE2A_THEMES.md](./docs/PHASE2A_THEMES.md)** - Theme system and customization
- **[docs/PHASE2B_PROMPT_COMPOSER.md](./docs/PHASE2B_PROMPT_COMPOSER.md)** - Prompt composer guide with tags and templates

### Developer
- **[CLAUDE.md](./CLAUDE.md)** - Complete developer documentation
- **[ROADMAP.md](./ROADMAP.md)** - Feature roadmap
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Contribution guide

## 🏗️ Architecture

### Mode System

The application uses a **3-mode architecture** to manage VRAM efficiently:

```
                ┌─→ CHAT (~5-7 GB, text or vision model)
IDLE (0 GB) ←→ ┤
                └─→ GENERATE (~12 GB ComfyUI+FLUX)
```

- **🔵 IDLE** - Nothing loaded, VRAM free
- **🟢 CHAT** - Combined Text + Vision chat in tabbed interface
  - Text Chat: Prompt development with llama3.1
  - Vision Chat: Image refinement with qwen2.5vl
- **🟠 GENERATE** - ComfyUI + FLUX for image generation
  - Image action buttons for quick operations
  - Auto-mode switching for seamless workflow

### Project Structure

```
ai-image-chat/
├── app.py                      # Main Gradio application (~1670 lines)
├── config.py                   # Runtime configuration values
├── comfyui_api.py              # ComfyUI integration helpers
├── ui/                         # UI components module
│   ├── __init__.py            # Module exports
│   └── components/            # Reusable UI component builders
│       ├── mode_selector.py   # Mode selection & status (96 lines)
│       ├── chat_interface.py  # Text & Vision chat (141 lines)
│       ├── generation_panel.py # Generation controls (440 lines)
│       ├── gallery_view.py    # Gallery & filters (105 lines)
│       └── README.md          # Component documentation
├── static/                     # Static assets (NEW)
│   └── js/                    # External JavaScript modules
│       ├── keyboard_shortcuts.js # Keyboard shortcuts (150 lines)
│       ├── toast.js           # Toast notification system (130 lines)
│       └── main.js            # Module initialization (40 lines)
├── core/                       # Core business logic modules (11 classes)
│   ├── generation_queue.py     # Batch processing pipeline
│   ├── image_gallery.py        # Gallery management utilities
│   ├── mode_manager.py         # Mode switching state machine
│   ├── workflow_manager.py     # Workflow discovery helpers
│   ├── vram_monitor.py         # GPU VRAM monitoring
│   ├── session_stats.py        # Generation statistics
│   ├── seed_manager.py         # Seed management
│   ├── prompt_history.py       # Prompt history & search
│   ├── smart_switch.py         # Smart mode suggestions
│   ├── vram_estimator.py       # VRAM estimation & warnings
│   └── exceptions.py           # Custom exception hierarchy
├── utils/                      # Shared utility helpers
│   └── image_utils.py          # Image conversion helpers (PIL/base64)
├── workflows/                  # ComfyUI workflow JSONs
│   ├── img2img/               # Image-to-image workflows
│   └── text2img/              # Text-to-image workflows
├── tests/                      # Test suite
│   ├── test_buttons.py         # Targeted UI regression checks
│   ├── test_comprehensive.py   # End-to-end smoke tests
│   ├── test_new_features.py    # Feature-specific unit tests
│   └── test_workflow_manager.py # Workflow manager unit tests
├── scripts/                    # Shell scripts
│   ├── start_app.sh            # Launch the Gradio app
│   ├── start_comfy.sh          # Launch ComfyUI
│   └── setup-dev.sh            # Dev environment setup
└── outputs/                    # Generated images (auto-created)
```

**Key Architecture Benefits:**
- 🎨 **Modular UI**: 4 reusable component builders in `ui/components/`
- 🧠 **Business Logic**: 11 specialized classes in `core/` for clean separation
- ⚡ **External JS**: Keyboard shortcuts and toast system in `static/js/` modules
- 🔌 **Easy Integration**: Dictionary-based component API for flexibility
- 📚 **Well Documented**: Comprehensive docstrings and component README
- 🧪 **Testable**: Components and logic can be tested independently

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
- ~5,500+ lines of code
- 13 modular core classes
- 6 reusable UI components
- Comprehensive test coverage
- Full documentation
- Phase 3 foundation complete
- UI/UX polish complete (themes, prompt composer, enhanced notifications)

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
