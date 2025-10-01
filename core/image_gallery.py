"""
Image Gallery Module

Manages session image gallery with auto-save functionality.
Enhanced with filtering, sorting, favorites, and deletion.
"""

import os
import json
from datetime import datetime
from PIL import Image
import logging
from typing import List, Dict, Optional
from config import OUTPUT_DIR, DEFAULT_WIDTH, DEFAULT_HEIGHT, DEFAULT_STEPS

logger = logging.getLogger(__name__)


class ImageGallery:
    """Manages image gallery with session storage and disk persistence"""

    def __init__(self):
        self.images = []  # List of {image: PIL, prompt: str, seed: int, settings: dict, timestamp: str, favorite: bool, filepath: str}
        self.last_seed = None
        self.favorites = set()  # Set of image indices that are favorited

        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def add_image(self, image, prompt, seed, settings):
        """Add image to gallery and save to disk"""
        if image is None:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create metadata
        metadata = {
            "prompt": prompt,
            "seed": seed,
            "width": settings.get("width", DEFAULT_WIDTH),
            "height": settings.get("height", DEFAULT_HEIGHT),
            "steps": settings.get("steps", DEFAULT_STEPS),
            "timestamp": timestamp
        }

        # Save image with metadata
        prompt_snippet = prompt[:50].replace(" ", "_").replace("/", "-") if prompt else "image"
        filename = f"{timestamp}_{seed}_{prompt_snippet}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # Save image
        image.save(filepath, "PNG")

        # Save metadata as JSON
        metadata_file = filepath.replace(".png", ".json")
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Add to session gallery
        self.images.append({
            "image": image,
            "prompt": prompt,
            "seed": seed,
            "settings": settings,
            "timestamp": timestamp,
            "filepath": filepath,
            "favorite": False
        })

        self.last_seed = seed

        logger.info(f"✓ Saved: {filename}")

    def get_images(self, filter_text: str = "", sort_by: str = "newest", favorites_only: bool = False):
        """Get list of images for gallery display with filtering and sorting"""
        # Start with all images
        filtered_images = self.images.copy()

        # Apply favorites filter
        if favorites_only:
            filtered_images = [img for i, img in enumerate(filtered_images) if i in self.favorites]

        # Apply text filter
        if filter_text:
            filter_lower = filter_text.lower()
            filtered_images = [
                img for img in filtered_images
                if filter_lower in img["prompt"].lower()
            ]

        # Apply sorting
        if sort_by == "newest":
            filtered_images = sorted(filtered_images, key=lambda x: x["timestamp"], reverse=True)
        elif sort_by == "oldest":
            filtered_images = sorted(filtered_images, key=lambda x: x["timestamp"])
        elif sort_by == "seed":
            filtered_images = sorted(filtered_images, key=lambda x: x["seed"])
        elif sort_by == "resolution":
            filtered_images = sorted(
                filtered_images,
                key=lambda x: x["settings"].get("width", 1024) * x["settings"].get("height", 1024),
                reverse=True
            )

        return [item["image"] for item in filtered_images]

    def get_image_by_index(self, index):
        """Get image and metadata by gallery index"""
        if 0 <= index < len(self.images):
            return self.images[index]
        return None

    def get_last_seed(self):
        """Get seed from last generation"""
        return self.last_seed

    def toggle_favorite(self, index: int) -> bool:
        """Toggle favorite status for an image"""
        if 0 <= index < len(self.images):
            if index in self.favorites:
                self.favorites.remove(index)
                self.images[index]["favorite"] = False
                logger.info(f"Removed favorite: index {index}")
                return False
            else:
                self.favorites.add(index)
                self.images[index]["favorite"] = True
                logger.info(f"Added favorite: index {index}")
                return True
        return False

    def is_favorite(self, index: int) -> bool:
        """Check if an image is favorited"""
        return index in self.favorites

    def delete_image(self, index: int) -> bool:
        """Delete an image from gallery and disk"""
        if 0 <= index < len(self.images):
            img_data = self.images[index]
            filepath = img_data["filepath"]

            # Delete files from disk
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    logger.info(f"Deleted image: {filepath}")

                # Delete metadata
                metadata_file = filepath.replace(".png", ".json")
                if os.path.exists(metadata_file):
                    os.remove(metadata_file)
                    logger.info(f"Deleted metadata: {metadata_file}")

            except Exception as e:
                logger.error(f"Error deleting files: {e}")
                return False

            # Remove from gallery
            self.images.pop(index)

            # Update favorites set (shift indices)
            new_favorites = set()
            for fav_idx in self.favorites:
                if fav_idx < index:
                    new_favorites.add(fav_idx)
                elif fav_idx > index:
                    new_favorites.add(fav_idx - 1)
            self.favorites = new_favorites

            logger.info(f"Removed image at index {index} from gallery")
            return True

        return False

    def delete_selected(self, indices: List[int]) -> int:
        """Delete multiple images by indices"""
        # Sort indices in reverse order to delete from end to start
        sorted_indices = sorted(set(indices), reverse=True)
        deleted = 0

        for index in sorted_indices:
            if self.delete_image(index):
                deleted += 1

        logger.info(f"Deleted {deleted} images")
        return deleted

    def get_favorites_count(self) -> int:
        """Get count of favorited images"""
        return len(self.favorites)

    def get_gallery_stats(self) -> Dict:
        """Get gallery statistics"""
        if not self.images:
            return {
                "total": 0,
                "favorites": 0,
                "total_size_mb": 0
            }

        total_size = 0
        for img_data in self.images:
            filepath = img_data["filepath"]
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)

        return {
            "total": len(self.images),
            "favorites": len(self.favorites),
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
