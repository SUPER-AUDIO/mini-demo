"""
Utility Effects Tools

This module provides utility audio effects including gain control,
compression algorithms, phase inversion, and testing utilities.
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

# Resolve classes individually to avoid misleading ImportError messages
Gain = getattr(_pb, 'Gain', None) if _pb else None
Invert = getattr(_pb, 'Invert', None) if _pb else None
MP3Compressor = getattr(_pb, 'MP3Compressor', None) if _pb else None
GSMFullRateCompressor = getattr(_pb, 'GSMFullRateCompressor', None) if _pb else None
AddLatency = getattr(_pb, 'AddLatency', None) if _pb else None


@tool("gain")
def gain(audio: Audio, sr: int, gain_db: float = 0.0) -> AudioBuf:
    """
    Apply gain/volume adjustment to the audio signal.
    
    Args:
        audio: Input audio array
        sr: Sample rate
        gain_db: Gain in decibels (positive for louder, negative for quieter)
        
    Returns:
        Tuple of (gained_audio, sample_rate)
    """
    if Gain is None:
        print("Pedalboard Gain unavailable, using simple gain")
        # Fallback implementation
        gain_linear = 10 ** (gain_db / 20.0)
        gained_audio = (audio * gain_linear).astype(np.float32)
        gained_audio = np.clip(gained_audio, -1.0, 1.0)
        return gained_audio, sr
    
    try:
        gain_effect = Gain(gain_db=gain_db)
        gained_audio = gain_effect(audio, sample_rate=sr)
        return gained_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in gain: {e}")
        # Fallback implementation
        gain_linear = 10 ** (gain_db / 20.0)
        gained_audio = (audio * gain_linear).astype(np.float32)
        gained_audio = np.clip(gained_audio, -1.0, 1.0)
        return gained_audio, sr


@tool("invert")
def invert(audio: Audio, sr: int) -> AudioBuf:
    """
    Flip the polarity of the signal (phase inversion).
    
    Args:
        audio: Input audio array
        sr: Sample rate
        
    Returns:
        Tuple of (inverted_audio, sample_rate)
    """
    if Invert is None:
        print("Pedalboard Invert unavailable, using simple inversion")
        # Fallback implementation - mathematically identical to pedalboard
        inverted_audio = (-audio).astype(np.float32)
        return inverted_audio, sr
    
    try:
        invert_effect = Invert()
        inverted_audio = invert_effect(audio, sample_rate=sr)
        return inverted_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in invert: {e}")
        # Fallback implementation
        inverted_audio = (-audio).astype(np.float32)
        return inverted_audio, sr


@tool("mp3_compressor")
def mp3_compressor(audio: Audio, sr: int, vbr_quality: float = 2.0) -> AudioBuf:
    """
    Apply MP3 compression artifacts using LAME encoder in real-time.
    
    Args:
        audio: Input audio array
        sr: Sample rate
        vbr_quality: Variable bit rate quality (0.0-10.0, lower is better quality)
        
    Returns:
        Tuple of (compressed_audio, sample_rate)
    """
    if MP3Compressor is None:
        print("Pedalboard MP3Compressor unavailable, returning original audio")
        return audio, sr
    
    try:
        mp3_effect = MP3Compressor(vbr_quality=vbr_quality)
        compressed_audio = mp3_effect(audio, sample_rate=sr)
        return compressed_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in mp3_compressor: {e}")
        return audio, sr


@tool("gsm_compressor")
def gsm_compressor(audio: Audio, sr: int, quality: str = "WindowedSinc8") -> AudioBuf:
    """
    Apply GSM 'Full Rate' compression to emulate 2G cellular phone connection.
    
    Args:
        audio: Input audio array
        sr: Sample rate
        quality: Resampling quality (ResamplingQuality enum value)
        
    Returns:
        Tuple of (compressed_audio, sample_rate)
    """
    if GSMFullRateCompressor is None:
        print("Pedalboard GSMFullRateCompressor unavailable, returning original audio")
        return audio, sr
    
    try:
        gsm_effect = GSMFullRateCompressor(quality=quality)
        compressed_audio = gsm_effect(audio, sample_rate=sr)
        return compressed_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in gsm_compressor: {e}")
        return audio, sr


@tool("add_latency")
def add_latency(audio: Audio, sr: int, samples: int = 44100) -> AudioBuf:
    """
    Add latency/delay by the specified number of samples (for testing purposes).
    
    Args:
        audio: Input audio array
        sr: Sample rate
        samples: Number of samples to delay the audio by
        
    Returns:
        Tuple of (delayed_audio, sample_rate)
    """
    if AddLatency is None:
        print("Pedalboard AddLatency unavailable, using simple delay")
        # Fallback implementation
        delayed_audio = np.concatenate([np.zeros(samples, dtype=np.float32), audio])
        return delayed_audio.astype(np.float32), sr
    
    try:
        latency_effect = AddLatency(samples=samples)
        delayed_audio = latency_effect(audio, sample_rate=sr)
        return delayed_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in add_latency: {e}")
        # Fallback implementation
        delayed_audio = np.concatenate([np.zeros(samples, dtype=np.float32), audio])
        return delayed_audio.astype(np.float32), sr
