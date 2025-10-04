#!/usr/bin/env python
"""
Test script for automatic mode switching functionality
"""

import sys
from core import Mode, ModeManager, VRAMMonitor
from comfyui_api import comfy

def test_auto_mode_switching():
    """Test the automatic mode switching logic"""

    print("=" * 60)
    print("Testing Automatic Mode Switching")
    print("=" * 60)

    # Initialize components
    vram_monitor = VRAMMonitor()
    mode_manager = ModeManager(vram_monitor, comfy)

    # Test 1: Start in IDLE mode
    print("\n1. Starting state:")
    print(f"   Current mode: {mode_manager.get_mode()}")
    assert mode_manager.get_mode() == Mode.IDLE, "Should start in IDLE mode"
    print("   ✅ PASSED")

    # Test 2: Auto-switch to CHAT mode
    print("\n2. Testing auto-switch to CHAT mode:")
    if mode_manager.get_mode() != Mode.CHAT:
        print("   Switching to CHAT mode...")
        status = mode_manager.switch_to_chat()
        print(f"   Status: {status}")
        print(f"   Current mode: {mode_manager.get_mode()}")
        assert mode_manager.get_mode() == Mode.CHAT, "Should be in CHAT mode"
        print("   ✅ PASSED")

    # Test 3: Auto-switch to GENERATE mode
    print("\n3. Testing auto-switch to GENERATE mode:")
    if mode_manager.get_mode() != Mode.GENERATE:
        print("   Switching to GENERATE mode...")
        status = mode_manager.switch_to_generate()
        print(f"   Status: {status}")
        print(f"   Current mode: {mode_manager.get_mode()}")
        assert mode_manager.get_mode() == Mode.GENERATE, "Should be in GENERATE mode"
        print("   ✅ PASSED")

    # Test 4: Return to IDLE
    print("\n4. Testing return to IDLE:")
    print("   Switching to IDLE mode...")
    status = mode_manager.switch_to_idle()
    print(f"   Status: {status}")
    print(f"   Current mode: {mode_manager.get_mode()}")
    assert mode_manager.get_mode() == Mode.IDLE, "Should be in IDLE mode"
    print("   ✅ PASSED")

    print("\n" + "=" * 60)
    print("All tests PASSED! ✅")
    print("=" * 60)

    return True

if __name__ == "__main__":
    try:
        success = test_auto_mode_switching()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
