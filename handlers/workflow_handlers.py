"""
Workflow management event handlers.

This module contains event handlers for workflow selection, import/export,
and category filtering.
"""

import logging

import gradio as gr

logger = logging.getLogger(__name__)


def get_workflow_info_display(workflow_manager):
    """
    Get formatted workflow info for display.

    Args:
        workflow_manager: WorkflowManager instance

    Returns:
        str: Formatted workflow information
    """
    current = workflow_manager.get_current_workflow()
    if not current:
        return "No workflow selected"

    info = f"**{current.metadata.name}**\n\n"
    info += f"*{current.metadata.description}*\n\n"
    info += f"**Category:** {current.metadata.category}\n"
    info += f"**Tags:** {', '.join(current.metadata.tags) if current.metadata.tags else 'None'}\n"
    info += f"**Author:** {current.metadata.author}\n"
    return info


def switch_workflow(workflow_name, category_filter, workflow_manager):
    """
    Switch to selected workflow.

    Args:
        workflow_name: Name of workflow to switch to
        category_filter: Current category filter
        workflow_manager: WorkflowManager instance

    Returns:
        tuple: (workflow_dropdown, workflow_info, generation_status)
    """
    # Find workflow by name
    for filename, wf in workflow_manager.workflows.items():
        if wf.metadata.name == workflow_name:
            success = workflow_manager.set_current_workflow(filename)
            if success:
                gr.Info(f"✅ Workflow loaded: {workflow_name}")
                return (
                    gr.update(value=workflow_name),
                    get_workflow_info_display(workflow_manager),
                    f"✅ Switched to: {workflow_name}",
                )
            else:
                gr.Warning("Failed to switch workflow")
                return (
                    gr.update(),
                    get_workflow_info_display(workflow_manager),
                    "❌ Failed to switch workflow",
                )

    gr.Warning(f"Workflow not found: {workflow_name}")
    return (
        gr.update(),
        get_workflow_info_display(workflow_manager),
        f"⚠️ Workflow not found: {workflow_name}",
    )


def refresh_workflows(category_filter, workflow_manager):
    """
    Refresh workflow list.

    Args:
        category_filter: Current category filter
        workflow_manager: WorkflowManager instance

    Returns:
        tuple: (workflow_dropdown, workflow_info, generation_status)
    """
    workflow_manager.load_all_workflows()

    # Get filtered workflows
    if category_filter == "All":
        workflows = workflow_manager.get_workflows_list()
    else:
        workflows = [
            {"name": wf.metadata.name, "category": wf.metadata.category}
            for wf in workflow_manager.get_workflows_by_category(category_filter)
        ]

    choices = [wf["name"] for wf in workflows]
    current = workflow_manager.get_current_workflow()
    current_name = current.metadata.name if current else None

    return (
        gr.update(choices=choices, value=current_name),
        get_workflow_info_display(workflow_manager),
        f"✅ Refreshed: {len(workflows)} workflows",
    )


def filter_workflows_by_category(category, workflow_manager):
    """
    Filter workflow dropdown by category.

    Args:
        category: Category to filter by
        workflow_manager: WorkflowManager instance

    Returns:
        gr.update: Dropdown update with filtered choices
    """
    if category == "All":
        workflows = workflow_manager.get_workflows_list()
    else:
        workflows = [
            {"name": wf.metadata.name}
            for wf in workflow_manager.get_workflows_by_category(category)
        ]

    choices = [wf["name"] for wf in workflows]
    return gr.update(choices=choices)


def import_workflow_from_file(filepath, workflow_manager):
    """
    Import workflow from uploaded file.

    Args:
        filepath: Path to uploaded workflow file
        workflow_manager: WorkflowManager instance

    Returns:
        tuple: (workflow_info, status_message, workflow_dropdown)
    """
    if not filepath:
        return get_workflow_info_display(workflow_manager), "⚠️ No file selected", gr.update()

    success = workflow_manager.import_workflow(filepath)
    if success:
        # Refresh dropdown
        workflows = workflow_manager.get_workflows_list()
        return (
            get_workflow_info_display(workflow_manager),
            "✅ Workflow imported successfully!",
            gr.update(choices=[wf["name"] for wf in workflows]),
        )
    else:
        return (get_workflow_info_display(workflow_manager), "❌ Failed to import workflow", gr.update())


def export_current_workflow(workflow_manager):
    """
    Export current workflow.

    Args:
        workflow_manager: WorkflowManager instance

    Returns:
        str: Status message
    """
    current = workflow_manager.get_current_workflow()
    if not current:
        return "⚠️ No workflow selected"

    export_path = f"./exported_{current.filename}"
    success = workflow_manager.export_workflow(current.filename, export_path)
    if success:
        return f"✅ Exported to: {export_path}"
    else:
        return "❌ Failed to export workflow"
