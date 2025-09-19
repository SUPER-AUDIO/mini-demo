"""
Tool Template

This is a template for creating new audio processing tools.
Copy this file, rename it, and implement your audio processing function.

Example: tools/reverb.py, tools/noise_reduction.py, etc.
"""

import numpy as np
from typing import Tuple

# Import types and decorator from parent directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api import tool, Audio, AudioBuf


# Uncomment and modify the following to create your tool:

# @tool("your_tool_name")  # Or just @tool() to use function name
# def your_function_name(audio: Audio, sr: int, parameter1: float = 0.0, parameter2: str = "default") -> AudioBuf:
#     """
#     Brief description of what your tool does.
#     
#     Args:
#         audio: Input audio array (numpy.ndarray of float32 values between -1.0 and 1.0)
#         sr: Sample rate (int, typically 16000, 22050, 44100, etc.)
#         parameter1: Description of parameter1
#         parameter2: Description of parameter2
#         
#     Returns:
#         Tuple of (processed_audio, sample_rate)
#         processed_audio should be numpy.ndarray of float32 values between -1.0 and 1.0
#     """
#     
#     # Your audio processing logic here
#     processed_audio = audio.copy()  # Replace with actual processing
#     
#     # Always ensure audio is float32 and clipped to [-1.0, 1.0]
#     processed_audio = processed_audio.astype(np.float32)
#     processed_audio = np.clip(processed_audio, -1.0, 1.0)
#     
#     return processed_audio, sr

# (Example implementation removed to keep this file as a pure template.)
