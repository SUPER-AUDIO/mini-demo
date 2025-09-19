# 🎵 SuperAudio Mini - AI Audio Processor

An intelligent audio processing application that converts natural language requests into audio effects using AI.

## Features

- **Natural Language Processing**: Describe what you want to do with your audio in plain English
- **AI-Powered Routing**: Uses LLM to automatically create processing plans from user queries
- **Professional Audio Tools**: 16 high-quality audio processors powered by Pedalboard
- **Web Interface**: Easy-to-use Gradio interface for uploading and processing audio
- **Debug Tool**: Individual tool testing interface for parameter tuning and validation

## Available Audio Effects

### 🔊 Speech Enhancement
- **Purpose**: Adjust volume/gain of audio
- **Parameters**: `gain_db` (positive for louder, negative for quieter)
- **Example**: "Make the audio 6dB louder"

### 🎼 Voice Conversion  
- **Purpose**: Change pitch/tone of audio
- **Parameters**: `semitones` (positive for higher pitch, negative for lower)
- **Example**: "Lower the pitch by 2 semitones"

## Usage Examples

| User Request | Generated Plan | Effect |
|-------------|----------------|---------|
| "Make this audio louder" | `{"speech_enhancement": {"gain_db": 6.0}}` | Increases volume by 6dB |
| "Lower the pitch and reduce volume" | `{"voice_conversion": {"semitones": -3.0}, "speech_enhancement": {"gain_db": -3.0}}` | Lowers pitch by 3 semitones and reduces volume by 3dB |
| "Boost audio by 10dB and raise pitch by 2 semitones" | `{"speech_enhancement": {"gain_db": 10.0}, "voice_conversion": {"semitones": 2.0}}` | Applies both volume boost and pitch increase |

## How It Works

### Main App (AI-Powered)
1. **Upload Audio**: Supports WAV, MP3, FLAC and other common formats
2. **Describe Request**: Tell the AI what you want to do in natural language
3. **AI Processing**: LLM converts your request into a structured processing plan
4. **Audio Processing**: The plan is executed using the audio processing pipeline
5. **Download Result**: Get your processed audio file

### Debug Tool (Manual Testing)
1. **Upload Audio**: Load your test audio file
2. **Select Tool**: Choose from 16 available audio processing tools
3. **Adjust Parameters**: Use sliders and controls to fine-tune settings
4. **Process**: Apply the tool with your custom parameters
5. **Compare**: Listen to before/after results and analyze processing details

## Technical Architecture

The application consists of three main components:

### 1. Audio Processing Engine (`api.py`)
- Modular tool registry system
- Extensible plugin architecture with `@tool` decorator
- Sequential processing pipeline with `run_audio_chain()`

### 2. AI Query Parser (`app.py`)
- Google Gemma 2 2B IT model for natural language understanding
- Local model execution (no API keys required)
- Prompt engineering to map queries to processing plans
- JSON plan generation and validation

### 3. Web Interface (`app.py`)
- Gradio-based user interface
- File upload/download handling
- Real-time processing status

## Setup for Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd superaudio_mini
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**

**Option A: Main App (AI-Powered Interface)**
```bash
python app.py
# or
python launch.py
```

**Option B: Debug Tool (Individual Tool Testing)**
```bash
python debug_tools.py
# or
python launch.py --mode debug
```

**Option C: Launch Both Interfaces**
```bash
python launch.py --mode all
```

**Note**: On first run, the Gemma 2 2B IT model will be downloaded (~5GB). This may take several minutes depending on your internet connection.

## System Requirements

- **GPU (Recommended)**: CUDA-compatible GPU for faster inference
- **CPU**: Works on CPU but will be slower (4+ cores recommended)
- **RAM**: 8GB+ recommended (4GB for model + audio processing)
- **Storage**: ~5GB for model download on first run

## Supported Audio Formats

- WAV (recommended)
- MP3
- FLAC  
- M4A
- OGG
- And other formats supported by librosa

## Adding New Audio Tools

To extend the system with new audio processing capabilities:

### 1. **Define your function** in `api.py`
```python
@tool("reverb")
def add_reverb(audio: Audio, sr: int, room_size: float = 0.5) -> AudioBuf:
    # Your reverb implementation here
    return processed_audio, sr
```

### 2. **Add tool configuration** to `tools_config.json`

**Option A: Manual editing**
```json
{
  "reverb": {
    "name": "reverb",
    "description": "Adds reverb effect to audio",
    "parameters": {
      "room_size": "float - Size of the room (0.0-1.0, larger = more reverb)"
    },
    "use_cases": [
      "add reverb",
      "add echo",
      "make sound spacious",
      "concert hall effect"
    ],
    "examples": [
      "Add reverb to this audio",
      "Make it sound like a concert hall",
      "Add echo with room size 0.8"
    ]
  }
}
```

**Option B: Interactive helper script**
```bash
python add_tool_config.py
```

The system will automatically discover and use new tools when both the function and configuration are added!

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.