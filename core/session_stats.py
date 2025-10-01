"""
Session Statistics Module

Tracks generation performance metrics for the current session.
"""

from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class SessionStats:
    """
    Track generation statistics for the session.

    Maintains metrics like total images, generation times, and compute totals.
    """

    def __init__(self) -> None:
        self.session_start: datetime = datetime.now()
        self.total_images: int = 0
        self.generation_times: List[float] = []
        self.total_compute_time: float = 0

    def add_generation(self, generation_time: float) -> None:
        """
        Record a completed generation.

        Args:
            generation_time: Time taken to generate image in seconds
        """
        self.total_images += 1
        self.generation_times.append(generation_time)
        self.total_compute_time += generation_time

    def get_stats(self) -> Dict[str, float]:
        """
        Get formatted statistics.

        Returns:
            Dictionary containing total_images, avg_time, fastest, slowest,
            total_time, and session_duration
        """
        if self.total_images == 0:
            return {
                'total_images': 0,
                'avg_time': 0,
                'fastest': 0,
                'slowest': 0,
                'total_time': 0,
                'session_duration': 0
            }

        session_duration = (datetime.now() - self.session_start).total_seconds()

        return {
            'total_images': self.total_images,
            'avg_time': round(sum(self.generation_times) / len(self.generation_times), 1),
            'fastest': round(min(self.generation_times), 1),
            'slowest': round(max(self.generation_times), 1),
            'total_time': round(self.total_compute_time, 1),
            'session_duration': round(session_duration / 60, 1)  # in minutes
        }

    def get_stats_display(self) -> str:
        """
        Get formatted stats string for display.

        Returns:
            Markdown-formatted string with session statistics
        """
        stats = self.get_stats()

        if stats['total_images'] == 0:
            return "📊 **Session Stats**: No images generated yet"

        return f"""📊 **Session Stats**
• Generated: {stats['total_images']} image{'s' if stats['total_images'] != 1 else ''}
• Average time: {stats['avg_time']}s
• Fastest: {stats['fastest']}s | Slowest: {stats['slowest']}s
• Total compute: {stats['total_time']}s
• Session duration: {stats['session_duration']} min"""
