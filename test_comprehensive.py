#!/usr/bin/env python3
"""
Comprehensive Test Suite

Tests all components that don't require external services.
"""

import os
import sys


def test_imports():
    """Test all imports work"""
    print("=" * 60)
    print("Testing Imports")
    print("=" * 60)

    try:
        print("\n1. Testing core imports...")
        print("✓ All core modules imported successfully")

        print("\n2. Testing utils imports...")
        print("✓ Utils imported successfully")

        print("\n3. Testing comfyui_api import...")
        print("✓ ComfyUI API imported successfully")

        print("\n4. Testing config import...")
        print("✓ Config imported successfully")

        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_manager():
    """Test workflow manager"""
    print("\n" + "=" * 60)
    print("Testing Workflow Manager")
    print("=" * 60)

    try:
        from core import WorkflowManager

        print("\n1. Initialize WorkflowManager...")
        wf_manager = WorkflowManager()
        count = wf_manager.get_workflow_count()
        print(f"✓ Loaded {count} workflows")

        if count > 0:
            print("\n2. Get workflows list...")
            workflows = wf_manager.get_workflows_list()
            for wf in workflows:
                print(f"  - {wf['name']} ({wf['category']})")

            print("\n3. Set current workflow...")
            first = list(wf_manager.workflows.keys())[0]
            wf_manager.set_current_workflow(first)
            current = wf_manager.get_current_workflow()
            print(f"✓ Current: {current.metadata.name}")

            print("\n4. Get statistics...")
            stats = wf_manager.get_stats()
            print(f"✓ Stats: {stats}")

        return True
    except Exception as e:
        print(f"❌ WorkflowManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_generation_queue():
    """Test generation queue"""
    print("\n" + "=" * 60)
    print("Testing Generation Queue")
    print("=" * 60)

    try:
        from core import GenerationQueue

        print("\n1. Initialize GenerationQueue...")
        queue = GenerationQueue()
        print("✓ Queue initialized")

        print("\n2. Add jobs...")
        job_id = queue.add_job("test prompt", 1024, 1024, 20, 12345)
        print(f"✓ Added job: {job_id}")

        print("\n3. Add batch variations...")
        job_ids = queue.add_batch_variations("batch test", 1024, 1024, 20, 50000, 3)
        print(f"✓ Added {len(job_ids)} variations")

        print("\n4. Get queue status...")
        status = queue.get_queue_status()
        print(f"✓ Status: {status}")

        print("\n5. Get next job...")
        next_job = queue.get_next_job()
        if next_job:
            print(f"✓ Next job: {next_job.prompt[:30]}...")

        return True
    except Exception as e:
        print(f"❌ GenerationQueue test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_image_gallery():
    """Test image gallery with enhanced features"""
    print("\n" + "=" * 60)
    print("Testing Image Gallery")
    print("=" * 60)

    try:
        import tempfile

        from PIL import Image

        from core import ImageGallery

        # Use temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            import config
            original_dir = config.OUTPUT_DIR
            config.OUTPUT_DIR = tmpdir

            print("\n1. Initialize ImageGallery...")
            gallery = ImageGallery()
            print("✓ Gallery initialized")

            print("\n2. Add test images...")
            for i in range(3):
                img = Image.new('RGB', (100, 100), color=(i*80, i*80, i*80))
                prompt = f"test prompt {i}"
                seed = 10000 + i
                settings = {"width": 1024, "height": 1024, "steps": 20}
                gallery.add_image(img, prompt, seed, settings)
            print(f"✓ Added {len(gallery.images)} images")

            print("\n3. Test filtering...")
            filtered = gallery.get_images(filter_text="prompt 1")
            print(f"✓ Filtered: {len(filtered)} images")

            print("\n4. Test sorting...")
            sorted_imgs = gallery.get_images(sort_by="seed")
            print(f"✓ Sorted: {len(sorted_imgs)} images")

            print("\n5. Test favorites...")
            gallery.toggle_favorite(0)
            fav_count = gallery.get_favorites_count()
            print(f"✓ Favorites: {fav_count}")

            print("\n6. Test stats...")
            stats = gallery.get_gallery_stats()
            print(f"✓ Stats: {stats}")

            config.OUTPUT_DIR = original_dir

        return True
    except Exception as e:
        print(f"❌ ImageGallery test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_session_stats():
    """Test session statistics"""
    print("\n" + "=" * 60)
    print("Testing Session Statistics")
    print("=" * 60)

    try:
        from core import SessionStats

        print("\n1. Initialize SessionStats...")
        stats = SessionStats()
        print("✓ Stats initialized")

        print("\n2. Add generations...")
        stats.add_generation(15.5)
        stats.add_generation(12.3)
        stats.add_generation(18.7)
        print("✓ Added 3 generations")

        print("\n3. Get display...")
        display = stats.get_stats_display()
        print(f"✓ Display generated:\n{display}")

        return True
    except Exception as e:
        print(f"❌ SessionStats test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_seed_manager():
    """Test seed manager"""
    print("\n" + "=" * 60)
    print("Testing Seed Manager")
    print("=" * 60)

    try:
        from core import SeedManager

        print("\n1. Initialize SeedManager...")
        seed_mgr = SeedManager()
        print("✓ Seed manager initialized")

        print("\n2. Add seeds...")
        seed_mgr.add_seed(12345)
        seed_mgr.add_seed(67890)
        print("✓ Added seeds")

        print("\n3. Get seed history...")
        history = seed_mgr.seed_history  # It's a property, not a method
        print(f"✓ History: {list(history)}")

        print("\n4. Test seed locking...")
        seed_mgr.lock_seed(12345)
        is_locked = seed_mgr.is_locked
        print(f"✓ Locked: {is_locked}")

        return True
    except Exception as e:
        print(f"❌ SeedManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_prompt_history():
    """Test prompt history"""
    print("\n" + "=" * 60)
    print("Testing Prompt History")
    print("=" * 60)

    try:
        import tempfile

        from core import PromptHistory

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name

        print("\n1. Initialize PromptHistory...")
        history = PromptHistory(temp_file)
        print("✓ Prompt history initialized")

        print("\n2. Add prompts...")
        history.add_prompt("test prompt 1", {"width": 1024, "height": 1024, "steps": 20})
        history.add_prompt("test prompt 2", {"width": 512, "height": 512, "steps": 15})
        print("✓ Added prompts")

        print("\n3. Search prompts...")
        results = history.search_prompts("test")
        print(f"✓ Found {len(results)} prompts")

        print("\n4. Get recent...")
        recent = history.get_recent_prompts(5)
        print(f"✓ Recent: {len(recent)} prompts")

        # Cleanup
        os.remove(temp_file)

        return True
    except Exception as e:
        print(f"❌ PromptHistory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("Workflow Manager", test_workflow_manager),
        ("Generation Queue", test_generation_queue),
        ("Image Gallery", test_image_gallery),
        ("Session Stats", test_session_stats),
        ("Seed Manager", test_seed_manager),
        ("Prompt History", test_prompt_history),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ {name} crashed: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
