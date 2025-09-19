import gradio as gr
import numpy as np
import json
import tempfile
import uuid
import os
import shutil
from typing import Dict, Any, Optional, Tuple
import librosa
import soundfile as sf
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Import our audio processing API
from api import run_audio_chain, REG, AudioBuf, get_tool_messages

# Initialize Gemma 2 2B IT model
MODEL_NAME = "google/gemma-2-2b-it"
print("Loading Gemma 2 2B IT model...")

# Global variables for model and tokenizer
tokenizer = None
model = None

def load_model():
    """Load the Gemma model and tokenizer."""
    global tokenizer, model
    
    if tokenizer is None or model is None:
        print("Loading Gemma 2 2B IT model...")
        
        try:
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            
            # Configure model loading based on available hardware
            if torch.cuda.is_available():
                print("CUDA available - loading model on GPU")
                model = AutoModelForCausalLM.from_pretrained(
                    MODEL_NAME,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    low_cpu_mem_usage=True
                )
            else:
                print("CUDA not available - loading model on CPU")
                model = AutoModelForCausalLM.from_pretrained(
                    MODEL_NAME,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True
                )
            
            device_info = "GPU" if torch.cuda.is_available() else "CPU"
            print(f"Model loaded successfully on {device_info}")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            raise e

# Load model at startup (comment out for preview mode)
load_model()

# Preview mode flag
PREVIEW_MODE = False

def load_tools_config():
    """Load tool configurations from JSON file."""
    try:
        with open("tools_config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: tools_config.json not found. Using empty configuration.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing tools_config.json: {e}")
        return {}


# Text extraction is now handled by the LLM directly

def get_available_tools_description():
    """Generate a description of all available audio processing tools for the LLM prompt."""
    tools_config = load_tools_config()
    tools_info = []
    
    # Get all registered tools and match with config
    for tool_name in REG._tools.keys():
        if tool_name in tools_config:
            # Use configuration from JSON file
            tools_info.append(tools_config[tool_name])
        else:
            # Fallback for tools not in config (auto-generate basic info)
            print(f"Warning: Tool '{tool_name}' not found in tools_config.json")
            tools_info.append({
                "name": tool_name,
                "description": f"Audio processing tool: {tool_name}",
                "parameters": {"params": "various parameters"},
                "use_cases": [f"use {tool_name}"],
                "examples": [f"Apply {tool_name} to audio"]
            })
    
    return tools_info

def create_llm_prompt(user_query: str, tools_info: list) -> str:
    """Create a prompt for the LLM to convert user query into audio processing plan."""
    
    tools_description = ""
    for tool in tools_info:
        tools_description += f"""
Tool: {tool['name']}
Description: {tool['description']}
Parameters: {json.dumps(tool['parameters'], indent=2)}
Use cases: {', '.join(tool['use_cases'])}"""
        
        # Add examples if available
        if 'examples' in tool:
            tools_description += f"""
Examples: {', '.join(tool['examples'])}"""
        
        tools_description += "\n---\n"
    
    prompt = f"""Convert this user request into a JSON plan for audio processing.

AVAILABLE TOOLS:
{tools_description}

TASK: Convert the user request into valid JSON using only the available tools above.

SPECIAL INSTRUCTIONS FOR TEXT-TO-SPEECH:
- If the user wants to generate speech, create voice, say something, or convert text to audio, use the "text_to_speech" tool
- Extract the text from quotes in the user's request and put it in the "text" parameter
- TTS requests do NOT require an input audio file - they generate audio from text
- Look for patterns like: "Say [text]", "Generate speech [text]", "Create voice saying [text]", "TTS [text]", "Synthesize [text]"

RESPONSE FORMAT: Return ONLY valid JSON, no other text.

EXAMPLES:
Request: "Make the audio louder"
Response: {{"speech_enhancement": {{"gain_db": 6.0}}}}

Request: "Lower the pitch and make it quieter"  
Response: {{"voice_conversion": {{"semitones": -3.0}}, "speech_enhancement": {{"gain_db": -3.0}}}}

Request: "Increase volume by 10dB and raise pitch by 2 semitones"
Response: {{"speech_enhancement": {{"gain_db": 10.0}}, "voice_conversion": {{"semitones": 2.0}}}}

Request: "Say \"Hello world\""
Response: {{"text_to_speech": {{"text": "Hello world"}}}}

Request: "Generate speech for \"Welcome to our service\""
Response: {{"text_to_speech": {{"text": "Welcome to our service"}}}}

Request: "Create audio saying \"Good morning everyone\""
Response: {{"text_to_speech": {{"text": "Good morning everyone"}}}}

Request: "Make TTS for \"Thank you for your patience\""
Response: {{"text_to_speech": {{"text": "Thank you for your patience"}}}}

Request: "Synthesize the text \"Please hold while we connect you\""
Response: {{"text_to_speech": {{"text": "Please hold while we connect you"}}}}

Request: "Convert \"Have a great day\" to speech"
Response: {{"text_to_speech": {{"text": "Have a great day"}}}}

USER REQUEST: "{user_query}"

JSON RESPONSE:"""
    
    return prompt

def query_llm(prompt: str) -> Dict[str, Any]:
    """Query the Gemma model and parse the response into a processing plan."""
    try:
        # Format prompt for Gemma 2 IT model
        system_message = "You are a helpful audio processing assistant. Respond only with valid JSON."
        formatted_prompt = f"""<start_of_turn>user
{system_message}

{prompt}<end_of_turn>
<start_of_turn>model
"""
        
        # Tokenize input
        inputs = tokenizer(formatted_prompt, return_tensors="pt")
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.1,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        
        # Decode response
        response = tokenizer.decode(outputs[0], skip_special_tokens=False)
        
        # Extract the model's response (after the last "model" token)
        response_text = response.split("<start_of_turn>model")[-1].strip()
        
        # Extract JSON from response (in case there's extra text)
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            plan = json.loads(json_str)
            return plan
        else:
            # Try to find JSON without regex if the above fails
            try:
                # Look for lines that start and end with braces
                lines = response_text.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('{') and line.endswith('}'):
                        plan = json.loads(line)
                        return plan
            except:
                pass
            return {}
            
    except Exception as e:
        print(f"LLM query error: {e}")
        return {}

def process_audio_with_query(audio_file, user_query: str, chat_history):
    """Main function that processes audio based on user query and updates chat."""
    
    if not user_query.strip():
        return None, chat_history, ""
    
    # For now, allow processing without audio file - the LLM will determine if TTS is needed
    # If it's not a TTS request and no audio is provided, the LLM will handle the error appropriately
    
    # Preview mode - show demo audio inside chat history
    if PREVIEW_MODE:
        demo_dir = os.path.join("static", "demo")
        os.makedirs(demo_dir, exist_ok=True)
        demo_filename = "tts_Coffee_Shop_03.wav"
        demo_path = os.path.join(demo_dir, demo_filename)
        if not os.path.exists(demo_path):
            # Create a simple sine tone if the demo file is missing
            sr_demo = 22050
            t = np.linspace(0, 2.0, int(sr_demo * 2.0), endpoint=False)
            tone = 0.1 * np.sin(2 * np.pi * 440 * t).astype(np.float32)
            sf.write(demo_path, tone, sr_demo)

        abs_demo_path = os.path.abspath(demo_path)
        demo_src = f"file={abs_demo_path}"

        # Create download link for demo audio
        demo_download_link = f'<a href="file={abs_demo_path}" download="{demo_filename}" style="color: #6366f1; text-decoration: none; font-weight: bold;">📥 Download Demo Audio</a>'
        
        demo_response = f"""🎭 **Preview Mode Active**

📝 **Your Request:** "{user_query}"

✨ **Simulated Plan:**
```json
{{"speech_enhancement": {{"gain_db": 3.0}}, "spatial_effects": {{"reverb_amount": 0.3}}}}
```

▶️ **Demo Processed Audio:**
<audio controls src="{demo_src}" style="width:100%; margin: 8px 0;"></audio>

{demo_download_link}

🔧 **To enable full functionality:**
1. Set `PREVIEW_MODE = False` in `app.py`
2. Uncomment `load_model()`
3. Restart the application"""

        # Don't append to chat_history here since submit_message already added the user message
        # Just update the last entry (which should be [user_message, None])
        if chat_history and len(chat_history) > 0:
            chat_history[-1][1] = demo_response
        else:
            chat_history.append([user_query, demo_response])
        
        # In preview mode, return the demo audio path so it can be displayed in the output component
        return demo_path, chat_history, ""
    
    try:
        # Load audio file (or create dummy audio for TTS)
        if audio_file is not None:
            audio, sr = librosa.load(audio_file, sr=None)
            audio = audio.astype(np.float32)
        else:
            # For TTS requests, create dummy audio (will be replaced by synthesized audio)
            sr = 22050  # Standard TTS output sample rate
            audio = np.zeros(1, dtype=np.float32)  # Minimal dummy audio
        
        # Get available tools and create LLM prompt
        tools_info = get_available_tools_description()
        prompt = create_llm_prompt(user_query, tools_info)
        
        # Query LLM to get processing plan
        plan = query_llm(prompt)
        # Debug print the plan to server logs for visibility
        try:
            print("🔧 LLM plan:\n" + json.dumps(plan, indent=2))
        except Exception:
            print(f"🔧 LLM plan (raw): {plan}")
        
        if not plan:
            error_msg = f"❌ Could not create a processing plan for: '{user_query}'. Please try rephrasing your request."
            # Update the last entry (which should be [user_message, None])
            if chat_history and len(chat_history) > 0:
                chat_history[-1][1] = error_msg
            else:
                chat_history.append([user_query, error_msg])
            return None, chat_history, ""
        
        # Handle requests without an audio file
        no_audio_tools = {"text_to_speech", "list_capabilities"}
        if audio_file is None:
            # If ALL requested tools can run without input audio, proceed with dummy audio
            if all(name in no_audio_tools for name in plan.keys()):
                sr = 22050
                audio = np.zeros(1, dtype=np.float32)
            else:
                error_msg = f"❌ This request requires an audio file. Please upload an audio file first."
                if chat_history and len(chat_history) > 0:
                    chat_history[-1][1] = error_msg
                else:
                    chat_history.append([user_query, error_msg])
                return None, chat_history, ""
        
        # Execute the audio processing chain
        processed_audio, final_sr = run_audio_chain(audio, sr, plan)
        
        # Check for tool messages (like transcripts)
        tool_messages = get_tool_messages()
        
        # If the plan is only list_capabilities, return the grouped list message without audio
        only_list_caps = set(plan.keys()) == {"list_capabilities"}
        if only_list_caps:
            response = ""
            if tool_messages and "list_capabilities" in tool_messages:
                response = tool_messages["list_capabilities"]
            else:
                response = "🧰 Available tools listed."
            if chat_history and len(chat_history) > 0:
                chat_history[-1][1] = response
            else:
                chat_history.append([user_query, response])
            return None, chat_history, ""

        # Save processed audio to static path so it can be shown in chat
        os.makedirs(os.path.join("static", "chat_audio"), exist_ok=True)
        unique_name = f"processed_{uuid.uuid4().hex}.wav"
        saved_path = os.path.join("static", "chat_audio", unique_name)
        sf.write(saved_path, processed_audio, final_sr)
        
        # Create response for chat
        plan_str = json.dumps(plan, indent=2)
        
        # Check if this was a TTS-only request
        is_tts_only = "text_to_speech" in plan and len(plan) == 1 and audio_file is None
        
        # Create absolute path and download link
        abs_saved_path = os.path.abspath(saved_path)
        download_link = ""
        
        if is_tts_only:
            response = f"""✅ **Text-to-Speech Complete!**

🎛️ **Generated Plan:**
```json
{plan_str}
```

📊 **Audio Info:**
- Generated Duration: {len(processed_audio)/final_sr:.1f}s
- Sample Rate: {final_sr}Hz
- Source: Text-to-Speech Synthesis
{download_link}"""
        else:
            response = f"""✅ **Processing Complete!**

🎛️ **Generated Plan:**
```json
{plan_str}
```

📊 **Audio Info:**
- Duration: {len(audio)/sr:.1f}s → {len(processed_audio)/final_sr:.1f}s
- Sample Rate: {sr}Hz → {final_sr}Hz
{download_link}"""

        # Add tool messages if any (like speech recognition transcripts)
        if tool_messages:
            response += "\n\n📋 **Tool Output:**\n"
            for tool_name, message in tool_messages.items():
                response += f"\n{message}\n"
        
        # Update the last entry (which should be [user_message, None])
        if chat_history and len(chat_history) > 0:
            chat_history[-1][1] = response
        else:
            chat_history.append([user_query, response])
        
        return saved_path, chat_history, ""
        
    except Exception as e:
        error_message = f"❌ **Error:** {str(e)}"
        # Update the last entry (which should be [user_message, None])
        if chat_history and len(chat_history) > 0:
            chat_history[-1][1] = error_message
        else:
            chat_history.append([user_query, error_message])
        return None, chat_history, ""

def load_css_file(filename: str) -> str:
    """Load CSS from an external file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: CSS file {filename} not found. Using empty styles.")
        return ""
    except Exception as e:
        print(f"Error loading CSS file {filename}: {e}")
        return ""

# Load custom CSS from external files
base_css = load_css_file("static/styles.css")
components_css = load_css_file("static/components.css")
custom_css = base_css + "\n" + components_css

# Create Gradio interface
def create_interface():
    """Create the Gradio web interface with clean layout and custom styling."""
    
    with gr.Blocks(title="🎵 SuperAudio Mini - AI Audio Processor", theme=gr.themes.Soft(), css=custom_css) as interface:
        
        # Header - Keep original simple markdown but with custom styling
        gr.Markdown("""
        # 🎵 SuperAudio Mini - AI Audio Processor
        """, elem_classes=["custom-header-text"])
        
        # (removed) separate top chat bar; input will live with chat history
        
        # Main Content - Two Column Layout with Logo
        with gr.Row(elem_classes=["app-container"]):
            # LEFT COLUMN - Logo Only
            with gr.Column(scale=2, elem_classes=["logo-column"]):
                # Logo using gr.Image with hidden button styling
                logo_image = gr.Image(
                    value="static/images/chat_nobkg.png",
                    label="",
                    show_fullscreen_button=False,
                    show_label=False,
                    show_download_button=False,
                    show_share_button=False,
                    interactive=False,
                    elem_classes=["main-logo"],
                    container=False,
                    height=None,
                    width=None,
                    scale=1.5
                )
            
            # RIGHT COLUMN - Chat Interface
            with gr.Column(scale=5, elem_classes=["section-card", "centered-chat"]):
                chatbot = gr.Chatbot(
                    label="",
                    height=600,
                    show_label=False,
                    show_copy_button=True,
                    avatar_images=None,
                    value=[["Hey Agent, what can you do for me?", "🎵 Welcome to SuperAudio Agent! 🎵\n\n🎯 Your one-stop shop for everything audio! Our mission is to bring world-class audio intelligence to you via a simple chat interface.\n\n🎧 Upload your audio and ask the agent to do anything with it - the agent will process your audio file for you!\n\n💡 Here are some things you can try:\n• 🔊 Make it louder\n• 🎼 Lower the pitch\n• ✨ Add reverb and compression\n• 🎚️ Professional mastering\n• 🎤 Speech enhancement\n• 🎸 Guitar effects\n• 🥁 Drum processing\n• 🌟 Vintage warm sound\n\n✨ Ready to transform your audio? Let's get started! 🚀"]],
                    placeholder="Chat history will appear here..."
                )
                
                # Status bar showing current audio file
                status_bar = gr.HTML(
                    '<div class="audio-status-bar" id="audio-status-bar">Upload your audio file to start your adventure with SuperAudio!</div>',
                    elem_classes=["status-bar"]
                )
                
                # Audio display for uploaded files
                uploaded_audio_display = gr.Audio(
                    label="🎵 Your Uploaded Audio",
                    interactive=False,
                    show_download_button=True,
                    show_share_button=False,
                    elem_classes=["uploaded-audio-display"],
                    visible=False
                )

                # Chat input inside the same block as chat history
                with gr.Row(elem_classes=["chat-input-row"]):
                    msg_input = gr.Textbox(
                        label="",
                        placeholder="Describe what you want to do with your audio... (e.g., 'Make it louder and add reverb')",
                        lines=2,
                        scale=6,
                        show_label=False,
                        container=False,
                        elem_classes=["chat-input-text"]
                    )
                    # Compact audio upload button
                    upload_btn = gr.UploadButton("🎵 Click here to upload", file_types=["audio"], file_count="single", scale=1, elem_classes=["chat-input-action"])
                    send_btn = gr.Button("Send", variant="primary", scale=1, interactive=False, elem_classes=["chat-input-action"])
            
            # Hidden audio output component (for processing logic)
            audio_output = gr.Audio(
                label="Processed Audio",
                interactive=False,
                show_download_button=True,
                show_share_button=False,
                elem_classes=["equal-audio"],
                visible=False,
                format="wav"
            )
        
        # Hidden audio input component (used by upload button)
        audio_input = gr.Audio(
            label="Upload Audio File",
            type="filepath",
            sources=["upload", "microphone"],
            show_download_button=False,
            elem_classes=["equal-audio"],
            visible=False
        )
        
        # Presets Section (Original)
        with gr.Row(visible=False):
            preset_dropdown = gr.Dropdown(
                choices=[
                    "🔊 Make it louder",
                    "🎼 Lower the pitch", 
                    "✨ Add reverb and compress",
                    "🎚️ Professional master",
                    "🌟 Vintage warm sound",
                    "🎯 Clean vocal processing",
                    "🎸 Guitar enhancement",
                    "🥁 Drum processing"
                ],
                label="Try these examples",
                value=None,
                scale=3
            )
            load_preset_btn = gr.Button("Load", variant="secondary", scale=1)
        
        # (removed) Former bottom chat bar now placed at the top
        
        # Add subtle JavaScript enhancements (non-intrusive)
        gr.HTML('''
        <script>
            window.SuperAudioMini = { enhanced: true };
            
            // Set page zoom to 100% on load
            document.addEventListener('DOMContentLoaded', function() {
                document.body.style.zoom = '100%';
            });
            
            // Also set on window load as backup
            window.addEventListener('load', function() {
                document.body.style.zoom = '100%';
            });
        </script>
        ''')

        def load_preset(preset_choice):
            if preset_choice:
                # Remove emoji and return the text
                preset_text = preset_choice.split(" ", 1)[1]
                return preset_text
            return ""

        def submit_message(message, history, audio_file):
            if not message.strip():
                return history, "", None, "", None
            
            # Create user message without immediate audio embed
            user_message = message
            
            # Use the original audio file for processing if available
            audio_file_for_processing = audio_file
            
            # Add user message to history
            history.append([user_message, None])
            # If user provided an uploaded audio file, show it as a gr.Audio bubble now
            if audio_file:
                abs_uploaded = os.path.abspath(audio_file)
                audio_component = gr.Audio(
                    value=abs_uploaded,
                    interactive=False,
                    show_download_button=True,
                    show_share_button=False,
                    autoplay=False,
                    elem_classes=["chat-audio"]
                )
                history.append([audio_component, None])
            
            # Process with the agent using the static file path
            processed_audio, updated_history, cleared_msg = process_audio_with_query(audio_file_for_processing, message, history)

            # Append assistant-side audio bubble mirroring user audio display
            try:
                if processed_audio:
                    abs_processed = os.path.abspath(processed_audio)
                    agent_audio_component = gr.Audio(
                        value=abs_processed,
                        interactive=False,
                        show_download_button=True,
                        show_share_button=False,
                        autoplay=False,
                        elem_classes=["chat-audio"]
                    )
                    updated_history.append([None, agent_audio_component])
            except Exception as e:
                print(f"⚠️ Unable to append agent audio bubble: {e}")
            
            # Update status bar
            status_text = f'<div class="audio-status-bar" id="audio-status-bar">🎵 Currently working on: <span class="filename-highlight">{os.path.basename(audio_file) if audio_file else "No audio file"}</span>. To work on another file, upload a new one.</div>'
            
            # Show uploaded audio in the dedicated display component
            return updated_history, cleared_msg, processed_audio, status_text, audio_file
        
        # Load preset when button clicked (legacy, hidden UI)
        load_preset_btn.click(fn=load_preset, inputs=[preset_dropdown], outputs=[msg_input])
        
        # Enable Send only when there is text
        def toggle_send_interactive(message: str):
            return gr.update(interactive=bool(message.strip()))
        msg_input.change(toggle_send_interactive, inputs=[msg_input], outputs=[send_btn])

        # Chip click handlers to populate the textbox
        def set_text(s: str):
            return s
        for label in [
            ("🔊 Louder", "Make it louder"),
            ("🎼 Lower pitch", "Lower the pitch"),
            ("✨ Reverb + Compress", "Add reverb and compress"),
            ("🎚️ Master", "Professional master"),
        ]:
            pass

        # Chip click handlers removed - chips are not currently implemented in the UI

        # When upload button receives a file, set it into the main audio_input component
        def set_uploaded_file(file):
            # UploadButton returns a file object; extract the path
            if file is not None:
                if hasattr(file, 'name'):
                    file_path = file.name
                    print(f"🎵 Uploaded audio file path: {file_path}")
                    return file_path
                elif isinstance(file, str):
                    print(f"🎵 Uploaded audio file path: {file}")
                    return file
                else:
                    file_path = str(file)
                    print(f"🎵 Uploaded audio file path: {file_path}")
                    return file_path
            return None
        upload_btn.upload(set_uploaded_file, inputs=[upload_btn], outputs=[audio_input])

        # Update status bar when audio file is uploaded
        def update_status_and_chat(audio_file, history):
            if audio_file is not None:
                print(f"🎵 Audio input changed to: {audio_file}")
                filename = os.path.basename(audio_file)
                status_html = f'<div class="audio-status-bar" id="audio-status-bar"> SuperAudio is geared up! Your file <span class="filename-highlight">{filename}</span> is ready for processing.</div>'
                return status_html, history
            else:
                status_html = '<div class="audio-status-bar" id="audio-status-bar">Upload your audio file to start your adventure with SuperAudio!</div>'
                return status_html, history
        
        audio_input.change(update_status_and_chat, inputs=[audio_input, chatbot], outputs=[status_bar, chatbot])

        # Send button click
        send_btn.click(fn=submit_message, inputs=[msg_input, chatbot, audio_input], outputs=[chatbot, msg_input, audio_output, status_bar, uploaded_audio_display], show_progress=True)
        
        # Enter key submit
        msg_input.submit(
            fn=submit_message,
            inputs=[msg_input, chatbot, audio_input],
            outputs=[chatbot, msg_input, audio_output, status_bar, uploaded_audio_display],
            show_progress=True
        )
    
    return interface

# Launch the app
if __name__ == "__main__":
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        allowed_paths=["static", "static/uploaded_audio", "static/chat_audio", "."]
    )
