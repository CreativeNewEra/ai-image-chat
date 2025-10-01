"""
AI Image Chat - Configuration
All settings in one place
"""

import logging
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("ai_image_chat.log"), logging.StreamHandler()],
)

# Set log level from environment variable if provided
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.getLogger().setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

# ============================================================================
# PATHS
# ============================================================================

# ComfyUI installation path
COMFYUI_PATH = os.getenv("COMFYUI_PATH", "/home/ant/AI/ComfyUI")

# Workflow file (in same directory as this app)
WORKFLOW_PATH = os.getenv("WORKFLOW_PATH", "./flux1_krea_dev.json")

# Your custom FLUX finetune
FINETUNE_NAME = os.getenv("FINETUNE_NAME", "unstableEvolution_Fp811GB.safetensors")

# Output directory for saved images
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./outputs")

# Prompt history file
PROMPT_HISTORY_FILE = os.getenv("PROMPT_HISTORY_FILE", "./prompt_history.json")

# ============================================================================
# API ENDPOINTS
# ============================================================================

# ComfyUI API (local on laptop)
COMFYUI_API = os.getenv("COMFYUI_API", "http://localhost:8188")

# Ollama API (local on laptop)
OLLAMA_API = os.getenv("OLLAMA_API", "http://localhost:11434/api")

# ============================================================================
# MODELS
# ============================================================================

# Ollama chat model for prompt refinement (text-only)
# Options: mistral:7b (4.4GB), llama3.1:latest (4.9GB)
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "llama3.1:latest")

# Ollama vision model for image-aware iteration
# Options: qwen2.5vl:latest, llava:7b, llava:13b
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "qwen2.5vl:latest")

# ============================================================================
# GENERATION DEFAULTS
# ============================================================================

# Image dimensions
DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 1024

# Generation constraints
MIN_WIDTH = 512
MAX_WIDTH = 2048
MIN_HEIGHT = 512
MAX_HEIGHT = 2048
MIN_STEPS = 1
MAX_STEPS = 100
MIN_PROMPT_LENGTH = 10

# Sampling parameters (Krea-dev optimized)
DEFAULT_STEPS = 20
DEFAULT_CFG = 1.0
DEFAULT_SAMPLER = "euler"
DEFAULT_SCHEDULER = "simple"

# Seed
DEFAULT_SEED = None  # None = random, or set a number for reproducibility

# Generation Presets
PRESETS = {
    "Fast Draft": {"width": 768, "height": 768, "steps": 15},
    "Balanced": {"width": 1024, "height": 1024, "steps": 20},
    "High Quality": {"width": 1024, "height": 1024, "steps": 30},
    "Ultra Detail": {"width": 1536, "height": 1536, "steps": 35},
}

# ============================================================================
# GRADIO SETTINGS
# ============================================================================

# Server settings
GRADIO_SERVER_NAME = "0.0.0.0"  # Listen on all interfaces (allows desktop access)
GRADIO_SERVER_PORT = 7860
GRADIO_SHARE = False  # Set to True for public Gradio link

# ============================================================================
# SYSTEM PROMPTS
# ============================================================================

SYSTEM_PROMPT = """You are an expert AI assistant helping users create detailed image generation prompts.

Your role:
1. Help users refine their image ideas into detailed, effective prompts
2. When they describe an image, expand it with relevant details (lighting, style, composition, mood)
3. Keep prompts concise but descriptive (50-150 words)
4. Use clear, visual language that works well for image generation
5. For iterative refinement, focus on the specific changes they request

Always be encouraging and creative!"""

VISION_SYSTEM_PROMPT = """You are an expert AI assistant helping users refine AI-generated images through iterative feedback.

Your role:
1. Analyze the image the user shows you and understand what they want to change
2. Provide specific, actionable modifications to the image generation prompt
3. Focus on the requested changes while preserving what works well
4. Be concrete: instead of "make it better", say "add dramatic purple sunset clouds, increase contrast"
5. Keep refined prompts concise but descriptive (50-150 words)
6. When you provide a refined prompt, put it in quotes so it's easy to extract

Always be encouraging and help users achieve their creative vision!"""

# ============================================================================
# COMFYUI STARTUP COMMAND
# ============================================================================

# The exact command to start ComfyUI (for instructions to user)
COMFYUI_START_COMMAND = """
cd /home/ant/AI/ComfyUI
conda activate comfy-env
python main.py --listen --cuda-malloc --force-channels-last --use-sage-attention --dont-upcast-attention --fast
"""

# ============================================================================
# VRAM ESTIMATES (for UI display)
# ============================================================================

VRAM_ESTIMATES = {
    "idle": "0 GB",
    "chat": "~5 GB (llama3.1)",
    "vision": "~7 GB (qwen2.5vl)",
    "generate": "~12 GB (ComfyUI + FLUX finetune)",
}
