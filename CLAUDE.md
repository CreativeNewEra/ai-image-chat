# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Image Chat is a Gradio application for AI-assisted image generation using ComfyUI + FLUX with Ollama for chat-based prompt refinement. The system uses a **3-mode architecture** (Idle, Chat, Generate) to manage GPU VRAM, with Text Chat and Vision Chat combined into tabbed interface within Chat mode.

**Target System:**
- Laptop: nobara-laptop (192.168.1.175)
- GPU: RTX 4090M (16GB VRAM)
- OS: Nobara Linux
- ComfyUI: `/home/ant/AI/ComfyUI`
- FLUX Finetune: `unstableEvolution_Fp811GB.safetensors`

## Quick Reference

**Most commonly used commands:**

```bash
# Start services
./scripts/start_comfy.sh      # Start ComfyUI (Terminal 1)
./scripts/start_app.sh         # Start app (Terminal 2)

# Development
make check                     # Run all checks (format + lint + test)
make test                      # Run tests
make coverage                  # Test coverage report
bash scripts/setup-dev.sh      # Setup dev environment

# Configuration
cp .env.example .env           # Create environment config
nano .env                      # Edit configuration
```

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

# Check if services are running
curl http://localhost:11434/api/tags  # Ollama
curl http://localhost:8188/system_stats  # ComfyUI
```

### Access URLs
- App: http://localhost:7860 (laptop) or http://192.168.1.175:7860 (desktop)
- ComfyUI: http://localhost:8188

### Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (includes testing, linting, formatting)
pip install -r requirements-dev.txt

# Or use make commands
make install         # Production only
make install-dev     # Development environment

# Quick dev setup with pre-commit hooks
bash scripts/setup-dev.sh
```

### Testing

```bash
# Run all tests
pytest

# Run tests with coverage
make coverage

# Run specific test file
pytest test_workflow_manager.py
pytest test_comprehensive.py

# Run tests by marker
pytest -m unit                 # Unit tests only
pytest -m integration          # Integration tests only
pytest -m "not slow"           # Exclude slow tests

# Manual testing workflow
# 1. Start app → Switch to Chat mode → Verify Ollama loads
# 2. Send chat message → Verify prompt extraction
# 3. Switch to Generate mode → Verify ComfyUI connection
# 4. Generate image with prompt → Verify image appears
# 5. Test workflow switching → Load different workflows
```

## Architecture

### Core Components

**`app.py`** (~2,200 lines, 75KB)
- Main Gradio application entry point
- UI layout and component wiring
- Event handler registration (delegates to handlers/ modules)
- Three operation modes with explicit switching (Idle, Chat, Generate)
- **Visual mode indicators** with color-coded banners and tips
- **Image action buttons** for quick operations
- **Auto-mode switching** with toast notifications
- **Primary focus: UI assembly and event wiring**
- **Event handlers extracted to handlers/ module** (58 functions)
- **UI components extracted to ui/components/ module** (6 builders)

**`handlers/`** (event handler modules - **58** functions across 6 modules)
- `mode_handlers.py`: Mode switching and auto-switch logic (2 functions)
- `gallery_handlers.py`: Gallery operations, favorites, img2img loading (9 functions)
- `workflow_handlers.py`: Workflow switching, import/export (6 functions)
- `chat_handlers.py`: Text/vision chat, prompt extraction, history (10 functions)
- `generation_handlers.py`: Image generation, seeds, queue, presets (13 functions)
- `ui_handlers.py`: Toast notifications, theme, composer, modals (18 functions)
- **Benefits:** Testable handlers, clear responsibility, easier to maintain

**`ui/components/`** (UI component builders - **6** modules)
- `mode_selector.py`: Mode selection radio buttons with status display (96 lines)
- `chat_interface.py`: Text Chat and Vision Chat tabbed interface (141 lines)
- `generation_panel.py`: Generation controls, settings, workflow selector, **image action buttons** (475 lines)
- `gallery_view.py`: Session gallery with filtering and sorting (105 lines)
- `theme_settings.py`: Theme customization panel with live preview (110 lines)
- `prompt_composer_panel.py`: Tag browser and template library UI (200 lines)
- **Benefits:** Reusable components, better maintainability, clear separation of concerns

**`core/`** (business logic modules - **13** classes + exceptions)
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
- `theme_manager.py`: UI theme system with 5 color schemes and 3 densities
- `prompt_composer.py`: Tag-based prompt building with 60+ tags and templates
- `exceptions.py`: Custom exception hierarchy for error handling

**`static/`** (static assets for enhanced UI/UX)
- `css/styles.css`: Central stylesheet with CSS variables, themes, animations (500 lines)
- `js/toast.js`: Enhanced toast notification system with progress bars
- `js/keyboard_shortcuts.js`: Keyboard shortcut handlers (Phase 2.5)
- `js/main.js`: JavaScript module initialization

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
                    ┌─→ CHAT (~5-7 GB, text or vision model)
IDLE (0 GB) ←→ ───┤
                    └─→ GENERATE (~12 GB ComfyUI+FLUX)
```

**IDLE Mode:**
- Unloads Ollama via `keep_alive=0`
- Clears CUDA cache with `torch.cuda.empty_cache()`
- Starting state, used for transitions
- Visual: 🔵 Blue banner with "IDLE MODE"

**CHAT Mode (Combined Text + Vision):**
- Warm-starts Ollama to load text or vision model to GPU
- **Text Chat Tab:** Uses llama3.1 (~5 GB) for prompt development
- **Vision Chat Tab:** Uses qwen2.5vl (~7 GB) for image refinement
- Uses Ollama `/api/chat` endpoint with conversation history
- Extracts prompts from responses (quotes or descriptive text)
- `keep_alive=5m` to keep model loaded
- Visual: 🟢 Green banner with "CHAT MODE"
- **Auto-switching:** Clicking gallery images auto-switches to Vision Chat tab

**GENERATE Mode:**
- Unloads Ollama first (if coming from CHAT)
- Requires ComfyUI running externally
- Modifies workflow JSON at runtime
- Queues prompt and polls for completion
- Auto-saves images with metadata to `./outputs/`
- Visual: 🟠 Orange banner with "GENERATE MODE"
- **Image action buttons:** Variations, Refine, Favorite, Copy Seed

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

The project uses environment variables for configuration. Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
nano .env  # Edit configuration
```

### Changing Chat Model

Edit `.env` or `config.py`:
```bash
# In .env
OLLAMA_CHAT_MODEL=mistral:7b  # Faster, smaller

# Or in config.py
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "mistral:7b")
```

### Changing Generation Defaults

Edit `.env` or `config.py`:
```bash
# In .env (if supported)
DEFAULT_WIDTH=768
DEFAULT_HEIGHT=768
DEFAULT_STEPS=15

# Or in config.py
DEFAULT_WIDTH = 768
DEFAULT_HEIGHT = 768
DEFAULT_STEPS = 15  # Faster iterations
```

### Using Different Finetune

1. Place model in `/home/ant/AI/ComfyUI/models/diffusion_models/`
2. Edit `.env`:
```bash
FINETUNE_NAME=your_model.safetensors
```

### Network Configuration

The app binds to `0.0.0.0:7860` for LAN access. ComfyUI must be started with `--listen` flag for network access.

Configure in `.env`:
```bash
COMFYUI_API=http://localhost:8188
OLLAMA_API=http://localhost:11434/api
```

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

### Development Workflow Commands

The project includes a `Makefile` with convenient commands for common development tasks:

```bash
# Code Quality
make format           # Format code with Black
make lint             # Lint and auto-fix with Ruff
make lint-check       # Lint without auto-fix (check only)
make type-check       # Run mypy type checking

# Testing
make test             # Run all tests
make test-unit        # Run unit tests only
make test-integration # Run integration tests only
make coverage         # Generate coverage report (opens htmlcov/index.html)

# Combined
make check            # Run format + lint + type-check + test
make all              # Same as 'make check'

# Cleanup
make clean            # Remove __pycache__, .pytest_cache, coverage files

# Installation
make install          # Install production dependencies
make install-dev      # Install development dependencies

# Help
make help             # Show all available commands
```

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
├── app.py                      # Main Gradio application (~2,200 lines)
├── comfyui_api.py             # ComfyUI API bridge (~350 lines)
├── config.py                  # Configuration (~160 lines)
├── handlers/                  # Event handler modules (NEW - extracted from app.py)
│   ├── __init__.py           # Handler exports
│   ├── mode_handlers.py      # Mode switching (2 functions, 109 lines)
│   ├── gallery_handlers.py   # Gallery operations (9 functions, 286 lines)
│   ├── workflow_handlers.py  # Workflow management (6 functions, 178 lines)
│   ├── chat_handlers.py      # Chat & prompt handling (10 functions, 298 lines)
│   ├── generation_handlers.py # Image generation (13 functions, 472 lines)
│   └── ui_handlers.py        # UI controls (18 functions, 335 lines)
├── ui/                        # UI components module (modular UI architecture)
│   ├── __init__.py           # Module exports
│   └── components/           # Reusable UI component builders
│       ├── __init__.py       # Component exports
│       ├── mode_selector.py  # Mode selection & status (96 lines)
│       ├── chat_interface.py # Text & Vision chat tabs (141 lines)
│       ├── generation_panel.py # Generation controls & settings (440 lines)
│       ├── gallery_view.py   # Gallery with filters & sorting (105 lines)
│       ├── theme_settings.py # Theme customization panel (110 lines)
│       ├── prompt_composer_panel.py # Prompt composer UI (200 lines)
│       └── README.md         # Component documentation
├── static/                    # Static assets (external JS/CSS)
│   ├── css/
│   │   └── styles.css        # Custom styling, themes, animations (500 lines)
│   └── js/                   # JavaScript modules
│       ├── keyboard_shortcuts.js # Keyboard shortcuts (fixed with stopPropagation)
│       ├── toast.js          # Toast notification system (enhanced)
│       └── main.js           # Entry point, module initialization
├── core/                      # Core business logic modules (13 classes + exceptions)
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
│   ├── theme_manager.py      # UI theme and customization (NEW)
│   ├── prompt_composer.py    # Tag-based prompt building (NEW)
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
│   ├── setup-dev.sh           # Development environment setup
│   ├── start_comfy.sh         # ComfyUI launcher script
│   ├── start_app.sh           # App launcher script
│   └── check_code.sh          # Code quality checker
├── requirements.txt           # Python dependencies
├── requirements-dev.txt       # Development dependencies
├── pyproject.toml             # Tool configuration (black, ruff, pytest, mypy)
├── .pre-commit-config.yaml    # Pre-commit hooks configuration
├── .env.example               # Environment variables template
├── Makefile                   # Development commands
├── flux1_krea_dev.json        # Legacy workflow file (only needed if manually copying older setups)
├── test_new_features.py       # Core feature tests
├── test_buttons.py            # Button functionality tests
├── test_phase25_completion.py # Phase 2.5 completion tests
├── test_workflow_manager.py   # Workflow manager tests (Phase 3)
├── test_comprehensive.py      # Comprehensive integration tests
├── outputs/                   # Generated images (auto-created)
├── prompt_history.json        # Saved prompts
├── prompt_templates.json      # Custom prompt templates (auto-created)
├── theme_preferences.json     # UI theme settings (auto-created)
├── .gitignore                # Git ignore rules
├── README.md                 # User guide
├── QUICKSTART.md             # Quick setup guide
├── DEPLOYMENT.md             # Production deployment
├── CONTRIBUTING.md           # Contributor guide & code style
├── CLAUDE.md                 # This file - Developer guide
├── TROUBLESHOOTING.md        # Issue tracking & solutions
├── ROADMAP.md                # Feature planning
├── docs/                      # Documentation directory
│   ├── PHASE1_UI_IMPROVEMENTS.md    # UI Polish Phase 1 (toasts, loading, accordions)
│   ├── PHASE2A_THEMES.md            # Theme system documentation
│   ├── PHASE2B_PROMPT_COMPOSER.md   # Prompt composer guide
│   └── archive/               # Historical documentation
│       ├── PHASE3_TROUBLESHOOTING.md # Phase 3 specific troubleshooting
│       ├── BEST_PRACTICES.md         # Code quality recommendations
│       ├── QUICK_REFERENCE.md        # Command cheat sheet
│       ├── REFACTORING_SUMMARY.md    # Modularization details
│       ├── CURRENT_STATUS.md         # Current development status
│       ├── PHASE3_PROGRESS.md        # Phase 3 progress tracking
│       └── PHASE25_COMPLETION_SUMMARY.md # Phase 2.5 completion summary
```

## Modular Architecture (Phases 2.5, 3 & UI Refactoring)

**Last Updated:** 2025-10-04
**Goal:** Improve maintainability, add Phase 2.5 polish, enable Phase 3 features, modular UI, and UI/UX polish

### Changes:
- **Event Handlers Extraction (2025-10-04 - NEW):**
  - Created `handlers/` module with **6** handler modules containing **58** functions
  - Reduced app.py from ~2,885 to ~2,216 lines (**669 line reduction**, 23.2%)
  - Extracted all event handler logic into testable, reusable functions
  - Mode, gallery, workflow, chat, generation, and UI handlers
  - All handlers use dependency injection for testability
  - **Result:** app.py now focuses solely on UI assembly and event wiring

- **UI Components Extraction (2025-10-01):**
  - Created `ui/components/` module with **6** reusable UI component builders
  - Extracted mode selector, chat interface, generation panel, gallery view, theme settings, and prompt composer
  - All components return dictionaries for flexible access
  - Comprehensive docstrings with parameter/return documentation

- **UI/UX Polish (2025-10-03 - NEW):**
  - **Enhanced Toast System:** Title support, progress bars, 4 notification types, dark mode
  - **Loading States:** Skeleton loaders, enhanced progress with time estimates, smooth animations
  - **Theme System:** Dark/Light/Auto modes, 5 color schemes, 3 layout densities, CSS variables
  - **Prompt Composer:** 60+ tags in 7 categories, template library, smart ordering, custom templates
  - **Accordion Reorganization:** Reduced from 6 to 4 accordions with tabbed interface
  - **CSS Framework:** Central styles.css with animations, variables, and responsive design

- **Business Logic (Phases 2.5 & 3):**
  - Created `core/` module with **13** business logic classes + **custom exception hierarchy**
  - Enhanced `image_gallery.py` with filtering, sorting, favorites, and deletion
  - Added `generation_queue.py` for batch processing
  - Added `workflow_manager.py` for multiple workflow support (Phase 3)
  - Added `theme_manager.py` for UI customization and preferences
  - Added `prompt_composer.py` for tag-based prompt building
  - Added `exceptions.py` with 8 custom exception classes for better error handling
  - Created `workflows/` directory structure with category organization
  - Enhanced `comfyui_api.py` with `load_workflow_from_data()` method
  - Created `utils/` module for helper functions

- **Code Quality:**
  - Added comprehensive type hints and docstrings
  - Zero breaking changes - fully backward compatible
  - **100% test coverage** for new features
  - Professional CSS with animations and responsive design

### Importing Modules:
```python
# Import event handlers
from handlers import (
    handle_mode_change,
    toggle_auto_switch,
    update_gallery_display,
    generate_and_store,
    # ... 54 more handler functions
)

# Import UI components
from ui.components import (
    create_mode_selector,
    create_chat_interface,
    create_generation_panel,
    create_gallery_view,
    create_theme_settings,
    create_prompt_composer
)

# Import from core
from core import (
    VRAMMonitor,
    Mode,
    ModeManager,
    WorkflowManager,
    ThemeManager,
    PromptComposer
)

# Or import specific module
from core.vram_monitor import VRAMMonitor
from core.workflow_manager import WorkflowManager, Workflow, WorkflowMetadata
from core.theme_manager import ThemeManager, ThemePreferences
from core.prompt_composer import PromptComposer, PromptTag, PromptTemplate
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
- **Maintainability:** Single responsibility per module, clear separation of UI and logic
- **Testability:** Classes and components can be unit tested independently
- **Readability:** Easier to find and understand code, organized by responsibility
- **Scalability:** Ready for Phase 3+ features with modular architecture
- **Reusability:** UI components can be reused or customized without touching app.py
- **Flexibility:** Multiple workflows, batch processing, advanced gallery, modular UI
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

**Keyboard Shortcuts:** ⚠️ DISABLED (Gradio 5 Compatibility Issue - 2025-10-01)
- ✅ Implemented in `static/js/keyboard_shortcuts.js` with proper `stopPropagation()`
- ❌ Temporarily disabled due to Gradio 5 static file serving changes
- ⚠️ External JS modules cannot be loaded using `/file=` path in Gradio 5
- 📝 All functionality still accessible via mouse clicks (no features lost)
- 📝 See `GRADIO5_MIGRATION.md` for details and future fix options

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

## UI/UX Improvements (October 2025) ✅ COMPLETE

**Completion Date:** 2025-10-02

### Combined Chat Mode
- ✅ Merged Text Chat and Vision Chat into single mode with tabs
- ✅ Reduced from 4 modes to 3 (Idle, Chat, Generate)
- ✅ Auto-tab switching when loading images from gallery
- ✅ Better VRAM efficiency with unified chat mode
- 📝 **Documentation:** `COMBINED_CHAT_MODE.md`

### Modal Gallery
- ✅ Gallery moved from embedded to modal overlay
- ✅ Accessible from any mode via header button
- ✅ Auto-close on image selection
- ✅ Cleaner main interface without vertical scrolling
- 📝 **Documentation:** `MODAL_GALLERY.md`

### Visual Mode Indicators
- ✅ Color-coded mode status banners (Blue/Green/Orange)
- ✅ Real-time VRAM display in banner
- ✅ Active mode button highlighting with gradients
- ✅ Mode-specific contextual tips
- ✅ Smooth CSS animations (slideInDown, fadeIn, pulseGlow)
- 📝 **Documentation:** `VISUAL_MODE_INDICATORS.md`

### Image Action Buttons
- ✅ **Generated Image Actions:** Variations, Refine, Favorite, Copy Seed
- ✅ **Gallery Actions:** Toggle Favorite, Use for Img2Img, Open in Vision Chat, Delete
- ✅ **Image Preview Modal:** Full-size preview with metadata and actions
- ✅ One-click seed variations (adds 4 jobs to queue)
- ✅ Auto-mode switching for refine operations
- 📝 **Documentation:** `IMAGE_ACTION_BUTTONS.md`

### Auto-Mode Switching
- ✅ Send message → Auto-switch to Chat mode
- ✅ Generate image → Auto-switch to Generate mode
- ✅ Toast notifications for all mode changes
- ✅ Seamless workflow without manual mode selection

## Current Development Status

**Phase 2:** ✅ **COMPLETE**
**Phase 2.5:** ✅ **COMPLETE**
**Phase 3 Foundation:** ✅ **COMPLETE** (Workflow Manager + Img2img)
**UI/UX Improvements:** ✅ **COMPLETE** (October 2025)
**Phase 3 Advanced:** 🚧 **IN PROGRESS** (ControlNet, Inpainting, LoRA, Upscaling, Animation)

**Status:** 🟢 **PRODUCTION READY**
**Latest Feature:** Image Action Buttons + Visual Mode Indicators (2025-10-02)
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

**Last Updated:** 2025-10-03 (UI/UX Polish Complete - Themes + Prompt Composer)
**Current Phase:** Phase 3 Foundation + UI/UX Improvements + UI/UX Polish Complete
**Total Lines of Code:** ~5,500+ (core functionality + img2img + UI improvements + themes + composer)
**Test Coverage:** Comprehensive unit and integration tests
**Production Status:** ✅ Ready for deployment
**Latest Addition:** Theme system (5 color schemes, dark mode), Prompt Composer (60+ tags, templates), Enhanced toasts, Loading states
