# Accordion Default States - Implementation Summary

**Date:** 2025-10-02
**Feature:** Updated accordion defaults and labels for better UX

## Overview

Updated all accordions in the UI to start closed by default (except the most important ones which are not in accordions), and improved accordion labels to be more descriptive.

## Changes Made

### Accordion States

All accordions now default to `open=False` for a cleaner initial UI:

1. **📚 Prompt History (Last 10 prompts)** - `open=False` ✅
   - Location: `ui/components/generation_panel.py:175`
   - Contains: Search, dropdown, load/refresh/export/import buttons

2. **🔀 Workflow Selector (Current: {workflow_name})** - `open=False` ✅
   - Location: `ui/components/generation_panel.py:213`
   - Shows current workflow name in accordion header
   - Contains: Workflow dropdown, category filter, import/export

3. **⚙️ Advanced Settings (Size, Steps, Seed)** - `open=False` ✅
   - Location: `ui/components/generation_panel.py:250`
   - Renamed from "Generation Settings" for clarity
   - Contains: Steps slider, width/height sliders, seed controls

4. **🖼️ Img2Img Settings (Optional)** - `open=False` ✅
   - Location: `ui/components/generation_panel.py:311`
   - Already labeled as optional
   - Contains: Input image uploader, denoise slider

5. **📊 Session Statistics (View performance metrics)** - `open=False` ✅
   - Location: `ui/components/generation_panel.py:354`
   - Contains: Performance metrics markdown

6. **🔄 Batch Generation Queue (Sequential processing)** - `open=False` ✅
   - Location: `ui/components/generation_panel.py:358`
   - Contains: Add to queue, seed variations, process controls

### Always Visible (Not in Accordions)

These important UI elements remain always visible:

1. **Current Prompt** - Textbox (lines 162-167)
   - Main prompt editor, always visible for quick access
   - 6 lines, interactive

2. **⚡ Quick Presets** - Button group (lines 199-205)
   - Fast Draft, Balanced, Quality, Ultra Detail presets
   - Most frequently used feature, stays visible

3. **Quick Actions Toolbar** - Button row (lines 155-159)
   - Quick Generate, Copy, Clear, Extract buttons
   - Primary actions always accessible

## Label Improvements

### Before → After

1. `"📚 Prompt History"` → `"📚 Prompt History (Last 10 prompts)"`
   - Clarifies what's shown in the dropdown

2. `"🔀 Workflow Selector"` → `"🔀 Workflow Selector (Current: {workflow_name})"`
   - Shows active workflow without opening accordion
   - Dynamic based on current selection

3. `"⚙️ Generation Settings"` → `"⚙️ Advanced Settings (Size, Steps, Seed)"`
   - More descriptive of what's inside
   - Indicates these are advanced/optional controls

4. `"📊 Session Statistics"` → `"📊 Session Statistics (View performance metrics)"`
   - Clarifies the purpose

5. `"🔄 Batch Generation Queue"` → `"🔄 Batch Generation Queue (Sequential processing)"`
   - Explains how the queue works

6. `"🖼️ Img2Img Settings (Optional)"` → (no change, already clear)

## User Experience Benefits

### Cleaner Initial UI
- Less visual clutter on startup
- Focus on essential controls (prompt, presets, generate button)
- Advanced features tucked away but clearly labeled

### Better Discoverability
- Accordion labels now explain what's inside
- Workflow selector shows current selection
- Users can quickly see what each accordion contains

### Improved Workflow
1. User sees clean interface with prompt and presets
2. Click accordion to access advanced features when needed
3. Accordion labels guide users to the right controls
4. Current workflow visible in header without opening accordion

## Technical Details

### File Modified
- `ui/components/generation_panel.py` - 6 accordion labels updated

### Accordion Structure
```python
# Example: Workflow Selector with dynamic label
current_workflow_name = (
    workflow_manager.get_current_workflow().metadata.name
    if workflow_manager.get_current_workflow()
    else "Default Workflow"
)
with gr.Accordion(f"🔀 Workflow Selector (Current: {current_workflow_name})", open=False):
    # Accordion contents...
```

### Default State
All accordions: `open=False`
- Users must click to expand
- Reduces initial visual noise
- Essential controls remain visible outside accordions

## Testing Checklist

**Visual Verification:**
- [ ] Start app → All accordions closed by default
- [ ] Current Prompt textbox visible and editable
- [ ] Quick Presets buttons visible (4 preset cards)
- [ ] Quick Actions toolbar visible (4 buttons)
- [ ] Generate button prominent and visible

**Accordion Labels:**
- [ ] Prompt History shows "(Last 10 prompts)"
- [ ] Workflow Selector shows "(Current: {workflow_name})"
- [ ] Advanced Settings shows "(Size, Steps, Seed)"
- [ ] Img2Img shows "(Optional)"
- [ ] Session Statistics shows "(View performance metrics)"
- [ ] Batch Queue shows "(Sequential processing)"

**Functionality:**
- [ ] Each accordion expands/collapses correctly
- [ ] Contents inside accordions work as before
- [ ] Workflow name in header matches actual current workflow
- [ ] No breaking changes to existing features

## Backward Compatibility

✅ **Fully backward compatible:**
- No changes to accordion contents
- No changes to event handlers
- No changes to functionality
- Only label text and default state modified
- All existing features work identically

## Files Modified

1. `ui/components/generation_panel.py`
   - Line 175: Prompt History label
   - Lines 208-213: Workflow Selector with dynamic label
   - Line 250: Advanced Settings label (renamed)
   - Line 311: Img2Img Settings (unchanged)
   - Line 354: Session Statistics label
   - Line 358: Batch Queue label

## Notes

- Workflow name is determined at UI creation time
- To update workflow name in accordion header, user must refresh the UI
- Could be enhanced with dynamic updates using Gradio's `.update()` method
- Labels use emoji prefixes for visual consistency
- Parenthetical descriptions follow a consistent pattern

## Future Enhancements

Possible improvements:
- Dynamic accordion label updates (workflow name updates live)
- Show stats count in Session Statistics label (e.g., "12 images")
- Show queue count in Batch Queue label (e.g., "3 pending")
- Remember user's last accordion state (open/closed) in session
- Add tooltips on hover for more detailed descriptions
