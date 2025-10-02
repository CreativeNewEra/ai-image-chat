# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Image Chat is a Gradio application for AI-assisted image generation using ComfyUI + FLUX with Ollama for chat-based prompt refinement. The system uses a 4-mode architecture (Idle, Text Chat, Vision Chat, Generate) to manage GPU VRAM across three distinct workloads: text LLM chat, vision LLM chat, and image generation.

**Target System:**
- Laptop: nobara-laptop (192.168.1.175)
- GPU: RTX 4090M (16GB VRAM)
- OS: Nobara Linux
- ComfyUI: `/home/ant/AI/ComfyUI`
- FLUX Finetune: `unstableEvolution_Fp811GB.safetensors`

## Key Commands

### Running the Application

```bash
# Start ComfyUI (Terminal 1)
./scripts/start_comfy.sh

# Or manually:
cd /home/ant/AI/ComfyUI
conda activate comfy-env
python main.py --listen --cuda-malloc --force-channels-last --use-sage-attention --dont-upcast-attention --fast

# Start the app (Terminal 2)
python app.py

# Or via script:
./scripts/start_app.sh
```

### Access URLs
- App: http://localhost:7860 (laptop) or http://192.168.1.175:7860 (desktop)
- ComfyUI: http://localhost:8188

### Dependencies

```bash
pip install -r requirements.txt
# Installs: gradio, requests, pillow, websocket-client
```

### Testing

```bash
# Unit tests for core modules
pytest tests/test_new_features.py          # Phase 2.5 features
pytest tests/test_phase25_completion.py    # Phase 2.5 completion tests
pytest tests/test_workflow_manager.py      # Workflow manager tests
pytest tests/test_comprehensive.py         # Comprehensive integration tests

# Run all tests
pytest tests/

# Manual testing workflow
# 1. Start app → Switch to Chat mode → Verify Ollama loads
# 2. Send chat message → Verify prompt extraction
# 3. Switch to Generate mode → Verify ComfyUI connection
# 4. Generate image with prompt → Verify image appears
# 5. Test workflow switching → Load different workflows
```

## Architecture

### Core Components

**`app.py`** (~2,000 lines, 65KB)
- Main Gradio application
- UI layout and event handlers
- Ollama chat integration functions
- Image generation workflow
- Four operation modes with explicit switching
- Workflow manager integration
- Batch queue and gallery management

**`core/`** (modular architecture - **11** business logic classes + exceptions)
- `mode_manager.py`: Mode switching and VRAM management
- `image_gallery.py`: Session storage with auto-save, filtering, sorting, favorites
- `vram_monitor.py`: Real-time GPU VRAM monitoring
- `session_stats.py`: Generation performance tracking
- `vram_estimator.py`: VRAM usage estimation and warnings
- `seed_manager.py`: Seed history and locking
- `prompt_history.py`: Prompt storage with search/export
- `smart_switch.py`: Context-aware mode suggestions
- `generation_queue.py`: Batch generation queue management
- `workflow_manager.py`: Multiple workflow support with categories
- `exceptions.py`: Custom exception hierarchy for error handling

**`utils/`** (helper functions)
- `image_utils.py`: PIL/base64 image conversion utilities

**`comfyui_api.py`** (~350 lines)
- `ComfyUIBridge` class: All ComfyUI API communication
- Workflow loading: Converts UI format JSON to API format
- Runtime workflow modification: Injects prompt, steps, dimensions, seed
- Image retrieval: Polls ComfyUI history endpoint for results
- `load_workflow()`: Load from file (legacy)
- `load_workflow_from_data()`: Load from workflow dict (Phase 3)

**`config.py`** (130 lines)
- Centralized configuration
- All paths, API endpoints, model names, defaults
- Easy customization point for different setups

**`workflows/`** (Phase 3 - Workflow organization)
- `text2img/`: Default FLUX text-to-image workflow (`flux_krea_text2img.json` + metadata)
- `img2img/`: Default FLUX image-to-image workflow (`flux_img2img.json` + metadata)
- Additional directories (e.g., `controlnet/`, `upscale/`) can be added by users as needed

### Mode System Architecture

The application operates in exactly one mode at a time:

```
                    ┌─→ CHAT (~5 GB llama3.1)
IDLE (0 GB) ←→ ───┼─→ VISION (~7 GB qwen2.5vl)
                    └─→ GENERATE (~12 GB ComfyUI+FLUX)
```

**IDLE Mode:**
- Unloads Ollama via `keep_alive=0`
- Clears CUDA cache with `torch.cuda.empty_cache()`
- Starting state, used for transitions

**CHAT Mode (Text):**
- Warm-starts Ollama to load text model to GPU
- Uses Ollama `/api/chat` endpoint with conversation history
- Extracts prompts from responses (quotes or descriptive text)
- `keep_alive=5m` to keep model loaded

**VISION Mode:**
- Warm-starts Ollama to load vision model to GPU
- Sends image + text to `/api/chat` with base64 encoded image
- Image context provided to understand refinement requests
- Extracts refined prompts from vision model responses

**GENERATE Mode:**
- Unloads Ollama first (if coming from CHAT or VISION)
- Requires ComfyUI running externally
- Modifies workflow JSON at runtime
- Queues prompt and polls for completion
- Auto-saves images with metadata to `./outputs/`

### Workflow Processing

Workflows can be loaded from file or from the workflow manager. The `ComfyUIBridge` converts UI format to API format:

1. **Load**: Parse UI JSON, extract nodes
2. **Convert**: Transform to API format with `class_type` and `inputs`
3. **Filter**: Skip UI-only nodes (MarkdownNote, Note, Reroute)
4. **Modify**: Runtime injection of:
   - Prompt text → `CLIPTextEncode` nodes
   - Steps, seed → `KSampler` node
   - Width, height → `EmptySD3LatentImage` node
   - Finetune name → `UNETLoader` node (from `config.FINETUNE_NAME`)

**Workflow Manager (Phase 3):**
- Scans `workflows/` directory on startup
- Loads workflows with metadata (name, description, category, tags, author)
- Category-based filtering (text2img, img2img, controlnet, upscale, custom)
- Import/export functionality
- Search by name, description, or tags

### VRAM Management Strategy

The system prevents VRAM conflicts through explicit mode switching rather than automatic unloading:

- Only one workload active at a time
- User-initiated mode switches (no surprises)
- Clear status messages about what's loaded
- Ollama unload via API, not process kill (clean)

## Configuration Points

### Changing Chat Model

Edit `config.py`:
```python
OLLAMA_CHAT_MODEL = "mistral:7b"  # Faster, smaller
```

### Changing Generation Defaults

Edit `config.py`:
```python
DEFAULT_WIDTH = 768
DEFAULT_HEIGHT = 768
DEFAULT_STEPS = 15  # Faster iterations
```

### Using Different Finetune

1. Place model in `/home/ant/AI/ComfyUI/models/diffusion_models/`
2. Edit `config.py`:
```python
FINETUNE_NAME = "your_model.safetensors"
```

### Network Configuration

The app binds to `0.0.0.0:7860` for LAN access. ComfyUI must be started with `--listen` flag for network access.

## Common Issues

**📝 For detailed troubleshooting steps, see [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)**

### "Cannot connect to Ollama"
- Verify: `curl http://localhost:11434/api/tags`
- Start: `ollama serve` (runs in background by default)

### "ComfyUI Not Running"
- Check: `curl http://localhost:8188/system_stats`
- Start: `./start_comfy.sh` or manually with full command

### Out of VRAM
- Switch to IDLE mode and back
- Lower resolution (768x768 instead of 1024x1024)
- Reduce steps (15 instead of 20)
- Check: `nvidia-smi` for other GPU processes

### Timeout Waiting for Image
- Check ComfyUI UI at http://localhost:8188 for errors
- Verify workflow exists in `workflows/` directory
- Confirm finetune exists in ComfyUI models directory
- Check ComfyUI terminal for Python errors

### Mode Switch Fails
- Wait 2-3 seconds between switches (unload takes time)
- Check terminal output for specific errors
- Verify both Ollama and ComfyUI are accessible

### Workflow Loading Errors
- Ensure workflow JSON has valid structure
- Check metadata file exists (`*_meta.json`)
- Verify category directory exists in `workflows/`
- See PHASE3_TROUBLESHOOTING.md for details

## Development Guidelines

### Code Quality & Formatting

The project uses automated code formatting and linting to maintain consistent code quality:

**Tools:**
- **Black**: Python code formatter (line length: 100)
- **Ruff**: Fast Python linter with auto-fix
- **Mypy**: Static type checker for Python
- **Pre-commit**: Git hooks for automated checks

**Setup:**
```bash
# Quick setup (installs deps, hooks, and runs initial formatting)
bash scripts/setup-dev.sh

# Or manually
pip install -r requirements-dev.txt
pre-commit install
```

**Configuration Files:**
- `pyproject.toml`: Black, Ruff, pytest, coverage, mypy configuration
- `.pre-commit-config.yaml`: Pre-commit hooks configuration
- `Makefile`: Convenient commands for formatting, linting, testing

**Pre-commit Hooks:**
Pre-commit hooks run automatically on `git commit`. They:
1. Format code with Black (auto-fix)
2. Lint with Ruff (auto-fix)
3. Remove trailing whitespace (auto-fix)
4. Ensure files end with newline (auto-fix)
5. Validate YAML/JSON syntax
6. Check for large files (>100MB)
7. Detect private keys
8. Check for merge conflicts

**Running Manually:**
```bash
make format           # Format with Black
make lint             # Lint with Ruff
make type-check       # Run mypy type checking
make check            # Format + Lint + Type-check + Test
pre-commit run --all-files  # Run all hooks
```

**Type Checking:**
The project uses gradual typing - types are added incrementally rather than all at once.

- **Configuration**: `mypy.ini` with lenient global settings
- **Strictly Typed Modules**: `core/vram_estimator.py`, `core/seed_manager.py`, `core/prompt_history.py`, `utils/image_utils.py`
- **Run mypy**: `make type-check` or `mypy .`
- **CI Integration**: Type checking runs automatically on PRs

See **[docs/TYPING.md](./docs/TYPING.md)** for complete type hinting guide.

**Skipping Hooks (when needed):**
```bash
git commit --no-verify -m "WIP: work in progress"
```

See **[CONTRIBUTING.md](./CONTRIBUTING.md)** for complete code style guide.

### Adding New Chat Models
1. Ensure model is pulled: `ollama pull model-name`
2. Add to dropdown in `app.py`: `get_available_models()`
3. Optionally update default in `config.py`

### Modifying Workflow Parameters
1. Identify node class_type in ComfyUI workflow
2. Add modification logic in `comfyui_api.py`: `modify_prompt()`
3. Add UI control in `app.py`: generation settings section
4. Pass parameter through `generate_image()` function

### Adding New Modes
1. Add enum value to `Mode` class in `core/mode_manager.py`
2. Implement switch method in `ModeManager`: `switch_to_<mode>()`
3. Update `_get_status_message()` with new status text
4. Add UI button and event handler in `app.py`
5. Consider VRAM impact and unload strategy

### Adding New Workflows
1. Create workflow in ComfyUI and export as JSON
2. Place in appropriate `workflows/` subdirectory (text2img, img2img, etc.)
3. Create metadata file: `workflow_name_meta.json`
4. Metadata structure:
```json
{
  "name": "Workflow Name",
  "description": "What this workflow does",
  "category": "text2img",
  "tags": ["tag1", "tag2"],
  "author": "Your Name",
  "created": "2025-09-30",
  "modified": "2025-09-30"
}
```
5. Refresh workflows in UI or restart app

## File Structure

```
ai-image-chat/
├── app.py                      # Main Gradio application (~2000 lines, 65KB)
├── comfyui_api.py             # ComfyUI API bridge (~350 lines)
├── config.py                  # Configuration (130 lines)
├── core/                      # Core business logic modules (11 classes + exceptions)
│   ├── __init__.py           # Module exports
│   ├── vram_monitor.py       # GPU VRAM monitoring
│   ├── session_stats.py      # Generation statistics
│   ├── vram_estimator.py     # VRAM estimation & warnings
│   ├── seed_manager.py       # Seed management
│   ├── prompt_history.py     # Prompt history with search
│   ├── smart_switch.py       # Smart mode suggestions
│   ├── mode_manager.py       # Mode switching logic
│   ├── image_gallery.py      # Image gallery management (enhanced)
│   ├── generation_queue.py   # Batch generation queue
│   ├── workflow_manager.py   # Multiple workflow support (Phase 3)
│   └── exceptions.py         # Custom exception hierarchy
├── utils/                     # Utility functions
│   ├── __init__.py           # Module exports
│   └── image_utils.py        # PIL/base64 helpers
├── workflows/                 # Workflow library (Phase 3)
│   ├── text2img/
│   │   ├── flux_krea_text2img.json        # Default text-to-image workflow shipped with repo
│   │   └── flux_krea_text2img_meta.json   # Metadata consumed by workflow manager
│   └── img2img/
│       ├── flux_img2img.json              # Default image-to-image workflow shipped with repo
│       └── flux_img2img_meta.json         # Metadata consumed by workflow manager
├── scripts/                   # Development scripts
│   └── setup-dev.sh           # Development environment setup
├── requirements.txt           # Python dependencies
├── requirements-dev.txt       # Development dependencies
├── pyproject.toml             # Tool configuration (black, ruff, pytest, mypy)
├── .pre-commit-config.yaml    # Pre-commit hooks configuration
├── Makefile                   # Development commands
├── flux1_krea_dev.json        # Legacy workflow file (only needed if manually copying older setups)
├── start_comfy.sh             # ComfyUI launcher script
├── start_app.sh               # App launcher script
├── check_code.sh              # Code quality checker
├── test_new_features.py       # Core feature tests
├── test_buttons.py            # Button functionality tests
├── test_phase25_completion.py # Phase 2.5 completion tests
├── test_workflow_manager.py   # Workflow manager tests (Phase 3)
├── test_comprehensive.py      # Comprehensive integration tests
├── outputs/                   # Generated images (auto-created)
├── prompt_history.json        # Saved prompts
├── .gitignore                # Git ignore rules
├── README.md                 # User guide
├── QUICKSTART.md             # Quick setup guide
├── DEPLOYMENT.md             # Production deployment
├── CONTRIBUTING.md           # Contributor guide & code style
├── CLAUDE.md                 # This file - Developer guide
├── TROUBLESHOOTING.md        # Issue tracking & solutions
├── PHASE3_TROUBLESHOOTING.md # Phase 3 specific troubleshooting
├── BEST_PRACTICES.md         # Code quality recommendations
├── ROADMAP.md                # Feature planning
├── QUICK_REFERENCE.md        # Command cheat sheet
├── REFACTORING_SUMMARY.md    # Modularization details
├── CURRENT_STATUS.md         # Current development status
├── PHASE3_PROGRESS.md        # Phase 3 progress tracking
└── PHASE25_COMPLETION_SUMMARY.md # Phase 2.5 completion summary
```

## Modular Architecture (Phases 2.5 & 3)

**Last Updated:** 2025-09-30
**Goal:** Improve maintainability, add Phase 2.5 polish, and enable Phase 3 advanced features

### Changes:
- Enhanced app.py to ~2,000 lines (added batch queue, gallery features, workflow manager)
- Created `core/` module with **11** business logic classes + **custom exception hierarchy**
- Enhanced `image_gallery.py` with filtering, sorting, favorites, and deletion
- Added `generation_queue.py` for batch processing
- Added `workflow_manager.py` for multiple workflow support (Phase 3)
- Added `exceptions.py` with 8 custom exception classes for better error handling
- Created `workflows/` directory structure with category organization
- Enhanced `comfyui_api.py` with `load_workflow_from_data()` method
- Created `utils/` module for helper functions
- Added comprehensive type hints and docstrings
- Zero breaking changes - fully backward compatible
- **100% test coverage** for new features

### Importing Modules:
```python
# Import from core
from core import VRAMMonitor, Mode, ModeManager, WorkflowManager

# Or import specific module
from core.vram_monitor import VRAMMonitor
from core.workflow_manager import WorkflowManager, Workflow, WorkflowMetadata
from utils import pil_to_base64

# Import custom exceptions
from core import (
    AIImageChatException,
    ComfyUINotAvailableError,
    OllamaConnectionError,
    WorkflowLoadError,
    ModeTransitionError,
    VRAMInsufficientError,
    ImageGenerationError,
    ModelNotFoundError,
)
```

### Exception Hierarchy:

The application uses a custom exception hierarchy for better error handling and debugging. All custom exceptions inherit from `AIImageChatException`, making it easy to catch any app-specific error.

**Exception Classes:**

1. **`AIImageChatException`** (base class)
   - Base exception for all AI Image Chat specific errors
   - Use to catch any app-specific error with a single except clause

2. **`ComfyUINotAvailableError`**
   - Raised when ComfyUI is not available or not responding
   - Common causes: ComfyUI not started, wrong API endpoint, network issues
   - Location: `comfyui_api.py`, `mode_manager.py`

3. **`OllamaConnectionError`**
   - Raised when Ollama service is not available or not responding
   - Common causes: Ollama not started, model not pulled, service crashed
   - Location: `mode_manager.py`, `app.py`

4. **`VRAMInsufficientError`**
   - Raised when there is insufficient VRAM for an operation
   - Common causes: Resolution too high, other processes using GPU
   - Location: Can be raised by `vram_estimator.py` (optional usage)

5. **`WorkflowLoadError`**
   - Raised when a ComfyUI workflow fails to load or parse
   - Common causes: Malformed JSON, missing nodes, incompatible version
   - Location: `comfyui_api.py`, `workflow_manager.py`

6. **`ModeTransitionError`**
   - Raised when switching between modes fails
   - Common causes: Service not responding, VRAM not freed, timeout
   - Location: `mode_manager.py`

7. **`ImageGenerationError`**
   - Raised when image generation fails
   - Common causes: Workflow execution error, timeout, missing models
   - Location: `comfyui_api.py`, `app.py`

8. **`ModelNotFoundError`**
   - Raised when a required model file is not found
   - Common causes: Model not downloaded, wrong filename, wrong directory
   - Location: `comfyui_api.py`

**Usage Example:**
```python
from core import ModeManager, OllamaConnectionError, ModeTransitionError

try:
    mode_manager.switch_to_chat()
except OllamaConnectionError as e:
    # Handle Ollama-specific error
    logger.error(f"Ollama not available: {e}")
    show_user_message("Please start Ollama with 'ollama serve'")
except ModeTransitionError as e:
    # Handle general mode transition error
    logger.error(f"Mode switch failed: {e}")
    show_user_message("Failed to switch modes. Try switching to Idle first.")
except AIImageChatException as e:
    # Catch any other app-specific error
    logger.error(f"Application error: {e}")
    show_user_message(f"Error: {e}")
```

**Exception Documentation:**
All custom exceptions are documented in `core/exceptions.py` with:
- Clear docstrings explaining when they're raised
- Common causes and solutions
- Usage examples

### Benefits:
- **Maintainability:** Single responsibility per module
- **Testability:** Classes can be unit tested independently
- **Readability:** Easier to find and understand code
- **Scalability:** Ready for Phase 3 features
- **Flexibility:** Multiple workflows, batch processing, advanced gallery
- **Error Handling:** Custom exceptions for better debugging and user feedback

See **[docs/archive/REFACTORING_SUMMARY.md](./docs/archive/REFACTORING_SUMMARY.md)** and **[docs/archive/PHASE3_PROGRESS.md](./docs/archive/PHASE3_PROGRESS.md)** for complete details.

## Documentation Guide

### Core Documentation (Root)
- **[README.md](./README.md)** - Start here for setup and usage
- **[QUICKSTART.md](./QUICKSTART.md)** - Quick setup guide
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Contributor guide & code style
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Solutions to common issues
- **[ROADMAP.md](./ROADMAP.md)** - Feature timeline and planning
- **[CLAUDE.md](./CLAUDE.md)** - This file - Complete developer reference

### Additional Documentation (docs/)
- **[docs/QUICK_REFERENCE.md](./docs/QUICK_REFERENCE.md)** - Commands and shortcuts cheat sheet
- **[docs/IMG2IMG_GUIDE.md](./docs/IMG2IMG_GUIDE.md)** - Image-to-image user guide
- **[docs/IMG2IMG_IMPLEMENTATION.md](./docs/IMG2IMG_IMPLEMENTATION.md)** - Image-to-image technical details
- **[docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md)** - Production deployment guide

### Historical Documentation (docs/archive/)
- **[docs/archive/PHASE25_COMPLETION_SUMMARY.md](./docs/archive/PHASE25_COMPLETION_SUMMARY.md)** - Phase 2.5 completion summary
- **[docs/archive/PHASE3_PROGRESS.md](./docs/archive/PHASE3_PROGRESS.md)** - Phase 3 progress tracking
- **[docs/archive/REFACTORING_SUMMARY.md](./docs/archive/REFACTORING_SUMMARY.md)** - Modularization details
- **[docs/archive/CURRENT_STATUS.md](./docs/archive/CURRENT_STATUS.md)** - Historical development status

## Important Implementation Details

### Image Gallery & Auto-Save

The `ImageGallery` class manages session images and auto-saves to disk:
- Images saved as PNG with metadata JSON
- Filename format: `{timestamp}_{seed}_{prompt_snippet}.png`
- Metadata includes: prompt, seed, width, height, steps, timestamp
- Gallery stored in memory for session, files persist on disk
- Click gallery images to load into Vision Chat
- Filter by prompt keywords, sort by date/seed/resolution
- Star/favorite images, bulk delete functionality

See `core/image_gallery.py` for implementation.

### Prompt Extraction Logic

Both chat systems attempt to extract prompts from responses:
1. **Quoted text**: Regex match for content in quotes (`"..."`)
2. **Descriptive text**: Long responses with multiple commas (likely detailed prompts)

Extracted prompts automatically populate the generation prompt field.

### Vision Chat Image Processing

Images are converted to base64 JPEG before sending to Ollama:
1. Convert PIL Image to RGB (if needed)
2. Save to BytesIO buffer as JPEG (quality=95)
3. Encode to base64 string
4. Send in message `images` array

See `utils/image_utils.py`: `pil_to_base64()` function.

### Workflow Node Mapping

The workflow converter maps UI widgets to API inputs based on node type. Key mappings:
- `UNETLoader`: `widgets_values[0]` → Override with `FINETUNE_NAME`
- `CLIPTextEncode`: `widgets_values[0]` → Replaced with user prompt
- `KSampler`: `widgets_values[0,2,3,4,5,6]` → seed, steps, cfg, sampler, scheduler, denoise
- `EmptySD3LatentImage`: `widgets_values[0,1,2]` → width, height, batch
- `SaveImage`: `inputs['filename_prefix']` → Handled for output saving

See `comfyui_api.py`: `load_workflow()` and `load_workflow_from_data()` functions.

### Image Retrieval Strategy

After queuing a prompt, the system polls `/history/{prompt_id}` every second:
1. Check if prompt_id exists in history
2. Look for `outputs` with `images` key
3. Extract filename and subfolder
4. Download via `/view` endpoint with parameters
5. Timeout after 300 seconds (5 minutes)

See `comfyui_api.py`: `get_image()` function.

### Batch Generation Queue

The `GenerationQueue` class manages batch generation jobs:
- Queue jobs with different prompts, seeds, or settings
- Process one job at a time to avoid VRAM conflicts
- Track job status (pending, processing, completed, failed, cancelled)
- Estimate time remaining based on average generation time
- Clear completed jobs or cancel all pending

See `core/generation_queue.py` for implementation.

### Workflow Manager

The `WorkflowManager` class handles multiple workflows:
- Scans `workflows/` directory on startup
- Loads workflows with metadata (name, description, category, tags, author)
- Category-based organization (text2img, img2img, controlnet, upscale, custom)
- Import workflows from JSON files with automatic categorization
- Export workflows with metadata
- Search workflows by name, description, or tags
- Track workflow usage statistics

See `core/workflow_manager.py` for implementation.

## Phase 2 Features (COMPLETED)

**Vision Chat:**
- ✅ qwen2.5vl integration
- ✅ Image-aware prompt refinement
- ✅ Base64 image encoding for Ollama
- ✅ Separate vision chat history
- ✅ Image preview in Vision Chat tab

**QOL Features:**
- ✅ Session gallery with thumbnails
- ✅ Click-to-load images into Vision Chat
- ✅ Auto-save images with metadata
- ✅ Generation presets (Fast/Balanced/Quality/Ultra)
- ✅ Seed management (use last seed button)
- ✅ Copy prompt to clipboard
- ✅ Seed tracking and display

## Phase 2.5 Features (COMPLETED)
**Completion Date:** 2025-09-30

**Batch Generation Queue:** ✅ COMPLETED
- ✅ GenerationQueue class for managing batch jobs
- ✅ Add single jobs or batch seed variations
- ✅ Job status tracking (pending, processing, completed, failed, cancelled)
- ✅ Process queue one job at a time
- ✅ Queue status display with job counts
- ✅ Clear completed/cancel all functionality
- ✅ Time remaining estimation
- 📝 **Location:** `core/generation_queue.py`, integrated in `app.py`

**Enhanced Gallery Features:** ✅ COMPLETED
- ✅ Filter images by prompt keywords
- ✅ Sort by newest, oldest, seed, or resolution
- ✅ Toggle favorite/star images
- ✅ Favorites-only filter mode
- ✅ Delete images (single or bulk)
- ✅ Gallery statistics (total, favorites, file size)
- ✅ Auto-refresh on filter/sort changes
- 📝 **Location:** `core/image_gallery.py`, integrated in `app.py`

**Keyboard Shortcuts:** ⚠️ DISABLED (Known Issue)
- ⚠️ Custom JavaScript keyboard event handler **DISABLED**
- ⚠️ Causes button click interference - see TROUBLESHOOTING.md Issue #1
- ✅ Implementation exists but commented out in app.py
- ❌ Needs refactoring to use `stopPropagation()` instead of `preventDefault()`
- 📝 **TODO:** Fix JavaScript to not block button clicks

**Model Status Indicators:** ✅ COMPLETED
- ✅ VRAMMonitor class with nvidia-smi integration
- ✅ Status icons: 🔵 Idle, 🟡 Loading, 🟢 Active
- ✅ Live VRAM tracking (used GB, percentage)
- ✅ 2-second caching to minimize overhead
- ✅ Real-time status display in mode panel

**Generation Statistics:** ✅ COMPLETED
- ✅ SessionStats class for metrics tracking
- ✅ Per-generation timing
- ✅ Average, fastest, slowest stats
- ✅ Total compute time and session duration
- ✅ Expandable stats accordion in UI
- ✅ Auto-update on each generation

**Smart Mode Switching:** ✅ COMPLETED
- ✅ SmartSwitchManager class
- ✅ Context-aware suggestions (prompt extracted, image generated)
- ✅ Toggle for enable/disable
- ✅ Non-intrusive suggestion UI
- ✅ Workflow-optimized suggestions

**Enhanced Seed Management:** ✅ COMPLETED
- ✅ SeedManager class for history and locking
- ✅ Seed variation buttons (+/-1, +/-10, +/-100)
- ✅ Lock seed checkbox with 🔒 indicator
- ✅ Seed history tracking (last 10 seeds)
- ✅ Seed history dropdown for quick access
- ✅ Random seed generator button
- ✅ Smart seed adjustment (uses last or random if empty)

**Generation Warnings:** ✅ COMPLETED
- ✅ VRAMEstimator class for VRAM usage estimation
- ✅ Real-time warnings based on resolution, steps, and current VRAM usage
- ✅ Warning levels: info, warning, error with visual indicators
- ✅ Automatic suggestions for optimal settings
- ✅ Live updates when sliders or presets change
- ✅ Warnings for extreme aspect ratios and high step counts

**Prompt History:** ✅ COMPLETED
- ✅ PromptHistory class with persistent JSON storage
- ✅ Automatic prompt saving after each generation
- ✅ Dropdown with last 10 prompts (shows use count)
- ✅ Search functionality with keyword filtering
- ✅ Load prompt from history to editor
- ✅ Export/import prompt collections as JSON
- ✅ Duplicate detection and use count tracking

## Phase 3 Features (IN PROGRESS)

**Multiple Workflow Support:** ✅ COMPLETE
- ✅ WorkflowManager class with metadata system
- ✅ Category-based organization (text2img, img2img, controlnet, upscale, custom)
- ✅ Workflow import/export functionality
- ✅ UI integration with workflow selector
- ✅ Search and filter workflows
- ✅ Full backward compatibility maintained
- ✅ **TESTED AND WORKING IN PRODUCTION**
- 📝 **Location:** `core/workflow_manager.py`, `workflows/` directory

**Img2img Mode:** ✅ COMPLETE
- ✅ Image upload functionality
- ✅ Denoise strength control (0.0-1.0)
- ✅ FLUX img2img workflow template
- ✅ ComfyUI image upload via API
- ✅ Workflow modification for img2img
- ✅ Automatic mode detection (text2img vs img2img)
- ✅ UI integration with accordion
- ✅ **TESTED AND READY FOR USE**
- 📝 **Location:** `workflows/img2img/`, `comfyui_api.py`, `app.py`
- 📚 **Documentation:** `IMG2IMG_GUIDE.md`, `IMG2IMG_IMPLEMENTATION.md`

**Next Phase 3 Features (See ROADMAP.md):**
- [ ] **ControlNet Integration** - Upload reference images, pose control, style transfer
- [ ] **Inpainting** - Mask editing, selective area modification
- [ ] **Advanced Parameters** - LoRA selector, prompt weighting, negative prompts
- [ ] **Upscaling Pipeline** - Built-in upscaler, tiled upscaling, face restoration
- [ ] **Animation Support** - Frame-by-frame generation, AnimateDiff integration

## Current Development Status

**Phase 2:** ✅ **COMPLETE**
**Phase 2.5:** ✅ **COMPLETE**
**Phase 3 Foundation:** ✅ **COMPLETE** (Workflow Manager + Img2img)
**Phase 3 Advanced:** 🚧 **IN PROGRESS** (ControlNet, Inpainting, LoRA, Upscaling, Animation)

**Status:** 🟢 **PRODUCTION READY**
**Latest Feature:** Img2img Mode (2025-09-30)
**Next Recommended Feature:** ControlNet Integration or Inpainting

See **[docs/archive/CURRENT_STATUS.md](./docs/archive/CURRENT_STATUS.md)** for detailed status and recommendations.

## Future Enhancements (Phase 3+)

Based on **[ROADMAP.md](./ROADMAP.md)**, remaining features include:

**Phase 3 - Advanced ComfyUI:**
- ControlNet integration
- Img2img & inpainting
- LoRA selector with weight control
- Advanced upscaling pipeline
- Animation support (AnimateDiff)
- Advanced comparison tools

**Phase 4 - Platform & Integration:**
- Multi-user support
- Sharing & collaboration
- Cloud storage
- REST API
- CLI tools
- Advanced vision features

---

**Last Updated:** 2025-09-30 (Evening - Img2img Complete)
**Current Phase:** Phase 3 Foundation + Img2img Complete
**Total Lines of Code:** ~3,700+ (core functionality + img2img)
**Test Coverage:** Comprehensive unit and integration tests
**Production Status:** ✅ Ready for deployment
**Latest Addition:** Img2img mode with FLUX support
