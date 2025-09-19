from typing import Callable, Dict, Any, Tuple, Union, Optional
import numpy as np

Audio = np.ndarray
AudioBuf = Tuple[Audio, int]  # (audio, sample_rate)


# ----------------------------
# Global tool registry and message store
# ----------------------------
class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}

    def register(self, name: str, fn: Callable):
        key = name.strip().lower()
        if key in self._tools:
            raise ValueError(f"Tool '{name}' already registered.")
        self._tools[key] = fn

    def get(self, name: str) -> Callable:
        key = name.strip().lower()
        if key not in self._tools:
            raise KeyError(f"Unknown tool '{name}'")
        return self._tools[key]


class ToolMessageStore:
    """Store for tools to communicate additional information (like transcripts)."""
    def __init__(self):
        self._messages: Dict[str, str] = {}
    
    def add_message(self, tool_name: str, message: str):
        """Add a message from a tool."""
        self._messages[tool_name] = message
    
    def get_messages(self) -> Dict[str, str]:
        """Get all tool messages."""
        return self._messages.copy()
    
    def clear(self):
        """Clear all stored messages."""
        self._messages.clear()


REG = ToolRegistry()
TOOL_MESSAGES = ToolMessageStore()


# ----------------------------
# The @tool decorator
# ----------------------------
def tool(name: Optional[str] = None):
    """
    Usage:
      @tool()   -> registers with function name
      @tool("custom_name") -> registers under custom name
    """
    def decorator(fn: Callable):
        reg_name = name or fn.__name__
        REG.register(reg_name, fn)
        return fn
    return decorator


# ----------------------------
# Import all tools from tools package
# ----------------------------
# Tools are automatically discovered and registered via the tools package
try:
    import tools
    print("🔧 Audio processing tools loaded successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import tools package: {e}")
except Exception as e:
    print(f"⚠️ Warning: Error loading tools: {e}")


# ----------------------------
# Execution engine
# ----------------------------
def run_audio_chain(audio: Audio, sr: int, plan: Dict[str, Any]) -> AudioBuf:
    """Execute the audio processing chain and return processed audio."""
    # Clear any previous tool messages
    TOOL_MESSAGES.clear()
    
    out_audio, out_sr = audio, sr
    for name, params in plan.items():
        fn = REG.get(name)
        out_audio, out_sr = fn(out_audio, out_sr, **params)
    return out_audio, out_sr


def get_tool_messages() -> Dict[str, str]:
    """Get messages from tools (like transcripts) that were generated during the last run."""
    return TOOL_MESSAGES.get_messages()


# ----------------------------
# Example usage
# ----------------------------
if __name__ == "__main__":
    sr = 16000
    t = np.arange(sr) / sr
    audio = np.sin(2 * np.pi * 440 * t).astype(np.float32)

    plan = {
        "speech_enhancement": {"gain_db": 6.0},
        "voice_conversion": {"semitones": -2.0}
    }

    final_audio, final_sr = run_audio_chain(audio, sr, plan)
    print(final_audio.shape, final_sr)
