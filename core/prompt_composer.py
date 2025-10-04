"""
Prompt Composer Module

Helps users build better prompts using tags, templates, and smart composition.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)

# Type aliases
TagCategory = Literal["subject", "style", "lighting", "mood", "camera", "quality", "colors"]


@dataclass
class PromptTag:
    """A reusable prompt tag."""

    name: str
    category: TagCategory
    description: str = ""
    aliases: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        return self.name


@dataclass
class PromptTemplate:
    """A pre-built prompt template."""

    name: str
    description: str
    prompt: str
    tags: list[str] = field(default_factory=list)
    category: str = "general"
    author: str = "System"
    preview_image: str | None = None  # Optional path to preview image


class PromptComposer:
    """
    Manage prompt composition with tags and templates.

    Features:
    - Tag-based prompt building
    - Template library
    - Smart tag ordering
    - Custom template saving
    """

    # Comprehensive tag library organized by category
    TAG_LIBRARY = {
        "subject": [
            PromptTag("portrait", "subject", "Portrait of a person"),
            PromptTag("landscape", "subject", "Natural landscape scene"),
            PromptTag("cityscape", "subject", "Urban city scene"),
            PromptTag("fantasy character", "subject", "Fantasy or mythical character"),
            PromptTag("animal", "subject", "Animal subject"),
            PromptTag("robot", "subject", "Robotic or mechanical being"),
            PromptTag("architecture", "subject", "Building or structure"),
            PromptTag("still life", "subject", "Arranged objects"),
            PromptTag("abstract", "subject", "Abstract composition"),
            PromptTag("vehicle", "subject", "Car, spaceship, etc."),
        ],
        "style": [
            PromptTag("photorealistic", "style", "Like a photograph"),
            PromptTag("anime", "style", "Japanese animation style"),
            PromptTag("oil painting", "style", "Traditional oil paint"),
            PromptTag("watercolor", "style", "Watercolor painting"),
            PromptTag("digital art", "style", "Digital illustration"),
            PromptTag("3D render", "style", "3D CGI rendering"),
            PromptTag("sketch", "style", "Pencil or pen sketch"),
            PromptTag("pixel art", "style", "Retro pixel style"),
            PromptTag("vector art", "style", "Clean vector graphics"),
            PromptTag("comic book", "style", "Comic/manga style"),
            PromptTag("art nouveau", "style", "Art nouveau aesthetic"),
            PromptTag("cyberpunk", "style", "Cyberpunk aesthetic"),
            PromptTag("steampunk", "style", "Victorian sci-fi"),
            PromptTag("minimalist", "style", "Simple, clean design"),
        ],
        "lighting": [
            PromptTag("golden hour", "lighting", "Warm sunset/sunrise light"),
            PromptTag("dramatic lighting", "lighting", "High contrast shadows"),
            PromptTag("soft lighting", "lighting", "Diffused, gentle light"),
            PromptTag("studio lighting", "lighting", "Professional studio setup"),
            PromptTag("natural lighting", "lighting", "Ambient daylight"),
            PromptTag("neon lights", "lighting", "Glowing neon signs"),
            PromptTag("candlelight", "lighting", "Warm flickering light"),
            PromptTag("backlit", "lighting", "Light from behind subject"),
            PromptTag("rim lighting", "lighting", "Edge highlighting"),
            PromptTag("volumetric lighting", "lighting", "Light rays/god rays"),
        ],
        "mood": [
            PromptTag("serene", "mood", "Peaceful and calm"),
            PromptTag("dramatic", "mood", "Intense and powerful"),
            PromptTag("mysterious", "mood", "Enigmatic and intriguing"),
            PromptTag("cheerful", "mood", "Happy and uplifting"),
            PromptTag("melancholic", "mood", "Sad or nostalgic"),
            PromptTag("epic", "mood", "Grand and heroic"),
            PromptTag("whimsical", "mood", "Playful and fantastical"),
            PromptTag("ominous", "mood", "Dark and foreboding"),
            PromptTag("romantic", "mood", "Love and passion"),
            PromptTag("energetic", "mood", "Dynamic and lively"),
        ],
        "camera": [
            PromptTag("close-up", "camera", "Tight framing on subject"),
            PromptTag("wide angle", "camera", "Broad field of view"),
            PromptTag("aerial view", "camera", "Bird's eye perspective"),
            PromptTag("macro", "camera", "Extreme close-up detail"),
            PromptTag("low angle", "camera", "Camera below subject"),
            PromptTag("high angle", "camera", "Camera above subject"),
            PromptTag("fisheye", "camera", "Extreme wide distortion"),
            PromptTag("telephoto", "camera", "Compressed perspective"),
            PromptTag("portrait lens", "camera", "Shallow depth of field"),
            PromptTag("panoramic", "camera", "Ultra-wide view"),
        ],
        "quality": [
            PromptTag("highly detailed", "quality", "Intricate details"),
            PromptTag("4k", "quality", "High resolution"),
            PromptTag("8k", "quality", "Ultra high resolution"),
            PromptTag("masterpiece", "quality", "Exceptional quality"),
            PromptTag("professional", "quality", "Expert level work"),
            PromptTag("trending on artstation", "quality", "Popular contemporary"),
            PromptTag("award winning", "quality", "Recognized excellence"),
            PromptTag("cinematic", "quality", "Movie-quality visuals"),
            PromptTag("hyper realistic", "quality", "Extremely realistic"),
            PromptTag("sharp focus", "quality", "Crisp and clear"),
        ],
        "colors": [
            PromptTag("vibrant colors", "colors", "Bold, saturated"),
            PromptTag("muted colors", "colors", "Subdued, desaturated"),
            PromptTag("monochrome", "colors", "Single color/grayscale"),
            PromptTag("pastel", "colors", "Soft, light colors"),
            PromptTag("warm tones", "colors", "Reds, oranges, yellows"),
            PromptTag("cool tones", "colors", "Blues, greens, purples"),
            PromptTag("neon", "colors", "Bright glowing colors"),
            PromptTag("earth tones", "colors", "Natural browns/greens"),
            PromptTag("black and white", "colors", "No color"),
            PromptTag("colorful", "colors", "Multi-colored"),
        ],
    }

    # Pre-built templates
    DEFAULT_TEMPLATES = [
        PromptTemplate(
            name="Realistic Portrait",
            description="Professional portrait photography",
            prompt="portrait, photorealistic, studio lighting, highly detailed, 4k, sharp focus, professional",
            tags=["portrait", "photorealistic", "studio lighting", "highly detailed", "4k", "sharp focus", "professional"],
            category="portrait",
        ),
        PromptTemplate(
            name="Fantasy Landscape",
            description="Epic fantasy scenery",
            prompt="fantasy landscape, dramatic lighting, highly detailed, cinematic, vibrant colors, masterpiece, 8k",
            tags=["landscape", "dramatic lighting", "highly detailed", "cinematic", "vibrant colors", "masterpiece"],
            category="landscape",
        ),
        PromptTemplate(
            name="Anime Character",
            description="Anime-style character art",
            prompt="anime character portrait, digital art, soft lighting, vibrant colors, highly detailed, trending on artstation",
            tags=["portrait", "anime", "digital art", "soft lighting", "vibrant colors", "highly detailed"],
            category="anime",
        ),
        PromptTemplate(
            name="Cyberpunk City",
            description="Futuristic urban scene",
            prompt="cyberpunk cityscape, neon lights, dramatic lighting, highly detailed, cinematic, 8k, sharp focus",
            tags=["cityscape", "cyberpunk", "neon lights", "dramatic lighting", "highly detailed", "cinematic"],
            category="sci-fi",
        ),
        PromptTemplate(
            name="Oil Painting",
            description="Classical oil painting style",
            prompt="oil painting, serene landscape, golden hour lighting, warm tones, masterpiece, highly detailed",
            tags=["landscape", "oil painting", "golden hour", "warm tones", "masterpiece", "highly detailed"],
            category="classical",
        ),
        PromptTemplate(
            name="Macro Nature",
            description="Close-up nature photography",
            prompt="macro photography, nature, natural lighting, highly detailed, sharp focus, vibrant colors, 4k",
            tags=["macro", "natural lighting", "highly detailed", "sharp focus", "vibrant colors", "4k"],
            category="nature",
        ),
    ]

    def __init__(self, templates_path: str = "prompt_templates.json"):
        """
        Initialize prompt composer.

        Args:
            templates_path: Path to save/load custom templates
        """
        self.templates_path = Path(templates_path)
        self.custom_templates: list[PromptTemplate] = []
        self.selected_tags: list[PromptTag] = []

        self._load_custom_templates()

    def _load_custom_templates(self) -> None:
        """Load custom templates from file."""
        if self.templates_path.exists():
            try:
                with open(self.templates_path, "r") as f:
                    data = json.load(f)
                    for item in data:
                        template = PromptTemplate(**item)
                        self.custom_templates.append(template)
                logger.info(f"Loaded {len(self.custom_templates)} custom templates")
            except Exception as e:
                logger.warning(f"Failed to load custom templates: {e}")

    def save_custom_templates(self) -> None:
        """Save custom templates to file."""
        try:
            data = [
                {
                    "name": t.name,
                    "description": t.description,
                    "prompt": t.prompt,
                    "tags": t.tags,
                    "category": t.category,
                    "author": t.author,
                }
                for t in self.custom_templates
            ]
            with open(self.templates_path, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.custom_templates)} custom templates")
        except Exception as e:
            logger.error(f"Failed to save custom templates: {e}")

    def get_tags_by_category(self, category: TagCategory) -> list[PromptTag]:
        """Get all tags in a category."""
        return self.TAG_LIBRARY.get(category, [])

    def get_all_categories(self) -> list[str]:
        """Get list of all tag categories."""
        return list(self.TAG_LIBRARY.keys())

    def add_tag(self, tag: PromptTag) -> None:
        """Add a tag to selected tags."""
        if tag not in self.selected_tags:
            self.selected_tags.append(tag)
            logger.debug(f"Added tag: {tag.name}")

    def remove_tag(self, tag: PromptTag) -> None:
        """Remove a tag from selected tags."""
        if tag in self.selected_tags:
            self.selected_tags.remove(tag)
            logger.debug(f"Removed tag: {tag.name}")

    def clear_tags(self) -> None:
        """Clear all selected tags."""
        self.selected_tags.clear()
        logger.debug("Cleared all tags")

    def build_prompt(self) -> str:
        """
        Build a prompt from selected tags.

        Tags are ordered by category for better composition:
        Subject -> Style -> Lighting -> Mood -> Camera -> Quality -> Colors
        """
        if not self.selected_tags:
            return ""

        # Define category order
        category_order = ["subject", "style", "lighting", "mood", "camera", "quality", "colors"]

        # Group tags by category
        categorized = {cat: [] for cat in category_order}
        for tag in self.selected_tags:
            if tag.category in categorized:
                categorized[tag.category].append(tag.name)

        # Build prompt in order
        prompt_parts = []
        for category in category_order:
            if categorized[category]:
                prompt_parts.extend(categorized[category])

        return ", ".join(prompt_parts)

    def get_all_templates(self) -> list[PromptTemplate]:
        """Get all templates (default + custom)."""
        return self.DEFAULT_TEMPLATES + self.custom_templates

    def get_templates_by_category(self, category: str) -> list[PromptTemplate]:
        """Get templates filtered by category."""
        all_templates = self.get_all_templates()
        if category.lower() == "all":
            return all_templates
        return [t for t in all_templates if t.category.lower() == category.lower()]

    def get_template_categories(self) -> list[str]:
        """Get list of unique template categories."""
        all_templates = self.get_all_templates()
        categories = set(t.category for t in all_templates)
        return sorted(list(categories))

    def load_template(self, template: PromptTemplate) -> str:
        """
        Load a template and update selected tags.

        Returns:
            The template's prompt string
        """
        self.clear_tags()

        # Find and add matching tags
        for tag_name in template.tags:
            for category_tags in self.TAG_LIBRARY.values():
                for tag in category_tags:
                    if tag.name.lower() == tag_name.lower():
                        self.add_tag(tag)
                        break

        logger.info(f"Loaded template: {template.name}")
        return template.prompt

    def save_as_template(
        self, name: str, description: str, category: str = "custom", author: str = "User"
    ) -> PromptTemplate:
        """
        Save current composition as a custom template.

        Args:
            name: Template name
            description: Template description
            category: Template category
            author: Author name

        Returns:
            The created template
        """
        prompt = self.build_prompt()
        tag_names = [tag.name for tag in self.selected_tags]

        template = PromptTemplate(
            name=name,
            description=description,
            prompt=prompt,
            tags=tag_names,
            category=category,
            author=author,
        )

        self.custom_templates.append(template)
        self.save_custom_templates()

        logger.info(f"Saved custom template: {name}")
        return template

    def get_selected_tags_display(self) -> str:
        """Get formatted display of selected tags."""
        if not self.selected_tags:
            return "No tags selected"

        tags_by_category = {}
        for tag in self.selected_tags:
            if tag.category not in tags_by_category:
                tags_by_category[tag.category] = []
            tags_by_category[tag.category].append(tag.name)

        lines = []
        for category, tags in tags_by_category.items():
            emoji_map = {
                "subject": "🎭",
                "style": "🖌️",
                "lighting": "💡",
                "mood": "🎭",
                "camera": "📷",
                "quality": "✨",
                "colors": "🎨",
            }
            emoji = emoji_map.get(category, "•")
            lines.append(f"{emoji} **{category.title()}:** {', '.join(tags)}")

        return "\n".join(lines)
