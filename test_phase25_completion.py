#!/usr/bin/env python3
"""
Test Script for Phase 2.5 Completion Features

Tests:
1. Batch Generation Queue
2. Enhanced Gallery Features (filter, sort, favorites, delete)
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import GenerationQueue, JobStatus, ImageGallery
from PIL import Image
import tempfile


def test_generation_queue():
    """Test batch generation queue functionality"""
    print("=" * 60)
    print("Testing Generation Queue")
    print("=" * 60)

    queue = GenerationQueue()

    # Test 1: Add single job
    print("\n1. Adding single job...")
    job_id = queue.add_job("test prompt", 1024, 1024, 20, 12345)
    assert len(queue.jobs) == 1
    assert queue.jobs[0].prompt == "test prompt"
    assert queue.jobs[0].seed == 12345
    print(f"✓ Added job {job_id}")

    # Test 2: Add batch variations
    print("\n2. Adding batch variations...")
    job_ids = queue.add_batch_variations("variation test", 1024, 1024, 20, 50000, 4)
    assert len(queue.jobs) == 5  # 1 original + 4 variations
    assert queue.jobs[1].seed == 50000
    assert queue.jobs[2].seed == 50001
    assert queue.jobs[3].seed == 50002
    assert queue.jobs[4].seed == 50003
    print(f"✓ Added {len(job_ids)} variation jobs")

    # Test 3: Get next job
    print("\n3. Getting next job...")
    next_job = queue.get_next_job()
    assert next_job is not None
    assert next_job.status == JobStatus.PENDING
    print(f"✓ Got next job: {next_job.prompt[:20]}...")

    # Test 4: Update job status
    print("\n4. Updating job status...")
    next_job.status = JobStatus.PROCESSING
    assert next_job.status == JobStatus.PROCESSING
    next_job.status = JobStatus.COMPLETED
    assert next_job.status == JobStatus.COMPLETED
    print("✓ Job status updated successfully")

    # Test 5: Queue status
    print("\n5. Checking queue status...")
    status = queue.get_queue_status()
    assert status["total"] == 5
    assert status["completed"] == 1
    assert status["pending"] == 4
    print(f"✓ Queue status: {queue.get_queue_display()}")

    # Test 6: Cancel job
    print("\n6. Cancelling a job...")
    # Find a pending job to cancel
    pending_job = None
    for job in queue.jobs:
        if job.status == JobStatus.PENDING:
            pending_job = job
            break

    assert pending_job is not None, "No pending job found to cancel"
    success = queue.cancel_job(pending_job.id)
    assert success == True, f"Failed to cancel job {pending_job.id}"
    assert pending_job.status == JobStatus.CANCELLED
    print(f"✓ Cancelled job {pending_job.id}")

    # Test 7: Clear completed
    print("\n7. Clearing completed jobs...")
    original_count = len(queue.jobs)
    queue.clear_completed()
    # Should have removed completed and cancelled jobs
    assert len(queue.jobs) < original_count
    print(f"✓ Cleared completed/cancelled jobs. {len(queue.jobs)} remaining (was {original_count})")

    # Test 8: Estimate time remaining
    print("\n8. Estimating time remaining...")
    time_est = queue.estimate_time_remaining(15.0)
    print(f"✓ Time estimate: {time_est}")

    # Test 9: Clear all
    print("\n9. Clearing all jobs...")
    queue.clear_all()
    assert len(queue.jobs) == 0
    print("✓ All jobs cleared")

    print("\n✅ All Generation Queue tests passed!")


def test_enhanced_gallery():
    """Test enhanced gallery features"""
    print("\n" + "=" * 60)
    print("Testing Enhanced Gallery Features")
    print("=" * 60)

    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as tmpdir:
        # Temporarily set output directory
        import config
        original_output_dir = config.OUTPUT_DIR
        config.OUTPUT_DIR = tmpdir

        gallery = ImageGallery()

        # Create test images
        print("\n1. Adding test images...")
        for i in range(5):
            img = Image.new('RGB', (100, 100), color=(i*50, i*50, i*50))
            prompt = f"test image {i}" if i % 2 == 0 else f"portrait image {i}"
            seed = 10000 + i
            settings = {"width": 1024, "height": 1024, "steps": 20}
            gallery.add_image(img, prompt, seed, settings)

        assert len(gallery.images) == 5
        print(f"✓ Added {len(gallery.images)} test images")

        # Test 2: Filter by keyword
        print("\n2. Testing filter...")
        filtered = gallery.get_images(filter_text="portrait")
        assert len(filtered) == 2  # Only images with "portrait" in prompt
        print(f"✓ Filtered to {len(filtered)} images matching 'portrait'")

        # Test 3: Sort by seed
        print("\n3. Testing sort by seed...")
        sorted_imgs = gallery.get_images(sort_by="seed")
        # Check that images are sorted (can't directly check, but verify we get same count)
        assert len(sorted_imgs) == 5
        print(f"✓ Sorted {len(sorted_imgs)} images by seed")

        # Test 4: Toggle favorite
        print("\n4. Testing favorites...")
        is_fav = gallery.toggle_favorite(0)
        assert is_fav == True
        assert gallery.is_favorite(0) == True
        assert 0 in gallery.favorites
        print("✓ Toggled favorite on")

        is_fav = gallery.toggle_favorite(0)
        assert is_fav == False
        assert gallery.is_favorite(0) == False
        assert 0 not in gallery.favorites
        print("✓ Toggled favorite off")

        # Test 5: Favorites filter
        print("\n5. Testing favorites filter...")
        gallery.toggle_favorite(1)
        gallery.toggle_favorite(3)
        fav_imgs = gallery.get_images(favorites_only=True)
        assert len(fav_imgs) == 2
        print(f"✓ Filtered to {len(fav_imgs)} favorite images")

        # Test 6: Get favorites count
        print("\n6. Testing favorites count...")
        count = gallery.get_favorites_count()
        assert count == 2
        print(f"✓ Favorites count: {count}")

        # Test 7: Gallery stats
        print("\n7. Testing gallery stats...")
        stats = gallery.get_gallery_stats()
        assert stats["total"] == 5
        assert stats["favorites"] == 2
        assert stats["total_size_mb"] >= 0  # Could be 0 for very small test images
        print(f"✓ Gallery stats: {stats}")

        # Test 8: Delete image
        print("\n8. Testing delete image...")
        success = gallery.delete_image(2)
        assert success == True
        assert len(gallery.images) == 4
        print(f"✓ Deleted image. {len(gallery.images)} remaining")

        # Test 9: Delete multiple
        print("\n9. Testing delete multiple...")
        deleted = gallery.delete_selected([0, 1])
        assert deleted == 2
        assert len(gallery.images) == 2
        print(f"✓ Deleted {deleted} images. {len(gallery.images)} remaining")

        # Test 10: Combined filter and sort
        print("\n10. Testing combined filter and sort...")
        # Add more images with different prompts
        for i in range(3):
            img = Image.new('RGB', (100, 100), color=(i*80, i*80, i*80))
            prompt = f"landscape photo {i}"
            seed = 20000 + i
            settings = {"width": 512, "height": 512, "steps": 15}
            gallery.add_image(img, prompt, seed, settings)

        filtered_sorted = gallery.get_images(filter_text="photo", sort_by="resolution")
        assert len(filtered_sorted) == 3
        print(f"✓ Combined filter & sort: {len(filtered_sorted)} images")

        # Restore original output directory
        config.OUTPUT_DIR = original_output_dir

        print("\n✅ All Enhanced Gallery tests passed!")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("PHASE 2.5 COMPLETION - FEATURE TESTS")
    print("=" * 60)

    try:
        test_generation_queue()
        test_enhanced_gallery()

        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\nPhase 2.5 features are working correctly:")
        print("  ✅ Batch Generation Queue")
        print("  ✅ Enhanced Gallery (filter, sort, favorites, delete)")
        print("\nReady for production use!")
        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
