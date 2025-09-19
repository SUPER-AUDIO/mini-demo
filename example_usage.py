#!/usr/bin/env python3
"""
Example Usage of HTML Templates and Custom CSS in SuperAudio Mini

This file demonstrates how to use the custom HTML templates and CSS system
that has been separated from the main app.py file.
"""

from templates import (
    render_header, 
    render_status_card, 
    render_audio_visualizer,
    render_processing_panel,
    render_chat_message,
    render_tool_card,
    render_javascript
)

def example_header():
    """Example of rendering a custom header."""
    header_html = render_header()
    print("=== CUSTOM HEADER ===")
    print(header_html)
    print()

def example_status_cards():
    """Example of rendering different status cards."""
    print("=== STATUS CARDS ===")
    
    # Success status
    success_card = render_status_card(
        status_type="success",
        icon="✅",
        title="Processing Complete!",
        message="Your audio has been successfully processed.",
        action_buttons='<button class="btn-primary">Download</button>'
    )
    print("Success Card:")
    print(success_card)
    print()
    
    # Error status
    error_card = render_status_card(
        status_type="error",
        icon="❌",
        title="Processing Failed",
        message="There was an error processing your audio file.",
        action_buttons='<button class="btn-secondary">Try Again</button>'
    )
    print("Error Card:")
    print(error_card)
    print()

def example_audio_visualizer():
    """Example of rendering an audio visualizer."""
    print("=== AUDIO VISUALIZER ===")
    
    visualizer_html = render_audio_visualizer(
        title="My Audio File",
        audio_id="example-audio",
        duration="3:45",
        format="MP3",
        sample_rate="44100",
        channels="2",
        bitrate="320 kbps"
    )
    print(visualizer_html)
    print()

def example_chat_message():
    """Example of rendering chat messages."""
    print("=== CHAT MESSAGES ===")
    
    user_message = render_chat_message(
        message_type="user",
        avatar_url="/static/user-avatar.png",
        sender="User",
        timestamp="2:30 PM",
        content="Make this audio louder and add some reverb",
        message_id="msg-001",
        status="online"
    )
    print("User Message:")
    print(user_message)
    print()
    
    bot_message = render_chat_message(
        message_type="bot",
        avatar_url="/static/bot-avatar.png",
        sender="SuperAudio AI",
        timestamp="2:31 PM",
        content="I'll increase the volume by 6dB and add a medium reverb effect. Processing now...",
        message_id="msg-002",
        status="online",
        additional_actions='<button class="action-btn">Apply Again</button>'
    )
    print("Bot Message:")
    print(bot_message)
    print()

def example_tool_card():
    """Example of rendering a tool card."""
    print("=== TOOL CARD ===")
    
    tool_card = render_tool_card(
        icon="🔊",
        name="Volume Booster",
        category="Enhancement",
        status="available",
        description="Increase or decrease the volume of your audio file with precise control.",
        parameters="gain_db: -20 to +20 (default: 0)",
        tool_id="volume_booster",
        usage_count="1,234",
        success_rate="98"
    )
    print(tool_card)
    print()

def example_integration():
    """Example of how to integrate templates in a Gradio app."""
    print("=== INTEGRATION EXAMPLE ===")
    
    example_code = '''
# In your Gradio app:

import gradio as gr
from templates import render_header, render_status_card

def create_custom_interface():
    with gr.Blocks(css=custom_css) as interface:
        # Custom header
        gr.HTML(render_header())
        
        # Dynamic status card
        status_card = render_status_card(
            status_type="info",
            icon="🎵",
            title="Ready to Process",
            message="Upload an audio file to get started"
        )
        gr.HTML(status_card)
        
        # Your other components...
        audio_input = gr.Audio(elem_classes=["custom-audio"])
        
        # Add JavaScript functions
        gr.HTML(render_javascript())
    
    return interface
'''
    print(example_code)

def main():
    """Run all examples."""
    print("SuperAudio Mini - HTML Template Examples")
    print("=" * 50)
    print()
    
    example_header()
    example_status_cards()
    example_audio_visualizer()
    example_chat_message()
    example_tool_card()
    example_integration()
    
    print("=== CSS FILES TO INCLUDE ===")
    print("Make sure to load these CSS files in your Gradio app:")
    print("- static/styles.css (base styles)")
    print("- static/components.css (component-specific styles)")
    print()
    
    print("=== JAVASCRIPT FUNCTIONS ===")
    print("The JavaScript functions are automatically included via render_javascript()")
    print("Available functions:")
    print("- SuperAudioUI.toggleTheme()")
    print("- SuperAudioUI.updateProgress(elementId, percentage)")
    print("- SuperAudioUI.showNotification(message, type)")
    print("- SuperAudioUI.updateProcessingStep(stepName, status)")
    print("- SuperAudioUI.updateStats()")

if __name__ == "__main__":
    main()
