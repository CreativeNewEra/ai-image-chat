"""
VRAM Monitoring Module

Provides real-time GPU VRAM usage monitoring via nvidia-smi with caching.
"""

import time
import subprocess
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class VRAMMonitor:
    """
    Monitor GPU VRAM usage via nvidia-smi.

    Caches results for 2 seconds to minimize polling overhead.
    """

    def __init__(self) -> None:
        self.last_check: float = 0
        self.cache_duration: int = 2  # Cache for 2 seconds
        self.cached_vram: Optional[Dict[str, float]] = None

    def get_vram_usage(self) -> Dict[str, float]:
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
                ['nvidia-smi', '--query-gpu=memory.used,memory.total', '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                used, total = map(int, result.stdout.strip().split(','))
                used_gb = used / 1024
                total_gb = total / 1024
                percentage = (used / total) * 100

                self.cached_vram = {
                    'used_gb': round(used_gb, 1),
                    'total_gb': round(total_gb, 1),
                    'percentage': round(percentage, 1),
                    'available': True
                }
                self.last_check = current_time
                return self.cached_vram
        except Exception as e:
            logger.debug(f"VRAM check failed: {e}")

        # Return unavailable status if check failed
        return {'used_gb': 0, 'total_gb': 16, 'percentage': 0, 'available': False}
