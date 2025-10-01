#!/usr/bin/env python3
"""
Test Workflow Manager

Quick test to verify workflow manager functionality.
"""

import sys
from core import WorkflowManager

def test_workflow_manager():
    """Test workflow manager basic functionality"""
    print("=" * 60)
    print("Testing Workflow Manager")
    print("=" * 60)

    # Initialize manager
    print("\n1. Initializing WorkflowManager...")
    wf_manager = WorkflowManager()
    print(f"✓ Initialized with {wf_manager.get_workflow_count()} workflows")

    # Check workflows loaded
    print("\n2. Listing workflows...")
    workflows = wf_manager.get_workflows_list()
    for wf in workflows:
        print(f"  - {wf['name']} ({wf['category']})")
        print(f"    {wf['description']}")

    # Get categories
    print("\n3. Categories...")
    categories = wf_manager.get_all_categories()
    print(f"  Categories: {', '.join(categories)}")

    # Get stats
    print("\n4. Statistics...")
    stats = wf_manager.get_stats()
    print(f"  Total workflows: {stats['total']}")
    print(f"  By category: {stats['categories']}")

    # Set current workflow
    print("\n5. Setting current workflow...")
    if workflows:
        filename = workflows[0]['filename']
        success = wf_manager.set_current_workflow(filename)
        if success:
            current = wf_manager.get_current_workflow()
            print(f"✓ Current workflow: {current.metadata.name}")
            print(f"  Nodes in workflow: {len(current.workflow_data.get('nodes', []))}")

    print("\n" + "=" * 60)
    print("✅ Workflow Manager test passed!")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    try:
        sys.exit(test_workflow_manager())
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
