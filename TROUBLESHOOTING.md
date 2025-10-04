# 🔧 Troubleshooting Log

This document tracks issues encountered during development and their resolutions.

---

## Issue #1: Buttons Not Responding After Phase 2.5 Implementation

**Date:** 2025-09-30
**Severity:** Critical
**Status:** FIXED ✅ (2025-10-01)

### Symptoms
- All buttons in the app became unresponsive (no click events firing)
- App stayed in Idle mode, mode switching buttons didn't work
- No debug output in terminal when clicking buttons
- No errors in terminal or browser console

### Root Cause
Custom JavaScript keyboard shortcuts were interfering with Gradio's button click handlers. The keyboard event handler was using `e.preventDefault()` which blocked ALL default browser behavior, including button clicks.

### Investigation Steps
1. Verified Python syntax: `python -m py_compile app.py` - No errors
2. Created minimal test app (`test_buttons.py`) - Buttons worked fine in isolation
3. This confirmed the issue was specific to the main app, not Gradio itself
4. Temporarily disabled JavaScript by commenting out `js=keyboard_js` parameter
5. Buttons immediately started working
6. Identified that `preventDefault()` was the culprit

### Resolution (IMPLEMENTED 2025-10-01)

**The Fix:** Refactored JavaScript to use `e.stopPropagation()` instead of `e.preventDefault()`

**What Changed:**
- `preventDefault()` blocks the default action (button clicks, text selection, etc.)
- `stopPropagation()` only prevents event bubbling while allowing the default action

**Implementation:**
1. Extracted all JavaScript to external modules in `static/js/`:
   - `static/js/keyboard_shortcuts.js` - Keyboard shortcuts with proper event handling
   - `static/js/toast.js` - Toast notification system
   - `static/js/main.js` - Entry point and initialization

2. Updated `keyboard_shortcuts.js` to use `stopPropagation()`:
   ```javascript
   // OLD (BROKEN):
   case 'i':
       e.preventDefault();  // ❌ Blocks button clicks!
       btn = findButtonByText('🔵 Idle');
       break;

   // NEW (FIXED):
   case 'i':
       e.stopPropagation();  // ✅ Only stops event bubbling
       btn = findButtonByText('🔵 Idle');
       break;
   ```

3. Updated `app.py` to load external JavaScript modules:
   ```python
   custom_js = """
   // Load external JavaScript modules
   import('/file=static/js/main.js');
   """
   ```

### Benefits of the Fix
✅ Keyboard shortcuts work without interfering with buttons
✅ All button clicks function normally
✅ Text selection and other browser features work
✅ Cleaner code organization with external JS files
✅ Easier to maintain and debug JavaScript

### Files Modified
- `app.py` - Updated to load external JS modules (-128 lines)
- `static/js/keyboard_shortcuts.js` (NEW) - Keyboard shortcuts with stopPropagation
- `static/js/toast.js` (NEW) - Toast notification system
- `static/js/main.js` (NEW) - Module initialization

### Testing
To verify the fix works:
1. Start app: `python app.py`
2. Test button clicks (should work) ✅
3. Test keyboard shortcuts:
   - Alt+I: Switch to Idle
   - Alt+C: Switch to Text Chat
   - Alt+V: Switch to Vision Chat
   - Alt+G: Switch to Generate
   - Ctrl+G: Generate Image
   - Ctrl+K: Copy Prompt
4. Verify buttons still work after using shortcuts ✅

### Permanent Fix Status
✅ **COMPLETE** - JavaScript refactored and working correctly
```javascript
document.addEventListener('keydown', function(e) {
    // Don't interfere with text inputs
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        return;  // Let inputs work normally
    }

    // Handle shortcuts but don't prevent default
    if (e.altKey && e.key === 'c') {
        e.stopPropagation();  // Stop bubbling, but don't prevent default
        // Find and click button programmatically
    }
});
```

2. **Use Gradio's `Blocks.load()` event** instead of inline JS
3. **Test thoroughly** after making changes

### Prevention
- ✅ **Always disable custom JS first when debugging button issues**
- Always test button functionality after adding custom JavaScript
- Consider using Gradio's built-in event handling instead of custom JS where possible
- Add console.log statements in JavaScript for debugging
- Document known JS issues in code comments

### Related Code
```python
# Location: app.py lines 936-1039
keyboard_js = """
function setupKeyboardShortcuts() {
    // Custom keyboard handling
    document.addEventListener('keydown', function(e) {
        // ... event handling code ...
    });
}
"""
```

---

## Issue #2: Preset Buttons Returning Wrong Number of Values

**Date:** 2025-09-30
**Severity:** High
**Status:** Resolved ✅

### Symptoms
- Preset buttons (Fast Draft, Balanced, etc.) not working
- Generation warnings not displaying correctly

### Root Cause
The `apply_preset()` function was returning 5 values (width, height, steps, warning_text, warning_update) but the output list only had 3 components (width_slider, height_slider, steps_slider). Additionally, the warning display component was listed twice in outputs.

### Investigation Steps
1. Checked event handler outputs at `app.py:1687-1709`
2. Found mismatch: function returns 5 values, outputs only expect 3
3. Identified duplicate `vram_warning_display` in output list

### Resolution
1. Simplified `apply_preset()` to return only width, height, steps
2. Removed warning updates from preset handlers (warnings update via slider change events instead)
3. Fixed slider change handlers to use single `gr.update()` with both value and visible parameters

### Files Modified
- `app.py:1683-1709` - Preset button handlers
- `app.py:1711-1732` - Slider change handlers

### Prevention
- Always ensure function return values match output component list length
- Use `gr.update()` properly when updating multiple properties of a component
- Test all buttons after making changes to event handlers

---

## Issue #3: VRAM Warning Display Not Updating

**Date:** 2025-09-30
**Severity:** Medium
**Status:** Resolved ✅

### Symptoms
- VRAM warnings not appearing when sliders changed
- Warning component exists but stays hidden

### Root Cause
Event handlers were trying to update the same component (`vram_warning_display`) twice in the outputs list, which is invalid in Gradio.

### Resolution
Changed from:
```python
return warning_text, gr.update(visible=warning_visible)
# Output: [vram_warning_display, vram_warning_display]  # WRONG!
```

To:
```python
return gr.update(value=warning_text, visible=warning_visible)
# Output: [vram_warning_display]  # CORRECT!
```

### Files Modified
- `app.py:1711-1732` - Slider change event handlers

---

## Phase 3 - Workflow Manager Issues

### Issue #4: "No module named 'websocket'"

**Date:** 2025-09-30
**Status:** Resolved ✅

**Symptom:**
```
ModuleNotFoundError: No module named 'websocket'
```

**Solution:**
```bash
pip install websocket-client
```

### Issue #5: "Loading workflows from workflows - Loaded 0 workflows"

**Date:** 2025-09-30
**Status:** Resolved ✅

**Symptom:**
Terminal shows "Loaded 0 workflows" on startup

**Cause:** Workflow directory is empty or metadata files missing

**Solution:**
```bash
# Check if workflow exists
ls -la workflows/text2img/

# If missing, restore from git
git checkout -- workflows/text2img/flux_krea_text2img.json \
    workflows/text2img/flux_krea_text2img_meta.json

# Or create metadata manually
cat > workflows/text2img/flux_krea_text2img_meta.json << 'EOF'
{
  "name": "FLUX Krea Text2Image",
  "description": "Default FLUX text-to-image workflow",
  "category": "Text2Image",
  "tags": ["flux", "text2img", "default"],
  "author": "ant",
  "created_at": "2025-09-30T12:00:00",
  "modified_at": "2025-09-30T12:00:00"
}
EOF
```

### Issue #6: Workflow Selector UI Not Visible

**Date:** 2025-09-30
**Status:** Resolved ✅

**Symptom:** Can't find "🔀 Workflow Selector" accordion

**Solution:**
1. Switch to Generate Mode (click 🎨 Generate button)
2. Scroll down past the prompt textbox
3. Look for "🔀 Workflow Selector" accordion (collapsed by default)
4. Click to expand

---

## Known Issues & Limitations

### Keyboard Shortcuts Disabled ⚠️

**Status:** DISABLED (Current Workaround)
**Severity:** Medium

The custom JavaScript keyboard shortcuts cause button click interference and are currently disabled in `app.py:381`. All buttons work correctly without keyboard shortcuts. See Issue #1 above for details.

**Permanent Fix (TODO):**
- Refactor JavaScript to use `stopPropagation()` instead of `preventDefault()`
- Add proper event target checking
- Test thoroughly before re-enabling

### No Unit Tests

**Status:** Open
**Severity:** Low

Core modules lack unit tests. Manual testing required for all changes.

**Solution:**
Create `tests/` directory with pytest tests for core modules.

### VRAM Monitoring Overhead

**Status:** Acceptable
**Severity:** Low

`VRAMMonitor` polls nvidia-smi with 2-second caching. Impact is minimal but could be optimized with background thread polling if needed.

---

## Common Issues & Quick Fixes

### Buttons Not Working ⚠️ MOST COMMON ISSUE
**FIRST STEP:** Custom JavaScript keyboard shortcuts interfere with button clicks!

**Quick Fix:**
```python
# In app.py line ~381, comment out the js parameter:
with gr.Blocks(
    # js=keyboard_js,  # DISABLE THIS LINE
```

**Other checks:**
1. ✅ Disable custom JavaScript first (see above) - **this fixes 99% of button issues**
2. Verify event handlers are wired up - look for `DEBUG: ...btn wired` messages
3. Check terminal for Python exceptions during handler execution
4. Verify return values match output component list
5. Restart the app after making changes

### Components Not Updating
1. Ensure output list matches number of return values from function
2. Use `gr.update()` for dynamic updates (value, visible, choices, etc.)
3. Don't list the same component twice in outputs
4. Check if component is defined before use in event handler

### Mode Switching Fails
1. Verify Ollama is running: `curl http://localhost:11434/api/tags`
2. Check ComfyUI is running: `curl http://localhost:8188/system_stats`
3. Look for timeout errors in terminal (30s for Ollama warmup)
4. Check VRAM availability: `nvidia-smi`

### Import Errors
1. Ensure all dependencies installed: `pip install -r requirements.txt`
2. Check Python version compatibility (3.10+)
3. Verify virtual environment is activated if using one

---

## Debug Commands

```bash
# Check Python syntax
python -m py_compile app.py

# Test imports
python -c "import gradio; print(gradio.__version__)"

# Check if Ollama is running
curl http://localhost:11434/api/tags

# Check if ComfyUI is running
curl http://localhost:8188/system_stats

# Check GPU status
nvidia-smi

# View VRAM usage
watch -n 1 nvidia-smi

# Test minimal button functionality
python test_buttons.py
```

---

## Development Best Practices

1. **Always test incrementally** - Test each feature before adding the next
2. **Check event handler returns** - Ensure return values match outputs
3. **Use debug prints** - Add print statements in event handlers
4. **Test button clicks** - Click every button after making changes
5. **Verify imports** - Run `python -c "import app"` to catch import errors early
6. **Use version control** - Commit working versions before major changes
7. **Keep backups** - Save working versions before refactoring

---

## Useful Gradio Patterns

### Basic Button Handler
```python
def my_handler():
    print("Button clicked!")
    return "New value for textbox"

button.click(my_handler, None, [textbox])
```

### Multiple Outputs
```python
def multi_return():
    return "Value 1", "Value 2", gr.update(visible=True)

button.click(multi_return, None, [output1, output2, output3])
```

### Update Component Properties
```python
# Update value only
return gr.update(value="New text")

# Update visibility only
return gr.update(visible=True)

# Update multiple properties
return gr.update(value="Text", visible=True, interactive=False)
```

### Chain Events
```python
button.click(
    handler1, [input1], [output1]
).then(
    handler2, [output1], [output2]
)
```

---

## Contact & Resources

- Gradio Docs: https://gradio.app/docs
- Project README: `./README.md`
- Project Roadmap: `./ROADMAP.md`
- Claude Code Docs: `./CLAUDE.md`

**Last Updated:** 2025-09-30
