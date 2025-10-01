"""
VRAM Monitoring Module

Provides real-time GPU VRAM usage monitoring via nvidia-smi with caching.
"""

import logging
import subprocess
import time

logger = logging.getLogger(__name__)


class VRAMMonitor:
    """
    Monitor GPU VRAM usage via nvidia-smi.

    Caches results for 2 seconds to minimize polling overhead.
    """

    def __init__(self) -> None:
        self.last_check: float = 0
        self.cache_duration: int = 2  # Cache for 2 seconds
        self.cached_vram: dict[str, float] | None = None

    def get_vram_usage(self) -> dict[str, float]:
        """
        Get VRAM usage in GB and percentage.

        Returns:
            Dict with keys: 'used_gb', 'total_gb', 'percentage', 'available'
        """
        current_time = time.time()

        # Return cached value if recent
        if self.cached_vram and (current_time - self.last_check) < self.cache_duration:
            return self.cached_vram

        try:
            # Query nvidia-smi for VRAM usage
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=memory.used,memory.total",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=2,
            )

            if result.returncode == 0:
                lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
                for line in lines:
                    parts = [part.strip() for part in line.split(",")]
                    if len(parts) < 2:
                        continue

                    try:
                        used = int(parts[0])
                        total = int(parts[1])
                    except ValueError:
                        logger.debug("Unable to parse VRAM usage from line: %s", line)
                        continue

                    if total <= 0:
                        logger.debug("Ignoring VRAM usage entry with non-positive total: %s", line)
                        continue

                    used_gb = used / 1024
                    total_gb = total / 1024
                    percentage = (used / total) * 100 if total else 0

                    self.cached_vram = {
                        "used_gb": round(used_gb, 1),
                        "total_gb": round(total_gb, 1),
                        "percentage": round(percentage, 1),
                        "available": True,
                    }
                    self.last_check = current_time
                    return self.cached_vram
        except Exception as e:
            logger.debug(f"VRAM check failed: {e}")

        # Return unavailable status if check failed
        return {"used_gb": 0, "total_gb": 16, "percentage": 0, "available": False}
