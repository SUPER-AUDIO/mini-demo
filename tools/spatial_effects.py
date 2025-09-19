"""
Spatial Effects Tools

This module provides spatial audio effects including reverb, delay,
chorus, and phaser for creating depth and movement in audio.
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

Reverb = getattr(_pb, 'Reverb', None) if _pb else None
Delay = getattr(_pb, 'Delay', None) if _pb else None
Chorus = getattr(_pb, 'Chorus', None) if _pb else None
Phaser = getattr(_pb, 'Phaser', None) if _pb else None


@tool("reverb")
def reverb(audio: Audio, sr: int, room_size: float = 0.25, damping: float = 0.5,
           wet_level: float = 0.15, dry_level: float = 0.85, width: float = 1.0, 
           freeze_mode: float = 0.0) -> AudioBuf:
    """
    Add reverb effect to create spatial depth and ambience.
    
    Args:
        audio: Input audio array
        sr: Sample rate
        room_size: Room size (0.0 to 1.0, larger = bigger space)
        damping: High frequency damping (0.0 to 1.0, higher = more damped)
        wet_level: Volume of the reverberated signal (0.0 to 1.0)
        dry_level: Volume of the original, uneffected signal (0.0 to 1.0)
        width: Stereo width of the reverb (1.0 = full stereo, 0.0 = mono)
        freeze_mode: Freeze mode (when > 0, the reverb freezes and sustains indefinitely)
        
    Returns:
        Tuple of (reverb_audio, sample_rate)
    """
    if Reverb is None:
        print("Pedalboard not available, returning original audio")
        return audio, sr
    
    try:
        reverb_effect = Reverb(
            room_size=room_size,
            damping=damping,
            wet_level=wet_level,
            dry_level=dry_level,
            width=width,
            freeze_mode=freeze_mode
        )
        reverb_audio = reverb_effect(audio, sample_rate=sr)
        return reverb_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in reverb: {e}")
        return audio, sr


@tool("delay")
def delay(audio: Audio, sr: int, delay_seconds: float = 0.35, 
          feedback: float = 0.25, mix: float = 0.2) -> AudioBuf:
    """
    Add delay effect for echo and rhythmic repeats.
    
    Args:
        audio: Input audio array
        sr: Sample rate
        delay_seconds: Delay time in seconds (0.0 to 30.0)
        feedback: Feedback amount (0.0 to 1.0, higher = more repeats)
        mix: Dry/wet mix ratio (0.0 = dry only, 1.0 = wet only)
        
    Returns:
        Tuple of (delayed_audio, sample_rate)
    """
    if Delay is None:
        print("Pedalboard not available, returning original audio")
        return audio, sr
    
    try:
        delay_effect = Delay(
            delay_seconds=delay_seconds,
            feedback=feedback,
            mix=mix
        )
        delayed_audio = delay_effect(audio, sample_rate=sr)
        return delayed_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in delay: {e}")
        return audio, sr


@tool("chorus")
def chorus(audio: Audio, sr: int, rate_hz: float = 1.0, depth: float = 0.25,
           centre_delay_ms: float = 7.0, feedback: float = 0.0, mix: float = 0.25) -> AudioBuf:
    """
    Add chorus effect for thicker, richer sound with subtle pitch modulation.
    
    Args:
        audio: Input audio array
        sr: Sample rate
        rate_hz: Speed of the chorus effect's LFO in Hz (0-100)
        depth: Depth of the chorus effect
        centre_delay_ms: Centre delay of the modulation in milliseconds
        feedback: Feedback amount for the chorus effect
        mix: Dry/wet mix ratio (0.0 = dry only, 1.0 = wet only)
        
    Returns:
        Tuple of (chorus_audio, sample_rate)
    """
    if Chorus is None:
        print("Pedalboard not available, returning original audio")
        return audio, sr
    
    try:
        chorus_effect = Chorus(
            rate_hz=rate_hz,
            depth=depth,
            centre_delay_ms=centre_delay_ms,
            feedback=feedback,
            mix=mix
        )
        chorus_audio = chorus_effect(audio, sample_rate=sr)
        return chorus_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in chorus: {e}")
        return audio, sr


@tool("phaser")
def phaser(audio: Audio, sr: int, rate_hz: float = 0.5, depth: float = 0.5,
           centre_frequency_hz: float = 1300.0, feedback: float = 0.0, mix: float = 0.25) -> AudioBuf:
    """
    Add phaser effect for sweeping, swooshing sounds.
    
    Args:
        audio: Input audio array
        sr: Sample rate
        rate_hz: Speed of the phaser's LFO in Hz
        depth: Depth of the phaser effect
        centre_frequency_hz: Centre frequency of the modulation in Hz
        feedback: Feedback amount
        mix: Dry/wet mix ratio (0.0 = dry only, 1.0 = wet only)
        
    Returns:
        Tuple of (phased_audio, sample_rate)
    """
    if Phaser is None:
        print("Pedalboard not available, returning original audio")
        return audio, sr
    
    try:
        phaser_effect = Phaser(
            rate_hz=rate_hz,
            depth=depth,
            centre_frequency_hz=centre_frequency_hz,
            feedback=feedback,
            mix=mix
        )
        phased_audio = phaser_effect(audio, sample_rate=sr)
        return phased_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in phaser: {e}")
        return audio, sr
