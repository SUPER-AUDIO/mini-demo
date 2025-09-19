"""
Master Tools

This module provides mastering and final output tools including
limiting for peak control and output safety.
"""

import numpy as np
from typing import Tuple

# Import types and decorator from parent directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api import tool, Audio, AudioBuf

try:
    from pedalboard import Limiter
except ImportError:
    print("Warning: pedalboard not installed. Install with: pip install pedalboard")
    Limiter = None


@tool("limiter")
def limiter(audio: Audio, sr: int, threshold_db: float = -1.0, 
            release_ms: float = 100.0) -> AudioBuf:
    """
    Apply limiter to prevent digital clipping and control peak levels.
    
    Args:
        audio: Input audio array
        sr: Sample rate
        threshold_db: Limiting threshold in dB (peaks above this are limited)
        release_ms: Release time in milliseconds
        
    Returns:
        Tuple of (limited_audio, sample_rate)
    """
    if Limiter is None:
        print("Pedalboard not available, returning original audio")
        return audio, sr
    
    try:
        limiter_effect = Limiter(
            threshold_db=threshold_db,
            release_ms=release_ms
        )
        limited_audio = limiter_effect(audio, sample_rate=sr)
        return limited_audio.astype(np.float32), sr
    except Exception as e:
        print(f"Error in limiter: {e}")
        return audio, sr
