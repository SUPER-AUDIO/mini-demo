"""
Debug Tools Interface

A Gradio interface for testing individual audio processing tools with
adjustable parameters. Perfect for manual testing and parameter tuning.
"""

import gradio as gr
import numpy as np
import json
import tempfile
import os
from typing import Dict, Any, Optional, Tuple, List
import librosa
import soundfile as sf
import inspect

# Import our audio processing API
from api import run_audio_chain, REG, AudioBuf

def load_tools_config():
    """Load tool configurations from JSON file."""
    try:
        with open("tools_config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: tools_config.json not found.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing tools_config.json: {e}")
        return {}

def get_tool_parameters(tool_name: str) -> Dict[str, Any]:
    """Get parameter information for a specific tool."""
    if tool_name not in REG._tools:
        return {}
    
    tool_fn = REG._tools[tool_name]
    sig = inspect.signature(tool_fn)
    
    # Get default values from function signature
    params = {}
    for param_name, param in sig.parameters.items():
        if param_name in ['audio', 'sr']:  # Skip audio and sample rate
            continue
        
        if param.default != inspect.Parameter.empty:
            params[param_name] = {
                'default': param.default,
                'type': type(param.default).__name__
            }
        else:
            params[param_name] = {
                'default': 0.0,
                'type': 'float'
            }
    
    return params


def process_single_tool(audio_file, tool_name: str, params_json: str) -> Tuple[Optional[str], str]:
    """Process audio with a single tool and custom parameters from JSON."""
    
    if audio_file is None:
        return None, "Please upload an audio file."
    
    if not tool_name or tool_name not in REG._tools:
        return None, f"Tool '{tool_name}' not found."
    
    try:
        # Load audio file
        audio, sr = librosa.load(audio_file, sr=None)
        audio = audio.astype(np.float32)
        
        # Parse JSON parameters
        try:
            tool_params = json.loads(params_json) if params_json.strip() else {}
        except json.JSONDecodeError as e:
            return None, f"❌ Invalid JSON: {str(e)}"
        
        # Create processing plan
        plan = {tool_name: tool_params}
        
        # Process audio
        processed_audio, final_sr = run_audio_chain(audio, sr, plan)
        
        # Save processed audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            sf.write(temp_file.name, processed_audio, final_sr)
        
        # Create status message
        plan_str = json.dumps(plan, indent=2)
        status_message = f"""✅ Tool: {tool_name}
        
📊 Parameters Used:
{json.dumps(tool_params, indent=2)}

📈 Audio Info:
- Input length: {len(audio)/sr:.2f}s
- Sample rate: {sr} Hz
- Output length: {len(processed_audio)/final_sr:.2f}s

🔧 Processing Plan:
{plan_str}"""
        
        return temp_file.name, status_message
        
    except Exception as e:
        error_message = f"❌ Error processing with {tool_name}: {str(e)}"
        return None, error_message


def get_default_params_json(tool_name: str) -> str:
    """Get default parameters for a tool as JSON string."""
    if not tool_name or tool_name not in REG._tools:
        return "{}"
    
    params = get_tool_parameters(tool_name)
    default_params = {name: info['default'] for name, info in params.items()}
    return json.dumps(default_params, indent=2)

def create_debug_interface():
    """Create the debug interface."""
    
    # Get available tools
    available_tools = sorted(REG._tools.keys())
    
    with gr.Blocks(title="🔧 SuperAudio Mini - Tool Debugger", theme=gr.themes.Soft()) as interface:
        
        gr.Markdown("""
        # 🔧 SuperAudio Mini - Tool Debugger
        
        Test individual audio processing tools with custom parameters.
        Perfect for debugging, parameter tuning, and understanding tool behavior.
        
        **Instructions:**
        1. Upload an audio file
        2. Select a tool from the dropdown
        3. Edit the JSON parameters below
        4. Click "Process Audio" to test
        5. Compare original vs processed audio
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📤 Input & Tool Selection")
                
                audio_input = gr.Audio(
                    label="Upload Audio File",
                    type="filepath",
                    sources=["upload", "microphone"]
                )
                
                tool_dropdown = gr.Dropdown(
                    choices=available_tools,
                    label="Select Tool to Test",
                    value=available_tools[0] if available_tools else None
                )
                
                gr.Markdown("### 🎛️ Tool Parameters (JSON)")
                
                params_editor = gr.Code(
                    label="Edit Parameters",
                    language="json",
                    value=get_default_params_json(available_tools[0]) if available_tools else "{}",
                    lines=8
                )
                
                with gr.Row():
                    process_btn = gr.Button("🚀 Process Audio", variant="primary", size="lg")
                    reset_btn = gr.Button("🔄 Reset to Defaults", variant="secondary")
            
            with gr.Column(scale=1):
                gr.Markdown("### 📥 Output & Analysis")
                
                audio_output = gr.Audio(label="Processed Audio")
                
                status_output = gr.Textbox(
                    label="Processing Details",
                    lines=12,
                    max_lines=15
                )
                
                gr.Markdown("### 💡 Tool Info")
                tool_info = gr.Textbox(
                    label="Tool Description & Parameters",
                    lines=8,
                    interactive=False
                )
        
        # Update tool info and reset params when tool selection changes
        def update_tool_info_and_reset_params(tool_name):
            if not tool_name:
                return "Select a tool to see its description.", "{}"
            
            config = load_tools_config()
            tool_config = config.get(tool_name, {})
            params = get_tool_parameters(tool_name)
            
            # Build tool info
            info = f"🔧 Tool: {tool_name}\n"
            info += f"📝 Description: {tool_config.get('description', 'No description available')}\n\n"
            
            # Add parameter information
            if params:
                info += "🎛️ Available Parameters:\n"
                for param_name, param_info in params.items():
                    param_desc = tool_config.get('parameters', {}).get(param_name, '')
                    info += f"• {param_name}: {param_info['type']} (default: {param_info['default']})\n"
                    if param_desc:
                        info += f"  {param_desc}\n"
                info += "\n"
            
            # Add use cases
            if tool_config.get('use_cases'):
                info += "🎯 Use Cases:\n" + "\n".join([f"• {use_case}" for use_case in tool_config.get('use_cases', [])])
            
            # Get default parameters JSON
            default_json = get_default_params_json(tool_name)
            
            return info, default_json
        
        # Reset parameters to defaults
        def reset_parameters(tool_name):
            return get_default_params_json(tool_name)
        
        tool_dropdown.change(
            fn=update_tool_info_and_reset_params,
            inputs=[tool_dropdown],
            outputs=[tool_info, params_editor]
        )
        
        reset_btn.click(
            fn=reset_parameters,
            inputs=[tool_dropdown],
            outputs=[params_editor]
        )
        
        # Process audio when button is clicked
        process_btn.click(
            fn=process_single_tool,
            inputs=[audio_input, tool_dropdown, params_editor],
            outputs=[audio_output, status_output],
            show_progress=True
        )
        
        # Initialize with first tool
        if available_tools:
            interface.load(
                fn=update_tool_info_and_reset_params,
                inputs=[gr.State(available_tools[0])],
                outputs=[tool_info, params_editor]
            )
    
    return interface

# Launch the debug interface
if __name__ == "__main__":
    print("🔧 Loading SuperAudio Mini Tool Debugger...")
    interface = create_debug_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7861,  # Different port from main app
        share=True
    )
