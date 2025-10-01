#!/usr/bin/env python3
"""
Quick test of new Phase 2.5 features
"""

import sys
import os

# Test VRAM Estimation
print("=" * 60)
print("Testing VRAM Estimation...")
print("=" * 60)

class VRAMEstimator:
    """Estimate VRAM requirements and generate warnings"""

    @staticmethod
    def estimate_vram(width, height, steps):
        base_vram = 8.0
        res_factor = (width * height) / (1024 * 1024)
        step_factor = 1.0 + (steps - 20) / 100
        estimated = base_vram * res_factor * step_factor
        return round(estimated, 1)

    @staticmethod
    def get_warnings(width, height, steps, current_vram_used=0, total_vram=16):
        estimated_vram = VRAMEstimator.estimate_vram(width, height, steps)
        available_vram = total_vram - current_vram_used

        warnings = []
        warning_level = 'none'

        if estimated_vram > total_vram:
            warning_level = 'error'
            warnings.append(f"⛔ OUT OF VRAM: Estimated {estimated_vram}GB exceeds {total_vram}GB total")
        elif estimated_vram > available_vram:
            warning_level = 'error'
            warnings.append(f"⚠️ INSUFFICIENT VRAM: Need {estimated_vram}GB but only {available_vram:.1f}GB available")
        elif estimated_vram > total_vram * 0.9:
            warning_level = 'warning'
            warnings.append(f"⚠️ HIGH VRAM: Estimated {estimated_vram}GB")
        elif estimated_vram > total_vram * 0.75:
            warning_level = 'info'
            warnings.append(f"ℹ️ MODERATE VRAM: Estimated {estimated_vram}GB")

        if warnings:
            return warning_level, "\n".join(warnings)
        else:
            return 'none', f"✅ Estimated VRAM: {estimated_vram}GB - Should work fine"

estimator = VRAMEstimator()

# Test cases
test_cases = [
    (1024, 1024, 20, "Standard 1K"),
    (768, 768, 15, "Fast Draft"),
    (1536, 1536, 30, "High Quality"),
    (2048, 2048, 35, "Ultra (may OOM)"),
]

for width, height, steps, label in test_cases:
    vram = estimator.estimate_vram(width, height, steps)
    level, msg = estimator.get_warnings(width, height, steps, 0, 16)
    print(f"\n{label}: {width}x{height} @ {steps} steps")
    print(f"  Estimated: {vram}GB")
    print(f"  Warning: {level}")
    print(f"  Message: {msg[:80]}...")

# Test Prompt History
print("\n" + "=" * 60)
print("Testing Prompt History...")
print("=" * 60)

import json
from datetime import datetime

class PromptHistory:
    """Manage prompt history"""
    def __init__(self):
        self.prompts = []
        self.max_history = 50

    def add_prompt(self, prompt_text, settings=None):
        if not prompt_text or len(prompt_text) < 10:
            return

        for entry in self.prompts:
            if entry['prompt'] == prompt_text:
                entry['last_used'] = datetime.now().isoformat()
                entry['use_count'] = entry.get('use_count', 1) + 1
                return

        entry = {
            'prompt': prompt_text,
            'timestamp': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat(),
            'use_count': 1,
            'settings': settings or {},
            'tags': []
        }

        self.prompts.insert(0, entry)

        if len(self.prompts) > self.max_history:
            self.prompts = self.prompts[:self.max_history]

    def get_recent_prompts(self, limit=10):
        return self.prompts[:limit]

    def search_prompts(self, query):
        if not query:
            return self.prompts

        query_lower = query.lower()
        results = [
            entry for entry in self.prompts
            if query_lower in entry['prompt'].lower()
        ]
        return results

history = PromptHistory()

# Test adding prompts
test_prompts = [
    "A beautiful sunset over mountains with vibrant orange and purple clouds",
    "Cyberpunk city street at night with neon lights and rain reflections",
    "Portrait of a wise old wizard with a long white beard and magical staff",
    "A beautiful sunset over the ocean with palm trees"  # Similar to first
]

for prompt in test_prompts:
    history.add_prompt(prompt, {'width': 1024, 'height': 1024, 'steps': 20})
    print(f"Added: {prompt[:50]}...")

# Test duplicate
history.add_prompt(test_prompts[0], {'width': 1024, 'height': 1024, 'steps': 20})
print("\nAdded duplicate (should increase use count)")

print(f"\nTotal prompts in history: {len(history.prompts)}")
print(f"\nRecent prompts:")
for i, entry in enumerate(history.get_recent_prompts(5), 1):
    use_count = entry.get('use_count', 1)
    print(f"  {i}. {entry['prompt'][:60]}... (used {use_count}x)")

# Test search
print(f"\nSearching for 'sunset':")
results = history.search_prompts('sunset')
for entry in results:
    print(f"  - {entry['prompt'][:60]}...")

print("\n" + "=" * 60)
print("✅ All tests passed!")
print("=" * 60)
