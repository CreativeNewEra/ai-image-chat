# 🔧 Phase 3 Troubleshooting Guide

**Multiple Workflow Support - Common Issues & Solutions**

---

## 🚀 Quick Start Testing

### Step 1: Start the App

```bash
cd ~/ai-image-chat
python app.py
```

**Expected Output:**
```
============================================================
AI IMAGE CHAT - Phase 2 (Vision Chat)
============================================================
User: ant
Hostname: nobara-laptop
ComfyUI: http://localhost:8188/api
Ollama: http://localhost:11434/api
...
Loading workflows from workflows
✓ Loaded workflow: FLUX Krea Text2Image
Loaded 1 workflows
✓ Switched to workflow: FLUX Krea Text2Image
Auto-selected first workflow: FLUX Krea Text2Image
```

### Step 2: Open in Browser

- **Laptop:** http://localhost:7860
- **Desktop:** http://192.168.1.175:7860

---

## ❌ Common Issues

### Issue #1: "No module named 'websocket'"

**Symptom:**
```
ModuleNotFoundError: No module named 'websocket'
```

**Solution:**
```bash
pip install websocket-client
```

Or reinstall all dependencies:
```bash
pip install -r requirements.txt
```

---

### Issue #2: "Loading workflows from workflows - Loaded 0 workflows"

**Symptom:**
```
Loading workflows from workflows
Loaded 0 workflows
```

**Cause:** Workflow directory is empty or doesn't exist

**Solution:**

1. **Check if workflow exists:**
```bash
ls -la workflows/text2img/
# Should show: flux_krea_text2img.json and flux_krea_text2img_meta.json
```

2. **If missing, restore the shipped workflow files:**
```bash
git checkout -- workflows/text2img/flux_krea_text2img.json \
    workflows/text2img/flux_krea_text2img_meta.json
```

   > Migrating an older manual setup? Copy your legacy `flux1_krea_dev.json` into `workflows/text2img/` and rename it to `flux_krea_text2img.json` so the workflow manager can detect it.

3. **Create metadata file:**
```bash
cat > workflows/text2img/flux_krea_text2img_meta.json << 'EOF'
{
  "name": "FLUX Krea Text2Image",
  "description": "Default FLUX text-to-image workflow with Krea optimizations",
  "category": "Text2Image",
  "tags": ["flux", "text2img", "krea", "default"],
  "author": "ant",
  "created_at": "2025-09-30T12:00:00",
  "modified_at": "2025-09-30T12:00:00"
}
EOF
```

4. **Restart the app**

---

### Issue #3: Workflow Selector UI Not Visible

**Symptom:** Can't find the "🔀 Workflow Selector" accordion

**Solution:**

1. Make sure you're in **Generate Mode** (click 🎨 Generate button)
2. Scroll down past the prompt textbox
3. Look for the "🔀 Workflow Selector" accordion (it's collapsed by default)
4. Click to expand it

**Location:**
```
[Mode buttons]
[Prompt textbox]
[Presets: Fast/Balanced/Quality/Ultra]
[🔀 Workflow Selector] ← HERE (click to expand)
[⚙️ Generation Settings]
```

---

### Issue #4: "Failed to load workflow"

**Symptom:**
When generating: "❌ Failed to load workflow"

**Possible Causes:**

1. **No workflow selected**
   - Check if workflow dropdown shows a workflow
   - If blank, select one from dropdown
   - Or click "🔄 Refresh" button

2. **Corrupted workflow JSON**
   - Check terminal for JSON parse errors
   - Validate JSON: `python -m json.tool workflows/text2img/flux_krea_text2img.json`

3. **Missing workflow file**
   - Verify file exists: `ls workflows/text2img/flux_krea_text2img.json`

**Solution:**
```bash
# Restore the workflow files shipped with the repo
git checkout -- workflows/text2img/flux_krea_text2img.json \
    workflows/text2img/flux_krea_text2img_meta.json

# Restart app
```

> Only fall back to copying a legacy `flux1_krea_dev.json` into `workflows/text2img/flux_krea_text2img.json` if you're migrating from an older manual setup that doesn't have the new directory layout.

---

### Issue #5: Workflow Dropdown is Empty

**Symptom:** Workflow dropdown shows no options

**Debug Steps:**

1. **Check terminal output:**
```bash
# Look for this on startup:
Loading workflows from workflows
✓ Loaded workflow: FLUX Krea Text2Image
Loaded 1 workflows
```

2. **If shows "Loaded 0 workflows":**
```bash
# Check directory structure
ls -R workflows/

# Should show:
workflows/text2img/flux_krea_text2img.json
workflows/text2img/flux_krea_text2img_meta.json
```

3. **Click "🔄 Refresh" button** in Workflow Selector

4. **Check for Python errors** in terminal

**Solution:**
See Issue #2 above for recreating workflow files

---

### Issue #6: Import Workflow Fails

**Symptom:** Clicking "📥 Import Workflow" shows error

**Common Causes:**

1. **No file selected**
   - Click "Choose File" first
   - Select a .json file
   - Then click "📥 Import Workflow"

2. **Invalid JSON file**
   - Make sure it's a ComfyUI workflow JSON
   - Not a random JSON file

3. **Permissions error**
   - Check write permissions: `ls -ld workflows/custom/`
   - Should be writable: `chmod 755 workflows/custom/`

**Solution:**
```bash
# Ensure custom directory exists and is writable
mkdir -p workflows/custom
chmod 755 workflows/custom

# Test with a valid workflow file
cp workflows/text2img/flux_krea_text2img.json /tmp/test_workflow.json
# Then import /tmp/test_workflow.json via UI
```

---

### Issue #7: Generation Fails After Switching Workflow

**Symptom:** Image generation works with default workflow, fails after switching

**Possible Causes:**

1. **Incompatible workflow format**
   - Not all ComfyUI workflows are compatible
   - Workflow must have compatible nodes

2. **Missing models in workflow**
   - Workflow references models you don't have
   - Check ComfyUI terminal for "Model not found" errors

3. **Workflow needs different parameters**
   - Some workflows need different dimensions
   - Some need specific CFG values

**Debug:**
```bash
# Check ComfyUI terminal when generation fails
# Look for errors like:
# - "Model not found: xyz.safetensors"
# - "Node not found: XYZ"
# - "Invalid input for node ABC"
```

**Solution:**
1. Switch back to default workflow
2. If using custom workflow, verify it works in ComfyUI directly first
3. Check workflow metadata for required models/nodes

---

### Issue #8: Export Workflow Creates File But Can't Find It

**Symptom:** Click "📤 Export Current" - says success but can't find file

**Location:** Exported files are saved in the app directory

```bash
# Find exported workflows
ls -la exported_*.json

# They're in the same directory where you ran the app
pwd  # Shows current directory
```

**Solution:**
Export path is `./exported_[workflow_filename].json` in the current directory

---

## 🔍 Advanced Debugging

### Check Workflow Manager State

Add this to test workflow manager:

```bash
python test_workflow_manager.py
```

**Expected Output:**
```
✅ Workflow Manager test passed!
```

### Check All Components

```bash
python test_comprehensive.py
```

**Expected Output:**
```
✅ Passed: 6/7
```

(websocket import failure is OK if you haven't installed it)

### Verify Workflow JSON Structure

```bash
# Validate workflow JSON
python -m json.tool workflows/text2img/flux_krea_text2img.json > /dev/null
echo $?
# Should output: 0 (success)

# Check metadata
cat workflows/text2img/flux_krea_text2img_meta.json
```

### Check App Imports

```python
# Run this to test imports
python -c "from core import WorkflowManager; print('✅ WorkflowManager imported')"
python -c "from app import workflow_manager; print(f'✅ Workflows: {workflow_manager.get_workflow_count()}')"
```

---

## 🐛 Debugging Tips

### Enable Verbose Logging

Add this to top of `app.py` after imports:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Workflow Loading

Look for these log messages on startup:
```
INFO - Loading workflows from workflows
INFO - ✓ Loaded workflow: [name]
INFO - Loaded N workflows
INFO - ✓ Switched to workflow: [name]
```

### Test Workflow Manager Separately

```python
# Test in Python REPL
python

>>> from core import WorkflowManager
>>> wf = WorkflowManager()
>>> print(f"Loaded: {wf.get_workflow_count()}")
>>> print(wf.get_workflows_list())
>>> current = wf.get_current_workflow()
>>> print(current.metadata.name if current else "None")
```

### Check ComfyUI Connection

If generation fails:
```bash
# Test ComfyUI is running
curl http://localhost:8188/system_stats

# Should return JSON with system stats
# If "Connection refused" - start ComfyUI first
```

---

## 📋 Verification Checklist

Use this to verify everything works:

### Basic Workflow Management
- [ ] App starts without errors
- [ ] Terminal shows "Loaded 1 workflows" (or more)
- [ ] Workflow Selector accordion exists
- [ ] Dropdown shows at least one workflow
- [ ] Workflow info displays when selected
- [ ] "🔄 Refresh" button works

### Workflow Operations
- [ ] Can switch between workflows (if multiple exist)
- [ ] Can filter by category
- [ ] Can import a workflow file
- [ ] Can export current workflow
- [ ] Imported workflow appears in dropdown

### Generation Integration
- [ ] Can generate image with default workflow
- [ ] Can generate after switching workflows
- [ ] Terminal shows "Using workflow: [name]"
- [ ] Images still save to gallery
- [ ] All Phase 2.5 features still work

### Batch Queue Integration
- [ ] Can add jobs to queue
- [ ] Queue works with workflow manager
- [ ] Processing jobs uses selected workflow

---

## 🆘 Still Having Issues?

### Collect Debug Info

```bash
# 1. Check Python version
python --version
# Should be 3.10+

# 2. Check dependencies
pip list | grep -E "gradio|PIL|requests|websocket"

# 3. Check file structure
tree workflows/
# or
find workflows/ -type f

# 4. Check app.py syntax
python -m py_compile app.py
echo $?
# Should output: 0

# 5. Run tests
python test_comprehensive.py 2>&1 | tail -20
```

### Get Detailed Error

Run app with full error output:
```bash
python app.py 2>&1 | tee app_debug.log
```

Then check `app_debug.log` for errors

### Reset to Working State

If everything is broken:

```bash
# 1. Backup current state
cp -r workflows workflows_backup

# 2. Recreate workflow directory
rm -rf workflows
mkdir -p workflows/text2img workflows/img2img

# 3. Restore default workflows shipped with repo
git checkout -- workflows/text2img/flux_krea_text2img.json \
    workflows/text2img/flux_krea_text2img_meta.json \
    workflows/img2img/flux_img2img.json \
    workflows/img2img/flux_img2img_meta.json

# 4. (Optional) Recreate metadata manually if git checkout is unavailable
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

# 5. Restart app
python app.py
```

> Legacy setups: if you only have `flux1_krea_dev.json`, place it in `workflows/text2img/` as `flux_krea_text2img.json` after running the steps above so the workflow manager can load it.

---

## 📞 Getting Help

If you're still stuck:

1. **Check terminal output** - Most issues show clear error messages
2. **Check ComfyUI terminal** - For generation-related errors
3. **Run test scripts** - `test_comprehensive.py` and `test_workflow_manager.py`
4. **Check file permissions** - Especially `workflows/` directory
5. **Verify workflow JSON** - Use `python -m json.tool` to validate

### Useful Commands

```bash
# Restart from clean state
pkill -f "python app.py"
python app.py

# Check what's running
ps aux | grep python

# Check ports
netstat -tlnp | grep -E "7860|8188|11434"

# Check VRAM
nvidia-smi
```

---

## ✅ Success Indicators

You'll know everything works when you see:

**In Terminal:**
```
✓ Loaded workflow: FLUX Krea Text2Image
Loaded 1 workflows
✓ Switched to workflow: FLUX Krea Text2Image
Auto-selected first workflow: FLUX Krea Text2Image
Running on local URL:  http://0.0.0.0:7860
```

**In Browser:**
- Workflow Selector accordion exists and expands
- Dropdown shows "FLUX Krea Text2Image"
- Workflow info shows complete metadata
- Can generate images successfully
- All Phase 2.5 features work

---

**Last Updated:** 2025-09-30
**Applies to:** Phase 3 - Multiple Workflow Support
