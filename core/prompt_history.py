"""
Prompt History Module

Manages prompt history with search, tagging, export/import functionality.
"""

import os
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PromptHistory:
    """Manage prompt history with search, tagging, and export"""

    def __init__(self, history_file='prompt_history.json'):
        self.prompts = []  # List of prompt entries
        self.max_history = 50
        self.history_file = history_file
        self.load_from_file()

    def load_from_file(self):
        """Load prompt history from JSON file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.prompts = data.get('prompts', [])
            except Exception as e:
                logger.error(f"Error loading prompt history: {e}")
                self.prompts = []

    def save_to_file(self):
        """Save prompt history to JSON file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump({'prompts': self.prompts}, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving prompt history: {e}")

    def add_prompt(self, prompt_text, settings=None):
        """Add a prompt to history"""
        if not prompt_text or len(prompt_text) < 10:
            return

        # Check if prompt already exists (avoid exact duplicates)
        for entry in self.prompts:
            if entry['prompt'] == prompt_text:
                # Update timestamp and count
                entry['last_used'] = datetime.now().isoformat()
                entry['use_count'] = entry.get('use_count', 1) + 1
                self.save_to_file()
                return

        # Add new prompt
        entry = {
            'prompt': prompt_text,
            'timestamp': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat(),
            'use_count': 1,
            'settings': settings or {},
            'tags': []
        }

        self.prompts.insert(0, entry)

        # Limit history size
        if len(self.prompts) > self.max_history:
            self.prompts = self.prompts[:self.max_history]

        self.save_to_file()

    def get_recent_prompts(self, limit=10):
        """Get recent prompts"""
        return self.prompts[:limit]

    def search_prompts(self, query):
        """Search prompts by keyword"""
        if not query:
            return self.prompts

        query_lower = query.lower()
        results = [
            entry for entry in self.prompts
            if query_lower in entry['prompt'].lower()
            or any(query_lower in tag.lower() for tag in entry.get('tags', []))
        ]
        return results

    def get_dropdown_choices(self, limit=10):
        """Get formatted choices for dropdown"""
        choices = []
        for entry in self.prompts[:limit]:
            # Truncate long prompts for display
            prompt = entry['prompt']
            if len(prompt) > 60:
                prompt = prompt[:60] + "..."

            use_info = f" ({entry['use_count']}x)" if entry.get('use_count', 1) > 1 else ""
            choices.append(f"{prompt}{use_info}")

        return choices

    def get_prompt_by_display_text(self, display_text):
        """Get full prompt from dropdown display text"""
        # Remove the use count suffix
        clean_text = display_text.split(" (")[0]

        # Find matching prompt
        for entry in self.prompts:
            if entry['prompt'].startswith(clean_text.rstrip(".")):
                return entry['prompt']

        return display_text

    def export_prompts(self, filepath=None):
        """Export prompt history to JSON file"""
        if filepath is None:
            filepath = f"prompt_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(filepath, 'w') as f:
                json.dump({'prompts': self.prompts}, f, indent=2)
            return f"✅ Exported {len(self.prompts)} prompts to {filepath}"
        except Exception as e:
            return f"❌ Export failed: {e}"

    def import_prompts(self, filepath):
        """Import prompts from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                imported = data.get('prompts', [])

                # Merge with existing, avoiding duplicates
                for entry in imported:
                    prompt_text = entry.get('prompt', '')
                    if prompt_text:
                        # Check if already exists
                        exists = any(p['prompt'] == prompt_text for p in self.prompts)
                        if not exists:
                            self.prompts.append(entry)

                # Limit size
                if len(self.prompts) > self.max_history:
                    self.prompts = self.prompts[:self.max_history]

                self.save_to_file()
                return f"✅ Imported {len(imported)} prompts"
        except Exception as e:
            return f"❌ Import failed: {e}"
