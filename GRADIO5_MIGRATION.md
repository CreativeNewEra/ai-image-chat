# Gradio 5 Migration Guide

**Date:** 2025-10-01
**Upgrade:** Gradio 4.44.1 → 5.48.0

---

## Summary of Changes

The app has been upgraded from Gradio 4 to Gradio 5. This required changes to the chatbot message format.

### Key API Changes

**1. Chatbot Message Format**

Gradio 5 changed from tuple-based messages to dictionary-based messages:

```python
# OLD (Gradio 4): Tuple format
chatbot = gr.Chatbot(type="tuples")
history = [
    ["user message", "assistant response"],
    ["another user message", "another response"]
]

# NEW (Gradio 5): Messages format
chatbot = gr.Chatbot(type="messages")
history = [
    {"role": "user", "content": "user message"},
    {"role": "assistant", "content": "assistant response"},
    {"role": "user", "content": "another user message"},
    {"role": "assistant", "content": "another response"}
]
```

---

## Files Modified

### 1. `ui/components/chat_interface.py`

**Changed chatbot type parameter:**

```python
# Line 82
chatbot = gr.Chatbot(type="messages")  # Was: type="tuples"

# Line 103
vision_chatbot = gr.Chatbot(type="messages")  # Was: type="tuples"
```

### 2. `app.py` - Chat Handler Functions

**Updated message processing to handle both formats:**

```python
def chat_with_ollama(message, history, model_choice, current_prompt):
    """Send message to Ollama and get response"""

    # Build message history
    # Gradio 5 uses 'messages' format with 'role' and 'content' keys
    messages = []
    for h in history:
        # History is already in messages format: {"role": "user/assistant", "content": "..."}
        if isinstance(h, dict) and "role" in h and "content" in h:
            messages.append(h)
        # Fallback for old tuple format (backwards compatibility)
        elif isinstance(h, (list, tuple)) and len(h) >= 2:
            messages.append({"role": "user", "content": h[0]})
            if h[1]:
                messages.append({"role": "assistant", "content": h[1]})

    # Add current message
    messages.append({"role": "user", "content": message})
    # ... rest of function
```

**Same changes applied to:**
- `chat_with_ollama()` (line 95)
- `vision_chat_with_ollama()` (line 144)

### 3. `app.py` - UI Helper Functions

**Updated user message and bot message helpers:**

```python
# Line 1074
def user_message(message, history):
    # Gradio 5 messages format: {"role": "user/assistant", "content": "..."}
    return "", history + [{"role": "user", "content": message}]

# Line 1078
def bot_message(history, model, current_prompt):
    # Gradio 5 messages format
    if not history or not history[-1].get("content"):
        return history, current_prompt, "", False

    message = history[-1]["content"]
    response = chat_with_ollama(message, history[:-1], model, current_prompt)
    # Update last message to include assistant response
    history[-1] = {"role": "user", "content": message}
    history.append({"role": "assistant", "content": response})
    # ... rest of function
```

**Same changes applied to:**
- `user_message()` (line 1074)
- `bot_message()` (line 1078)
- `vision_user_message()` (line 1136)
- `vision_bot_message()` (line 1140)

### 4. `requirements.txt`

**Updated version pins:**

```
gradio==5.48.0  # Was: 4.44.1
```

---

## Backwards Compatibility

The code maintains backwards compatibility by checking the message format:

```python
if isinstance(h, dict) and "role" in h and "content" in h:
    # Gradio 5 format
    messages.append(h)
elif isinstance(h, (list, tuple)) and len(h) >= 2:
    # Gradio 4 format (fallback)
    messages.append({"role": "user", "content": h[0]})
    if h[1]:
        messages.append({"role": "assistant", "content": h[1]})
```

This ensures the app works even if there's cached data in the old format.

---

## Testing Checklist

After the migration, test:

- [ ] **Mode switching** - All mode buttons work
- [ ] **Text chat** - Can send messages and receive responses
- [ ] **Vision chat** - Can send messages with images
- [ ] **Chat history** - Previous messages display correctly
- [ ] **Prompt extraction** - Prompts extracted from chat responses
- [ ] **Clear chat** - Clear button empties chat history
- [ ] **Model switching** - Can change chat models
- [ ] **All other buttons** - Generate, presets, etc.

---

## Benefits of Gradio 5

✅ **Fixed TypeError bug** - No more JSON schema errors
✅ **Better message format** - More explicit role-based messages
✅ **Improved performance** - Gradio 5 is faster and more stable
✅ **New features** - Access to latest Gradio capabilities
✅ **Future-proof** - Ready for future Gradio updates

---

## Rollback Instructions

If you need to roll back to Gradio 4:

```bash
# 1. Downgrade Gradio
pip install gradio==4.44.1

# 2. Revert chatbot type in ui/components/chat_interface.py
# Change type="messages" back to type="tuples"

# 3. Revert message format handlers in app.py
# Use the old h[0] and h[1] tuple access instead of h["content"]
```

However, rolling back is **not recommended** as it will bring back the TypeError bug.

---

## Troubleshooting

### Issue: Buttons don't work

**Cause:** Message format mismatch between chatbot type and handlers

**Solution:** Ensure all of these use the **same** format:
1. `ui/components/chat_interface.py` - `type="messages"`
2. `app.py` chat handlers - Check for `h.get("content")` not `h[0]`
3. `app.py` user/bot message functions - Return/use dict format

### Issue: Chat history displays incorrectly

**Cause:** Old cached history in tuple format

**Solution:** Clear the chat and start fresh, or add backwards compatibility checks (already implemented)

---

## Known Issues

### Keyboard Shortcuts Disabled

**Issue:** External JavaScript modules cannot be loaded in Gradio 5 using the `/file=` path

**Root Cause:** Gradio 5 changed how static files are served. The previous method:
```python
js="import('/file=static/js/main.js');"
```
Now causes a JavaScript syntax error in Gradio's generated code.

**Current Workaround:** Keyboard shortcuts are **disabled** until a Gradio 5-compatible solution is found.

**Future Fix Options:**
1. Use Gradio's `.load()` event to inject JavaScript
2. Use inline JavaScript (not recommended for maintainability)
3. Wait for Gradio to provide official static file serving API
4. Use a custom FastAPI route to serve static files

**Impact:** Low - keyboard shortcuts are a convenience feature. All core functionality works via mouse clicks.

---

## Additional Resources

- [Gradio 5 Release Notes](https://github.com/gradio-app/gradio/releases)
- [Gradio Chatbot Documentation](https://gradio.app/docs/chatbot)
- [Gradio Static Files Issue](https://github.com/gradio-app/gradio/issues)
- Project TROUBLESHOOTING.md

---

**Migration completed:** 2025-10-01
**Status:** ✅ All core features working
**Known Issue:** ⚠️ Keyboard shortcuts disabled (Gradio 5 static file serving)
