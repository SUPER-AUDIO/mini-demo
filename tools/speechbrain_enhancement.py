"""
Speech Enhancement Tool using SpeechBrain

This module provides speech enhancement using SpeechBrain's MetricGAN+ model
to improve speech quality by reducing noise and artifacts.
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
    from speechbrain.inference.enhancement import SpectralMaskEnhancement
    SPEECHBRAIN_ENHANCEMENT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: speechbrain or torchaudio not available: {e}")
    print("Install with: pip install speechbrain torchaudio")
    SpectralMaskEnhancement = None
    torchaudio = None
    SPEECHBRAIN_ENHANCEMENT_AVAILABLE = False
except Exception as e:
    print(f"Warning: speechbrain/torchaudio compatibility issue: {e}")
    print("This may be a version compatibility problem. Try updating PyTorch and torchaudio.")
    SpectralMaskEnhancement = None
    torchaudio = None
    SPEECHBRAIN_ENHANCEMENT_AVAILABLE = False

# Global enhancement model
enhancement_model = None

def get_enhancement_model():
    """Load and return the speech enhancement model, initializing it if necessary."""
    global enhancement_model
    
    if not SPEECHBRAIN_ENHANCEMENT_AVAILABLE:
        return None
    
    if enhancement_model is None and SpectralMaskEnhancement is not None:
        try:
            print("Loading SpeechBrain MetricGAN+ enhancement model...")
            enhancement_model = SpectralMaskEnhancement.from_hparams(
                source="speechbrain/metricgan-plus-voicebank",
                savedir="pretrained_se_metricgan"
            )
            print("✅ Speech enhancement model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading speech enhancement model: {e}")
            enhancement_model = None
    
    return enhancement_model


@tool("speechbrain_enhancement")
def speechbrain_enhancement(audio: Audio, sr: int) -> AudioBuf:
    """
    Enhance speech quality using SpeechBrain's MetricGAN+ model.
    
    This tool uses advanced neural network models to reduce noise, 
    improve speech clarity, and enhance overall audio quality.
    The model works best with 16kHz audio but can handle other sample rates.
    
    Args:
        audio: Input audio array (numpy.ndarray of float32 values between -1.0 and 1.0)
        sr: Sample rate (int, model optimized for 16000 Hz)
        
    Returns:
        Tuple of (enhanced_audio, sample_rate)
    """
    
    if not SPEECHBRAIN_ENHANCEMENT_AVAILABLE:
        error_msg = "❌ SpeechBrain enhancement not available. Please install with: pip install speechbrain torchaudio"
        TOOL_MESSAGES.add_message("speechbrain_enhancement", error_msg)
        return audio, sr
    
    try:
        # Get the enhancement model
        model = get_enhancement_model()
        if model is None:
            error_msg = "❌ Failed to load speech enhancement model"
            TOOL_MESSAGES.add_message("speechbrain_enhancement", error_msg)
            return audio, sr
        
        # Save input audio to temporary file for SpeechBrain processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as input_temp:
            # Ensure audio is in the right format
            audio_normalized = np.clip(audio.astype(np.float32), -1.0, 1.0)
            sf.write(input_temp.name, audio_normalized, sr)
            
            # Create output temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as output_temp:
                try:
                    # Enhance the audio file
                    enhanced = model.enhance_file(input_temp.name, output_filename=output_temp.name)
                    
                    # Load the enhanced audio
                    enhanced_audio, enhanced_sr = sf.read(output_temp.name)
                    enhanced_audio = enhanced_audio.astype(np.float32)
                    
                    # Clean up temporary files
                    os.unlink(input_temp.name)
                    os.unlink(output_temp.name)
                    
                    # Create success message
                    result_msg = f"""🔊 **Speech Enhancement Results:**

✨ **Enhancement Applied:**
- Model: MetricGAN+ (speechbrain/metricgan-plus-voicebank)
- Processing: Neural noise reduction and speech clarity improvement

📊 **Audio Info:**
- Input Duration: {len(audio)/sr:.1f} seconds
- Output Duration: {len(enhanced_audio)/enhanced_sr:.1f} seconds
- Input Sample Rate: {sr} Hz
- Output Sample Rate: {enhanced_sr} Hz
- Enhancement Quality: Professional-grade neural processing"""
                    
                    TOOL_MESSAGES.add_message("speechbrain_enhancement", result_msg)
                    
                    # Return enhanced audio
                    return enhanced_audio, enhanced_sr
                    
                except Exception as e:
                    # Clean up temp files on error
                    try:
                        os.unlink(input_temp.name)
                        os.unlink(output_temp.name)
                    except:
                        pass
                    raise e
        
    except Exception as e:
        error_msg = f"❌ Error in speech enhancement: {str(e)}"
        TOOL_MESSAGES.add_message("speechbrain_enhancement", error_msg)
        return audio, sr
