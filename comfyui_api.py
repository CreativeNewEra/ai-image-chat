"""
ComfyUI API Bridge
Handles all ComfyUI communication
"""

import requests
import json
import time
import io
import random
import logging
from PIL import Image
import websocket
import uuid
from config import (
    COMFYUI_API, WORKFLOW_PATH, FINETUNE_NAME,
    MIN_WIDTH, MAX_WIDTH, MIN_HEIGHT, MAX_HEIGHT, MIN_STEPS, MAX_STEPS
)

# Get logger for this module
logger = logging.getLogger(__name__)

class ComfyUIBridge:
    def __init__(self):
        self.api_url = COMFYUI_API
        self.workflow = None
        self.client_id = str(uuid.uuid4())
        
    def is_available(self):
        """Check if ComfyUI is running and accessible"""
        try:
            response = requests.get(f"{self.api_url}/system_stats", timeout=2)
            return response.status_code == 200
        except requests.RequestException as exc:
            logger.warning("ComfyUI not available: %s", exc)
        return False

    def get_status(self):
        """Get detailed status of ComfyUI"""
        try:
            response = requests.get(f"{self.api_url}/system_stats", timeout=2)
            if response.status_code == 200:
                stats = response.json()
                return {
                    "available": True,
                    "vram_used": stats.get("system", {}).get("vram_used_gb", "Unknown"),
                    "vram_total": stats.get("system", {}).get("vram_total_gb", "Unknown")
                }
        except requests.RequestException as exc:
            logger.exception("Error getting ComfyUI status: %s", exc)
        except ValueError as exc:
            logger.exception("Invalid JSON from ComfyUI status response: %s", exc)
        return {"available": False}
    
    def load_workflow(self):
        """Load and convert workflow to API format"""
        try:
            with open(WORKFLOW_PATH, 'r') as f:
                workflow_ui = json.load(f)
            
            # Convert UI format to API format
            self.workflow = {}
            
            # Skip UI-only nodes that don't affect generation
            skip_nodes = ["MarkdownNote", "Note", "Reroute"]
            
            for node in workflow_ui.get("nodes", []):
                node_id = str(node["id"])
                node_type = node.get("type")
                
                # Skip UI-only nodes
                if node_type in skip_nodes:
                    continue
                
                # Create API format node
                api_node = {
                    "class_type": node_type,
                    "inputs": {}
                }
                
                # Add widget values as inputs
                if "widgets_values" in node:
                    # Get input names from the node properties
                    widget_values = node["widgets_values"]
                    
                    # Map widget values to input names based on node type
                    if node_type == "UNETLoader":
                        api_node["inputs"]["unet_name"] = FINETUNE_NAME
                        if len(widget_values) > 1:
                            api_node["inputs"]["weight_dtype"] = widget_values[1]
                        logger.info(f"✓ Workflow configured to use: {FINETUNE_NAME}")
                    
                    elif node_type == "DualCLIPLoader":
                        if len(widget_values) >= 2:
                            api_node["inputs"]["clip_name1"] = widget_values[0]
                            api_node["inputs"]["clip_name2"] = widget_values[1]
                        if len(widget_values) >= 3:
                            api_node["inputs"]["type"] = widget_values[2]
                    
                    elif node_type == "VAELoader":
                        if len(widget_values) > 0:
                            api_node["inputs"]["vae_name"] = widget_values[0]
                    
                    elif node_type == "CLIPTextEncode":
                        if len(widget_values) > 0:
                            api_node["inputs"]["text"] = widget_values[0]
                    
                    elif node_type == "KSampler":
                        if len(widget_values) >= 7:
                            api_node["inputs"]["seed"] = widget_values[0]
                            api_node["inputs"]["steps"] = widget_values[2]
                            api_node["inputs"]["cfg"] = widget_values[3]
                            api_node["inputs"]["sampler_name"] = widget_values[4]
                            api_node["inputs"]["scheduler"] = widget_values[5]
                            api_node["inputs"]["denoise"] = widget_values[6]
                    
                    elif node_type == "EmptySD3LatentImage":
                        if len(widget_values) >= 3:
                            api_node["inputs"]["width"] = widget_values[0]
                            api_node["inputs"]["height"] = widget_values[1]
                            api_node["inputs"]["batch_size"] = widget_values[2]
                    
                    elif node_type == "SaveImage":
                        if len(widget_values) > 0:
                            api_node["inputs"]["filename_prefix"] = widget_values[0]
                
                # Add connections from links
                if "inputs" in node:
                    for input_def in node["inputs"]:
                        if "link" in input_def and input_def["link"] is not None:
                            # Find the link in the workflow
                            link_id = input_def["link"]
                            for link in workflow_ui.get("links", []):
                                if link[0] == link_id:
                                    # link format: [id, source_node, source_slot, target_node, target_slot, type]
                                    source_node = str(link[1])
                                    source_slot = link[2]
                                    api_node["inputs"][input_def["name"]] = [source_node, source_slot]
                                    break
                
                self.workflow[node_id] = api_node
            
            return True
        except Exception as e:
            logger.error(f"Error loading workflow: {e}")
            import traceback
            traceback.print_exc()
            return False

    def load_workflow_from_data(self, workflow_data: dict):
        """Load workflow from dictionary data instead of file

        This allows loading workflows from WorkflowManager
        """
        try:
            # Convert UI format to API format
            self.workflow = {}

            # Skip UI-only nodes that don't affect generation
            skip_nodes = ["MarkdownNote", "Note", "Reroute"]

            for node in workflow_data.get("nodes", []):
                node_id = str(node["id"])
                node_type = node.get("type")

                # Skip UI-only nodes
                if node_type in skip_nodes:
                    continue

                # Create API format node
                api_node = {
                    "class_type": node_type,
                    "inputs": {}
                }

                # Add widget values as inputs
                if "widgets_values" in node:
                    widget_values = node["widgets_values"]

                    # Map widget values to input names based on node type
                    if node_type == "UNETLoader":
                        api_node["inputs"]["unet_name"] = FINETUNE_NAME
                        if len(widget_values) > 1:
                            api_node["inputs"]["weight_dtype"] = widget_values[1]

                    elif node_type == "DualCLIPLoader":
                        if len(widget_values) >= 2:
                            api_node["inputs"]["clip_name1"] = widget_values[0]
                            api_node["inputs"]["clip_name2"] = widget_values[1]
                        if len(widget_values) >= 3:
                            api_node["inputs"]["type"] = widget_values[2]

                    elif node_type == "VAELoader":
                        if len(widget_values) > 0:
                            api_node["inputs"]["vae_name"] = widget_values[0]

                    elif node_type == "CLIPTextEncode":
                        # Will be replaced with actual prompt later
                        api_node["inputs"]["text"] = widget_values[0] if widget_values else ""

                    elif node_type == "KSampler":
                        # Default values, will be replaced
                        api_node["inputs"]["seed"] = widget_values[0] if len(widget_values) > 0 else 0
                        api_node["inputs"]["steps"] = widget_values[2] if len(widget_values) > 2 else 20
                        api_node["inputs"]["cfg"] = widget_values[3] if len(widget_values) > 3 else 1.0
                        api_node["inputs"]["sampler_name"] = widget_values[4] if len(widget_values) > 4 else "euler"
                        api_node["inputs"]["scheduler"] = widget_values[5] if len(widget_values) > 5 else "simple"
                        api_node["inputs"]["denoise"] = widget_values[6] if len(widget_values) > 6 else 1.0

                    elif node_type == "EmptySD3LatentImage":
                        # Default dimensions, will be replaced
                        api_node["inputs"]["width"] = widget_values[0] if len(widget_values) > 0 else 1024
                        api_node["inputs"]["height"] = widget_values[1] if len(widget_values) > 1 else 1024
                        api_node["inputs"]["batch_size"] = widget_values[2] if len(widget_values) > 2 else 1

                    elif node_type == "SaveImage":
                        if len(widget_values) > 0:
                            api_node["inputs"]["filename_prefix"] = widget_values[0]
                        else:
                            api_node["inputs"]["filename_prefix"] = "ComfyUI"

                # Handle connections between nodes
                # In ComfyUI format, inputs is a list of input objects
                if "inputs" in node:
                    for input_def in node["inputs"]:
                        if "link" in input_def and input_def["link"] is not None:
                            # Find the link in the workflow
                            link_id = input_def["link"]
                            for link in workflow_data.get("links", []):
                                if link[0] == link_id:
                                    # link format: [id, source_node, source_slot, target_node, target_slot, type]
                                    source_node = str(link[1])
                                    source_slot = link[2]
                                    api_node["inputs"][input_def["name"]] = [source_node, source_slot]
                                    break

                self.workflow[node_id] = api_node

            logger.info(f"✓ Workflow loaded from data with {len(self.workflow)} nodes")
            return True
        except Exception as e:
            logger.error(f"Error loading workflow from data: {e}")
            import traceback
            traceback.print_exc()
            return False

    def upload_image(self, image_path):
        """Upload an image to ComfyUI for img2img

        Args:
            image_path: Path to the image file

        Returns:
            str: Uploaded image filename, or None if failed
        """
        try:
            with open(image_path, 'rb') as f:
                files = {'image': f}
                response = requests.post(
                    f"{self.api_url}/upload/image",
                    files=files,
                    timeout=10
                )

                if response.status_code == 200:
                    result = response.json()
                    filename = result.get('name')
                    logger.info(f"✓ Image uploaded: {filename}")
                    return filename
                else:
                    logger.error(f"Failed to upload image: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            return None

    def modify_prompt(self, prompt_text, steps=20, width=1024, height=1024, seed=None,
                     denoise=1.0, input_image=None):
        """Modify workflow with new parameters

        Args:
            prompt_text: The text prompt for generation
            steps: Number of sampling steps
            width: Image width (for text2img only)
            height: Image height (for text2img only)
            seed: Random seed (None for random)
            denoise: Denoising strength for img2img (0.0-1.0)
            input_image: Uploaded image filename for img2img workflows

        Returns:
            tuple: (modified_workflow, actual_seed)
        """
        if not self.workflow:
            if not self.load_workflow():
                return None, None

        # Make a copy to avoid modifying original
        workflow = json.loads(json.dumps(self.workflow))

        # Track the actual seed used
        actual_seed = seed if seed is not None else random.randint(0, 2**32 - 1)

        # Find and update nodes by their class_type
        for node_id, node in workflow.items():
            class_type = node.get("class_type")

            # Update prompt
            if class_type == "CLIPTextEncode":
                node["inputs"]["text"] = prompt_text

            # Update sampler settings
            elif class_type == "KSampler":
                node["inputs"]["seed"] = actual_seed
                node["inputs"]["steps"] = steps
                node["inputs"]["denoise"] = denoise
                # cfg stays at default (1.0 for Krea)

            # Update image dimensions (text2img only)
            elif class_type == "EmptySD3LatentImage":
                node["inputs"]["width"] = width
                node["inputs"]["height"] = height

            # Update input image (img2img only)
            elif class_type == "LoadImage" and input_image:
                node["inputs"]["image"] = input_image

        return workflow, actual_seed
    
    def queue_prompt(self, workflow):
        """Send workflow to ComfyUI queue"""
        try:
            payload = {
                "prompt": workflow,
                "client_id": self.client_id
            }
            
            response = requests.post(
                f"{self.api_url}/prompt",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                prompt_id = result.get("prompt_id")
                return prompt_id
            else:
                return None
        except Exception as e:
            logger.error(f"Error queuing prompt: {e}")
            return None
    
    def get_image(self, prompt_id, timeout=300):
        """Wait for and retrieve generated image"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check history
                response = requests.get(f"{self.api_url}/history/{prompt_id}")
                if response.status_code == 200:
                    history = response.json()
                    
                    if prompt_id in history:
                        outputs = history[prompt_id].get("outputs", {})
                        
                        # Look for SaveImage node output
                        for node_id, node_output in outputs.items():
                            if "images" in node_output:
                                image_info = node_output["images"][0]
                                filename = image_info["filename"]
                                subfolder = image_info.get("subfolder", "")
                                
                                # Download image
                                img_url = f"{self.api_url}/view"
                                params = {"filename": filename, "subfolder": subfolder, "type": "output"}
                                
                                img_response = requests.get(img_url, params=params)
                                if img_response.status_code == 200:
                                    image = Image.open(io.BytesIO(img_response.content))
                                    return image
                
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error checking for image: {e}")
                time.sleep(1)
        
        return None
    
    def generate_image(self, prompt_text, steps=20, width=1024, height=1024, seed=None,
                      denoise=1.0, input_image_path=None):
        """Complete generation workflow (text2img or img2img)

        Args:
            prompt_text: The text prompt
            steps: Number of sampling steps
            width: Image width (text2img only)
            height: Image height (text2img only)
            seed: Random seed (None for random)
            denoise: Denoising strength (0.0-1.0, for img2img)
            input_image_path: Path to input image (for img2img)

        Returns:
            tuple: (image, message, seed)
        """

        # Validate inputs
        if not (MIN_WIDTH <= width <= MAX_WIDTH):
            return None, f"Width must be between {MIN_WIDTH} and {MAX_WIDTH}", None
        if not (MIN_HEIGHT <= height <= MAX_HEIGHT):
            return None, f"Height must be between {MIN_HEIGHT} and {MAX_HEIGHT}", None
        if not (MIN_STEPS <= steps <= MAX_STEPS):
            return None, f"Steps must be between {MIN_STEPS} and {MAX_STEPS}", None

        # Check availability
        if not self.is_available():
            return None, "ComfyUI is not running. Please start it first.", None

        # Upload input image if this is img2img
        uploaded_filename = None
        if input_image_path:
            uploaded_filename = self.upload_image(input_image_path)
            if not uploaded_filename:
                return None, "Failed to upload input image to ComfyUI", None
            logger.info(f"✓ Input image uploaded for img2img: {uploaded_filename}")

        # Modify workflow
        workflow, actual_seed = self.modify_prompt(
            prompt_text, steps, width, height, seed,
            denoise=denoise, input_image=uploaded_filename
        )
        if not workflow:
            return None, "Failed to prepare workflow", None

        # Queue prompt
        prompt_id = self.queue_prompt(workflow)
        if not prompt_id:
            return None, "Failed to queue prompt in ComfyUI", None

        logger.info(f"Prompt queued with ID: {prompt_id}")
        logger.info(f"Generating: {prompt_text[:60]}...")
        logger.info(f"Seed: {actual_seed}")
        if input_image_path:
            logger.info(f"Img2Img mode - Denoise: {denoise}")

        # Wait for image
        image = self.get_image(prompt_id)

        if image:
            mode_str = "img2img" if input_image_path else "text2img"
            msg = f"✅ Generated successfully! ({mode_str}, {steps} steps"
            if input_image_path:
                msg += f", denoise: {denoise}"
            else:
                msg += f", {width}x{height}"
            msg += ")"
            return image, msg, actual_seed
        else:
            return None, "⏱️ Timeout waiting for image. Check ComfyUI.", None

# Global instance
comfy = ComfyUIBridge()
