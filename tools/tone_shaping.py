"""
Tone Shaping Tools

This module provides EQ and filtering tools for tone shaping including
peak filters, shelf filters, and creative filtering effects.

Note: The filters used in this module (PeakFilter, HighShelfFilter, LowShelfFilter, LadderFilter) 
are not part of the standard pedalboard library functions as defined in paddleboard_functions.json.
These may be custom implementations or extensions.
"""

import numpy as np
from typing import Tuple

# Import types and decorator from parent directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api import tool, Audio, AudioBuf

try:
    from pedalboard import PeakFilter, HighShelfFilter, LowShelfFilter, LadderFilter
except ImportError:
    print("Warning: pedalboard not installed. Install with: pip install pedalboard")
    PeakFilter = HighShelfFilter = LowShelfFilter = LadderFilter = None


@tool("peak_filter")
def peak_filter(audio: Audio, sr: int, center_hz: float = 1000.0, 
                gain_db: float = 0.0, q: float = 1.0) -> AudioBuf:
    """
    Apply a peak/notch filter to boost or cut specific frequencies.
    
    Args:
        audio: Input audio array
        sr: Sample rate
        center_hz: Center frequency in Hz
        gain_db: Gain in dB (positive = boost, negative = cut)
        q: Filter Q factor (higher = narrower frequency range)
        
    Returns:
        Tuple of (filtered_audio, sample_rate)
    """
    if PeakFilter is None:
        print("Pedalboard not available, returning original audio")
        return audio, sr
    
    try:
        filter_effect = PeakFilter(
            center_frequency_hz=center_hz, 
            gain_db=gain_db, 
            q=q
        )
        filtered_audio = filter_effect(audio, sample_rate=sr)
        return filtered_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in peak_filter: {e}")
        return audio, sr


@tool("high_shelf")
def high_shelf(audio: Audio, sr: int, cutoff_hz: float = 8000.0, 
               gain_db: float = 0.0) -> AudioBuf:
    """
    Apply high-shelf filter to boost or cut high frequencies.
    
    Args:
        audio: Input audio array
        sr: Sample rate
        cutoff_hz: Shelf frequency in Hz (frequencies above this are affected)
        gain_db: Gain in dB (positive = boost highs, negative = cut highs)
        
    Returns:
        Tuple of (filtered_audio, sample_rate)
    """
    if HighShelfFilter is None:
        print("Pedalboard not available, returning original audio")
        return audio, sr
    
    try:
        filter_effect = HighShelfFilter(
            cutoff_frequency_hz=cutoff_hz, 
            gain_db=gain_db
        )
        filtered_audio = filter_effect(audio, sample_rate=sr)
        return filtered_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in high_shelf: {e}")
        return audio, sr


@tool("low_shelf")
def low_shelf(audio: Audio, sr: int, cutoff_hz: float = 200.0, 
              gain_db: float = 0.0) -> AudioBuf:
    """
    Apply low-shelf filter to boost or cut low frequencies.
    
    Args:
        audio: Input audio array
        sr: Sample rate
        cutoff_hz: Shelf frequency in Hz (frequencies below this are affected)
        gain_db: Gain in dB (positive = boost bass, negative = cut bass)
        
    Returns:
        Tuple of (filtered_audio, sample_rate)
    """
    if LowShelfFilter is None:
        print("Pedalboard not available, returning original audio")
        return audio, sr
    
    try:
        filter_effect = LowShelfFilter(
            cutoff_frequency_hz=cutoff_hz, 
            gain_db=gain_db
        )
        filtered_audio = filter_effect(audio, sample_rate=sr)
        return filtered_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in low_shelf: {e}")
        return audio, sr


@tool("ladder_filter")
def ladder_filter(audio: Audio, sr: int, cutoff_hz: float = 1000.0, 
                  resonance: float = 0.2, drive_db: float = 0.0) -> AudioBuf:
    """
    Apply Moog-style ladder filter for vintage synthesizer-like filtering.
    
    Args:
        audio: Input audio array
        sr: Sample rate
        cutoff_hz: Filter cutoff frequency in Hz
        resonance: Filter resonance (0.0 to 1.0, higher = more resonant)
        drive_db: Input drive in dB (adds harmonic distortion)
        
    Returns:
        Tuple of (filtered_audio, sample_rate)
    """
    if LadderFilter is None:
        print("Pedalboard not available, returning original audio")
        return audio, sr
    
    try:
        filter_effect = LadderFilter(
            cutoff_hz=cutoff_hz, 
            resonance=resonance, 
            drive_db=drive_db
        )
        filtered_audio = filter_effect(audio, sample_rate=sr)
        return filtered_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in ladder_filter: {e}")
        return audio, sr
