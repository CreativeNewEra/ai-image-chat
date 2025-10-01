"""
AI Image Chat - Custom Exception Hierarchy

This module defines custom exceptions for better error handling and debugging.
All exceptions inherit from AIImageChatException for easy catching of app-specific errors.

Usage:
    from core.exceptions import ComfyUINotAvailableError

    if not is_comfyui_running():
        raise ComfyUINotAvailableError("ComfyUI is not responding on http://localhost:8188")
"""


class AIImageChatException(Exception):
    """
    Base exception for all AI Image Chat specific errors.

    All custom exceptions in the application inherit from this class,
    making it easy to catch any app-specific error with a single except clause.

    Example:
        try:
            some_operation()
        except AIImageChatException as e:
            # Catch any AI Image Chat specific error
            logger.error(f"Application error: {e}")
    """

    def __init__(self, message: str = "An error occurred in AI Image Chat"):
        self.message = message
        super().__init__(self.message)


class ComfyUINotAvailableError(AIImageChatException):
    """
    Raised when ComfyUI is not available or not responding.

    This error indicates that the ComfyUI API endpoint is unreachable,
    either because ComfyUI is not running, the wrong URL is configured,
    or there's a network connectivity issue.

    Common causes:
        - ComfyUI not started (run ./start_comfy.sh)
        - Wrong COMFYUI_API endpoint in config/env
        - ComfyUI crashed or hung
        - Firewall blocking connection

    Example:
        if not check_comfyui_connection():
            raise ComfyUINotAvailableError(
                "Cannot connect to ComfyUI at http://localhost:8188. "
                "Please start ComfyUI with ./start_comfy.sh"
            )
    """

    def __init__(
        self, message: str = "ComfyUI is not available. Please start ComfyUI and try again."
    ):
        super().__init__(message)


class OllamaConnectionError(AIImageChatException):
    """
    Raised when Ollama service is not available or not responding.

    This error indicates that the Ollama API endpoint is unreachable,
    either because Ollama is not running, the wrong URL is configured,
    or the requested model is not available.

    Common causes:
        - Ollama not started (run `ollama serve`)
        - Wrong OLLAMA_API endpoint in config/env
        - Requested model not pulled (`ollama pull model-name`)
        - Ollama service crashed

    Example:
        try:
            response = ollama_api_call()
        except requests.ConnectionError:
            raise OllamaConnectionError(
                "Cannot connect to Ollama at http://localhost:11434. "
                "Please start Ollama with 'ollama serve'"
            )
    """

    def __init__(self, message: str = "Cannot connect to Ollama. Please ensure Ollama is running."):
        super().__init__(message)


class VRAMInsufficientError(AIImageChatException):
    """
    Raised when there is insufficient VRAM for an operation.

    This error indicates that the requested operation would exceed
    available GPU VRAM, likely causing an out-of-memory error.

    Common causes:
        - Resolution too high for available VRAM
        - Too many steps requested
        - Another process using GPU memory
        - Model not unloaded from previous operation

    Solutions:
        - Switch to IDLE mode to free VRAM
        - Reduce image resolution
        - Reduce number of steps
        - Close other GPU applications

    Example:
        if estimated_vram > available_vram:
            raise VRAMInsufficientError(
                f"Estimated VRAM usage ({estimated_vram}GB) exceeds "
                f"available VRAM ({available_vram}GB). "
                f"Please reduce resolution or switch to IDLE mode first."
            )
    """

    def __init__(
        self,
        message: str = "Insufficient VRAM for this operation. Please reduce settings or free GPU memory.",
    ):
        super().__init__(message)


class WorkflowLoadError(AIImageChatException):
    """
    Raised when a ComfyUI workflow fails to load or parse.

    This error indicates that a workflow file is malformed, missing required
    nodes, or incompatible with the current ComfyUI setup.

    Common causes:
        - Malformed JSON in workflow file
        - Missing required nodes in workflow
        - Workflow created with incompatible ComfyUI version
        - Missing custom nodes or extensions
        - Corrupted workflow file
        - Invalid metadata file

    Example:
        try:
            workflow_data = json.loads(workflow_file)
        except json.JSONDecodeError as e:
            raise WorkflowLoadError(
                f"Failed to parse workflow file '{filename}': {e}"
            )
    """

    def __init__(
        self, message: str = "Failed to load workflow. Please check the workflow file is valid."
    ):
        super().__init__(message)


class ModeTransitionError(AIImageChatException):
    """
    Raised when switching between modes fails.

    This error indicates that a mode transition (IDLE → CHAT → GENERATE)
    could not be completed successfully, usually due to service availability
    or resource conflicts.

    Common causes:
        - Service (Ollama/ComfyUI) not responding during switch
        - VRAM not freed from previous mode
        - API call timeout during transition
        - Invalid mode requested

    Example:
        try:
            unload_current_mode()
            load_new_mode()
        except Exception as e:
            raise ModeTransitionError(
                f"Failed to switch from {old_mode} to {new_mode}: {e}"
            )
    """

    def __init__(
        self, message: str = "Failed to switch modes. Please try switching to IDLE first."
    ):
        super().__init__(message)


class ImageGenerationError(AIImageChatException):
    """
    Raised when image generation fails.

    This error indicates that the image generation process failed,
    either during workflow submission, processing, or image retrieval.

    Common causes:
        - ComfyUI workflow execution error
        - Timeout waiting for generation
        - Missing model files
        - Invalid generation parameters
        - VRAM overflow during generation

    Example:
        if not generation_completed:
            raise ImageGenerationError(
                f"Image generation timed out after {timeout} seconds. "
                f"Check ComfyUI for errors."
            )
    """

    def __init__(
        self, message: str = "Image generation failed. Please check ComfyUI logs for details."
    ):
        super().__init__(message)


class ModelNotFoundError(AIImageChatException):
    """
    Raised when a required model file is not found.

    This error indicates that a model referenced in the workflow or
    configuration does not exist in the expected location.

    Common causes:
        - Model file not downloaded
        - Wrong model filename in config
        - Model in wrong directory
        - Finetune file missing

    Example:
        if not model_file.exists():
            raise ModelNotFoundError(
                f"Model file '{model_name}' not found in "
                f"{COMFYUI_PATH}/models/diffusion_models/"
            )
    """

    def __init__(
        self, message: str = "Required model file not found. Please check your model installation."
    ):
        super().__init__(message)
