"""
Text-to-Speech (TTS) Tool using SpeechBrain

This module provides text-to-speech synthesis using SpeechBrain's Tacotron2
and HiFiGAN models to convert text into natural-sounding speech audio.
"""

import numpy as np
import tempfile
import soundfile as sf
import re
from typing import Tuple

# Import types and decorator from parent directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api import tool, Audio, AudioBuf, TOOL_MESSAGES

try:
    import warnings
    warnings.filterwarnings("ignore", message=".*list_audio_backends.*")
    import torch
    import torchaudio
    # Try canonical imports first
    try:
        from speechbrain.inference.TTS import Tacotron2
    except Exception as e_tts:
        Tacotron2 = None
        _tts_import_err = e_tts
    # HIFIGAN moved in some SpeechBrain versions; try multiple locations
    HIFIGAN = None
    _hifigan_import_err = None
    try:
        from speechbrain.inference.TTS import HIFIGAN as _HIFIGAN
        HIFIGAN = _HIFIGAN
    except Exception:
        try:
            from speechbrain.inference.vocoders import HIFIGAN as _HIFIGAN
            HIFIGAN = _HIFIGAN
        except Exception as e_hifi:
            _hifigan_import_err = e_hifi
    SPEECHBRAIN_TTS_AVAILABLE = Tacotron2 is not None and HIFIGAN is not None
    if not SPEECHBRAIN_TTS_AVAILABLE:
        # Defer detailed messaging until tool use to avoid noisy startup
        pass
except ImportError as e:
    Tacotron2 = None
    HIFIGAN = None
    torch = None
    torchaudio = None
    SPEECHBRAIN_TTS_AVAILABLE = False
except Exception as e:
    Tacotron2 = None
    HIFIGAN = None
    torch = None
    torchaudio = None
    SPEECHBRAIN_TTS_AVAILABLE = False

# Global TTS models
tacotron2_model = None
hifigan_model = None

def get_tts_models():
    """Load and return the TTS models, initializing them if necessary."""
    global tacotron2_model, hifigan_model
    
    if not SPEECHBRAIN_TTS_AVAILABLE:
        return None, None
    
    if tacotron2_model is None and hifigan_model is None:
        try:
            print("Loading SpeechBrain TTS models...")
            print("  Loading Tacotron2 (text → mel-spectrogram)...")
            tacotron2_model = Tacotron2.from_hparams(
                source="speechbrain/tts-tacotron2-ljspeech",
                savedir="tmpdir_tts_tacotron2"
            )
            
            print("  Loading HiFiGAN vocoder (mel-spectrogram → waveform)...")
            hifigan_model = HIFIGAN.from_hparams(
                source="speechbrain/tts-hifigan-ljspeech",
                savedir="tmpdir_tts_hifigan"
            )
            print("✅ TTS models loaded successfully")
        except Exception as e:
            print(f"❌ Error loading TTS models: {e}")
            tacotron2_model = None
            hifigan_model = None
    
    return tacotron2_model, hifigan_model


def extract_text_from_quotes(text: str) -> str:
    """Extract text from quotes in user input."""
    # Look for text in double quotes
    double_quote_match = re.search(r'"([^"]*)"', text)
    if double_quote_match:
        return double_quote_match.group(1)
    
    # Look for text in single quotes
    single_quote_match = re.search(r"'([^']*)'", text)
    if single_quote_match:
        return single_quote_match.group(1)
    
    # If no quotes found, return the original text (fallback)
    return text.strip()


@tool("text_to_speech")
def text_to_speech(audio: Audio, sr: int, text: str = "") -> AudioBuf:
    """
    Convert text to speech using SpeechBrain's Tacotron2 and HiFiGAN models.
    
    This tool generates natural-sounding speech from text input using advanced
    neural text-to-speech synthesis. No input audio file is required - this tool
    creates audio from scratch based on the provided text.
    
    Args:
        audio: Input audio array (ignored for TTS - can be empty/dummy)
        sr: Input sample rate (ignored for TTS - output will be 22050 Hz)
        text: Text to convert to speech (extracted from quotes in user request)
        
    Returns:
        Tuple of (synthesized_audio, sample_rate) - sample_rate will be 22050
    """
    
    if not SPEECHBRAIN_TTS_AVAILABLE:
        details = []
        if 'torch' in globals() and torch is None:
            details.append("PyTorch not available")
        if 'torchaudio' in globals() and (torchaudio is None or isinstance(torchaudio, Exception)):
            details.append("torchaudio not available")
        if 'Tacotron2' in globals() and Tacotron2 is None:
            details.append(f"Tacotron2 import failed: {str(globals().get('_tts_import_err', 'unknown'))}")
        if 'HIFIGAN' in globals() and HIFIGAN is None:
            details.append(f"HIFIGAN import failed: {str(globals().get('_hifigan_import_err', 'unknown'))}")
        extra = ("; ".join([d for d in details if d])) or "Unknown import issue"
        error_msg = f"❌ SpeechBrain TTS unavailable. {extra}"
        TOOL_MESSAGES.add_message("text_to_speech", error_msg)
        return audio, sr
    
    # Extract text from quotes if provided
    if text:
        text_to_synthesize = extract_text_from_quotes(text)
    else:
        error_msg = "❌ No text provided for TTS. Please provide text in quotes like: 'Say \"Hello World\"'"
        TOOL_MESSAGES.add_message("text_to_speech", error_msg)
        return audio, sr
    
    if not text_to_synthesize.strip():
        error_msg = "❌ Empty text provided for TTS. Please provide text in quotes."
        TOOL_MESSAGES.add_message("text_to_speech", error_msg)
        return audio, sr
    
    try:
        # Get the TTS models
        tacotron2, hifigan = get_tts_models()
        if tacotron2 is None or hifigan is None:
            error_msg = "❌ Failed to load TTS models"
            TOOL_MESSAGES.add_message("text_to_speech", error_msg)
            return audio, sr
        
        # Generate mel spectrogram from text
        print(f"🎤 Synthesizing text: \"{text_to_synthesize}\"")
        mel_output, mel_length, alignment = tacotron2.encode_text(text_to_synthesize)
        
        # Vocoder turns mel spectrogram into audio waveform
        waveforms = hifigan.decode_batch(mel_output)
        
        # Convert to numpy array and ensure proper format
        synthesized_audio = waveforms.squeeze(1).cpu().numpy().astype(np.float32)
        
        # Handle batch dimension if present
        if synthesized_audio.ndim > 1:
            synthesized_audio = synthesized_audio[0]  # Take first sample if batched
        
        # Ensure audio is in proper range
        synthesized_audio = np.clip(synthesized_audio, -1.0, 1.0)
        
        # TTS output sample rate is 22050 Hz for LJSpeech models
        output_sr = 22050
        
        # Create success message
        result_msg = f"""🎤 **Text-to-Speech Results:**

📝 **Synthesized Text:**
"{text_to_synthesize}"

🔊 **Generation Info:**
- Model: Tacotron2 + HiFiGAN 
- Technology: Neural text-to-speech synthesis
- Voice: Female English speaker (LJSpeech dataset)

📊 **Audio Info:**
- Duration: {len(synthesized_audio)/output_sr:.1f} seconds
- Sample Rate: {output_sr} Hz
- Quality: High-quality neural synthesis"""
        
        TOOL_MESSAGES.add_message("text_to_speech", result_msg)
        
        # Return synthesized audio
        return synthesized_audio, output_sr
        
    except Exception as e:
        error_msg = f"❌ Error in text-to-speech synthesis: {str(e)}"
        TOOL_MESSAGES.add_message("text_to_speech", error_msg)
        return audio, sr
