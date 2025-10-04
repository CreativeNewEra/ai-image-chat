"""
Theme Manager Module

Manages application themes, color schemes, and layout preferences.
"""

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)

# Type aliases
ThemeMode = Literal["light", "dark", "auto"]
ColorScheme = Literal["default", "ocean", "forest", "sunset", "monochrome"]
LayoutDensity = Literal["compact", "comfortable", "spacious"]


@dataclass
class ThemePreferences:
    """User theme preferences."""

    mode: ThemeMode = "auto"
    color_scheme: ColorScheme = "default"
    layout_density: LayoutDensity = "comfortable"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ThemePreferences":
        """Create from dictionary."""
        return cls(
            mode=data.get("mode", "auto"),
            color_scheme=data.get("color_scheme", "default"),
            layout_density=data.get("layout_density", "comfortable"),
        )


class ThemeManager:
    """
    Manage application themes and user preferences.

    Handles:
    - Dark/Light mode switching
    - Color scheme selection
    - Layout density options
    - Preference persistence
    """

    # Color scheme definitions
    COLOR_SCHEMES = {
        "default": {
            "name": "Default",
            "description": "Blue & Purple gradient",
            "primary": "#667eea",
            "secondary": "#764ba2",
            "accent": "#f093fb",
        },
        "ocean": {
            "name": "Ocean",
            "description": "Cool blue tones",
            "primary": "#2196f3",
            "secondary": "#0288d1",
            "accent": "#03a9f4",
        },
        "forest": {
            "name": "Forest",
            "description": "Natural green tones",
            "primary": "#4caf50",
            "secondary": "#388e3c",
            "accent": "#8bc34a",
        },
        "sunset": {
            "name": "Sunset",
            "description": "Warm orange & pink",
            "primary": "#ff9800",
            "secondary": "#f57c00",
            "accent": "#ff6f00",
        },
        "monochrome": {
            "name": "Monochrome",
            "description": "Elegant grayscale",
            "primary": "#607d8b",
            "secondary": "#455a64",
            "accent": "#78909c",
        },
    }

    def __init__(self, config_path: str = "theme_preferences.json"):
        """
        Initialize theme manager.

        Args:
            config_path: Path to save/load theme preferences
        """
        self.config_path = Path(config_path)
        self.preferences = self._load_preferences()

    def _load_preferences(self) -> ThemePreferences:
        """Load preferences from file or use defaults."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                    prefs = ThemePreferences.from_dict(data)
                    logger.info(f"Loaded theme preferences: {prefs}")
                    return prefs
            except Exception as e:
                logger.warning(f"Failed to load theme preferences: {e}. Using defaults.")

        return ThemePreferences()

    def save_preferences(self) -> None:
        """Save current preferences to file."""
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.preferences.to_dict(), f, indent=2)
            logger.info(f"Saved theme preferences: {self.preferences}")
        except Exception as e:
            logger.error(f"Failed to save theme preferences: {e}")

    def set_mode(self, mode: ThemeMode) -> None:
        """Set theme mode (light/dark/auto)."""
        self.preferences.mode = mode
        self.save_preferences()

    def set_color_scheme(self, scheme: ColorScheme) -> None:
        """Set color scheme."""
        if scheme in self.COLOR_SCHEMES:
            self.preferences.color_scheme = scheme
            self.save_preferences()
        else:
            logger.warning(f"Invalid color scheme: {scheme}")

    def set_layout_density(self, density: LayoutDensity) -> None:
        """Set layout density."""
        self.preferences.layout_density = density
        self.save_preferences()

    def get_mode(self) -> ThemeMode:
        """Get current theme mode."""
        return self.preferences.mode

    def get_color_scheme(self) -> ColorScheme:
        """Get current color scheme."""
        return self.preferences.color_scheme

    def get_layout_density(self) -> LayoutDensity:
        """Get current layout density."""
        return self.preferences.layout_density

    def get_color_scheme_info(self, scheme: ColorScheme | None = None) -> dict:
        """
        Get color scheme information.

        Args:
            scheme: Color scheme name, or None for current scheme

        Returns:
            Dictionary with scheme colors and metadata
        """
        if scheme is None:
            scheme = self.preferences.color_scheme

        return self.COLOR_SCHEMES.get(scheme, self.COLOR_SCHEMES["default"])

    def get_css_variables(self) -> str:
        """
        Generate CSS variables for current theme.

        Returns:
            CSS string with custom properties
        """
        scheme_info = self.get_color_scheme_info()
        density = self.preferences.layout_density

        # Density-based spacing
        spacing_map = {
            "compact": {"base": "8px", "multiplier": 0.75},
            "comfortable": {"base": "12px", "multiplier": 1.0},
            "spacious": {"base": "16px", "multiplier": 1.25},
        }
        spacing = spacing_map[density]

        return f"""
        :root {{
            /* Color Scheme */
            --theme-primary: {scheme_info['primary']};
            --theme-secondary: {scheme_info['secondary']};
            --theme-accent: {scheme_info['accent']};

            /* Spacing */
            --spacing-base: {spacing['base']};
            --spacing-xs: calc(var(--spacing-base) * 0.5);
            --spacing-sm: calc(var(--spacing-base) * 0.75);
            --spacing-md: var(--spacing-base);
            --spacing-lg: calc(var(--spacing-base) * 1.5);
            --spacing-xl: calc(var(--spacing-base) * 2);

            /* Layout Density */
            --density-multiplier: {spacing['multiplier']};
        }}
        """

    def get_theme_display(self) -> str:
        """
        Get formatted theme info for display.

        Returns:
            Markdown-formatted string with current theme settings
        """
        scheme_info = self.get_color_scheme_info()
        mode_emoji = {"light": "☀️", "dark": "🌙", "auto": "🌓"}[self.preferences.mode]
        density_emoji = {"compact": "📦", "comfortable": "📐", "spacious": "📏"}[
            self.preferences.layout_density
        ]

        return f"""**Current Theme Settings**

{mode_emoji} **Mode:** {self.preferences.mode.title()}
🎨 **Color Scheme:** {scheme_info['name']} - {scheme_info['description']}
{density_emoji} **Layout:** {self.preferences.layout_density.title()}
"""

    def reset_to_defaults(self) -> None:
        """Reset all preferences to defaults."""
        self.preferences = ThemePreferences()
        self.save_preferences()
        logger.info("Reset theme preferences to defaults")

    def get_all_color_schemes(self) -> list[tuple[str, str]]:
        """
        Get list of all color schemes.

        Returns:
            List of (scheme_id, display_name) tuples
        """
        return [(key, info["name"]) for key, info in self.COLOR_SCHEMES.items()]
