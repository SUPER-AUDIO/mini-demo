"""
Distortion Effects Tools

This module provides distortion and saturation effects including
distortion, clipping, and bitcrushing for creative audio processing.
"""

import numpy as np
from typing import Tuple

# Import types and decorator from parent directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api import tool, Audio, AudioBuf

try:
    import pedalboard as _pb
except ImportError:
    _pb = None

Distortion = getattr(_pb, 'Distortion', None) if _pb else None
Clipping = getattr(_pb, 'Clipping', None) if _pb else None
Bitcrush = getattr(_pb, 'Bitcrush', None) if _pb else None


@tool("distortion")
def distortion(audio: Audio, sr: int, drive_db: float = 25.0) -> AudioBuf:
    """
    Apply harmonic distortion using hyperbolic tangent waveshaping.
    
    Args:
        audio: Input audio array
        sr: Sample rate
        drive_db: Drive amount in decibels (higher = more distortion)
        
    Returns:
        Tuple of (distorted_audio, sample_rate)
    """
    if Distortion is None:
        print("Pedalboard not available, returning original audio")
        return audio, sr
    
    try:
        distortion_effect = Distortion(drive_db=drive_db)
        distorted_audio = distortion_effect(audio, sample_rate=sr)
        return distorted_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in distortion: {e}")
        return audio, sr


@tool("clipping")
def clipping(audio: Audio, sr: int, threshold_db: float = -6.0) -> AudioBuf:
    """
    Apply hard clipping distortion at the specified threshold.
    
    Args:
        audio: Input audio array
        sr: Sample rate
        threshold_db: Threshold in dB at which to clip the signal
        
    Returns:
        Tuple of (clipped_audio, sample_rate)
    """
    if Clipping is None:
        print("Pedalboard not available, returning original audio")
        return audio, sr
    
    try:
        clipping_effect = Clipping(threshold_db=threshold_db)
        clipped_audio = clipping_effect(audio, sample_rate=sr)
        return clipped_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in clipping: {e}")
        return audio, sr


@tool("bitcrush")
def bitcrush(audio: Audio, sr: int, bit_depth: float = 8.0) -> AudioBuf:
    """
    Apply bit depth reduction for lo-fi, digitized sound.
    
    Args:
        audio: Input audio array
        sr: Sample rate
        bit_depth: Bit depth to quantize the signal to (0-32 bits, floating-point supported)
        
    Returns:
        Tuple of (bitcrushed_audio, sample_rate)
    """
    if Bitcrush is None:
        print("Pedalboard not available, returning original audio")
        return audio, sr
    
    try:
        bitcrush_effect = Bitcrush(bit_depth=bit_depth)
        bitcrushed_audio = bitcrush_effect(audio, sample_rate=sr)
        return bitcrushed_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in bitcrush: {e}")
        return audio, sr
