# 🐛 Known Issues

This document tracks known issues and limitations in the AI Image Chat project.

---

## Critical Issues

### Issue #1: Keyboard Shortcuts Disabled ⚠️

**Status:** DISABLED (Working Around)  
**Severity:** Medium  
**Affects:** User Experience  
**First Reported:** 2025-09-30  

**Problem:**
The custom JavaScript keyboard shortcuts interfere with Gradio button click events, causing all buttons to become unresponsive.

**Root Cause:**
The JavaScript uses `preventDefault()` which blocks all default browser behavior, including Gradio's button click handlers.

**Current Workaround:**
Keyboard shortcuts are disabled in `app.py:381`:
```python
# js=keyboard_js,  # DISABLED: Causes button click interference
```

**Impact:**
- ❌ No keyboard shortcuts available
- ✅ All buttons work correctly
- ✅ App is fully functional

**Permanent Fix (TODO):**
1. Refactor JavaScript to use `stopPropagation()` instead of `preventDefault()`
2. Add proper event target checking (don't intercept input/textarea events)
3. Use Gradio's native event system where possible
4. Test thoroughly before re-enabling

**References:**
- `TROUBLESHOOTING.md` Issue #1
- `BUTTON_DEBUG_CHECKLIST.md`
- `app.py` lines 88-376 (keyboard_js code)

---

## Minor Issues

### Issue #2: No Unit Tests

**Status:** Open  
**Severity:** Low  
**Affects:** Development Quality  

**Problem:**
Core modules lack unit tests, making refactoring risky.

**Impact:**
- Harder to verify changes don't break existing functionality
- Manual testing required for all changes

**Solution:**
Create `tests/` directory with pytest tests for:
- `core/vram_estimator.py`
- `core/prompt_history.py`
- `core/seed_manager.py`
- Other core modules

**Effort:** 2-3 hours

---

### Issue #3: Batch Generation - RESOLVED ✅

**Status:** RESOLVED (2025-09-30)
**Severity:** Low
**Affects:** Feature Completeness

**Problem:**
Batch generation queue feature was not implemented.

**Solution Implemented:**
Created `core/generation_queue.py` module with:
- ✅ Queue management (add/remove jobs)
- ✅ Job status tracking (pending, processing, completed, failed, cancelled)
- ✅ Seed variation batch generation
- ✅ Queue display and status
- ✅ Clear completed/cancel all functionality

**Files Modified:**
- `core/generation_queue.py` (NEW)
- `core/__init__.py` (exports)
- `app.py` (UI integration lines 270-389, 835-861, 1451-1487)

---

### Issue #4: Enhanced Gallery Features - RESOLVED ✅

**Status:** RESOLVED (2025-09-30)
**Severity:** Low
**Affects:** Feature Completeness

**Problem:**
Advanced gallery features were not implemented.

**Solution Implemented:**
Enhanced `core/image_gallery.py` with:
- ✅ Filter by prompt keywords
- ✅ Sort by date, seed, or resolution
- ✅ Star/favorite images with toggle
- ✅ Delete images (single and bulk)
- ✅ Gallery statistics (total, favorites, file size)

**Files Modified:**
- `core/image_gallery.py` (enhanced)
- `app.py` (UI integration lines 867-889, 913-935, 1489-1522)

---

## Compatibility Notes

### Torch Import (Not an Issue)

**Note:** `core/mode_manager.py` imports torch with optional handling:
```python
try:
    import torch
except ImportError:
    torch = None
```

This is by design - torch is only needed when running the app with the conda environment. Core modules can be imported and tested without torch installed.

**Status:** Working as intended

---

## Performance Notes

### VRAM Monitoring Polling

**Note:** `VRAMMonitor` polls nvidia-smi every time `get_vram_usage()` is called, with 2-second caching.

**Impact:** Minimal - calls are infrequent and cached

**Potential Optimization:** Background thread polling if needed in future

**Status:** Acceptable for current usage

---

## Documentation Status

All known issues are documented in:
- ✅ `TROUBLESHOOTING.md` - Detailed troubleshooting steps
- ✅ `BUTTON_DEBUG_CHECKLIST.md` - Quick fix guide
- ✅ `README.md` - User-facing troubleshooting section
- ✅ `CLAUDE.md` - Developer reference
- ✅ `BEST_PRACTICES.md` - Pre-Phase 3 checklist

---

**Last Updated:** 2025-09-30
**Total Open Issues:** 2 (1 minor - keyboard shortcuts disabled, 1 minor - no unit tests)
**Total Resolved Issues:** 5 (see TROUBLESHOOTING.md and above)
