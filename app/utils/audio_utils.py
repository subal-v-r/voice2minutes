import librosa
import numpy as np
from typing import Tuple
import soundfile as sf

def convert_to_wav(input_path: str, output_path: str, target_sr: int = 16000) -> str:
    """Convert audio file to WAV format with specified sample rate"""
    try:
        # Load audio file
        audio, sr = librosa.load(input_path, sr=target_sr)
        
        # Save as WAV
        sf.write(output_path, audio, target_sr)
        
        return output_path
    except Exception as e:
        raise Exception(f"Audio conversion failed: {str(e)}")

def extract_audio_from_video(video_path: str, output_path: str) -> str:
    """Extract audio from video file using librosa"""
    try:
        # librosa can handle most video formats and extract audio
        audio, sr = librosa.load(video_path, sr=16000)
        sf.write(output_path, audio, sr)
        return output_path
    except Exception as e:
        raise Exception(f"Audio extraction failed: {str(e)}")

def get_audio_duration(file_path: str) -> float:
    """Get duration of audio file in seconds"""
    try:
        audio, sr = librosa.load(file_path, sr=None)
        return len(audio) / sr
    except Exception as e:
        raise Exception(f"Could not get audio duration: {str(e)}")

def normalize_audio(audio: np.ndarray) -> np.ndarray:
    """Normalize audio to prevent clipping"""
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        return audio / max_val
    return audio

def remove_silence(audio: np.ndarray, sr: int, threshold: float = 0.01) -> np.ndarray:
    """Remove silence from audio"""
    # Simple silence removal based on amplitude threshold
    mask = np.abs(audio) > threshold
    return audio[mask]
