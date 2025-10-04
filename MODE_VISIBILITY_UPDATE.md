# Mode-Specific UI Visibility Implementation

**Date:** 2025-10-02
**Goal:** Eliminate vertical scrolling by showing only UI relevant to the current mode

## Problem
- All UI sections (Chat, Generation, Gallery, etc.) were always visible
- Required lots of scrolling even though only one mode is active at a time
- Wasted screen space showing inactive features

## Solution
Implemented mode-specific UI visibility that shows ONLY the UI for the active mode.

## Changes Made

### 1. UI Structure Reorganization
Created three distinct UI sections wrapped in `gr.Column` with visibility control:

- **IDLE MODE (`idle_section`)**:
  - Welcome message with mode instructions
  - Workflow guide
  - Always starts visible (initial state)

- **CHAT MODE (`chat_section`)**:
  - AI Chat Assistant header
  - Text Chat and Vision Chat tabs
  - Chat history
  - Model selection
  - Starts hidden

- **GENERATE MODE (`generate_section`)**:
  - Generation panel with all controls
  - Prompt management
  - Settings and presets
  - Image preview
  - Batch queue
  - Stats and accordions
  - Starts hidden

### 2. State Management
- Added `current_mode_state = gr.State("IDLE")` to track current mode
- State updates when mode changes
- Used for maintaining UI consistency

### 3. Mode Change Handler (`handle_mode_change`)
Enhanced to return UI visibility updates:
```python
def handle_mode_change(mode_choice):
    # ... existing code ...

    # Returns: status, smart_suggestion, banner, tip,
    #          idle_vis, chat_vis, generate_vis, current_mode

    # Example for CHAT mode:
    idle_vis = gr.update(visible=False)
    chat_vis = gr.update(visible=True)
    generate_vis = gr.update(visible=False)
    current_mode = "CHAT"
```

### 4. Auto-Switch Functions Updated
Modified auto-switching behavior to also update UI visibility:

- **`bot_message`** (Chat auto-switch):
  - When auto-switching to CHAT mode
  - Hides idle/generate sections
  - Shows chat section

- **`generate_and_store`** (Generate auto-switch):
  - When auto-switching to GENERATE mode
  - Hides idle/chat sections
  - Shows generate section

### 5. Event Handler Updates
Updated all mode-related event handlers to include visibility outputs:

```python
# Mode radio change
mode_radio.change(
    handle_mode_change,
    [mode_radio],
    [mode_status, smart_suggestion, mode_status_banner, mode_tip,
     idle_section, chat_section, generate_section, current_mode_state]
)

# Chat messages
msg.submit(...).then(
    bot_message,
    [...],
    [..., idle_section, chat_section, generate_section, current_mode_state]
)

# Generate button
generate_btn.click(
    generate_and_store,
    [...],
    [..., idle_section, chat_section, generate_section, current_mode_state]
)
```

## Behavior

### IDLE MODE
**Shows:**
- Mode Control section (mode buttons + status + banner + tip)
- Welcome card with instructions

**Hides:**
- All chat UI
- All generation UI

### CHAT MODE
**Shows:**
- Mode Control section (mode buttons + status + banner + tip)
- Chat interface (Text Chat + Vision Chat tabs)
- Chat history accordion
- Model selection

**Hides:**
- Welcome card
- All generation UI

### GENERATE MODE
**Shows:**
- Mode Control section (mode buttons + status + banner + tip)
- Current Prompt field
- Quick Presets buttons
- Generated Image preview
- Image action buttons
- All generation settings (in accordions)
- Batch queue
- Stats

**Hides:**
- Welcome card
- All chat UI

### Gallery
- Gallery button always visible in header
- Opens as modal/overlay on any mode
- Can be opened from any mode without switching modes
- Separate from mode-specific UI

## Benefits

1. **No Vertical Scrolling**: Only relevant UI is visible
2. **Cleaner Interface**: Focused on current task
3. **Better UX**: Less visual clutter
4. **Faster Workflow**: No need to scroll to find controls
5. **Maintains All Features**: Nothing removed, just hidden when not needed
6. **Seamless Mode Switching**: UI updates automatically with mode changes

## Testing

To test the implementation:

1. **Start in IDLE mode:**
   - Should see welcome message only
   - No chat or generation UI visible

2. **Switch to CHAT mode:**
   - Welcome message disappears
   - Chat interface appears
   - Generation UI remains hidden

3. **Switch to GENERATE mode:**
   - Chat UI disappears
   - Generation panel appears with all controls

4. **Auto-switching:**
   - Send a chat message → Auto-switches to Chat + shows chat UI
   - Click generate → Auto-switches to Generate + shows generation UI

5. **Gallery:**
   - Click Gallery button from any mode
   - Modal opens without affecting mode
   - Select image → Switches to Chat mode + shows chat UI

## Files Modified

- `/home/ant/ai-image-chat/app.py`:
  - Added `current_mode_state` state variable
  - Restructured main interface into 3 mode-specific sections
  - Updated `handle_mode_change()` to control visibility
  - Updated `bot_message()` auto-switch to control visibility
  - Updated `generate_and_store()` auto-switch to control visibility
  - Updated all event handlers to include visibility outputs

## Backward Compatibility

✅ All existing functionality preserved
✅ No breaking changes
✅ All features still accessible
✅ Auto-switching still works
✅ Gallery still works as modal

## Next Steps

None required - implementation is complete and ready for use!

The UI now provides a focused, clutter-free experience that shows only what's needed for the current task.
