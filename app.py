"""
AI Image Chat - Main Application
Phase 2: Text Chat + Vision Chat + ComfyUI Generation with Mode Switching
"""

import logging
import random
import time
from datetime import datetime

import gradio as gr
import requests

from comfyui_api import comfy

# Local imports
from config import *
from core import (
    GenerationQueue,
    ImageGallery,
    JobStatus,
    Mode,
    ModeManager,
    PromptHistory,
    SeedManager,
    SessionStats,
    SmartSwitchManager,
    VRAMEstimator,
    VRAMMonitor,
    WorkflowManager,
)
from utils import pil_to_base64

# Get logger for this module
logger = logging.getLogger(__name__)

# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

# Initialize all core components
vram_monitor = VRAMMonitor()
session_stats = SessionStats()
vram_estimator = VRAMEstimator()
seed_manager = SeedManager()
prompt_history = PromptHistory(PROMPT_HISTORY_FILE)
smart_switch = SmartSwitchManager()
gallery = ImageGallery()
gen_queue = GenerationQueue()
workflow_manager = WorkflowManager()

# Set first workflow as current if none selected
if not workflow_manager.get_current_workflow() and workflow_manager.get_workflow_count() > 0:
    first_workflow = list(workflow_manager.workflows.keys())[0]
    workflow_manager.set_current_workflow(first_workflow)
    logger.info(
        f"Auto-selected first workflow: {workflow_manager.get_current_workflow().metadata.name}"
    )

# Mode manager needs vram_monitor and comfy
mode_manager = ModeManager(vram_monitor, comfy)

# ============================================================================
# OLLAMA CHAT
# ============================================================================


def get_available_models():
    """Get list of Ollama models"""
    try:
        response = requests.get(f"{OLLAMA_API.replace('/api', '')}/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [model["name"] for model in models]
    except:
        pass
    return [OLLAMA_CHAT_MODEL, "mistral:7b", "mistral-small3.2:latest"]


def chat_with_ollama(message, history, model_choice, current_prompt):
    """Send message to Ollama and get response"""

    if mode_manager.get_mode() != Mode.CHAT:
        return "⚠️ Please switch to Text Chat Mode first!"

    try:
        # Build message history
        messages = []
        for h in history:
            messages.append({"role": "user", "content": h[0]})
            if h[1]:
                messages.append({"role": "assistant", "content": h[1]})

        # Add current message
        messages.append({"role": "user", "content": message})

        # Add context about current prompt
        context = ""
        if current_prompt:
            context = f"\n\nCurrent working prompt: '{current_prompt}'\n"

        # Call Ollama
        response = requests.post(
            f"{OLLAMA_API}/chat",
            json={
                "model": model_choice,
                "messages": [{"role": "system", "content": SYSTEM_PROMPT + context}] + messages,
                "stream": False,
                "keep_alive": "5m",
            },
            timeout=60,
        )

        if response.status_code == 200:
            return response.json()["message"]["content"]
        else:
            return f"Error: {response.status_code}"

    except Exception as e:
        return f"Error: {str(e)}"


def vision_chat_with_ollama(message, history, current_image, current_prompt):
    """Send message with image to Ollama vision model and get response"""

    if mode_manager.get_mode() != Mode.VISION:
        return "⚠️ Please switch to Vision Chat Mode first!"

    if current_image is None:
        return "⚠️ No image loaded! Generate an image first, then switch to Vision Chat mode."

    try:
        # Convert image to base64
        image_base64 = pil_to_base64(current_image)
        if not image_base64:
            return "⚠️ Failed to process image"

        # Build message history (text only for history)
        messages = []
        for h in history:
            messages.append({"role": "user", "content": h[0]})
            if h[1]:
                messages.append({"role": "assistant", "content": h[1]})

        # Add current message with image
        messages.append({"role": "user", "content": message, "images": [image_base64]})

        # Add context about current prompt
        context = ""
        if current_prompt:
            context = f"\n\nCurrent image generation prompt: '{current_prompt}'\n"

        # Call Ollama with vision model
        response = requests.post(
            f"{OLLAMA_API}/chat",
            json={
                "model": OLLAMA_VISION_MODEL,
                "messages": [{"role": "system", "content": VISION_SYSTEM_PROMPT + context}]
                + messages,
                "stream": False,
                "keep_alive": "5m",
            },
            timeout=120,  # Vision models may take longer
        )

        if response.status_code == 200:
            return response.json()["message"]["content"]
        else:
            return f"Error: {response.status_code}"

    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================================
# IMAGE GENERATION
# ============================================================================


def check_vram_warnings(steps, width, height):
    """Check VRAM warnings and return display markdown"""
    vram_info = vram_monitor.get_vram_usage()
    current_used = vram_info["used_gb"]
    total_vram = vram_info["total_gb"]

    warning_level, warning_msg = vram_estimator.get_warnings(
        width, height, steps, current_used, total_vram
    )

    # Return tuple: (markdown_text, visible_boolean)
    if warning_level == "none":
        return "", False
    elif warning_level == "info":
        return f"ℹ️ {warning_msg}", True
    elif warning_level == "warning":
        return f"⚠️ {warning_msg}", True
    elif warning_level == "error":
        return f"🚨 {warning_msg}", True
    else:
        return "", False


def generate_image(
    prompt_text, steps, width, height, seed_value, denoise=1.0, input_image_path=None
):
    """Generate image via ComfyUI (text2img or img2img)

    Args:
        prompt_text: The text prompt
        steps: Number of sampling steps
        width: Image width (text2img only)
        height: Image height (text2img only)
        seed_value: Random seed value as string
        denoise: Denoising strength (0.0-1.0, for img2img)
        input_image_path: Path to input image (for img2img, None for text2img)

    Returns:
        tuple: (image, status, actual_seed, stats_display)
    """

    if mode_manager.get_mode() != Mode.GENERATE:
        return None, "⚠️ Please switch to Generation Mode first!", None, None

    # Validate prompt
    if not prompt_text or len(prompt_text) < MIN_PROMPT_LENGTH:
        return (
            None,
            f"⚠️ Please provide a prompt (at least {MIN_PROMPT_LENGTH} characters)",
            None,
            None,
        )

    # Validate width/height only for text2img
    if not input_image_path:
        if not (MIN_WIDTH <= width <= MAX_WIDTH):
            return None, f"❌ Width must be between {MIN_WIDTH} and {MAX_WIDTH} pixels", None, None
        if not (MIN_HEIGHT <= height <= MAX_HEIGHT):
            return (
                None,
                f"❌ Height must be between {MIN_HEIGHT} and {MAX_HEIGHT} pixels",
                None,
                None,
            )

    # Validate steps
    if not (MIN_STEPS <= steps <= MAX_STEPS):
        return None, f"❌ Steps must be between {MIN_STEPS} and {MAX_STEPS}", None, None

    # Log mode
    mode_str = "img2img" if input_image_path else "text2img"
    logger.info(f"Generating image ({mode_str}): {width}x{height}, {steps} steps")
    if input_image_path:
        logger.info(f"Input image: {input_image_path}, denoise: {denoise}")

    # Load current workflow from manager
    current_workflow = workflow_manager.get_current_workflow()
    if current_workflow:
        logger.info(f"Using workflow: {current_workflow.metadata.name}")
        # Load workflow data into ComfyUI bridge
        if not comfy.load_workflow_from_data(current_workflow.workflow_data):
            return None, "❌ Failed to load workflow", None, None
    else:
        # Fallback to default workflow file
        logger.warning("No workflow selected, using default from file")
        if not comfy.load_workflow():
            return None, "❌ Failed to load default workflow", None, None

    # Parse seed
    seed = None
    if seed_value and seed_value.strip():
        try:
            seed = int(seed_value)
        except ValueError:
            logger.warning(f"Invalid seed input '{seed_value}'; using managed default")
            seed = None

    # Check if seed is locked
    seed = seed_manager.get_seed_for_generation(seed)

    # Track generation time
    start_time = time.time()

    # Generate
    image, status, actual_seed = comfy.generate_image(
        prompt_text=prompt_text,
        steps=steps,
        width=width,
        height=height,
        seed=seed,
        denoise=denoise,
        input_image_path=input_image_path,
    )

    # Calculate generation time
    generation_time = time.time() - start_time

    # If generation succeeded, save to gallery and record stats
    if image is not None and actual_seed is not None:
        settings = {"width": width, "height": height, "steps": steps}

        gallery.add_image(image, prompt_text, actual_seed, settings)

        # Record generation stats
        session_stats.add_generation(generation_time)

        # Add seed to history
        seed_manager.add_seed(actual_seed)

        # Add prompt to history
        prompt_history.add_prompt(prompt_text, settings)

        # Return seed info and time in status
        lock_status = " 🔒 LOCKED" if seed_manager.is_locked else ""
        status = (
            f"{status}\n\nSeed: {actual_seed}{lock_status} | Time: {round(generation_time, 1)}s"
        )

    # Return stats display as 4th value
    stats_display = session_stats.get_stats_display()

    return image, status, actual_seed, stats_display


# ============================================================================
# BATCH GENERATION QUEUE
# ============================================================================


def add_to_queue(prompt_text, steps, width, height, seed_value):
    """Add current settings to generation queue"""
    if not prompt_text or len(prompt_text) < MIN_PROMPT_LENGTH:
        return (
            f"⚠️ Please provide a prompt (at least {MIN_PROMPT_LENGTH} characters)",
            gen_queue.get_queue_display(),
        )

    # Parse seed
    seed = -1  # -1 means random
    if seed_value and seed_value.strip():
        try:
            seed = int(seed_value)
        except ValueError:
            logger.warning(f"Invalid seed input '{seed_value}'; using random seed")
            seed = -1

    job_id = gen_queue.add_job(prompt_text, width, height, steps, seed)
    logger.info(f"Added job {job_id} to queue")

    return f"✅ Added to queue (Job #{job_id[-4:]})", gen_queue.get_queue_display()


def add_batch_variations(prompt_text, steps, width, height, seed_value, count=4):
    """Add batch of seed variations to queue"""
    if not prompt_text or len(prompt_text) < MIN_PROMPT_LENGTH:
        return (
            f"⚠️ Please provide a prompt (at least {MIN_PROMPT_LENGTH} characters)",
            gen_queue.get_queue_display(),
        )

    # Parse seed
    seed = None
    if seed_value and seed_value.strip():
        try:
            seed = int(seed_value)
        except ValueError:
            logger.warning(
                f"Invalid seed input '{seed_value}'; using history/random fallback"
            )
            seed = None

    # If no seed provided, use last seed from history or generate random
    if seed is None or seed == -1:
        history = seed_manager.get_history()
        if history:
            seed = history[0]  # Use most recent seed
        else:
            seed = random.randint(0, 2**32 - 1)

    job_ids = gen_queue.add_batch_variations(prompt_text, width, height, steps, seed, count)
    logger.info(f"Added {count} variation jobs to queue")

    return (
        f"✅ Added {count} seed variations to queue (seed {seed} +1, +2, +3...)",
        gen_queue.get_queue_display(),
    )


def process_queue():
    """Process all jobs in the queue"""
    if mode_manager.get_mode() != Mode.GENERATE:
        return (
            None,
            "⚠️ Please switch to Generation Mode first!",
            gen_queue.get_queue_display(),
            None,
        )

    next_job = gen_queue.get_next_job()
    if not next_job:
        return None, "Queue is empty", gen_queue.get_queue_display(), None

    # Mark as processing
    next_job.status = JobStatus.PROCESSING
    gen_queue.current_job = next_job
    next_job.started_at = datetime.now()

    logger.info(f"Processing job {next_job.id}: {next_job.prompt[:50]}...")

    # Track generation time
    start_time = time.time()

    # Generate
    image, status, actual_seed = comfy.generate_image(
        prompt_text=next_job.prompt,
        steps=next_job.steps,
        width=next_job.width,
        height=next_job.height,
        seed=next_job.seed if next_job.seed != -1 else None,
    )

    generation_time = time.time() - start_time

    # Update job status
    next_job.completed_at = datetime.now()

    if image is not None and actual_seed is not None:
        # Success
        next_job.status = JobStatus.COMPLETED
        next_job.result_image = image
        next_job.result_seed = actual_seed

        # Save to gallery
        settings = {"width": next_job.width, "height": next_job.height, "steps": next_job.steps}
        gallery.add_image(image, next_job.prompt, actual_seed, settings)

        # Record stats
        session_stats.add_generation(generation_time)
        seed_manager.add_seed(actual_seed)
        prompt_history.add_prompt(next_job.prompt, settings)

        status = f"✅ Job completed\nSeed: {actual_seed} | Time: {round(generation_time, 1)}s\n{gen_queue.get_queue_display()}"
    else:
        # Failed
        next_job.status = JobStatus.FAILED
        next_job.error_message = status
        status = f"❌ Job failed: {status}\n{gen_queue.get_queue_display()}"

    gen_queue.current_job = None
    stats_display = session_stats.get_stats_display()

    return image, status, gen_queue.get_queue_display(), stats_display


def clear_queue():
    """Clear all completed jobs from queue"""
    gen_queue.clear_completed()
    return gen_queue.get_queue_display()


def cancel_all_queue():
    """Cancel all pending jobs"""
    gen_queue.clear_all()
    return gen_queue.get_queue_display()


# ============================================================================
# GRADIO INTERFACE
# ============================================================================


def create_app():
    """Create Gradio UI"""

    # JavaScript for toast notifications and keyboard shortcuts
    custom_js = """
    // Toast Notification System
    function showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const icon = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }[type] || 'ℹ️';

        toast.innerHTML = `<span class="toast-icon">${icon}</span><span class="toast-message">${message}</span>`;

        const container = document.getElementById('toast-container') || createToastContainer();
        container.appendChild(toast);

        // Trigger animation
        setTimeout(() => toast.classList.add('toast-show'), 10);

        // Auto remove
        setTimeout(() => {
            toast.classList.remove('toast-show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    function createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
        return container;
    }

    // Make showToast available globally
    window.showToast = showToast;

    // Keyboard shortcuts (disabled but kept for future)
    function setupKeyboardShortcuts() {
        // Helper function to find button by text content
        function findButtonByText(text) {
            const buttons = Array.from(document.querySelectorAll('button'));
            return buttons.find(btn => btn.textContent.includes(text));
        }

        document.addEventListener('keydown', function(e) {
            // Don't trigger if user is typing in an input/textarea
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                // Allow Ctrl+Enter in textareas to submit
                if (e.ctrlKey && e.key === 'Enter') {
                    e.preventDefault();
                    const sendBtn = findButtonByText('Send');
                    if (sendBtn) sendBtn.click();
                }
                return;
            }

            // Mode switching (Alt+key)
            if (e.altKey && !e.ctrlKey && !e.shiftKey) {
                let btn = null;
                switch(e.key.toLowerCase()) {
                    case 'i':
                        e.preventDefault();
                        btn = findButtonByText('🔵 Idle');
                        break;
                    case 'c':
                        e.preventDefault();
                        btn = findButtonByText('💬 Text Chat');
                        break;
                    case 'v':
                        e.preventDefault();
                        btn = findButtonByText('👁️ Vision Chat');
                        break;
                    case 'g':
                        e.preventDefault();
                        btn = findButtonByText('🎨 Generate');
                        break;
                }
                if (btn) btn.click();
            }

            // Actions (Ctrl+key)
            if (e.ctrlKey && !e.altKey && !e.shiftKey) {
                let btn = null;
                switch(e.key.toLowerCase()) {
                    case 'g':
                        e.preventDefault();
                        btn = findButtonByText('🎨 Generate Image');
                        break;
                    case 'k':
                        e.preventDefault();
                        btn = findButtonByText('📋 Copy Prompt');
                        break;
                    case 'l':
                        e.preventDefault();
                        btn = findButtonByText('🔄 Use Last');
                        break;
                    case '1':
                        e.preventDefault();
                        btn = findButtonByText('⚡ Fast Draft');
                        break;
                    case '2':
                        e.preventDefault();
                        btn = findButtonByText('⚖️ Balanced');
                        break;
                    case '3':
                        e.preventDefault();
                        btn = findButtonByText('✨ High Quality');
                        break;
                    case '4':
                        e.preventDefault();
                        btn = findButtonByText('🔥 Ultra Detail');
                        break;
                }
                if (btn) btn.click();
            }

            // Clear chat (Ctrl+Shift+C)
            if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'c') {
                e.preventDefault();
                const btn = findButtonByText('🗑️ Clear Chat');
                if (btn) btn.click();
            }

            // Show help (? or Shift+/)
            if (e.key === '?' || (e.shiftKey && e.key === '/')) {
                e.preventDefault();
                const btn = findButtonByText('⌨️ Shortcuts');
                if (btn) btn.click();
            }
        });
    }

    // Run setup when page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupKeyboardShortcuts);
    } else {
        setupKeyboardShortcuts();
    }
    """

    with gr.Blocks(
        theme=gr.themes.Soft(primary_hue="blue"),
        title="AI Image Chat",
        js=custom_js,  # Toast notifications enabled!
        css="""
        /* Mode Status Card */
        .mode-status {
            padding: 20px;
            border-radius: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-size: 16px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        /* Section Cards */
        .section-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            border: 1px solid #e5e7eb;
        }

        .section-header {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 16px;
            color: #1f2937;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Mode Switcher */
        .mode-switcher-container {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            border: 1px solid #e5e7eb;
        }

        .mode-radio-group .gr-radio {
            display: flex !important;
            flex-direction: row !important;
            gap: 12px !important;
        }

        .mode-radio-group label {
            background: #f3f4f6 !important;
            padding: 12px 20px !important;
            border-radius: 8px !important;
            border: 2px solid transparent !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            font-weight: 500 !important;
        }

        .mode-radio-group label:hover {
            background: #e5e7eb !important;
            transform: translateY(-1px);
        }

        .mode-radio-group input[type="radio"]:checked + label {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border-color: #667eea !important;
        }

        /* VRAM Display */
        .vram-display {
            font-family: 'Courier New', monospace;
            font-size: 14px;
            padding: 12px 16px;
            background: #f9fafb;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            margin-top: 12px;
        }

        /* Shortcuts Modal */
        .shortcuts-modal {
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            font-family: monospace;
        }

        /* Smart Suggestion */
        .smart-suggestion {
            padding: 15px;
            border-radius: 8px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            font-size: 14px;
            margin: 10px 0;
            box-shadow: 0 2px 6px rgba(240, 147, 251, 0.3);
        }

        /* Preset Cards */
        .preset-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            padding: 16px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 2px solid transparent;
        }

        .preset-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        /* Better Button Styling */
        .primary-action {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 12px 24px !important;
            border-radius: 8px !important;
            transition: all 0.2s ease !important;
        }

        .primary-action:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
        }

        /* Gallery Improvements */
        .gallery-controls {
            background: white;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        /* Toast Notifications */
        #toast-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 10px;
            pointer-events: none;
        }

        .toast {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            min-width: 300px;
            opacity: 0;
            transform: translateX(400px);
            transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            pointer-events: auto;
        }

        .toast-show {
            opacity: 1;
            transform: translateX(0);
        }

        .toast-icon {
            font-size: 20px;
            flex-shrink: 0;
        }

        .toast-message {
            font-size: 14px;
            font-weight: 500;
            color: #1f2937;
        }

        .toast-success {
            border-left: 4px solid #10b981;
        }

        .toast-error {
            border-left: 4px solid #ef4444;
        }

        .toast-warning {
            border-left: 4px solid #f59e0b;
        }

        .toast-info {
            border-left: 4px solid #3b82f6;
        }

        /* Progress Bar */
        .progress-container {
            width: 100%;
            height: 8px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 8px;
        }

        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
            border-radius: 4px;
        }

        .progress-bar.indeterminate {
            width: 30%;
            animation: indeterminate 1.5s infinite ease-in-out;
        }

        @keyframes indeterminate {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(400%); }
        }
        """,
    ) as app:

        # Header
        with gr.Row():
            with gr.Column(scale=4):
                gr.Markdown(
                    """
                # 🎨 AI Image Chat
                **Smart workflow for AI-assisted image generation**
                """
                )
            with gr.Column(scale=1):
                shortcuts_btn = gr.Button("⌨️ Shortcuts", size="sm")

        # State
        current_prompt_state = gr.State("")
        current_image_state = gr.State(None)

        # ====================================================================
        # MODE SELECTOR & STATUS
        # ====================================================================

        with gr.Row():
            with gr.Column(scale=3, elem_classes=["mode-switcher-container"]):
                gr.Markdown("### 🎛️ Mode Control")

                mode_radio = gr.Radio(
                    choices=["🔵 Idle", "💬 Text Chat", "👁️ Vision Chat", "🎨 Generate"],
                    value="🔵 Idle",
                    label="",
                    elem_classes=["mode-radio-group"],
                    interactive=True,
                )

                # Status and VRAM inline
                mode_status = gr.Markdown(
                    value=mode_manager._get_status_message(), elem_classes=["vram-display"]
                )

                with gr.Row():
                    check_status_btn = gr.Button("🔄 Refresh Status", size="sm", scale=1)
                    auto_switch_checkbox = gr.Checkbox(
                        value=True,
                        label="💡 Smart Suggestions",
                        info="Auto-suggest next steps",
                        scale=2,
                    )

        # Keyboard shortcuts help (collapsible)
        with gr.Accordion("⌨️ Keyboard Shortcuts", open=False, visible=False) as shortcuts_help:
            gr.Markdown(
                """
### Mode Switching
- `Alt+I` - Switch to Idle mode
- `Alt+C` - Switch to Text Chat mode
- `Alt+V` - Switch to Vision Chat mode
- `Alt+G` - Switch to Generate mode

### Actions
- `Ctrl+Enter` - Send chat message (when focused on message box)
- `Ctrl+G` - Generate image
- `Ctrl+K` - Copy prompt to clipboard
- `Ctrl+L` - Use last seed
- `Ctrl+Shift+C` - Clear chat

### Generation Presets
- `Ctrl+1` - Fast Draft preset
- `Ctrl+2` - Balanced preset
- `Ctrl+3` - High Quality preset
- `Ctrl+4` - Ultra Detail preset

### Help
- `?` or `Shift+/` - Toggle this help panel
            """,
                elem_classes=["shortcuts-modal"],
            )

        # Smart mode suggestion display
        smart_suggestion = gr.Markdown(value="", visible=False, elem_classes=["smart-suggestion"])

        gr.Markdown("---")

        # ====================================================================
        # MAIN INTERFACE
        # ====================================================================

        with gr.Row():
            # LEFT COLUMN - Chat Interface
            with gr.Column(scale=2):
                gr.Markdown(
                    '<div class="section-header">💬 AI Chat Assistant</div>',
                    elem_classes=["section-card"],
                )

                with gr.Tabs() as chat_tabs:
                    # Text Chat Tab
                    with gr.Tab("💬 Text Chat"):
                        gr.Markdown("**Develop new prompts from scratch**")

                        with gr.Row():
                            model_dropdown = gr.Dropdown(
                                choices=get_available_models(),
                                value=OLLAMA_CHAT_MODEL,
                                label="Chat Model",
                                interactive=True,
                                scale=3,
                            )
                            refresh_models_btn = gr.Button("🔄", size="sm", scale=1)

                        chatbot = gr.Chatbot(
                            height=350, label="Chat History", show_copy_button=True, type="tuples"
                        )

                        with gr.Row():
                            msg = gr.Textbox(
                                placeholder="Describe your image idea...", label="Message", scale=4
                            )
                            send_btn = gr.Button("Send", scale=1, variant="primary")

                        clear_chat_btn = gr.Button("🗑️ Clear Chat", size="sm")

                        gr.Markdown(
                            "**Tips:** Be specific about style, mood, lighting, composition"
                        )

                    # Vision Chat Tab
                    with gr.Tab("👁️ Vision Chat"):
                        gr.Markdown("**Refine existing images with AI vision**")

                        vision_chatbot = gr.Chatbot(
                            height=350,
                            label="Vision Chat History",
                            show_copy_button=True,
                            type="tuples",
                        )

                        # Image preview in vision chat
                        vision_image_preview = gr.Image(
                            label="Current Image Being Discussed",
                            type="pil",
                            interactive=False,
                            height=200,
                        )

                        with gr.Row():
                            vision_msg = gr.Textbox(
                                placeholder="Ask about the image or request changes...",
                                label="Message",
                                scale=4,
                            )
                            vision_send_btn = gr.Button("Send", scale=1, variant="primary")

                        clear_vision_btn = gr.Button("🗑️ Clear Vision Chat", size="sm")

                        gr.Markdown(
                            "**Tips:** 'Make the sky more dramatic', 'Change colors to warmer tones', 'Add more detail to the foreground'"
                        )

            # RIGHT COLUMN - Prompt & Generation
            with gr.Column(scale=2):
                gr.Markdown(
                    '<div class="section-header">🎨 Image Generation</div>',
                    elem_classes=["section-card"],
                )

                # Quick Actions Toolbar
                with gr.Row():
                    quick_generate_btn = gr.Button(
                        "⚡ Quick Generate", size="sm", variant="primary"
                    )
                    quick_copy_btn = gr.Button("📋 Copy", size="sm")
                    quick_clear_btn = gr.Button("🗑️ Clear", size="sm")
                    quick_extract_btn = gr.Button("📝 Extract", size="sm")

                # Prompt Editor
                prompt_display = gr.Textbox(
                    label="Current Prompt",
                    placeholder="Prompt will appear here after chatting...",
                    lines=6,
                    interactive=True,
                )

                with gr.Row():
                    extract_prompt_btn = gr.Button("📝 Extract from Chat", size="sm")
                    copy_prompt_btn = gr.Button("📋 Copy Prompt", size="sm")
                    clear_prompt_btn = gr.Button("🗑️ Clear", size="sm")

                # Prompt History Section
                with gr.Accordion("📚 Prompt History", open=False):
                    with gr.Row():
                        prompt_search = gr.Textbox(
                            placeholder="Search prompts...", label="Search", scale=3
                        )
                        search_btn = gr.Button("🔍 Search", size="sm", scale=1)

                    prompt_history_dropdown = gr.Dropdown(
                        label="Recent Prompts",
                        choices=prompt_history.get_dropdown_choices(),
                        value=None,
                        interactive=True,
                        allow_custom_value=False,
                    )

                    with gr.Row():
                        load_prompt_btn = gr.Button("📥 Load Selected", size="sm")
                        refresh_history_btn = gr.Button("🔄 Refresh", size="sm")

                    with gr.Row():
                        export_prompts_btn = gr.Button("💾 Export History", size="sm")
                        import_file = gr.File(
                            label="Import History", file_types=[".json"], type="filepath"
                        )

                    history_status = gr.Textbox(
                        label="Status", value="", interactive=False, visible=False
                    )

                # Generation Presets
                gr.Markdown("**⚡ Quick Presets**")
                with gr.Row():
                    preset_fast = gr.Button("⚡ Fast Draft\n768×768, 12 steps", size="sm")
                    preset_balanced = gr.Button("⚖️ Balanced\n1024×1024, 20 steps", size="sm")
                with gr.Row():
                    preset_quality = gr.Button("✨ High Quality\n1024×1024, 30 steps", size="sm")
                    preset_ultra = gr.Button("🔥 Ultra Detail\n1536×1536, 40 steps", size="sm")

                # Workflow Selector (Phase 3)
                with gr.Accordion("🔀 Workflow Selector", open=False):
                    gr.Markdown("Select a ComfyUI workflow to use for generation")

                    with gr.Row():
                        workflow_dropdown = gr.Dropdown(
                            label="Workflow",
                            choices=[wf["name"] for wf in workflow_manager.get_workflows_list()],
                            value=(
                                workflow_manager.get_current_workflow().metadata.name
                                if workflow_manager.get_current_workflow()
                                else None
                            ),
                            interactive=True,
                            scale=3,
                        )
                        workflow_refresh_btn = gr.Button("🔄 Refresh", size="sm", scale=1)

                    with gr.Row():
                        workflow_category_filter = gr.Dropdown(
                            label="Filter by Category",
                            choices=["All"] + workflow_manager.get_all_categories(),
                            value="All",
                            interactive=True,
                        )

                    workflow_info = gr.Markdown(value="Loading workflow info...")

                    with gr.Row():
                        workflow_upload_file = gr.File(
                            label="Upload Workflow JSON", file_types=[".json"], type="filepath"
                        )

                    with gr.Row():
                        workflow_import_btn = gr.Button("📥 Import Workflow", size="sm")
                        workflow_export_btn = gr.Button("📤 Export Current", size="sm")

                # Generation Settings
                with gr.Accordion("⚙️ Generation Settings", open=False):
                    with gr.Row():
                        steps_slider = gr.Slider(
                            minimum=4,
                            maximum=50,
                            value=DEFAULT_STEPS,
                            step=1,
                            label="Steps (20 recommended for Krea)",
                        )

                    with gr.Row():
                        width_slider = gr.Slider(
                            minimum=512, maximum=2048, value=DEFAULT_WIDTH, step=64, label="Width"
                        )
                        height_slider = gr.Slider(
                            minimum=512, maximum=2048, value=DEFAULT_HEIGHT, step=64, label="Height"
                        )

                    # Seed Management Section
                    gr.Markdown("**🎲 Seed Control**")

                    with gr.Row():
                        seed_input = gr.Textbox(
                            label="Seed (leave empty for random)",
                            placeholder="Random seed",
                            value="",
                            scale=3,
                        )
                        seed_lock_checkbox = gr.Checkbox(
                            label="🔒 Lock", value=False, info="Keep seed", scale=1
                        )

                    with gr.Row():
                        use_last_seed_btn = gr.Button("🔄 Use Last", size="sm")
                        seed_random_btn = gr.Button("🎲 Random", size="sm")

                    gr.Markdown("**Fine Tune Seed:**")
                    with gr.Row():
                        seed_minus_100_btn = gr.Button("−100", size="sm")
                        seed_minus_10_btn = gr.Button("−10", size="sm")
                        seed_minus_1_btn = gr.Button("−1", size="sm")
                        seed_plus_1_btn = gr.Button("+1", size="sm")
                        seed_plus_10_btn = gr.Button("+10", size="sm")
                        seed_plus_100_btn = gr.Button("+100", size="sm")

                    with gr.Row():
                        seed_history_dropdown = gr.Dropdown(
                            label="Seed History",
                            choices=[],
                            value=None,
                            interactive=True,
                            allow_custom_value=True,
                        )

                # Img2Img Settings
                with gr.Accordion("🖼️ Img2Img Settings (Optional)", open=False):
                    gr.Markdown(
                        "Upload an image to modify it instead of generating from scratch. Workflow must support img2img (LoadImage + VAEEncode)."
                    )

                    input_image = gr.Image(
                        label="Input Image (leave empty for text2img)",
                        type="filepath",
                        interactive=True,
                    )

                    denoise_slider = gr.Slider(
                        minimum=0.0,
                        maximum=1.0,
                        value=0.75,
                        step=0.05,
                        label="Denoise Strength",
                        info="0.0 = no change, 1.0 = complete regeneration",
                    )

                # Generate Button
                generate_btn = gr.Button(
                    "🎨 Generate Image",
                    variant="primary",
                    size="lg",
                    elem_classes=["primary-action"],
                )

                # VRAM Warning Display
                vram_warning_display = gr.Markdown(value="", visible=False)

                # Progress Bar
                generation_progress = gr.HTML(
                    value="", visible=False, elem_classes=["progress-container"]
                )

                # Status
                generation_status = gr.Textbox(
                    label="Status", value="Ready when you are!", interactive=False
                )

                # Image Display
                generated_image = gr.Image(
                    label="Generated Image", type="pil", interactive=False, height=400
                )

                # Session Stats Display
                with gr.Accordion("📊 Session Statistics", open=False):
                    stats_display = gr.Markdown(value=session_stats.get_stats_display())

                # Batch Queue Section
                with gr.Accordion("🔄 Batch Generation Queue", open=False):
                    gr.Markdown("Add multiple prompts to a queue and process them sequentially")

                    with gr.Row():
                        add_queue_btn = gr.Button("➕ Add to Queue", variant="secondary")
                        batch_variations_btn = gr.Button(
                            "🎲 Add 4 Seed Variations", variant="secondary"
                        )

                    with gr.Row():
                        variation_count = gr.Slider(
                            minimum=2, maximum=10, value=4, step=1, label="Variation Count"
                        )

                    queue_status = gr.Textbox(
                        label="Queue Status", value="Queue is empty", interactive=False
                    )

                    with gr.Row():
                        process_queue_btn = gr.Button("▶️ Process Next Job", variant="primary")
                        clear_completed_btn = gr.Button("🗑️ Clear Completed")
                        cancel_all_btn = gr.Button("❌ Cancel All", variant="stop")

        # Gallery Section (below main interface)
        gr.Markdown("---")

        with gr.Row(elem_classes=["gallery-controls"]):
            gr.Markdown('<div class="section-header">🖼️ Session Gallery</div>')

        # Gallery Controls
        with gr.Row(elem_classes=["gallery-controls"]):
            with gr.Column(scale=2):
                gallery_filter = gr.Textbox(
                    label="🔍 Filter Images", placeholder="Search by prompt keywords...", value=""
                )
            with gr.Column(scale=1):
                gallery_sort = gr.Dropdown(
                    label="📊 Sort By",
                    choices=["newest", "oldest", "seed", "resolution"],
                    value="newest",
                )
            with gr.Column(scale=1):
                favorites_only_check = gr.Checkbox(label="⭐ Favorites Only", value=False)

        with gr.Row():
            refresh_gallery_btn = gr.Button("🔄 Refresh Gallery")
            gallery_stats_btn = gr.Button("📊 Gallery Stats")

        with gr.Row():
            session_gallery = gr.Gallery(
                label="Generated Images (click to load into Vision Chat)",
                show_label=True,
                elem_id="gallery",
                columns=4,
                rows=2,
                height="auto",
                object_fit="contain",
            )

        with gr.Row():
            gallery_info = gr.Textbox(
                label="Gallery Info",
                value="No images generated yet this session",
                interactive=False,
            )

        # ====================================================================
        # EVENT HANDLERS
        # ====================================================================

        # Workflow helper functions
        def get_workflow_info_display():
            """Get formatted workflow info for display"""
            current = workflow_manager.get_current_workflow()
            if not current:
                return "No workflow selected"

            info = f"**{current.metadata.name}**\n\n"
            info += f"*{current.metadata.description}*\n\n"
            info += f"**Category:** {current.metadata.category}\n"
            info += f"**Tags:** {', '.join(current.metadata.tags) if current.metadata.tags else 'None'}\n"
            info += f"**Author:** {current.metadata.author}\n"
            return info

        def switch_workflow(workflow_name, category_filter):
            """Switch to selected workflow"""
            # Find workflow by name
            for filename, wf in workflow_manager.workflows.items():
                if wf.metadata.name == workflow_name:
                    success = workflow_manager.set_current_workflow(filename)
                    if success:
                        return (
                            gr.update(value=workflow_name),
                            get_workflow_info_display(),
                            f"✅ Switched to: {workflow_name}",
                        )
                    else:
                        return (
                            gr.update(),
                            get_workflow_info_display(),
                            "❌ Failed to switch workflow",
                        )

            return (
                gr.update(),
                get_workflow_info_display(),
                f"⚠️ Workflow not found: {workflow_name}",
            )

        def refresh_workflows(category_filter):
            """Refresh workflow list"""
            workflow_manager.load_all_workflows()

            # Get filtered workflows
            if category_filter == "All":
                workflows = workflow_manager.get_workflows_list()
            else:
                workflows = [
                    {"name": wf.metadata.name, "category": wf.metadata.category}
                    for wf in workflow_manager.get_workflows_by_category(category_filter)
                ]

            choices = [wf["name"] for wf in workflows]
            current = workflow_manager.get_current_workflow()
            current_name = current.metadata.name if current else None

            return (
                gr.update(choices=choices, value=current_name),
                get_workflow_info_display(),
                f"✅ Refreshed: {len(workflows)} workflows",
            )

        def filter_workflows_by_category(category):
            """Filter workflow dropdown by category"""
            if category == "All":
                workflows = workflow_manager.get_workflows_list()
            else:
                workflows = [
                    {"name": wf.metadata.name}
                    for wf in workflow_manager.get_workflows_by_category(category)
                ]

            choices = [wf["name"] for wf in workflows]
            return gr.update(choices=choices)

        def import_workflow_from_file(filepath):
            """Import workflow from uploaded file"""
            if not filepath:
                return get_workflow_info_display(), "⚠️ No file selected"

            success = workflow_manager.import_workflow(filepath)
            if success:
                # Refresh dropdown
                workflows = workflow_manager.get_workflows_list()
                return (
                    get_workflow_info_display(),
                    "✅ Workflow imported successfully!",
                    gr.update(choices=[wf["name"] for wf in workflows]),
                )
            else:
                return (get_workflow_info_display(), "❌ Failed to import workflow", gr.update())

        def export_current_workflow():
            """Export current workflow"""
            current = workflow_manager.get_current_workflow()
            if not current:
                return "⚠️ No workflow selected"

            export_path = f"./exported_{current.filename}"
            success = workflow_manager.export_workflow(current.filename, export_path)
            if success:
                return f"✅ Exported to: {export_path}"
            else:
                return "❌ Failed to export workflow"

        # Gallery helper functions
        def update_gallery_display(filter_text="", sort_by="newest", favorites_only=False):
            """Update gallery with filtering and sorting"""
            images = gallery.get_images(filter_text, sort_by, favorites_only)
            total = len(gallery.images)
            shown = len(images)

            if favorites_only:
                info = f"Showing {shown} favorite images (out of {total} total)"
            elif filter_text:
                info = f"Showing {shown} images matching '{filter_text}' (out of {total} total)"
            else:
                info = f"Showing all {shown} images"

            return images, info

        def show_gallery_stats():
            """Show gallery statistics"""
            stats = gallery.get_gallery_stats()
            if stats["total"] == 0:
                return "No images in gallery"

            return f"📊 Gallery Stats\n\nTotal Images: {stats['total']}\n⭐ Favorites: {stats['favorites']}\n💾 Total Size: {stats['total_size_mb']} MB"

        # Mode switching - unified handler for radio button
        def handle_mode_change(mode_choice):
            """Handle mode change from radio button"""
            logger.debug(f"Mode change requested: {mode_choice}")

            if mode_choice == "🔵 Idle":
                status = mode_manager.switch_to_idle()
            elif mode_choice == "💬 Text Chat":
                status = mode_manager.switch_to_chat()
            elif mode_choice == "👁️ Vision Chat":
                status = mode_manager.switch_to_vision()
            elif mode_choice == "🎨 Generate":
                status = mode_manager.switch_to_generate()
            else:
                status = "Unknown mode selected"

            return status, gr.update(value="", visible=False)

        # Wire up mode radio button
        mode_radio.change(handle_mode_change, [mode_radio], [mode_status, smart_suggestion])

        check_status_btn.click(
            lambda: (mode_manager._get_status_message(), gr.update(value="", visible=False)),
            None,
            [mode_status, smart_suggestion],
        )

        # Chat functions
        def user_message(message, history):
            return "", history + [[message, None]]

        def bot_message(history, model, current_prompt):
            if not history or not history[-1][0]:
                return history, current_prompt, "", False

            message = history[-1][0]
            response = chat_with_ollama(message, history[:-1], model, current_prompt)
            history[-1][1] = response

            # Try to extract prompt from response
            new_prompt = current_prompt
            prompt_extracted = False
            if len(response) > 30:
                # If response looks like a prompt (has quotes or is descriptive)
                if '"' in response:
                    import re

                    matches = re.findall(r'"([^"]*)"', response)
                    if matches and len(matches[-1]) > 30:
                        new_prompt = matches[-1]
                        prompt_extracted = True
                elif len(response) > 50 and response.count(",") > 2:
                    # Looks like a detailed prompt
                    new_prompt = response
                    prompt_extracted = True

            # Check for smart switch suggestion
            suggestion_update = gr.update(value="", visible=False)
            if prompt_extracted:
                suggested = smart_switch.should_suggest_switch(
                    "prompt_extracted", mode_manager.get_mode()
                )
                if suggested:
                    suggestion_msg = smart_switch.get_suggestion_message(suggested)
                    suggestion_update = gr.update(value=suggestion_msg, visible=True)

            return history, new_prompt, suggestion_update

        # Wire up chat
        msg.submit(user_message, [msg, chatbot], [msg, chatbot]).then(
            bot_message,
            [chatbot, model_dropdown, current_prompt_state],
            [chatbot, current_prompt_state, smart_suggestion],
        ).then(lambda x: x, [current_prompt_state], [prompt_display])

        send_btn.click(user_message, [msg, chatbot], [msg, chatbot]).then(
            bot_message,
            [chatbot, model_dropdown, current_prompt_state],
            [chatbot, current_prompt_state, smart_suggestion],
        ).then(lambda x: x, [current_prompt_state], [prompt_display])

        clear_chat_btn.click(lambda: ([], ""), None, [chatbot, current_prompt_state]).then(
            lambda: "", None, prompt_display
        )

        # Vision chat functions
        def vision_user_message(message, history):
            return "", history + [[message, None]]

        def vision_bot_message(history, current_image, current_prompt):
            if not history or not history[-1][0]:
                return history, current_prompt

            message = history[-1][0]
            response = vision_chat_with_ollama(message, history[:-1], current_image, current_prompt)
            history[-1][1] = response

            # Try to extract prompt from response
            new_prompt = current_prompt
            if len(response) > 30:
                # If response looks like a prompt (has quotes or is descriptive)
                if '"' in response:
                    import re

                    matches = re.findall(r'"([^"]*)"', response)
                    if matches and len(matches[-1]) > 30:
                        new_prompt = matches[-1]
                elif len(response) > 50 and response.count(",") > 2:
                    # Looks like a detailed prompt
                    new_prompt = response

            return history, new_prompt

        # Wire up vision chat
        vision_msg.submit(
            vision_user_message, [vision_msg, vision_chatbot], [vision_msg, vision_chatbot]
        ).then(
            vision_bot_message,
            [vision_chatbot, current_image_state, current_prompt_state],
            [vision_chatbot, current_prompt_state],
        ).then(
            lambda x: x, [current_prompt_state], [prompt_display]
        )

        vision_send_btn.click(
            vision_user_message, [vision_msg, vision_chatbot], [vision_msg, vision_chatbot]
        ).then(
            vision_bot_message,
            [vision_chatbot, current_image_state, current_prompt_state],
            [vision_chatbot, current_prompt_state],
        ).then(
            lambda x: x, [current_prompt_state], [prompt_display]
        )

        clear_vision_btn.click(lambda: [], None, [vision_chatbot])

        # Update vision image preview when current image changes
        current_image_state.change(lambda x: x, [current_image_state], [vision_image_preview])

        # Prompt management
        prompt_display.change(lambda x: x, [prompt_display], [current_prompt_state])

        def extract_from_chat(history):
            if not history:
                return "No chat history to extract from!"

            # Get last assistant message
            for h in reversed(history):
                if h[1] and len(h[1]) > 30:
                    return h[1]

            return "No suitable prompt found in chat history"

        extract_prompt_btn.click(extract_from_chat, [chatbot], [prompt_display])

        # Copy prompt to clipboard (via JS) with toast
        copy_prompt_btn.click(
            lambda x: x,
            [prompt_display],
            None,
            js="(prompt) => {navigator.clipboard.writeText(prompt); showToast('Prompt copied to clipboard!', 'success'); return prompt;}",
        )

        clear_prompt_btn.click(lambda: "", None, [prompt_display]).then(
            lambda: "", None, [current_prompt_state]
        )

        # Prompt History Handlers
        def load_selected_prompt(selected):
            """Load selected prompt from history"""
            if not selected:
                return ""
            full_prompt = prompt_history.get_prompt_by_display_text(selected)
            return full_prompt

        def search_and_update_dropdown(query):
            """Search prompts and update dropdown"""
            if not query:
                choices = prompt_history.get_dropdown_choices()
            else:
                results = prompt_history.search_prompts(query)
                choices = []
                for entry in results[:10]:
                    prompt = entry["prompt"]
                    if len(prompt) > 60:
                        prompt = prompt[:60] + "..."
                    use_info = f" ({entry['use_count']}x)" if entry.get("use_count", 1) > 1 else ""
                    choices.append(f"{prompt}{use_info}")

            return gr.update(choices=choices)

        def refresh_history():
            """Refresh prompt history dropdown"""
            return gr.update(choices=prompt_history.get_dropdown_choices())

        def export_history():
            """Export prompt history"""
            msg = prompt_history.export_prompts()
            return msg, gr.update(visible=True)

        def import_history(filepath):
            """Import prompt history from file"""
            if not filepath:
                return "❌ No file selected", gr.update(visible=True), gr.update()

            msg = prompt_history.import_prompts(filepath)
            choices = prompt_history.get_dropdown_choices()
            return msg, gr.update(visible=True), gr.update(choices=choices)

        load_prompt_btn.click(load_selected_prompt, [prompt_history_dropdown], [prompt_display])

        search_btn.click(search_and_update_dropdown, [prompt_search], [prompt_history_dropdown])

        prompt_search.submit(search_and_update_dropdown, [prompt_search], [prompt_history_dropdown])

        refresh_history_btn.click(refresh_history, None, [prompt_history_dropdown])

        export_prompts_btn.click(export_history, None, [history_status, history_status])

        import_file.change(
            import_history, [import_file], [history_status, history_status, prompt_history_dropdown]
        )

        # Preset buttons
        def apply_preset(preset_name):
            preset = PRESETS.get(preset_name, PRESETS["Balanced"])
            return preset["width"], preset["height"], preset["steps"]

        preset_fast.click(
            lambda: apply_preset("Fast Draft"), None, [width_slider, height_slider, steps_slider]
        )

        preset_balanced.click(
            lambda: apply_preset("Balanced"), None, [width_slider, height_slider, steps_slider]
        )

        preset_quality.click(
            lambda: apply_preset("High Quality"), None, [width_slider, height_slider, steps_slider]
        )

        preset_ultra.click(
            lambda: apply_preset("Ultra Detail"), None, [width_slider, height_slider, steps_slider]
        )

        # Update warnings when sliders change
        def update_warnings_from_sliders(steps, width, height):
            warning_text, warning_visible = check_vram_warnings(steps, width, height)
            return gr.update(value=warning_text, visible=warning_visible)

        steps_slider.change(
            update_warnings_from_sliders,
            [steps_slider, width_slider, height_slider],
            [vram_warning_display],
        )

        width_slider.change(
            update_warnings_from_sliders,
            [steps_slider, width_slider, height_slider],
            [vram_warning_display],
        )

        height_slider.change(
            update_warnings_from_sliders,
            [steps_slider, width_slider, height_slider],
            [vram_warning_display],
        )

        # Seed management functions
        def use_last_seed():
            last = gallery.get_last_seed()
            if last is not None:
                return str(last)
            return ""

        def adjust_seed(current_seed, adjustment):
            """Adjust seed by specified amount"""
            try:
                if current_seed and current_seed.strip():
                    seed_val = int(current_seed)
                else:
                    seed_val = gallery.get_last_seed()
                    if seed_val is None:
                        import random

                        seed_val = random.randint(0, 2**32 - 1)

                new_seed = max(0, seed_val + adjustment)
                return str(new_seed)
            except:
                return current_seed

        def random_seed():
            """Generate random seed"""
            import random

            return str(random.randint(0, 2**32 - 1))

        def toggle_seed_lock(is_locked, current_seed):
            """Toggle seed lock"""
            if is_locked:
                # Lock the seed
                try:
                    seed_val = int(current_seed) if current_seed else None
                    if seed_val is not None:
                        seed_manager.lock_seed(seed_val)
                    return is_locked
                except:
                    return False
            else:
                # Unlock the seed
                seed_manager.unlock_seed()
                return is_locked

        def select_from_history(selected_seed):
            """Load seed from history"""
            if selected_seed:
                return str(selected_seed)
            return ""

        def update_seed_history():
            """Update seed history dropdown"""
            history = seed_manager.get_history()
            return gr.update(choices=history)

        # Wire up seed management buttons
        use_last_seed_btn.click(use_last_seed, None, seed_input)

        seed_minus_100_btn.click(lambda s: adjust_seed(s, -100), [seed_input], seed_input)
        seed_minus_10_btn.click(lambda s: adjust_seed(s, -10), [seed_input], seed_input)
        seed_minus_1_btn.click(lambda s: adjust_seed(s, -1), [seed_input], seed_input)
        seed_plus_1_btn.click(lambda s: adjust_seed(s, 1), [seed_input], seed_input)
        seed_plus_10_btn.click(lambda s: adjust_seed(s, 10), [seed_input], seed_input)
        seed_plus_100_btn.click(lambda s: adjust_seed(s, 100), [seed_input], seed_input)
        seed_random_btn.click(random_seed, None, seed_input)

        # Seed lock toggle
        seed_lock_checkbox.change(
            toggle_seed_lock, [seed_lock_checkbox, seed_input], seed_lock_checkbox
        )

        # Seed history selection
        seed_history_dropdown.change(select_from_history, [seed_history_dropdown], seed_input)

        # Generation
        def generate_and_store(prompt_text, steps, width, height, seed_value, denoise, input_img):
            """Generate image and store in state and gallery"""
            # Show progress bar
            progress_html = '<div class="progress-bar indeterminate"></div>'

            yield (
                None,  # image
                "🎨 Generating image...",  # status
                None,  # current_image_state
                gr.update(),  # gallery
                gr.update(),  # gallery_info
                gr.update(),  # stats
                gr.update(value="", visible=False),  # smart_suggestion
                gr.update(),  # seed_history
                gr.update(value=progress_html, visible=True),  # progress
            )

            image, status, actual_seed, stats = generate_image(
                prompt_text,
                steps,
                width,
                height,
                seed_value,
                denoise=denoise,
                input_image_path=input_img,
            )

            # Update gallery display
            gallery_images = gallery.get_images()
            gallery_count = len(gallery_images)
            info = (
                f"Generated {gallery_count} image{'s' if gallery_count != 1 else ''} this session"
            )

            if actual_seed is not None:
                info += f" | Last seed: {actual_seed}"

            # Check for smart switch suggestion
            suggestion_update = gr.update(value="", visible=False)
            if image is not None:
                suggested = smart_switch.should_suggest_switch(
                    "image_generated", mode_manager.get_mode()
                )
                if suggested:
                    suggestion_msg = smart_switch.get_suggestion_message(suggested)
                    suggestion_update = gr.update(value=suggestion_msg, visible=True)

            # Update seed history dropdown
            seed_history_update = gr.update(choices=seed_manager.get_history())

            # Hide progress bar
            progress_update = gr.update(value="", visible=False)

            yield image, status, image, gallery_images, info, stats, suggestion_update, seed_history_update, progress_update

        generate_btn.click(
            generate_and_store,
            [
                prompt_display,
                steps_slider,
                width_slider,
                height_slider,
                seed_input,
                denoise_slider,
                input_image,
            ],
            [
                generated_image,
                generation_status,
                current_image_state,
                session_gallery,
                gallery_info,
                stats_display,
                smart_suggestion,
                seed_history_dropdown,
                generation_progress,
            ],
        )

        # Quick Actions Toolbar (wired after generate_and_store is defined)
        quick_generate_btn.click(
            generate_and_store,
            [
                prompt_display,
                steps_slider,
                width_slider,
                height_slider,
                seed_input,
                denoise_slider,
                input_image,
            ],
            [
                generated_image,
                generation_status,
                current_image_state,
                session_gallery,
                gallery_info,
                stats_display,
                smart_suggestion,
                seed_history_dropdown,
                generation_progress,
            ],
        )

        quick_copy_btn.click(
            lambda x: x,
            [prompt_display],
            None,
            js="(prompt) => {navigator.clipboard.writeText(prompt); showToast('Prompt copied!', 'success'); return prompt;}",
        )

        quick_clear_btn.click(lambda: "", None, [prompt_display]).then(
            lambda: "", None, [current_prompt_state]
        )

        quick_extract_btn.click(extract_from_chat, [chatbot], [prompt_display])

        # Gallery click to load image into vision chat
        def load_gallery_image(evt: gr.SelectData):
            """Load clicked gallery image into vision chat"""
            index = evt.index
            img_data = gallery.get_image_by_index(index)

            if img_data:
                image = img_data["image"]
                prompt = img_data["prompt"]
                seed = img_data["seed"]
                settings = img_data["settings"]

                info_text = f"Loaded image from gallery\nPrompt: {prompt[:100]}...\nSeed: {seed}\nSettings: {settings['width']}x{settings['height']}, {settings['steps']} steps"

                return image, info_text, image  # image for state, info text, image for preview

            return None, "Failed to load image", None

        session_gallery.select(
            load_gallery_image, None, [current_image_state, gallery_info, vision_image_preview]
        )

        # Refresh models
        refresh_models_btn.click(
            lambda: gr.update(choices=get_available_models()), None, model_dropdown
        )

        # Keyboard shortcuts toggle
        shortcuts_state = gr.State(False)

        def toggle_shortcuts(current_state):
            return not current_state, gr.update(visible=not current_state, open=not current_state)

        shortcuts_btn.click(toggle_shortcuts, [shortcuts_state], [shortcuts_state, shortcuts_help])

        # Auto-switch toggle
        def toggle_auto_switch(enabled):
            smart_switch.auto_switch_enabled = enabled
            return enabled

        auto_switch_checkbox.change(toggle_auto_switch, [auto_switch_checkbox], None)

        # ====================================================================
        # BATCH QUEUE EVENT HANDLERS
        # ====================================================================

        add_queue_btn.click(
            add_to_queue,
            [prompt_display, steps_slider, width_slider, height_slider, seed_input],
            [generation_status, queue_status],
        )

        batch_variations_btn.click(
            lambda p, st, w, h, s, count: add_batch_variations(p, st, w, h, s, int(count)),
            [
                prompt_display,
                steps_slider,
                width_slider,
                height_slider,
                seed_input,
                variation_count,
            ],
            [generation_status, queue_status],
        )

        process_queue_btn.click(
            process_queue, None, [generated_image, generation_status, queue_status, stats_display]
        ).then(
            update_gallery_display,
            [gallery_filter, gallery_sort, favorites_only_check],
            [session_gallery, gallery_info],
        )

        clear_completed_btn.click(clear_queue, None, queue_status)

        cancel_all_btn.click(cancel_all_queue, None, queue_status)

        # ====================================================================
        # ENHANCED GALLERY EVENT HANDLERS
        # ====================================================================

        refresh_gallery_btn.click(
            update_gallery_display,
            [gallery_filter, gallery_sort, favorites_only_check],
            [session_gallery, gallery_info],
        )

        gallery_stats_btn.click(show_gallery_stats, None, gallery_info)

        # Auto-refresh gallery when filter/sort changes
        gallery_filter.change(
            update_gallery_display,
            [gallery_filter, gallery_sort, favorites_only_check],
            [session_gallery, gallery_info],
        )

        gallery_sort.change(
            update_gallery_display,
            [gallery_filter, gallery_sort, favorites_only_check],
            [session_gallery, gallery_info],
        )

        favorites_only_check.change(
            update_gallery_display,
            [gallery_filter, gallery_sort, favorites_only_check],
            [session_gallery, gallery_info],
        )

        # ====================================================================
        # WORKFLOW MANAGER EVENT HANDLERS (Phase 3)
        # ====================================================================

        # Initialize workflow info on load
        app.load(get_workflow_info_display, None, workflow_info)

        # Workflow selection
        workflow_dropdown.change(
            switch_workflow,
            [workflow_dropdown, workflow_category_filter],
            [workflow_dropdown, workflow_info, generation_status],
        )

        # Refresh workflows
        workflow_refresh_btn.click(
            refresh_workflows,
            [workflow_category_filter],
            [workflow_dropdown, workflow_info, generation_status],
        )

        # Category filter
        workflow_category_filter.change(
            filter_workflows_by_category, [workflow_category_filter], workflow_dropdown
        )

        # Import workflow
        workflow_import_btn.click(
            import_workflow_from_file,
            [workflow_upload_file],
            [workflow_info, generation_status, workflow_dropdown],
        )

        # Export workflow
        workflow_export_btn.click(export_current_workflow, None, generation_status)

    return app


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("AI IMAGE CHAT - Phase 2 (Vision Chat)")
    logger.info("=" * 60)
    logger.info("User: ant")
    logger.info("Hostname: nobara-laptop")
    logger.info(f"ComfyUI: {COMFYUI_API}")
    logger.info(f"Ollama: {OLLAMA_API}")
    logger.info(f"Text Chat Model: {OLLAMA_CHAT_MODEL}")
    logger.info(f"Vision Chat Model: {OLLAMA_VISION_MODEL}")
    logger.info(f"FLUX Finetune: {FINETUNE_NAME}")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Access URLs:")
    logger.info("• Laptop: http://localhost:7860")
    logger.info("• Desktop: http://192.168.1.175:7860")
    logger.info("")
    logger.info("Workflow:")
    logger.info("1. Text Chat → Develop prompts")
    logger.info("2. Generate → Create images")
    logger.info("3. Vision Chat → AI sees image & suggests refinements")
    logger.info("4. Generate → Create refined images")
    logger.info("")
    logger.info("=" * 60)

    app = create_app()
    app.launch(server_name=GRADIO_SERVER_NAME, server_port=GRADIO_SERVER_PORT, share=GRADIO_SHARE)
