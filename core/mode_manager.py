"""
Mode Management Module

Handles switching between different operational modes (Idle, Chat, Vision, Generate)
and manages VRAM efficiently.
"""

import logging
import time
from enum import Enum

import requests

from config import OLLAMA_API, OLLAMA_CHAT_MODEL, OLLAMA_VISION_MODEL

from .exceptions import ModeTransitionError, OllamaConnectionError

# Lazy import for torch (only needed if using CUDA)
try:
    import torch
except ImportError:
    torch = None

logger = logging.getLogger(__name__)


class Mode(Enum):
    IDLE = "idle"
    CHAT = "chat"  # Now handles both text and vision chat via tabs
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
                    f"{OLLAMA_API}/generate", json={"model": model_name, "keep_alive": 0}, timeout=5
                )
                if response.status_code == 200:
                    logger.info(f"✓ Ollama model '{model_name}' unloaded")
                else:
                    logger.warning(
                        "⚠️ Ollama responded with status %s while unloading '%s': %s",
                        response.status_code,
                        model_name,
                        response.text,
                    )
            except requests.RequestException as exc:
                logger.warning("⚠️ Failed to unload Ollama model '%s': %s", model_name, exc)

        # Clear CUDA cache
        if torch and torch.cuda.is_available():
            torch.cuda.empty_cache()

        self.current_mode = Mode.IDLE
        return self._get_status_message()

    def switch_to_chat(self, preload_model=None):
        """
        Load Ollama on GPU for chat mode (supports both text and vision models)

        Args:
            preload_model: Optional model name to preload (OLLAMA_CHAT_MODEL or OLLAMA_VISION_MODEL)
                          If None, defaults to OLLAMA_CHAT_MODEL
        """
        model_to_load = preload_model or OLLAMA_CHAT_MODEL
        logger.info(f"Switching to CHAT mode (loading {model_to_load})...")

        # First unload anything else
        if self.current_mode != Mode.IDLE and self.current_mode != Mode.CHAT:
            self.switch_to_idle()
            time.sleep(2)

        # Warm up Ollama (loads model to GPU)
        try:
            response = requests.post(
                f"{OLLAMA_API}/generate",
                json={
                    "model": model_to_load,
                    "prompt": "Hi",
                    "stream": False,
                    "keep_alive": "5m",  # Keep loaded for 5 minutes
                },
                timeout=30,
            )
            if response.status_code == 200:
                self.current_mode = Mode.CHAT
                logger.info("✓ Chat mode ready")
                return self._get_status_message()
            else:
                # Non-200 status - model might not exist or Ollama issue
                error_msg = f"Ollama returned status {response.status_code}"
                logger.error(error_msg)
                raise OllamaConnectionError(
                    f"Failed to load chat model '{model_to_load}': {error_msg}. "
                    f"Please ensure the model is pulled with 'ollama pull {model_to_load}'"
                )
        except requests.RequestException as e:
            # Connection error - Ollama likely not running
            logger.error(f"Failed to connect to Ollama: {e}")
            raise OllamaConnectionError(
                f"Cannot connect to Ollama at {OLLAMA_API}. "
                f"Please start Ollama with 'ollama serve'"
            )
        except OllamaConnectionError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Unexpected error - wrap in ModeTransitionError
            logger.exception(f"Unexpected error switching to chat mode: {e}")
            raise ModeTransitionError(f"Failed to switch to chat mode: {str(e)}")


    def switch_to_generate(self):
        """
        Prepare for generation (unload Ollama, check ComfyUI)

        Raises:
            ComfyUINotAvailableError: If ComfyUI is not running or accessible
        """
        logger.info("Switching to GENERATE mode...")

        # Unload Ollama first
        if self.current_mode == Mode.CHAT:
            self.switch_to_idle()
            time.sleep(2)

        # Check ComfyUI
        if self.comfy.is_available():
            self.current_mode = Mode.GENERATE
            logger.info("✓ Generate mode ready")
            return self._get_status_message()
        else:
            # ComfyUI not available - return instructions (backward compatible)
            # Note: We don't raise an exception here to maintain backward compatibility
            # The UI can handle this gracefully by showing instructions
            return self._get_comfyui_instructions()

    def _get_status_message(self):
        """Get current status message with live VRAM"""
        mode = self.current_mode
        icon = self.get_status_icon()

        # Get live VRAM stats
        vram = self.vram_monitor.get_vram_usage()
        if vram["available"]:
            vram_display = (
                f"**VRAM:** {vram['used_gb']} / {vram['total_gb']} GB ({vram['percentage']}%)"
            )
        else:
            vram_display = "**VRAM:** Monitoring unavailable"

        if mode == Mode.IDLE:
            return f"{icon} **IDLE MODE** - Ready to start\n\n{vram_display}\n\nChoose a mode to begin."

        elif mode == Mode.CHAT:
            return f"{icon} **CHAT MODE** - Active\n\n{vram_display}\n\n💬 Text Chat: Develop prompts from scratch\n👁️ Vision Chat: Refine existing images\n\nSwitch tabs to change between text and vision!"

        elif mode == Mode.GENERATE:
            status = self.comfy.get_status()
            if status["available"]:
                return f"{icon} **GENERATION MODE** - Active\n\n{vram_display}\nBackend: ComfyUI + FLUX\n\nReady to generate images!"
            else:
                return self._get_comfyui_instructions()

        return "Unknown mode"

    def _get_comfyui_instructions(self):
        """Return instructions for starting ComfyUI"""
        return """⚠️ **ComfyUI Not Running**

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

Then click the "Check Status" button below.
""".rstrip()
