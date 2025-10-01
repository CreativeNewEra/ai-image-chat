# 🔘 Button Not Working? - Debug Checklist

**⚠️ 99% of button issues are caused by the keyboard shortcuts JavaScript!**

---

## ✅ Quick Fix (Do This First!)

### Step 1: Disable JavaScript
Edit `app.py` around line 381:

```python
with gr.Blocks(
    theme=gr.themes.Soft(primary_hue="blue"),
    title="AI Image Chat",
    # js=keyboard_js,  # ← COMMENT OUT THIS LINE
    css="""
```

### Step 2: Restart the app
```bash
# Stop the app (Ctrl+C)
python app.py
```

### Step 3: Test buttons
Click any button - it should work now!

---

## If Still Not Working...

### Check 1: Syntax Errors
```bash
python -m py_compile app.py
```

### Check 2: Event Handler Outputs
Look for this pattern in app.py:
```python
button.click(my_function, inputs, [output1, output2])
#                                   ↑ Must match number of return values
```

### Check 3: Terminal Output
- Look for `DEBUG: ...btn wired` messages
- Check for Python exceptions
- Look for traceback errors

### Check 4: Create Minimal Test
Run the test app to verify Gradio works:
```bash
python test_buttons.py
```

---

## Why This Happens

The custom JavaScript for keyboard shortcuts (`keyboard_js`) uses `preventDefault()` which blocks all click events, including button clicks.

**Permanent Fix Needed:**
- Refactor JavaScript to use `stopPropagation()` instead
- Or use Gradio's built-in event system
- See TROUBLESHOOTING.md Issue #1 for details

---

## Quick Reference

| Problem | Solution |
|---------|----------|
| No buttons work | Disable `js=keyboard_js` |
| Some buttons work | Check event handler returns |
| Error in terminal | Fix Python syntax/logic |
| Mode switching fails | Check Ollama/ComfyUI running |

---

**See TROUBLESHOOTING.md for complete details**
