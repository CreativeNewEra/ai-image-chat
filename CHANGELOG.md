# Changelog

All notable changes to AI Image Chat will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.5.0] - 2025-10-03

### 🎨 UI/UX Polish Phase

#### Phase 1: Quick Wins
- **Enhanced Toast Notifications**
  - Title support and custom styling
  - Progress bar animations with smooth transitions
  - 4 notification types (info, success, warning, error)
  - Dark mode support with proper theming
  - Close button and auto-dismiss functionality
  - Non-intrusive placement and animations

- **Better Loading States**
  - Skeleton loaders with shimmer animations
  - Enhanced progress indicators with spinners
  - Estimated time remaining display based on session stats
  - Smooth transitions and professional animations
  - Visual feedback for all async operations

- **Accordion Reorganization**
  - Reduced from 6 to 4 accordions (33% reduction)
  - Tabbed interface for related settings (Basic, Advanced, Img2Img)
  - Improved information hierarchy
  - Better use of vertical space
  - Cleaner, more organized interface

#### Phase 2a: Themes & Customization
- **Theme System**
  - Dark/Light/Auto mode with system detection
  - 5 color schemes (Default, Ocean, Forest, Sunset, Monochrome)
  - 3 layout densities (Compact, Comfortable, Spacious)
  - CSS variables for dynamic theming
  - Preference persistence via theme_preferences.json
  - Live theme preview and instant application
  - Accessible from header Settings button
  - Professional color palettes with proper contrast

#### Phase 2b: Prompt Composer
- **Tag Library System**
  - 60+ curated tags in 7 categories
  - Categories: Subject, Style, Lighting, Mood, Camera, Quality, Colors
  - Visual tag browser with organized tabs
  - Click-to-add tag interface
  - Each tag includes description for guidance

- **Template System**
  - 6 pre-built professional templates (Realistic Portrait, Fantasy Landscape, Anime Character, etc.)
  - Custom template creation and saving
  - Template persistence across sessions via prompt_templates.json
  - Category filtering for easy discovery
  - One-click template loading with auto-tag population

- **Smart Prompt Building**
  - Automatic tag ordering by category for optimal results
  - Professional prompt formatting
  - Selected tags display with category organization
  - One-click copy to main prompt editor
  - Build/Clear/Save workflow for efficient prompt creation
  - Accessible from header Composer button

### 🏗️ Technical Changes

#### New Core Classes
- `ThemeManager` - UI theme and customization management (~250 lines)
- `PromptComposer` - Tag-based prompt building system (~400 lines)

#### New UI Components
- `theme_settings.py` - Theme customization panel (~110 lines)
- `prompt_composer_panel.py` - Visual tag browser UI (~200 lines)

#### New Static Assets
- `static/css/styles.css` - Central stylesheet with variables, themes, animations (~500 lines)
- Enhanced `static/js/toast.js` with progress bars and titles

#### Core Updates
- Updated `core/__init__.py` with new exports
- Updated `ui/components/__init__.py` with new components
- Enhanced `app.py` with theme and composer integration (~100 lines added)
- Fixed generation progress to use session stats correctly

### 📝 Documentation
- Added `docs/PHASE1_UI_IMPROVEMENTS.md` - Quick wins documentation
- Added `docs/PHASE2A_THEMES.md` - Theme system guide
- Added `docs/PHASE2B_PROMPT_COMPOSER.md` - Prompt composer complete guide
- Updated `CLAUDE.md` with new components and architecture
- Updated `README.md` with UI/UX polish features
- Updated `ROADMAP.md` with completed improvements

### 🐛 Bug Fixes
- Fixed generation progress error (SessionStats.get_average_time → get_stats)
- Corrected accordion organization in generation panel
- Fixed CSS loading and dark mode support
- Proper event handler wiring for all new components

### 📦 Files Added
- `core/theme_manager.py`
- `core/prompt_composer.py`
- `ui/components/theme_settings.py`
- `ui/components/prompt_composer_panel.py`
- `static/css/styles.css`
- `docs/PHASE1_UI_IMPROVEMENTS.md`
- `docs/PHASE2A_THEMES.md`
- `docs/PHASE2B_PROMPT_COMPOSER.md`
- Auto-generated: `theme_preferences.json`, `prompt_templates.json`

### 📊 Statistics
- **Total new code**: ~1,800 lines
- **UI components**: 6 (was 4)
- **Core classes**: 13 (was 11)
- **Documentation**: 3 new comprehensive guides
- **Code quality**: Zero breaking changes, fully backward compatible

## [1.4.0] - 2025-10-02

### 🎨 UI/UX Improvements

#### Combined Chat Mode
- **Merged Text + Vision Chat** into single Chat mode with tabbed interface
- **Reduced modes** from 4 to 3 (Idle, Chat, Generate)
- **Auto-tab switching** when loading images from gallery
- **Better VRAM efficiency** with unified chat mode
- Simplified mental model for users

#### Modal Gallery
- **Gallery as modal overlay** instead of embedded component
- **Accessible from header button** - works in any mode
- **Auto-close on image selection** for seamless workflow
- **Cleaner main interface** without vertical scrolling
- Professional modal UX with backdrop

#### Visual Mode Indicators
- **Color-coded mode banners** (🔵 Blue for Idle, 🟢 Green for Chat, 🟠 Orange for Generate)
- **Real-time VRAM display** in mode banner
- **Active mode button highlighting** with gradient backgrounds
- **Mode-specific contextual tips** for better guidance
- **Smooth CSS animations** (slideInDown, fadeIn, pulseGlow)

#### Image Action Buttons
- **Generated Image Actions:**
  - 🔄 **Variations** - Add 4 seed variations to queue (+1, +10, +100, +1000)
  - 👁️ **Refine** - Open in Vision Chat with auto-mode switching
  - ⭐ **Favorite** - Toggle favorite status instantly
  - 📋 **Copy Seed** - Copy seed to clipboard with confirmation

- **Gallery Image Actions:**
  - ⭐ **Toggle Favorite** - Star/unstar selected images
  - 🎨 **Use for Img2Img** - Load into img2img input field
  - 👁️ **Open in Vision Chat** - Load with automatic mode switch
  - 🗑️ **Delete** - Remove images from gallery

- **Image Preview Modal:**
  - Full-size image display on click
  - Complete metadata (prompt, seed, dimensions, steps)
  - Quick action buttons in preview

#### Auto-Mode Switching
- **Send message** → Automatically switch to Chat mode
- **Generate image** → Automatically switch to Generate mode
- **Refine image** → Automatically switch to Chat/Vision
- **Toast notifications** for all mode transitions
- No manual mode selection needed for common workflows

### 📝 Documentation
- Added `COMBINED_CHAT_MODE.md` - Combined chat mode implementation
- Added `MODAL_GALLERY.md` - Modal gallery implementation details
- Added `VISUAL_MODE_INDICATORS.md` - Visual feedback system documentation
- Added `IMAGE_ACTION_BUTTONS.md` - Action buttons implementation guide
- Updated `CLAUDE.md` with latest architecture changes
- Updated `README.md` with new UI/UX features
- Updated `ROADMAP.md` with completed October 2025 improvements

### 🐛 Bug Fixes
- Fixed variable name inconsistencies (`image_gallery` → `gallery`)
- Fixed queue variable references (`generation_queue` → `gen_queue`)
- Fixed function parameter passing for image action buttons
- Corrected event handler wiring for all new features

### 🔧 Technical Changes
- Added 127 lines of CSS for visual indicators and animations
- Added ~300 lines of event handler code for image actions
- Updated `ui/components/generation_panel.py` with action buttons
- Enhanced mode manager status messages
- Improved error handling with proper parameter passing

## [1.3.0] - 2025-09-30

### ✨ Added
- **Img2img Mode** - Transform existing images with AI
  - Image upload functionality
  - Denoise strength control (0.0-1.0)
  - FLUX img2img workflow template
  - ComfyUI image upload API integration
  - Automatic mode detection (text2img vs img2img)
  - UI integration with accordion

### 📝 Documentation
- Added `IMG2IMG_GUIDE.md` - User guide for img2img feature
- Added `IMG2IMG_IMPLEMENTATION.md` - Technical implementation details

## [1.2.0] - 2025-09-30

### ✨ Added
- **Workflow Manager** - Multiple workflow support
  - Upload custom workflows
  - Workflow library with metadata
  - Category-based organization (text2img, img2img, controlnet, upscale)
  - Search and filter workflows by name, description, or tags
  - Import/export workflow functionality

### 📝 Documentation
- Added workflow manager documentation
- Updated CLAUDE.md with Phase 3 progress

## [1.1.0] - 2025-09-30

### ✨ Phase 2.5 Features

#### Batch Generation Queue
- Queue multiple generation jobs
- Add seed variations (4 variations with different offsets)
- Job status tracking (pending, processing, completed, failed, cancelled)
- Process queue one job at a time
- Queue status display with job counts
- Clear completed/cancel all functionality
- Time remaining estimation

#### Enhanced Gallery
- Filter images by prompt keywords
- Sort by newest, oldest, seed, or resolution
- Toggle favorite/star images
- Favorites-only filter mode
- Delete images (single or bulk)
- Gallery statistics (total, favorites, file size)
- Auto-refresh on filter/sort changes

#### Model Status Indicators
- Real-time VRAM monitoring via nvidia-smi
- Status icons: 🔵 Idle, 🟡 Loading, 🟢 Active
- Live VRAM usage (GB and percentage)
- Model name display in status panel
- 2-second caching to minimize overhead

#### Generation Statistics
- Session statistics tracking
- Per-generation timing
- Average, fastest, slowest stats
- Total compute time and session duration
- Expandable stats accordion in UI
- Auto-update on each generation

#### Smart Mode Switching
- Context-aware suggestions (prompt extracted → suggest Generate)
- Non-intrusive suggestion UI
- Toggle to enable/disable
- Workflow-optimized suggestions

#### Enhanced Seed Management
- Seed variation buttons: +1, +10, +100, -1, -10, -100
- Lock seed checkbox with 🔒 indicator
- Seed history tracking (last 10 seeds)
- Seed history dropdown for quick access
- Random seed generator button

#### Prompt History
- Dropdown with last 10 prompts
- Search functionality with keyword filtering
- Load prompt from history to editor
- Export/import prompt collections as JSON
- Duplicate detection and use count tracking

#### Generation Warnings
- Real-time VRAM usage estimation
- Warning levels: info, warning, error
- Automatic suggestions for optimal settings
- Live updates when sliders change
- Warnings for extreme aspect ratios

### 🐛 Bug Fixes
- Fixed keyboard shortcuts (disabled due to Gradio 5 compatibility)
- Improved error handling across all features

### 📝 Documentation
- Added `PHASE25_COMPLETION_SUMMARY.md`
- Updated all feature documentation

## [1.0.0] - 2025-09-15

### ✨ Initial Release - Phase 2 Complete

#### Core Features
- **3-Mode System** - Idle, Text Chat, Generate
- **Text Chat** - AI-powered prompt refinement with Ollama (llama3.1)
- **Vision Chat** - Image-aware refinement with qwen2.5vl
- **Image Generation** - ComfyUI + FLUX integration
- **VRAM Management** - Intelligent model loading/unloading

#### Gallery & Management
- Session gallery with thumbnails
- Click-to-load images into Vision Chat
- Auto-save images with metadata
- Generation presets (Fast/Balanced/Quality/Ultra)
- Seed management (use last seed button)
- Copy prompt to clipboard

#### Technical
- Ollama chat integration with conversation history
- ComfyUI API bridge with workflow modification
- Base64 image encoding for vision models
- Separate chat histories (text vs vision)
- Automatic prompt extraction

### 📝 Documentation
- Initial README, QUICKSTART, TROUBLESHOOTING
- Developer documentation (CLAUDE.md)
- Feature roadmap (ROADMAP.md)
- Contributing guidelines

---

## Version History

- **1.5.0** (2025-10-03) - UI/UX Polish: Themes, Prompt Composer, Enhanced Toasts, Loading States
- **1.4.0** (2025-10-02) - UI/UX Improvements: Combined Chat, Modal Gallery, Visual Indicators, Image Actions
- **1.3.0** (2025-09-30) - Img2img Mode
- **1.2.0** (2025-09-30) - Workflow Manager
- **1.1.0** (2025-09-30) - Phase 2.5 Polish Features
- **1.0.0** (2025-09-15) - Initial Release (Phase 2)

---

## Upgrade Notes

### 1.4.0 → 1.5.0
- No breaking changes
- New CSS file automatically loaded (`static/css/styles.css`)
- Two new JSON files auto-created on first use:
  - `theme_preferences.json` - Stores theme settings
  - `prompt_templates.json` - Stores custom prompt templates
- New UI features accessible via header buttons:
  - ⚙️ Settings - Theme customization
  - 🎨 Composer - Prompt builder
- All existing functionality preserved and enhanced
- Optional: Explore theme system and prompt composer for better workflow

### 1.4.0 → Current (if on 1.5.0+)
- No breaking changes
- New UI features are additive
- All existing functionality preserved
- Optional: Review new documentation for UI improvements

### 1.3.0 → 1.4.0
- Mode count reduced from 4 to 3 (Vision merged into Chat)
- Gallery now opens as modal instead of embedded
- All features remain backward compatible

### 1.2.0 → 1.3.0
- Img2img requires compatible workflows
- Upload img2img workflow to `workflows/img2img/`

### 1.1.0 → 1.2.0
- Workflows now stored in `workflows/` directory
- Legacy workflow files still supported

### 1.0.0 → 1.1.0
- No breaking changes
- Phase 2.5 features are optional enhancements
