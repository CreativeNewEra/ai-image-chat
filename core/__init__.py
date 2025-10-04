"""
Core Module

Contains all core business logic classes for the AI Image Chat application.
"""

from .exceptions import (
    AIImageChatException,
    ComfyUINotAvailableError,
    ImageGenerationError,
    ModelNotFoundError,
    ModeTransitionError,
    OllamaConnectionError,
    VRAMInsufficientError,
    WorkflowLoadError,
)
from .generation_queue import GenerationJob, GenerationQueue, JobStatus
from .image_gallery import ImageGallery
from .mode_manager import Mode, ModeManager
from .prompt_history import PromptHistory
from .seed_manager import SeedManager
from .session_stats import SessionStats
from .smart_switch import SmartSwitchManager
from .vram_estimator import VRAMEstimator
from .vram_monitor import VRAMMonitor
from .workflow_manager import Workflow, WorkflowManager, WorkflowMetadata
from .theme_manager import ThemeManager, ThemePreferences
from .prompt_composer import PromptComposer, PromptTag, PromptTemplate

__all__ = [
    "VRAMMonitor",
    "SessionStats",
    "VRAMEstimator",
    "SeedManager",
    "PromptHistory",
    "SmartSwitchManager",
    "Mode",
    "ModeManager",
    "ImageGallery",
    "GenerationQueue",
    "GenerationJob",
    "JobStatus",
    "WorkflowManager",
    "Workflow",
    "WorkflowMetadata",
    "ThemeManager",
    "ThemePreferences",
    "PromptComposer",
    "PromptTag",
    "PromptTemplate",
    # Exceptions
    "AIImageChatException",
    "ComfyUINotAvailableError",
    "OllamaConnectionError",
    "VRAMInsufficientError",
    "WorkflowLoadError",
    "ModeTransitionError",
    "ImageGenerationError",
    "ModelNotFoundError",
]
