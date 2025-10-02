#!/usr/bin/env python3
"""
Minimal button test to debug the issue
"""

import gradio as gr


def test_button_1():
    print("=" * 60)
    print("BUTTON 1 CLICKED!")
    print("=" * 60)
    return "Button 1 was clicked!", gr.update(visible=True)

def test_button_2():
    print("=" * 60)
    print("BUTTON 2 CLICKED!")
    print("=" * 60)
    return "Button 2 was clicked!", gr.update(visible=False)

with gr.Blocks() as demo:
    gr.Markdown("# Button Test")

    status = gr.Textbox(label="Status", value="Ready")
    warning = gr.Markdown(value="Hidden warning", visible=False)

    with gr.Row():
        btn1 = gr.Button("Test Button 1")
        btn2 = gr.Button("Test Button 2")

    btn1.click(
        test_button_1,
        None,
        [status, warning]
    )

    btn2.click(
        test_button_2,
        None,
        [status, warning]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7861)
