"""
Image Utility Functions

Helper functions for image processing and conversion.
"""

import io
import base64
from PIL import Image
import logging

logger = logging.getLogger(__name__)


def pil_to_base64(image):
    """Convert PIL Image to base64 string for Ollama"""
    if image is None:
        return None

    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Save to bytes buffer
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG', quality=95)
    buffer.seek(0)

    # Encode to base64
    img_bytes = buffer.read()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')

    return img_base64
