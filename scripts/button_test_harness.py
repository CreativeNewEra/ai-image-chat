"""Manual Gradio harness to inspect button behaviour during development."""

from __future__ import annotations

import gradio as gr


def build_demo() -> gr.Blocks:
    """Create the interactive demo layout without launching it."""

    with gr.Blocks() as demo:
        gr.Markdown("# Button Test")

        status = gr.Textbox(label="Status", value="Ready")
        warning = gr.Markdown(value="Hidden warning", visible=False)

        with gr.Row():
            btn1 = gr.Button("Test Button 1")
            btn2 = gr.Button("Test Button 2")

        btn1.click(handle_button_1, None, [status, warning])
        btn2.click(handle_button_2, None, [status, warning])

    return demo


def handle_button_1() -> tuple[str, dict]:
    """Show the warning markdown when button 1 is pressed."""

    return "Button 1 was clicked!", gr.update(visible=True)


def handle_button_2() -> tuple[str, dict]:
    """Hide the warning markdown when button 2 is pressed."""

    return "Button 2 was clicked!", gr.update(visible=False)


if __name__ == "__main__":
    build_demo().launch(server_name="0.0.0.0", server_port=7861)
