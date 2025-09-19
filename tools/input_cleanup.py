"""
Input Cleanup Tools

This module provides audio cleanup tools including high-pass filtering,
noise gating, and compression for cleaning up input audio.
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

HighpassFilter = getattr(_pb, 'HighpassFilter', None) if _pb else None
LowpassFilter = getattr(_pb, 'LowpassFilter', None) if _pb else None
NoiseGate = getattr(_pb, 'NoiseGate', None) if _pb else None
Compressor = getattr(_pb, 'Compressor', None) if _pb else None


@tool("highpass_filter")
def highpass_filter(audio: Audio, sr: int, cutoff_frequency_hz: float = 50.0) -> AudioBuf:
    """
    Apply high-pass filter to remove low-frequency noise and rumble.
    
    Args:
        audio: Input audio array
        sr: Sample rate
        cutoff_frequency_hz: Cutoff frequency in Hz (frequencies below this are attenuated)
        
    Returns:
        Tuple of (filtered_audio, sample_rate)
    """
    if HighpassFilter is None:
        print("Pedalboard not available, returning original audio")
        return audio, sr
    
    try:
        filter_effect = HighpassFilter(cutoff_frequency_hz=cutoff_frequency_hz)
        filtered_audio = filter_effect(audio, sample_rate=sr)
        return filtered_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in highpass_filter: {e}")
        return audio, sr


@tool("lowpass_filter")
def lowpass_filter(audio: Audio, sr: int, cutoff_frequency_hz: float = 8000.0) -> AudioBuf:
    """
    Apply low-pass filter to remove high-frequency noise and harshness.
    
    Args:
        audio: Input audio array
        sr: Sample rate
        cutoff_frequency_hz: Cutoff frequency in Hz (frequencies above this are attenuated)
        
    Returns:
        Tuple of (filtered_audio, sample_rate)
    """
    if LowpassFilter is None:
        print("Pedalboard not available, returning original audio")
        return audio, sr
    
    try:
        filter_effect = LowpassFilter(cutoff_frequency_hz=cutoff_frequency_hz)
        filtered_audio = filter_effect(audio, sample_rate=sr)
        return filtered_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in lowpass_filter: {e}")
        return audio, sr


@tool("noise_gate")
def noise_gate(audio: Audio, sr: int, threshold_db: float = -40.0, ratio: float = 2.0,
               attack_ms: float = 10.0, release_ms: float = 100.0) -> AudioBuf:
    """
    Apply noise gate to reduce background noise and unwanted sounds.
    
    Args:
        audio: Input audio array
        sr: Sample rate
        threshold_db: Gate threshold in dB (sounds below this are reduced)
        ratio: Reduction ratio (higher = more aggressive gating)
        attack_ms: Attack time in milliseconds
        release_ms: Release time in milliseconds
        
    Returns:
        Tuple of (gated_audio, sample_rate)
    """
    if NoiseGate is None:
        print("Pedalboard not available, returning original audio")
        return audio, sr
    
    try:
        gate_effect = NoiseGate(
            threshold_db=threshold_db, 
            ratio=ratio,
            attack_ms=attack_ms, 
            release_ms=release_ms
        )
        gated_audio = gate_effect(audio, sample_rate=sr)
        return gated_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in noise_gate: {e}")
        return audio, sr


@tool("compressor")
def compressor(audio: Audio, sr: int, threshold_db: float = -18.0, ratio: float = 3.0,
               attack_ms: float = 10.0, release_ms: float = 100.0) -> AudioBuf:
    """
    Apply dynamic range compression to even out audio levels.
    
    Args:
        audio: Input audio array
        sr: Sample rate
        threshold_db: Compression threshold in dB above which compression starts
        ratio: Compression ratio (>= 1.0, higher = more compression)
        attack_ms: Attack time in milliseconds
        release_ms: Release time in milliseconds
        
    Returns:
        Tuple of (compressed_audio, sample_rate)
    """
    if Compressor is None:
        print("Pedalboard not available, returning original audio")
        return audio, sr
    
    try:
        comp_effect = Compressor(
            threshold_db=threshold_db,
            ratio=ratio,
            attack_ms=attack_ms,
            release_ms=release_ms
        )
        compressed_audio = comp_effect(audio, sample_rate=sr)
        return compressed_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in compressor: {e}")
        return audio, sr
