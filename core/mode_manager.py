"""
Mode Management Module

Handles switching between different operational modes (Idle, Chat, Vision, Generate)
and manages VRAM efficiently.
"""

import time
import requests
import logging
from enum import Enum
from config import OLLAMA_API, OLLAMA_CHAT_MODEL, OLLAMA_VISION_MODEL

# Lazy import for torch (only needed if using CUDA)
try:
    import torch
except ImportError:
    torch = None

logger = logging.getLogger(__name__)


class Mode(Enum):
    IDLE = "idle"
    CHAT = "chat"
    VISION = "vision"
    GENERATE = "generate"


class ModeManager:
    """Manages application modes and VRAM usage"""

    def __init__(self, vram_monitor, comfy_bridge):
        self.current_mode = Mode.IDLE
        self.is_loading = False
        self.vram_monitor = vram_monitor
        self.comfy = comfy_bridge

    def get_mode(self):
        return self.current_mode

    def get_status_icon(self):
        """Get status icon based on current state"""
        if self.is_loading:
            return "🟡"  # Loading
        elif self.current_mode == Mode.IDLE:
            return "🔵"  # Idle
        else:
            return "🟢"  # Active

    def switch_to_idle(self):
        """Unload everything"""
        logger.info("Switching to IDLE mode...")

        # Unload Ollama models
        for model_name in (OLLAMA_CHAT_MODEL, OLLAMA_VISION_MODEL):
            try:
                response = requests.post(
                    f"{OLLAMA_API}/generate",
                    json={"model": model_name, "keep_alive": 0},
                    timeout=5
                )
                if response.status_code == 200:
                    logger.info(f"✓ Ollama model '{model_name}' unloaded")
                else:
                    logger.warning(
                        "⚠️ Ollama responded with status %s while unloading '%s': %s",
                        response.status_code,
                        model_name,
                        response.text
                    )
            except requests.RequestException as exc:
                logger.warning("⚠️ Failed to unload Ollama model '%s': %s", model_name, exc)

        # Clear CUDA cache
        if torch and torch.cuda.is_available():
            torch.cuda.empty_cache()

        self.current_mode = Mode.IDLE
        return self._get_status_message()

    def switch_to_chat(self):
        """Load Ollama on GPU"""
        logger.info(f"Switching to CHAT mode (loading {OLLAMA_CHAT_MODEL})...")

        # First unload anything else
        if self.current_mode != Mode.IDLE:
            self.switch_to_idle()
            time.sleep(2)

        # Warm up Ollama (loads model to GPU)
        try:
            response = requests.post(
                f"{OLLAMA_API}/generate",
                json={
                    "model": OLLAMA_CHAT_MODEL,
                    "prompt": "Hi",
                    "stream": False,
                    "keep_alive": "5m"  # Keep loaded for 5 minutes
                },
                timeout=30
            )
            if response.status_code == 200:
                self.current_mode = Mode.CHAT
                logger.info("✓ Chat mode ready")
                return self._get_status_message()
        except Exception as e:
            return f"❌ Failed to load Ollama: {str(e)}"

        return "❌ Failed to switch to chat mode"

    def switch_to_vision(self):
        """Load Ollama vision model on GPU"""
        logger.info(f"Switching to VISION CHAT mode (loading {OLLAMA_VISION_MODEL})...")

        # First unload anything else
        if self.current_mode != Mode.IDLE:
            self.switch_to_idle()
            time.sleep(2)

        # Warm up Ollama vision model (loads model to GPU)
        try:
            response = requests.post(
                f"{OLLAMA_API}/generate",
                json={
                    "model": OLLAMA_VISION_MODEL,
                    "prompt": "Hi",
                    "stream": False,
                    "keep_alive": "5m"  # Keep loaded for 5 minutes
                },
                timeout=30
            )
            if response.status_code == 200:
                self.current_mode = Mode.VISION
                logger.info("✓ Vision chat mode ready")
                return self._get_status_message()
        except Exception as e:
            return f"❌ Failed to load Ollama vision model: {str(e)}"

        return "❌ Failed to switch to vision chat mode"

    def switch_to_generate(self):
        """Prepare for generation (unload Ollama, check ComfyUI)"""
        logger.info("Switching to GENERATE mode...")

        # Unload Ollama first
        if self.current_mode in [Mode.CHAT, Mode.VISION]:
            self.switch_to_idle()
            time.sleep(2)

        # Check ComfyUI
        if self.comfy.is_available():
            self.current_mode = Mode.GENERATE
            logger.info("✓ Generate mode ready")
            return self._get_status_message()
        else:
            return self._get_comfyui_instructions()

    def _get_status_message(self):
        """Get current status message with live VRAM"""
        mode = self.current_mode
        icon = self.get_status_icon()

        # Get live VRAM stats
        vram = self.vram_monitor.get_vram_usage()
        if vram['available']:
            vram_display = f"**VRAM:** {vram['used_gb']} / {vram['total_gb']} GB ({vram['percentage']}%)"
        else:
            vram_display = "**VRAM:** Monitoring unavailable"

        if mode == Mode.IDLE:
            return f"{icon} **IDLE MODE** - Ready to start\n\n{vram_display}\n\nChoose a mode to begin."

        elif mode == Mode.CHAT:
            return f"{icon} **TEXT CHAT MODE** - Active\n\n{vram_display}\nModel: {OLLAMA_CHAT_MODEL}\n\nChat to develop new prompts from scratch!"

        elif mode == Mode.VISION:
            return f"{icon} **VISION CHAT MODE** - Active\n\n{vram_display}\nModel: {OLLAMA_VISION_MODEL}\n\nChat to refine existing images!"

        elif mode == Mode.GENERATE:
            status = self.comfy.get_status()
            if status["available"]:
                return f"{icon} **GENERATION MODE** - Active\n\n{vram_display}\nBackend: ComfyUI + FLUX\n\nReady to generate images!"
            else:
                return self._get_comfyui_instructions()

        return "Unknown mode"

    def _get_comfyui_instructions(self):
        """Return instructions for starting ComfyUI"""
        return f"""⚠️ **ComfyUI Not Running**

Please start ComfyUI in a terminal:

```bash
cd /home/ant/AI/ComfyUI
conda activate comfy-env
python main.py --listen --cuda-malloc --force-channels-last --use-sage-attention --dont-upcast-attention --fast
```

Or use the provided `start_comfy.sh` script.

Once started, ComfyUI will be available at:
• http://localhost:8188 (laptop)
• http://192.168.1.175:8188 (desktop)

Then click the "Check Status" button below."""
