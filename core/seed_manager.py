"""
Seed Management Module

Manages seed history, variations, and locking for reproducible image generation.
"""

import logging

logger = logging.getLogger(__name__)


class SeedManager:
    """Manage seed history and variations"""

    def __init__(self):
        self.seed_history = []  # List of seeds used
        self.max_history = 10
        self.locked_seed = None  # Locked seed value
        self.is_locked = False

    def add_seed(self, seed):
        """Add seed to history"""
        if seed is not None and seed not in self.seed_history:
            self.seed_history.insert(0, seed)
            if len(self.seed_history) > self.max_history:
                self.seed_history.pop()

    def get_history(self):
        """Get seed history as list"""
        return self.seed_history

    def lock_seed(self, seed):
        """Lock a specific seed"""
        self.locked_seed = seed
        self.is_locked = True

    def unlock_seed(self):
        """Unlock seed"""
        self.is_locked = False
        self.locked_seed = None

    def get_seed_for_generation(self, requested_seed=None):
        """Get seed to use for generation"""
        if self.is_locked and self.locked_seed is not None:
            return self.locked_seed
        return requested_seed
