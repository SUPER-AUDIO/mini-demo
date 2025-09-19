"""
Speech Enhancement Tool

This module provides speech enhancement functionality through volume/gain adjustment.
"""

import numpy as np
from typing import Tuple

# Import types and decorator from parent directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api import tool, Audio, AudioBuf

try:
    from pedalboard import Gain
except ImportError:
    print("Warning: pedalboard not installed. Install with: pip install pedalboard")
    Gain = None


@tool("speech_enhancement")
def speech_enhancement(audio: Audio, sr: int, gain_db: float = 0.0) -> AudioBuf:
    """
    Enhance speech audio by applying gain/volume adjustment.
    
    Args:
        audio: Input audio array
        sr: Sample rate
        gain_db: Gain in decibels (positive for louder, negative for quieter)
        
    Returns:
        Tuple of (processed_audio, sample_rate)
    """
    if Gain is None:
        print("Pedalboard not available, using simple gain")
        # Fallback to simple implementation
        gain_linear = 10 ** (gain_db / 20.0)
        enhanced_audio = (audio * gain_linear).astype(np.float32)
        enhanced_audio = np.clip(enhanced_audio, -1.0, 1.0)
        return enhanced_audio, sr
    
    try:
        gain_effect = Gain(gain_db=gain_db)
        enhanced_audio = gain_effect(audio, sample_rate=sr)
        return enhanced_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in speech_enhancement: {e}")
        # Fallback implementation
        gain_linear = 10 ** (gain_db / 20.0)
        enhanced_audio = (audio * gain_linear).astype(np.float32)
        enhanced_audio = np.clip(enhanced_audio, -1.0, 1.0)
        return enhanced_audio, sr
