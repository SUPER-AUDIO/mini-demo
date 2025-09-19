# 🔧 Adding New Audio Processing Tools

This guide explains how to add new audio processing tools to SuperAudio Mini.

## 📁 Project Structure

```
superaudio_mini/
├── api.py                 # Core API and tool registry
├── app.py                 # Gradio web interface  
├── tools_config.json      # Tool descriptions for AI
├── tools/                 # Audio processing tools
│   ├── __init__.py        # Auto-discovery system
│   ├── speech_enhancement.py
│   ├── voice_conversion.py
│   ├── tool_template.py   # Template for new tools
│   └── your_new_tool.py   # Your new tool here
└── ...
```

## 🚀 Quick Start: Adding a New Tool

### Step 1: Create Your Tool File

1. **Copy the template:**
   ```bash
   cp tools/tool_template.py tools/your_tool_name.py
   ```

2. **Edit the file** and implement your function:
   ```python
   @tool("your_tool_name")  # Or just @tool() to use function name
   def your_function_name(audio: Audio, sr: int, param1: float = 0.0) -> AudioBuf:
       """Your tool description."""
       
       # Your audio processing logic here
       processed_audio = audio.copy()  # Replace with actual processing
       
       # Always return (processed_audio, sample_rate)
       return processed_audio.astype(np.float32), sr
   ```

### Step 2: Add Tool Configuration

Edit `tools_config.json` to add your tool description:

```json
{
  "your_tool_name": {
    "name": "your_tool_name",
    "description": "What your tool does",
    "parameters": {
      "param1": "Description of param1"
    },
    "use_cases": [
      "when to use this tool",
      "keywords that trigger it"
    ],
    "examples": [
      "Example user request",
      "Another example"
    ]
  }
}
```

### Step 3: Test Your Tool

```bash
python -c "
from api import REG
print('Available tools:', sorted(REG._tools.keys()))

# Test your tool
import numpy as np
from api import run_audio_chain
sr = 16000
audio = np.sin(2 * np.pi * 440 * np.arange(sr) / sr).astype(np.float32)
plan = {'your_tool_name': {'param1': 1.0}}
result, _ = run_audio_chain(audio, sr, plan)
print('Tool test successful!')
"
```

## 📝 Detailed Guidelines

### Tool Function Requirements

1. **Function Signature:**
   ```python
   def your_tool(audio: Audio, sr: int, **params) -> AudioBuf:
   ```

2. **Input Parameters:**
   - `audio`: numpy.ndarray of float32 values between -1.0 and 1.0
   - `sr`: Sample rate (int, e.g., 16000, 44100)
   - Additional parameters as needed

3. **Return Value:**
   - Tuple: `(processed_audio, sample_rate)`
   - `processed_audio`: numpy.ndarray of float32, clipped to [-1.0, 1.0]

4. **Error Handling:**
   ```python
   try:
       # Your processing
       return processed_audio, sr
   except Exception as e:
       print(f"Error in {your_tool.__name__}: {e}")
       return audio, sr  # Return original audio on error
   ```

### Configuration Guidelines

1. **Tool Name:** Use snake_case, descriptive names
2. **Description:** Clear, concise explanation of functionality
3. **Parameters:** Document type, range, and default values
4. **Use Cases:** Keywords that help AI routing
5. **Examples:** Natural language requests users might make

### Example Tools

#### 1. Noise Reduction Tool

**File:** `tools/noise_reduction.py`
```python
@tool("noise_reduction")
def noise_reduction(audio: Audio, sr: int, strength: float = 0.5) -> AudioBuf:
    """Reduce background noise in audio."""
    # Simple spectral subtraction (replace with your algorithm)
    fft = np.fft.fft(audio)
    magnitude = np.abs(fft)
    phase = np.angle(fft)
    
    # Reduce magnitude of low-energy frequencies
    threshold = np.percentile(magnitude, 20)
    mask = magnitude > threshold * strength
    magnitude_clean = magnitude * mask
    
    # Reconstruct audio
    clean_fft = magnitude_clean * np.exp(1j * phase)
    clean_audio = np.real(np.fft.ifft(clean_fft))
    
    return np.clip(clean_audio, -1.0, 1.0).astype(np.float32), sr
```

**Config:**
```json
"noise_reduction": {
  "name": "noise_reduction",
  "description": "Reduces background noise and unwanted artifacts",
  "parameters": {
    "strength": "float - Noise reduction strength from 0.0 to 1.0 (default: 0.5)"
  },
  "use_cases": [
    "remove noise", "clean audio", "reduce background", "denoise"
  ],
  "examples": [
    "Remove background noise", "Clean up this recording", "Reduce the hiss"
  ]
}
```

#### 2. Compression Tool

**File:** `tools/compressor.py`
```python
@tool("compressor")
def compressor(audio: Audio, sr: int, threshold: float = -20.0, ratio: float = 4.0) -> AudioBuf:
    """Apply dynamic range compression."""
    # Convert to dB
    audio_db = 20 * np.log10(np.abs(audio) + 1e-10)
    
    # Apply compression above threshold
    compressed_db = np.where(
        audio_db > threshold,
        threshold + (audio_db - threshold) / ratio,
        audio_db
    )
    
    # Convert back to linear
    compressed_audio = np.sign(audio) * (10 ** (compressed_db / 20))
    
    return np.clip(compressed_audio, -1.0, 1.0).astype(np.float32), sr
```

## 🔄 Tool Discovery System

The system automatically discovers tools when:

1. **File is in `tools/` directory**
2. **Function has `@tool()` decorator**
3. **Module is imported** (happens automatically)

### Auto-Discovery Process:

```python
tools/
├── __init__.py           # Scans directory
├── your_tool.py         # Auto-discovered
└── another_tool.py      # Auto-discovered
```

The `tools/__init__.py` automatically:
- 🔍 Scans for `.py` files
- 📦 Imports each module
- 🔧 Registers `@tool` decorated functions
- ✅ Reports loaded tools

## 🧪 Testing New Tools

### Unit Testing
```python
# Test individual tool
from tools.your_tool import your_function
import numpy as np

audio = np.random.random(1000).astype(np.float32) * 0.1
sr = 16000
result, result_sr = your_function(audio, sr, param1=1.0)
assert result.shape == audio.shape
assert result_sr == sr
```

### Integration Testing
```python
# Test through pipeline
from api import run_audio_chain
plan = {"your_tool": {"param1": 1.0}}
result, _ = run_audio_chain(audio, sr, plan)
```

### AI Routing Testing
```python
# Test AI can route to your tool
from app import query_llm, create_llm_prompt, get_available_tools_description

tools_info = get_available_tools_description()
prompt = create_llm_prompt("your test query", tools_info)
plan = query_llm(prompt)
print("Generated plan:", plan)
```

## 🎯 Best Practices

1. **Keep tools focused:** One tool = one clear function
2. **Use descriptive names:** `pitch_shifter` not `ps`
3. **Handle edge cases:** Empty audio, invalid parameters
4. **Document thoroughly:** Clear docstrings and config
5. **Test extensively:** Unit tests + integration tests
6. **Optimize performance:** Consider vectorization, caching
7. **Fail gracefully:** Return original audio on errors

## 📚 Common Audio Processing Patterns

### Frequency Domain Processing
```python
# FFT-based processing
fft = np.fft.fft(audio)
# ... modify fft ...
processed = np.real(np.fft.ifft(fft))
```

### Time Domain Processing
```python
# Direct audio manipulation
processed = audio * gain
processed = np.convolve(audio, impulse_response, mode='same')
```

### Sliding Window Processing
```python
# Process in chunks
chunk_size = 1024
for i in range(0, len(audio), chunk_size):
    chunk = audio[i:i+chunk_size]
    # ... process chunk ...
```

## 🐛 Troubleshooting

**Tool not discovered?**
- Check file is in `tools/` directory
- Ensure `@tool()` decorator is used
- Verify no syntax errors in tool file

**Tool not working in AI routing?**
- Add/update configuration in `tools_config.json`
- Include diverse use cases and examples
- Test with various phrasings

**Performance issues?**
- Profile your tool function
- Consider chunked processing for long audio
- Use NumPy vectorized operations

## 📖 Next Steps

1. **Explore existing tools** in `tools/` directory
2. **Read the template** in `tools/tool_template.py`
3. **Check configurations** in `tools_config.json`
4. **Use the helper script** `add_tool_config.py`
5. **Test your tools** thoroughly before deploying

Happy coding! 🎵
