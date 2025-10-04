"""
UI Component: Chat Interface

This module provides both Text Chat and Vision Chat interfaces for the AI Image Chat application.
Extracted from app.py for better maintainability.
"""

import gradio as gr


def create_chat_interface(
    available_models: list[str], default_model: str
) -> dict[str, gr.components.Component]:
    """
    Create the chat interface UI component with Text Chat and Vision Chat tabs.

    This component includes two tabs:
    - Text Chat: For developing new prompts from scratch using Ollama
    - Vision Chat: For refining existing images with vision model

    Parameters
    ----------
    available_models : list[str]
        List of available Ollama models to show in the dropdown
    default_model : str
        Default model to select in the dropdown (from config.OLLAMA_CHAT_MODEL)

    Returns
    -------
    dict[str, gr.components.Component]
        Dictionary containing all chat-related components:
        - 'chat_tabs': Tabs component for switching between Text/Vision chat
        - 'model_dropdown': Dropdown for selecting chat model
        - 'refresh_models_btn': Button to refresh model list
        - 'chatbot': Text chat history display
        - 'msg': Text chat message input
        - 'send_btn': Text chat send button
        - 'clear_chat_btn': Clear text chat button
        - 'vision_chatbot': Vision chat history display
        - 'vision_image_preview': Image preview in vision chat
        - 'vision_msg': Vision chat message input
        - 'vision_send_btn': Vision chat send button
        - 'clear_vision_btn': Clear vision chat button

    Examples
    --------
    >>> from config import OLLAMA_CHAT_MODEL
    >>> components = create_chat_interface(
    ...     available_models=["llama3.1", "mistral"],
    ...     default_model=OLLAMA_CHAT_MODEL
    ... )
    >>> # Access individual components
    >>> chatbot = components['chatbot']
    >>> send_btn = components['send_btn']
    >>> # Wire up event handlers in main app
    >>> send_btn.click(fn=chat_handler, inputs=[components['msg']], outputs=[chatbot])

    Notes
    -----
    - Text Chat integrates with Ollama's /api/chat endpoint
    - Vision Chat requires a vision model (e.g., qwen2.5vl) and image context
    - Both chats support extracting prompts for image generation
    - Chat histories are separate and maintained independently
    - The vision image preview shows the image currently being discussed
    """
    with gr.TabItem("💬 Chat & Vision"):
        with gr.Tabs() as chat_tabs_component:
            # Text Chat Tab
            with gr.Tab("💬 Text Chat"):
                gr.Markdown("**Develop new prompts from scratch**")

                with gr.Row():
                    model_dropdown = gr.Dropdown(
                        choices=available_models,
                        value=default_model,
                        label="Chat Model",
                        interactive=True,
                        scale=3,
                    )
                    refresh_models_btn = gr.Button("🔄", size="sm", scale=1)

                chatbot = gr.Chatbot(
                    height=350, label="Chat History", show_copy_button=True, type="messages"
                )

                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Describe your image idea...", label="Message", scale=4
                    )
                    send_btn = gr.Button("Send", scale=1, variant="primary")

                clear_chat_btn = gr.Button("🗑️ Clear Chat", size="sm")

                gr.Markdown("**Tips:** Be specific about style, mood, lighting, composition")

            # Vision Chat Tab
            with gr.Tab("👁️ Vision Chat"):
                gr.Markdown("**Refine existing images with AI vision**")

                vision_chatbot = gr.Chatbot(
                    height=350,
                    label="Vision Chat History",
                    show_copy_button=True,
                    type="messages",
                )

                # Image preview in vision chat
                vision_image_preview = gr.Image(
                    label="Current Image Being Discussed",
                    type="pil",
                    interactive=False,
                    height=200,
                )

                with gr.Row():
                    vision_msg = gr.Textbox(
                        placeholder="Ask about the image or request changes...",
                        label="Message",
                        scale=4,
                    )
                    vision_send_btn = gr.Button("Send", scale=1, variant="primary")

                clear_vision_btn = gr.Button("🗑️ Clear Vision Chat", size="sm")

                gr.Markdown(
                    "**Tips:** 'Make the sky more dramatic', 'Change colors to warmer tones', 'Add more detail to the foreground'"
                )

    # Return all components as a dictionary for easy access
    return {
        "chat_tabs": chat_tabs_component,
        "model_dropdown": model_dropdown,
        "refresh_models_btn": refresh_models_btn,
        "chatbot": chatbot,
        "msg": msg,
        "send_btn": send_btn,
        "clear_chat_btn": clear_chat_btn,
        "vision_chatbot": vision_chatbot,
        "vision_image_preview": vision_image_preview,
        "vision_msg": vision_msg,
        "vision_send_btn": vision_send_btn,
        "clear_vision_btn": clear_vision_btn,
    }
