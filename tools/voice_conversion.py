"""
Voice Conversion Tool

This module provides voice conversion functionality through pitch shifting.
"""

import numpy as np
from typing import Tuple

# Import types and decorator from parent directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api import tool, Audio, AudioBuf

try:
    from pedalboard import PitchShift
except ImportError:
    print("Warning: pedalboard not installed. Install with: pip install pedalboard")
    PitchShift = None


def _to_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


@tool("voice_conversion")
def voice_conversion(audio: Audio, sr: int, semitones: float = 0.0) -> AudioBuf:
    """
    Change the pitch of voice/audio by shifting semitones using high-quality pitch shifting.
    
    Args:
        audio: Input audio array
        sr: Sample rate
        semitones: Number of semitones to shift (-72 to 72, positive for higher, negative for lower)
        
    Returns:
        Tuple of (processed_audio, sample_rate)
    """
    # Coerce and clamp semitones to a safe numeric range for Pedalboard
    semitones = _to_float(semitones, 0.0)
    if semitones < -72.0:
        semitones = -72.0
    if semitones > 72.0:
        semitones = 72.0

    if PitchShift is None:
        print("Pedalboard not available, using simple pitch shift")
        # Fallback to simple implementation
        if semitones == 0.0:
            return audio, sr
        
        factor = 2 ** (semitones / 12.0)
        n = len(audio)
        
        t_old = np.linspace(0, 1, n, endpoint=False)
        t_new = np.linspace(0, 1, int(n / factor), endpoint=False)
        
        a_new = np.interp(t_new, t_old, audio)
        converted_audio = np.interp(t_old, np.linspace(0, 1, len(a_new), endpoint=False), a_new)
        
        return converted_audio.astype(np.float32), sr
    
    try:
        pitch_shift_effect = PitchShift(semitones=semitones)
        converted_audio = pitch_shift_effect(audio, sample_rate=sr)
        return converted_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in voice_conversion: {e}")
        return audio, sr
