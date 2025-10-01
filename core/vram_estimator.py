"""
VRAM Estimation Module

Estimates VRAM requirements and generates warnings for image generation.
"""

import logging

logger = logging.getLogger(__name__)


class VRAMEstimator:
    """
    Estimate VRAM requirements and generate warnings.

    Provides static methods for VRAM estimation based on resolution and steps.
    """

    @staticmethod
    def estimate_vram(width: int, height: int, steps: int) -> float:
        """
        Estimate VRAM usage for image generation

        Formula based on FLUX fp8 requirements:
        - Base: ~8GB for model
        - Resolution scaling: relative to 1024x1024
        - Step scaling: minimal impact for FLUX
        """
        # Base VRAM for FLUX fp8
        base_vram = 8.0

        # Resolution factor (compared to 1024x1024)
        res_factor = (width * height) / (1024 * 1024)

        # Steps have minimal impact on VRAM for FLUX
        # But higher steps = longer time with memory in use
        step_factor = 1.0 + (steps - 20) / 100  # Small scaling

        estimated = base_vram * res_factor * step_factor

        return round(estimated, 1)

    @staticmethod
    def get_warnings(
        width: int, height: int, steps: int, current_vram_used: float = 0, total_vram: float = 16
    ) -> tuple[str, str]:
        """
        Generate warnings based on estimated VRAM usage

        Returns:
            tuple: (warning_level, warning_message)
            warning_level: 'none', 'info', 'warning', 'error'
        """
        estimated_vram = VRAMEstimator.estimate_vram(width, height, steps)
        available_vram = total_vram - current_vram_used

        warnings = []
        warning_level = "none"

        # Check total VRAM requirement
        if estimated_vram > total_vram:
            warning_level = "error"
            warnings.append(
                f"⛔ **OUT OF VRAM**: Estimated {estimated_vram}GB exceeds {total_vram}GB total"
            )

            # Suggest lower resolution
            if width > 1024 or height > 1024:
                warnings.append("💡 **Suggestion**: Try 1024x1024 (~8GB) or 768x768 (~4.5GB)")
            else:
                warnings.append("💡 **Suggestion**: Try 768x768 (~4.5GB) or 512x512 (~2GB)")

        elif estimated_vram > available_vram:
            warning_level = "error"
            warnings.append(
                f"⚠️ **INSUFFICIENT VRAM**: Need {estimated_vram}GB but only {available_vram:.1f}GB available"
            )
            warnings.append("💡 **Suggestion**: Switch to Idle mode first to free up VRAM")

        elif estimated_vram > total_vram * 0.9:
            warning_level = "warning"
            warnings.append(
                f"⚠️ **HIGH VRAM**: Estimated {estimated_vram}GB is {(estimated_vram/total_vram)*100:.0f}% of total"
            )
            warnings.append("💡 This may cause instability. Consider 1024x1024 or lower.")

        elif estimated_vram > total_vram * 0.75:
            warning_level = "info"
            warnings.append(
                f"ℹ️ **Moderate VRAM**: Estimated {estimated_vram}GB ({(estimated_vram/total_vram)*100:.0f}% of total)"
            )

        # Check for excessive steps
        if steps > 40:
            if warning_level == "none":
                warning_level = "info"
            warnings.append(f"⏱️ **High step count**: {steps} steps will take significant time")
            warnings.append("💡 FLUX typically converges well by 20-30 steps")

        # Check for unusual resolutions
        if width != height and abs(width - height) > 512:
            if warning_level == "none":
                warning_level = "info"
            warnings.append(f"📐 **Unusual aspect ratio**: {width}x{height}")
            warnings.append("💡 Extreme aspect ratios may produce unexpected results")

        if warnings:
            return warning_level, "\n".join(warnings)
        else:
            return "none", f"✅ Estimated VRAM: {estimated_vram}GB - Should work fine"
