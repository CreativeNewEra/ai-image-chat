"""
Workflow Manager Module

Manages multiple ComfyUI workflows with metadata and categorization.
"""

import os
import json
import shutil
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class WorkflowMetadata:
    """Metadata for a workflow"""

    def __init__(self, name: str, description: str = "", category: str = "General",
                 tags: List[str] = None, author: str = "Unknown",
                 created_at: str = None, modified_at: str = None):
        self.name = name
        self.description = description
        self.category = category
        self.tags = tags or []
        self.author = author
        self.created_at = created_at or datetime.now().isoformat()
        self.modified_at = modified_at or datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "tags": self.tags,
            "author": self.author,
            "created_at": self.created_at,
            "modified_at": self.modified_at
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary"""
        return cls(
            name=data.get("name", "Untitled"),
            description=data.get("description", ""),
            category=data.get("category", "General"),
            tags=data.get("tags", []),
            author=data.get("author", "Unknown"),
            created_at=data.get("created_at"),
            modified_at=data.get("modified_at")
        )


class Workflow:
    """Represents a ComfyUI workflow with metadata"""

    def __init__(self, filename: str, workflow_data: Dict, metadata: WorkflowMetadata):
        self.filename = filename
        self.workflow_data = workflow_data
        self.metadata = metadata

    def get_display_name(self) -> str:
        """Get formatted display name"""
        return f"{self.metadata.name} ({self.metadata.category})"

    def get_short_description(self) -> str:
        """Get short description for display"""
        desc = self.metadata.description
        if len(desc) > 100:
            return desc[:97] + "..."
        return desc if desc else "No description"

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            "filename": self.filename,
            "metadata": self.metadata.to_dict()
        }


class WorkflowManager:
    """Manages multiple ComfyUI workflows"""

    def __init__(self, workflows_dir: str = "./workflows"):
        self.workflows_dir = Path(workflows_dir)
        self.workflows: Dict[str, Workflow] = {}  # filename -> Workflow
        self.current_workflow_name: Optional[str] = None

        # Create workflows directory if it doesn't exist
        self.workflows_dir.mkdir(exist_ok=True)

        # Create subdirectories for organization
        (self.workflows_dir / "text2img").mkdir(exist_ok=True)
        (self.workflows_dir / "img2img").mkdir(exist_ok=True)
        (self.workflows_dir / "controlnet").mkdir(exist_ok=True)
        (self.workflows_dir / "upscale").mkdir(exist_ok=True)
        (self.workflows_dir / "custom").mkdir(exist_ok=True)

        # Load existing workflows
        self.load_all_workflows()

    def load_all_workflows(self):
        """Load all workflows from the workflows directory"""
        logger.info(f"Loading workflows from {self.workflows_dir}")

        # Scan for JSON files
        json_files = list(self.workflows_dir.rglob("*.json"))

        for json_file in json_files:
            # Skip metadata files
            if json_file.stem.endswith("_meta"):
                continue

            try:
                self._load_workflow_from_file(json_file)
            except Exception as e:
                logger.error(f"Failed to load workflow {json_file}: {e}")

        logger.info(f"Loaded {len(self.workflows)} workflows")

    def _load_workflow_from_file(self, filepath: Path):
        """Load a single workflow from file"""
        with open(filepath, 'r') as f:
            workflow_data = json.load(f)

        # Look for metadata file
        meta_file = filepath.parent / f"{filepath.stem}_meta.json"
        if meta_file.exists():
            with open(meta_file, 'r') as f:
                meta_data = json.load(f)
            metadata = WorkflowMetadata.from_dict(meta_data)
        else:
            # Create default metadata
            metadata = WorkflowMetadata(
                name=filepath.stem.replace("_", " ").title(),
                description=f"Workflow loaded from {filepath.name}",
                category=self._infer_category(filepath)
            )

        filename = filepath.name
        workflow = Workflow(filename, workflow_data, metadata)
        self.workflows[filename] = workflow

        logger.info(f"✓ Loaded workflow: {workflow.metadata.name}")

    def _infer_category(self, filepath: Path) -> str:
        """Infer category from file path"""
        # Check parent directory
        parent_name = filepath.parent.name.lower()

        if "text2img" in parent_name or "txt2img" in parent_name:
            return "Text2Image"
        elif "img2img" in parent_name:
            return "Image2Image"
        elif "controlnet" in parent_name:
            return "ControlNet"
        elif "upscal" in parent_name:
            return "Upscale"
        else:
            return "General"

    def add_workflow(self, filepath: str, metadata: WorkflowMetadata,
                    category_folder: str = "custom") -> bool:
        """Add a new workflow from file"""
        try:
            source_path = Path(filepath)
            if not source_path.exists():
                logger.error(f"Workflow file not found: {filepath}")
                return False

            # Determine destination
            dest_dir = self.workflows_dir / category_folder
            dest_dir.mkdir(exist_ok=True)

            # Copy workflow file
            dest_path = dest_dir / source_path.name
            shutil.copy2(source_path, dest_path)

            # Save metadata
            meta_path = dest_dir / f"{source_path.stem}_meta.json"
            with open(meta_path, 'w') as f:
                json.dump(metadata.to_dict(), f, indent=2)

            # Load into manager
            self._load_workflow_from_file(dest_path)

            logger.info(f"✓ Added workflow: {metadata.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to add workflow: {e}")
            return False

    def get_workflow(self, filename: str) -> Optional[Workflow]:
        """Get workflow by filename"""
        return self.workflows.get(filename)

    def get_current_workflow(self) -> Optional[Workflow]:
        """Get currently selected workflow"""
        if self.current_workflow_name:
            return self.workflows.get(self.current_workflow_name)
        return None

    def set_current_workflow(self, filename: str) -> bool:
        """Set current workflow"""
        if filename in self.workflows:
            self.current_workflow_name = filename
            logger.info(f"✓ Switched to workflow: {self.workflows[filename].metadata.name}")
            return True
        logger.error(f"Workflow not found: {filename}")
        return False

    def get_workflows_by_category(self, category: str) -> List[Workflow]:
        """Get all workflows in a category"""
        return [wf for wf in self.workflows.values() if wf.metadata.category == category]

    def get_all_categories(self) -> List[str]:
        """Get list of all categories"""
        categories = set(wf.metadata.category for wf in self.workflows.values())
        return sorted(categories)

    def get_workflows_list(self) -> List[Dict]:
        """Get list of workflows for display"""
        return [
            {
                "filename": filename,
                "name": wf.metadata.name,
                "category": wf.metadata.category,
                "description": wf.get_short_description(),
                "tags": wf.metadata.tags
            }
            for filename, wf in self.workflows.items()
        ]

    def search_workflows(self, query: str) -> List[Workflow]:
        """Search workflows by name, description, or tags"""
        query_lower = query.lower()
        results = []

        for wf in self.workflows.values():
            # Check name
            if query_lower in wf.metadata.name.lower():
                results.append(wf)
                continue

            # Check description
            if query_lower in wf.metadata.description.lower():
                results.append(wf)
                continue

            # Check tags
            if any(query_lower in tag.lower() for tag in wf.metadata.tags):
                results.append(wf)

        return results

    def delete_workflow(self, filename: str) -> bool:
        """Delete a workflow"""
        if filename not in self.workflows:
            return False

        try:
            workflow = self.workflows[filename]

            # Find and delete files
            for json_file in self.workflows_dir.rglob(filename):
                # Delete workflow file
                json_file.unlink()

                # Delete metadata file
                meta_file = json_file.parent / f"{json_file.stem}_meta.json"
                if meta_file.exists():
                    meta_file.unlink()

            # Remove from memory
            del self.workflows[filename]

            # Clear current if it was deleted
            if self.current_workflow_name == filename:
                self.current_workflow_name = None

            logger.info(f"✓ Deleted workflow: {workflow.metadata.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete workflow: {e}")
            return False

    def export_workflow(self, filename: str, export_path: str) -> bool:
        """Export a workflow with metadata"""
        if filename not in self.workflows:
            return False

        try:
            workflow = self.workflows[filename]

            # Create export package
            export_data = {
                "workflow": workflow.workflow_data,
                "metadata": workflow.metadata.to_dict(),
                "export_date": datetime.now().isoformat(),
                "format_version": "1.0"
            }

            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)

            logger.info(f"✓ Exported workflow to: {export_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export workflow: {e}")
            return False

    def import_workflow(self, import_path: str) -> bool:
        """Import a workflow from exported package"""
        try:
            with open(import_path, 'r') as f:
                package = json.load(f)

            # Check if it's an exported package or raw workflow
            if "metadata" in package and "workflow" in package:
                # Exported package
                workflow_data = package["workflow"]
                metadata = WorkflowMetadata.from_dict(package["metadata"])
            else:
                # Raw workflow - create default metadata
                workflow_data = package
                filename = Path(import_path).stem
                metadata = WorkflowMetadata(
                    name=filename.replace("_", " ").title(),
                    description=f"Imported from {import_path}"
                )

            # Generate unique filename
            base_name = metadata.name.lower().replace(" ", "_")
            filename = f"{base_name}.json"
            counter = 1
            while filename in self.workflows:
                filename = f"{base_name}_{counter}.json"
                counter += 1

            # Save to custom folder
            dest_path = self.workflows_dir / "custom" / filename
            with open(dest_path, 'w') as f:
                json.dump(workflow_data, f, indent=2)

            # Save metadata
            meta_path = self.workflows_dir / "custom" / f"{Path(filename).stem}_meta.json"
            with open(meta_path, 'w') as f:
                json.dump(metadata.to_dict(), f, indent=2)

            # Load into manager
            self._load_workflow_from_file(dest_path)

            logger.info(f"✓ Imported workflow: {metadata.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to import workflow: {e}")
            return False

    def get_workflow_count(self) -> int:
        """Get total number of workflows"""
        return len(self.workflows)

    def get_stats(self) -> Dict:
        """Get workflow statistics"""
        categories = {}
        for wf in self.workflows.values():
            cat = wf.metadata.category
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "total": len(self.workflows),
            "categories": categories,
            "current": self.current_workflow_name
        }
