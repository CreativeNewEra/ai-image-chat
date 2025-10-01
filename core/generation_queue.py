"""
Generation Queue Module

Manages batch image generation with queue system.
"""

import time
from datetime import datetime
from typing import List, Dict, Optional, Callable
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class JobStatus(Enum):
    """Status of a generation job"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GenerationJob:
    """Represents a single generation job in the queue"""

    _id_counter = 0  # Class variable to ensure unique IDs

    def __init__(self, prompt: str, width: int, height: int, steps: int, seed: int = -1):
        # Generate unique ID using timestamp + counter
        GenerationJob._id_counter += 1
        self.id = f"{int(time.time() * 1000)}_{GenerationJob._id_counter}"
        self.prompt = prompt
        self.width = width
        self.height = height
        self.steps = steps
        self.seed = seed
        self.status = JobStatus.PENDING
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.result_image = None
        self.result_seed = None

    def to_dict(self) -> Dict:
        """Convert job to dictionary for display"""
        return {
            "id": self.id,
            "prompt": self.prompt[:50] + "..." if len(self.prompt) > 50 else self.prompt,
            "settings": f"{self.width}x{self.height}, {self.steps} steps",
            "status": self.status.value,
            "seed": self.seed if self.seed != -1 else "random"
        }


class GenerationQueue:
    """Manages a queue of image generation jobs"""

    def __init__(self):
        self.jobs: List[GenerationJob] = []
        self.current_job: Optional[GenerationJob] = None
        self.is_processing = False
        self.paused = False

    def add_job(self, prompt: str, width: int, height: int, steps: int, seed: int = -1) -> str:
        """Add a job to the queue"""
        job = GenerationJob(prompt, width, height, steps, seed)
        self.jobs.append(job)
        logger.info(f"Added job {job.id} to queue")
        return job.id

    def add_batch_variations(self, prompt: str, width: int, height: int, steps: int,
                            seed: int, count: int = 4) -> List[str]:
        """Add multiple jobs with seed variations"""
        job_ids = []

        # Add original seed
        job_ids.append(self.add_job(prompt, width, height, steps, seed))

        # Add variations
        for i in range(1, count):
            variation_seed = seed + i
            job_ids.append(self.add_job(prompt, width, height, steps, variation_seed))

        logger.info(f"Added {count} seed variations to queue")
        return job_ids

    def get_next_job(self) -> Optional[GenerationJob]:
        """Get the next pending job"""
        for job in self.jobs:
            if job.status == JobStatus.PENDING:
                return job
        return None

    def get_job(self, job_id: str) -> Optional[GenerationJob]:
        """Get job by ID"""
        for job in self.jobs:
            if job.id == job_id:
                return job
        return None

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job"""
        job = self.get_job(job_id)
        if job and job.status == JobStatus.PENDING:
            job.status = JobStatus.CANCELLED
            logger.info(f"Cancelled job {job_id}")
            return True
        return False

    def clear_completed(self):
        """Remove completed, failed, and cancelled jobs"""
        original_count = len(self.jobs)
        self.jobs = [job for job in self.jobs
                    if job.status not in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]]
        removed = original_count - len(self.jobs)
        if removed > 0:
            logger.info(f"Cleared {removed} finished jobs")

    def clear_all(self):
        """Clear all jobs (except currently processing)"""
        if self.current_job and self.current_job.status == JobStatus.PROCESSING:
            self.jobs = [self.current_job]
        else:
            self.jobs = []
            self.current_job = None
        logger.info("Cleared all jobs")

    def pause(self):
        """Pause queue processing"""
        self.paused = True
        logger.info("Queue paused")

    def resume(self):
        """Resume queue processing"""
        self.paused = False
        logger.info("Queue resumed")

    def get_queue_status(self) -> Dict:
        """Get current queue status"""
        pending = sum(1 for job in self.jobs if job.status == JobStatus.PENDING)
        processing = sum(1 for job in self.jobs if job.status == JobStatus.PROCESSING)
        completed = sum(1 for job in self.jobs if job.status == JobStatus.COMPLETED)
        failed = sum(1 for job in self.jobs if job.status == JobStatus.FAILED)

        return {
            "total": len(self.jobs),
            "pending": pending,
            "processing": processing,
            "completed": completed,
            "failed": failed,
            "paused": self.paused,
            "current_job": self.current_job.to_dict() if self.current_job else None
        }

    def get_queue_display(self) -> str:
        """Get formatted queue status for display"""
        status = self.get_queue_status()

        if status["total"] == 0:
            return "Queue is empty"

        parts = []
        if status["pending"] > 0:
            parts.append(f"⏳ {status['pending']} pending")
        if status["processing"] > 0:
            parts.append(f"⚙️ {status['processing']} processing")
        if status["completed"] > 0:
            parts.append(f"✅ {status['completed']} completed")
        if status["failed"] > 0:
            parts.append(f"❌ {status['failed']} failed")

        if status["paused"]:
            parts.insert(0, "⏸️ PAUSED")

        return " | ".join(parts)

    def get_jobs_list(self) -> List[Dict]:
        """Get list of all jobs for display"""
        return [job.to_dict() for job in self.jobs]

    def estimate_time_remaining(self, avg_generation_time: float = 20.0) -> str:
        """Estimate time remaining for queue completion"""
        pending = sum(1 for job in self.jobs if job.status == JobStatus.PENDING)

        if pending == 0:
            return "No pending jobs"

        # Add current job if processing
        if self.current_job and self.current_job.status == JobStatus.PROCESSING:
            pending += 1

        total_seconds = pending * avg_generation_time

        if total_seconds < 60:
            return f"~{int(total_seconds)}s remaining"
        elif total_seconds < 3600:
            minutes = int(total_seconds / 60)
            return f"~{minutes}m remaining"
        else:
            hours = int(total_seconds / 3600)
            minutes = int((total_seconds % 3600) / 60)
            return f"~{hours}h {minutes}m remaining"
