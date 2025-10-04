# 🗺️ AI Image Chat - Feature Roadmap

This document tracks all planned features, improvements, and phases for the AI Image Chat project.

---

## ✅ Phase 1: Core Functionality (COMPLETED)
**Status:** Shipped ✓

- [x] 3-mode system (Idle, Text Chat, Generate)
- [x] Ollama text chat integration (llama3.1)
- [x] ComfyUI API integration
- [x] FLUX finetune support
- [x] Prompt refinement workflow
- [x] Basic image generation
- [x] VRAM management
- [x] Network access (laptop + desktop)

---

## ✅ Phase 2: Vision Chat (COMPLETED)
**Status:** Shipped ✓

### Core Vision Features
- [x] 4th mode: Vision Chat with image-aware AI
- [x] qwen2.5vl integration
- [x] Image-to-base64 conversion for Ollama
- [x] Vision chat UI with image preview
- [x] Separate chat histories (text vs vision)
- [x] Automatic prompt extraction from vision responses

### QOL Improvements (COMPLETED)
- [x] **Image Gallery** - Session history with thumbnails
- [x] **Click-to-Load** - Load gallery images into Vision Chat
- [x] **Seed Management** - "Use Last Seed" button
- [x] **Generation Presets** - Fast Draft, Balanced, High Quality, Ultra Detail
- [x] **Copy Prompt** - One-click copy to clipboard
- [x] **Auto-save Images** - Save with metadata (prompt, seed, settings as JSON)

---

## ✅ Phase 2.5: Polish & Power Features (COMPLETED)
**Status:** Shipped ✓
**Completion Date:** 2025-09-30

### High Priority
- [x] **Keyboard Shortcuts** ✅ COMPLETED
  - Ctrl+Enter to send chat messages
  - Alt+I/C/V/G for mode switching
  - Ctrl+G to generate
  - Ctrl+K to copy prompt
  - Ctrl+L to use last seed
  - Ctrl+Shift+C to clear chat
  - Ctrl+1/2/3/4 for generation presets
  - ? or Shift+/ to show shortcuts help

- [x] **Model Status Indicators** ✅ COMPLETED
  - Status dots: 🔵 Idle, 🟡 Loading, 🟢 Active
  - Live VRAM monitoring via nvidia-smi (2s cache)
  - Real-time VRAM display (GB and percentage)
  - Model name display in status panel

- [x] **Generation Counter & Stats** ✅ COMPLETED
  - Session statistics tracking
  - Total images generated counter
  - Average, fastest, slowest generation times
  - Total compute time tracking
  - Session duration display
  - Expandable stats accordion in UI

- [x] **Smart Mode Switching** ✅ COMPLETED
  - Smart suggestions after prompt extraction → "Switch to Generate?"
  - Smart suggestions after image generation → "Switch to Vision Chat?"
  - Toggle to enable/disable smart suggestions
  - Context-aware suggestion messages
  - Non-intrusive suggestion UI

### Medium Priority
- [x] **Prompt History** ✅ COMPLETED
  - Dropdown with last 10 prompts
  - Quick "reuse this prompt" from history
  - Search/filter prompt history
  - Export/import prompt collections

- [x] **Enhanced Seed Management** ✅ COMPLETED
  - Seed variation buttons: +1, +10, +100, -1, -10, -100
  - Lock seed checkbox to keep using same seed
  - Seed history dropdown (last 10 seeds)
  - Random seed button
  - Visual lock indicator in status

- [x] **Batch Generation** ✅ COMPLETED
  - Queue multiple prompts
  - Generate N variations (different seeds)
  - Queue status display with job tracking
  - Process queue one job at a time
  - Clear completed/cancel all functionality

- [x] **Image Gallery Enhancements** ✅ COMPLETED
  - Filter by prompt keywords
  - Sort by date, seed, or settings (newest, oldest, seed, resolution)
  - Star/favorite images
  - Delete images from gallery (single and bulk)
  - Gallery statistics display

- [x] **Generation Warnings** ✅ COMPLETED
  - VRAM usage estimation before generation
  - "This may OOM!" warning for large images
  - Suggested resolution based on available VRAM
  - Real-time warnings as sliders change
  - Info/warning/error severity levels

### Low Priority
- [ ] **Vision Chat Improvements**
  - "Analyze this image" quick button
  - "Suggest improvements" button
  - Quick action: "Make it more [dramatic/colorful/realistic]"
  - Show prompt diff (original vs suggested)

- [ ] **UI Themes**
  - Dark mode toggle
  - Custom color schemes
  - Compact/expanded view modes

- [ ] **Settings Persistence**
  - Save user preferences
  - Default preset selection
  - Favorite models auto-select
  - UI layout preferences

---

## ✅ UI/UX Improvements (October 2025) - COMPLETED
**Status:** Shipped ✓
**Completion Date:** 2025-10-02

### Combined Chat Mode ✅ COMPLETED
- [x] **Merged Text + Vision Chat** ✅ SHIPPED
  - Reduced from 4 modes to 3 (Idle, Chat, Generate)
  - Text Chat and Vision Chat in tabbed interface
  - Auto-tab switching when loading gallery images
  - Better VRAM efficiency with unified mode
  - Simplified mental model for users

### Modal Gallery ✅ COMPLETED
- [x] **Gallery as Modal Overlay** ✅ SHIPPED
  - Moved from embedded to modal overlay
  - Accessible from header button (any mode)
  - Auto-close on image selection
  - Cleaner main interface without scrolling
  - Professional modal UX

### Visual Mode Indicators ✅ COMPLETED
- [x] **Color-Coded Mode Feedback** ✅ SHIPPED
  - Mode status banners (Blue/Green/Orange)
  - Real-time VRAM display in banner
  - Active mode button highlighting
  - Mode-specific contextual tips
  - Smooth CSS animations (slideInDown, fadeIn, pulseGlow)

### Image Action Buttons ✅ COMPLETED
- [x] **Generated Image Actions** ✅ SHIPPED
  - 🔄 Variations - Add 4 seed variations to queue
  - 👁️ Refine - Open in Vision Chat (auto-switch)
  - ⭐ Favorite - Toggle favorite status
  - 📋 Copy Seed - Copy to clipboard
- [x] **Gallery Actions** ✅ SHIPPED
  - ⭐ Toggle Favorite - Star/unstar images
  - 🎨 Use for Img2Img - Load into img2img input
  - 👁️ Open in Vision Chat - Load with mode switch
  - 🗑️ Delete - Remove from gallery
- [x] **Image Preview Modal** ✅ SHIPPED
  - Full-size image display
  - Complete metadata (prompt, seed, dimensions, steps)
  - Quick action buttons

### Auto-Mode Switching ✅ COMPLETED
- [x] **Seamless Mode Transitions** ✅ SHIPPED
  - Send message → Auto-switch to Chat mode
  - Generate image → Auto-switch to Generate mode
  - Refine image → Auto-switch to Chat/Vision
  - Toast notifications for all switches
  - No manual mode selection needed

---

## ✅ UI/UX Polish Phase (October 2025 - Extended) - COMPLETED
**Status:** Shipped ✓
**Completion Date:** 2025-10-03

### Phase 1: Quick Wins ✅ COMPLETED
- [x] **Enhanced Toast Notifications** ✅ SHIPPED
  - Title support and custom styling
  - Progress bar animations
  - 4 notification types (info, success, warning, error)
  - Dark mode support
  - Close button and auto-dismiss

- [x] **Better Loading States** ✅ SHIPPED
  - Skeleton loaders with shimmer animations
  - Enhanced progress indicators
  - Estimated time remaining display
  - Smooth transitions and animations

- [x] **Accordion Reorganization** ✅ SHIPPED
  - Reduced from 6 to 4 accordions (33% reduction)
  - Tabbed interface for related settings
  - Improved information hierarchy
  - Better use of vertical space

### Phase 2a: Themes & Customization ✅ COMPLETED
- [x] **Theme System** ✅ SHIPPED
  - Dark/Light/Auto mode with system detection
  - 5 color schemes (Default, Ocean, Forest, Sunset, Monochrome)
  - 3 layout densities (Compact, Comfortable, Spacious)
  - CSS variables for dynamic theming
  - Preference persistence (theme_preferences.json)
  - Live theme preview and application

### Phase 2b: Prompt Composer ✅ COMPLETED
- [x] **Tag Library System** ✅ SHIPPED
  - 60+ curated tags in 7 categories
  - Categories: Subject, Style, Lighting, Mood, Camera, Quality, Colors
  - Visual tag browser with tabs
  - Click-to-add tag interface

- [x] **Template System** ✅ SHIPPED
  - 6 pre-built professional templates
  - Custom template creation and saving
  - Template persistence across sessions
  - Category filtering
  - One-click template loading

- [x] **Smart Prompt Building** ✅ SHIPPED
  - Automatic tag ordering by category
  - Professional prompt formatting
  - Selected tags display
  - One-click copy to prompt editor
  - Build/Clear/Save workflow

---

## 🔮 Phase 3: Advanced ComfyUI Integration (IN PROGRESS)
**Status:** Foundation Complete + Img2img Shipped ✓
**Latest Update:** 2025-10-02

### Workflow Management ✅ COMPLETED
- [x] **Multiple Workflow Support** ✅ SHIPPED
  - Upload custom workflows ✅
  - Workflow library/selector ✅
  - Workflow templates with metadata ✅
  - Dynamic workflow modification ✅
  - Category-based organization ✅
  - Search and filter workflows ✅

### Img2img Mode ✅ COMPLETED
- [x] **Img2img Basic Features** ✅ SHIPPED (2025-09-30)
  - Upload base image ✅
  - Strength/denoising control (0.0-1.0) ✅
  - FLUX img2img workflow template ✅
  - ComfyUI image upload API ✅
  - Automatic mode detection ✅
  - UI integration with accordion ✅
- [ ] **Inpainting Support** (Next Priority)
  - Mask editing UI
  - Selective area modification
  - Brush tools
  - Region-specific editing

### ControlNet Integration (Planned)
- [ ] **ControlNet Features**
  - Upload reference images
  - Pose detection and control
  - Edge/depth map control
  - Style transfer

- [ ] **Advanced Parameters**
  - LoRA selector and weights
  - Multiple LoRA stacking
  - Prompt weighting (word:1.5) syntax
  - Negative prompts (full support)
  - CFG scale control per workflow

### Generation Features
- [ ] **Upscaling Pipeline**
  - Built-in upscaler integration
  - Tiled upscaling for large images
  - Face restoration options
  - Detail enhancement

- [ ] **Animation Support**
  - Frame-by-frame generation
  - Prompt interpolation
  - Video export
  - AnimateDiff integration

### Quality of Life
- [ ] **Comparison Tools**
  - Side-by-side A/B testing
  - Slider comparison view
  - Multi-image grid view
  - Difference highlighting

- [ ] **Prompt Engineering**
  - Prompt templates library
  - Word/phrase autocomplete
  - Style preset tags
  - Wildcard support for variations

---

## 🌟 Phase 4: Platform & Integration (FUTURE)
**Status:** Conceptual

### Multi-User & Sharing
- [ ] **User Accounts**
  - Individual galleries per user
  - Saved preferences per user
  - Usage tracking per user

- [ ] **Sharing & Collaboration**
  - Share generated images with URL
  - Export image + metadata bundle
  - Import shared configurations
  - Collaborative prompt building

- [ ] **Cloud Storage**
  - Optional cloud backup
  - Sync across devices
  - Gallery migration tools

### API & Automation
- [ ] **REST API**
  - Programmatic image generation
  - Batch processing via API
  - Webhook notifications
  - API key management

- [ ] **CLI Tools**
  - Command-line generation
  - Batch processing scripts
  - Automated workflows
  - Integration with other tools

### Advanced Vision
- [ ] **Multi-Image Vision**
  - Compare multiple images
  - Generate variations of selected images
  - Style mixing between images

- [ ] **Vision-Driven Workflows**
  - Auto-adjust parameters based on image analysis
  - Intelligent cropping/composition
  - Style detection and transfer

---

## 🐛 Bug Fixes & Technical Debt
**Status:** Ongoing

### Known Issues
- [ ] Handle ComfyUI disconnections gracefully
- [ ] Better error messages for workflow failures
- [ ] Timeout handling for slow generations
- [ ] Memory cleanup for long sessions

### Performance Optimization
- [ ] Reduce gallery memory usage
- [ ] Optimize image preview loading
- [ ] Faster mode switching
- [ ] Background VRAM monitoring

### Code Quality
- [x] Add unit tests ✅ PARTIAL (handler tests added)
- [x] Extract event handlers to modules ✅ COMPLETED (58 handlers extracted)
- [x] Split large UI components ✅ COMPLETED (generation_panel split into 3)
- [ ] Type hints throughout
- [ ] Better error handling
- [ ] Documentation improvements
- [ ] Logging system

### Architecture Improvements
- [ ] **Application Class Pattern (Option 2)**
  - Replace global state with class-based architecture
  - Implement full dependency injection
  - Enable multiple app instances
  - Improve testability with mock-free testing
  - Add configuration-driven app initialization
  - **Effort:** 4-6 hours | **Benefit:** Best-practice architecture
  - **Status:** Planned (Option 1 completed - handlers extracted)
  - **Context:** See CLAUDE.md "Option 2: Application Class Pattern" section

---

## 📋 Phase 2.5 Features - Detailed Breakdown

### 1. Keyboard Shortcuts
**Complexity:** Low | **Impact:** High

```python
# Implementation notes:
# - Use Gradio's .key event handlers
# - Global shortcuts via JavaScript
# - Contextual shortcuts (different in each mode)
```

**Shortcuts:**
- `Enter` - Send chat message (in chat inputs)
- `Ctrl/Cmd + G` - Generate image
- `Ctrl/Cmd + C` - Copy current prompt
- `Ctrl/Cmd + V` - Paste into prompt
- `Esc` - Clear current input
- `Ctrl/Cmd + Z` - Undo prompt edit
- `Ctrl/Cmd + Shift + S` - Save current image

### 2. Model Status Indicators
**Complexity:** Medium | **Impact:** High

**Features:**
- Live status dots (🔴 unloaded, 🟡 loading, 🟢 loaded)
- VRAM usage bar chart
- Model load time display
- Temperature/power monitoring (optional)

**Technical:**
- Poll nvidia-smi every 2 seconds
- Update UI via Gradio state
- Cache status to avoid excessive polling

### 3. Generation Counter & Stats
**Complexity:** Low | **Impact:** Medium

**Metrics to Track:**
- Total images generated (session)
- Average generation time
- Fastest/slowest generation
- Most used resolution
- Total compute time

**Display:**
- Compact stats box in footer
- Expandable detailed stats panel
- Export stats as CSV/JSON

### 4. Smart Mode Switching
**Complexity:** Medium | **Impact:** High

**Auto-switch Logic:**
```
Text Chat → (prompt extracted) → Ask: "Switch to Generate?"
Generate → (image created) → Ask: "Switch to Vision Chat?"
Vision Chat → (prompt refined) → Ask: "Switch to Generate?"
```

**Settings:**
- Toggle auto-switch on/off
- Remember preference
- Confirmation dialog with "Don't ask again"

### 5. Prompt History
**Complexity:** Medium | **Impact:** High

**Storage:**
- SQLite database or JSON file
- Store: prompt, timestamp, seed, settings, image_path
- Search by keywords
- Tag prompts (favorites, good, experimental)

**UI:**
- Dropdown with recent prompts (last 20)
- Expanded history modal
- Click to load prompt
- Double-click to generate immediately

### 6. Enhanced Seed Management
**Complexity:** Low-Medium | **Impact:** Medium

**Features:**
- Seed variation explorer (+/- buttons)
- Lock seed checkbox (disable random)
- Batch variation generator (grid view)
- Seed history (last 10 seeds)

**Variation Grid:**
```
[Seed - 100] [Seed - 10] [Seed - 1]
[Seed]       [Seed + 1]  [Seed + 10]
[Seed + 100] [Random 1]  [Random 2]
```

### 7. Batch Generation
**Complexity:** High | **Impact:** High

**Architecture:**
- Queue system (list of generation jobs)
- Background processing
- Progress tracking per job
- Cancel/pause/resume support

**UI:**
- "Add to Queue" button
- Queue panel showing pending jobs
- Progress bars for each job
- Batch export when complete

### 8. Image Gallery Enhancements
**Complexity:** Medium | **Impact:** Medium

**Features:**
- Multi-select images (checkboxes)
- Bulk operations (delete, export, favorite)
- Filter bar (by prompt, date range, resolution)
- Sort options (newest, oldest, best seed)
- Pagination (show 20 at a time)

**Favorites System:**
- Star images in gallery
- Filter to favorites only
- Export favorites collection

### 9. Generation Warnings
**Complexity:** Low | **Impact:** High

**VRAM Estimation:**
```python
def estimate_vram(width, height, steps):
    base = 8  # GB base for FLUX
    res_factor = (width * height) / (1024 * 1024)  # compared to 1024x1024
    step_factor = steps / 20  # compared to 20 steps
    return base * res_factor * step_factor
```

**Warning Triggers:**
- Estimated VRAM > 15GB → Show warning
- Estimated VRAM > 16GB → Show error + suggest lower res
- Steps > 40 → Warn about generation time
- Resolution > 1536 → Warn about VRAM

### 10. Vision Chat Quick Actions
**Complexity:** Low | **Impact:** Medium

**Quick Buttons:**
- 🔍 "Analyze this image" → Sends: "Describe this image in detail"
- ✨ "Suggest improvements" → Sends: "What could be improved in this image?"
- 🎨 "Make it dramatic" → Sends: "How can I make this more dramatic?"
- 🌈 "Adjust colors" → Sends: "Suggest color adjustments"
- 🔥 "Add detail" → Sends: "How to add more detail to this image?"

---

## 💡 Community Requested Features
**Status:** Under Consideration

- [ ] Integration with other LLM providers (OpenAI, Anthropic)
- [ ] Support for other diffusion models (Midjourney, DALL-E)
- [ ] Mobile app or responsive web UI
- [ ] Discord bot integration
- [ ] Prompt marketplace/sharing
- [ ] Social features (like, comment, share)
- [ ] Tutorial mode for beginners
- [ ] Advanced analytics dashboard

---

## 📝 Notes

### Priority Legend
- **High Priority**: Significant UX improvement, frequently requested
- **Medium Priority**: Nice to have, improves workflow
- **Low Priority**: Edge case, minimal impact

### Complexity Legend
- **Low**: < 1 hour implementation
- **Medium**: 2-4 hours implementation
- **High**: 1+ day implementation

### Current Focus
**Next Sprint**: Phase 2.5 High Priority items (keyboard shortcuts, model status, stats)

---

## 🤝 Contributing

Want to implement a feature from this roadmap? Here's how:

1. Pick a feature from Phase 2.5 or Phase 3
2. Check complexity and current status
3. Create a branch: `feature/your-feature-name`
4. Implement with tests
5. Submit PR with reference to this roadmap

---

**Last Updated:** 2025-10-04
**Version:** Phase 2 Complete + QOL Features + UI/UX Polish + Handler Refactoring Complete
