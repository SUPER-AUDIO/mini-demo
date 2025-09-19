"""
Speech Recognition Tool

This module provides automatic speech recognition (ASR) using SpeechBrain.
It transcribes audio files to text using the asr-crdnn-rnnlm-librispeech model.
"""

import numpy as np
import tempfile
import soundfile as sf
from typing import Tuple

# Import types and decorator from parent directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api import tool, Audio, AudioBuf, TOOL_MESSAGES

try:
    import torchaudio
    from speechbrain.inference.ASR import EncoderDecoderASR
    SPEECHBRAIN_AVAILABLE = True
except ImportError as e:
    print(f"Warning: speechbrain or torchaudio not available: {e}")
    print("Install with: pip install speechbrain torchaudio")
    EncoderDecoderASR = None
    torchaudio = None
    SPEECHBRAIN_AVAILABLE = False
except Exception as e:
    print(f"Warning: speechbrain/torchaudio compatibility issue: {e}")
    print("This may be a version compatibility problem. Try updating PyTorch and torchaudio.")
    EncoderDecoderASR = None
    torchaudio = None
    SPEECHBRAIN_AVAILABLE = False

# Global ASR model
asr_model = None

def get_asr_model():
    """Load and return the ASR model, initializing it if necessary."""
    global asr_model
    
    if not SPEECHBRAIN_AVAILABLE:
        return None
    
    if asr_model is None and EncoderDecoderASR is not None:
        try:
            print("Loading SpeechBrain ASR model...")
            asr_model = EncoderDecoderASR.from_hparams(
                source="speechbrain/asr-crdnn-rnnlm-librispeech",
                savedir="pretrained_asr"
            )
            print("✅ ASR model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading ASR model: {e}")
            asr_model = None
    
    return asr_model


@tool("speech_recognition")
def speech_recognition(audio: Audio, sr: int) -> AudioBuf:
    """
    Transcribe audio to text using automatic speech recognition.
    
    This tool uses SpeechBrain's ASR model to convert speech to text.
    The transcript is displayed in the chat history, and the original
    audio is returned unchanged.
    
    Args:
        audio: Input audio array (numpy.ndarray of float32 values between -1.0 and 1.0)
        sr: Sample rate (int, typically 16000, 22050, 44100, etc.)
        
    Returns:
        Tuple of (original_audio, sample_rate) - audio is unchanged
        The transcript is printed to console and will appear in chat history
    """
    
    if not SPEECHBRAIN_AVAILABLE:
        error_msg = "❌ SpeechBrain not available. Please install with: pip install speechbrain torchaudio"
        TOOL_MESSAGES.add_message("speech_recognition", error_msg)
        return audio, sr
    
    try:
        # Get the ASR model
        model = get_asr_model()
        if model is None:
            error_msg = "❌ Failed to load ASR model"
            TOOL_MESSAGES.add_message("speech_recognition", error_msg)
            return audio, sr
        
        # Save audio to temporary file for SpeechBrain processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            # Ensure audio is in the right format for SpeechBrain
            audio_normalized = np.clip(audio.astype(np.float32), -1.0, 1.0)
            sf.write(temp_file.name, audio_normalized, sr)
            
            # Transcribe the audio
            transcript = model.transcribe_file(temp_file.name)
            
            # Clean up temporary file
            os.unlink(temp_file.name)
        
        # Store the transcript for display in chat history
        transcript_text = str(transcript).strip()
        if transcript_text:
            result_msg = f"""🎤 **Speech Recognition Results:**

📝 **Transcript:**
"{transcript_text}"

📊 **Audio Info:**
- Duration: {len(audio)/sr:.1f} seconds
- Sample Rate: {sr} Hz
- Processing: SpeechBrain ASR (asr-crdnn-rnnlm-librispeech)"""
        else:
            result_msg = "🎤 **Speech Recognition:** No speech detected or transcript is empty."
        
        # Store the message for display in the UI
        TOOL_MESSAGES.add_message("speech_recognition", result_msg)
        
        # Return original audio unchanged (ASR doesn't modify audio)
        return audio, sr
        
    except Exception as e:
        error_msg = f"❌ Error in speech recognition: {str(e)}"
        TOOL_MESSAGES.add_message("speech_recognition", error_msg)
        return audio, sr
