import whisper
import torch
import librosa
import soundfile as sf
import os
import tempfile
from typing import Dict, List, Any
from pyannote.audio import Pipeline
from pyannote.core import Segment
import numpy as np

class ASRService:
    def __init__(self):
        """Initialize ASR service with Whisper and pyannote models"""
        self.whisper_model = None
        self.diarization_pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_models(self):
        """Load Whisper and diarization models"""
        if self.whisper_model is None:
            print("Loading Whisper model...")
            self.whisper_model = whisper.load_model("base", device=self.device)
        
        if self.diarization_pipeline is None:
            print("Loading speaker diarization pipeline...")
            try:
                # Note: This requires HuggingFace token for pyannote models
                self.diarization_pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=os.getenv("HUGGINGFACE_TOKEN")
                )
            except Exception as e:
                print(f"Warning: Could not load diarization pipeline: {e}")
                print("Speaker diarization will be disabled. Set HUGGINGFACE_TOKEN environment variable.")
                self.diarization_pipeline = None

    def preprocess_audio(self, file_path: str) -> str:
        """Convert audio to format suitable for processing"""
        # Load audio file
        audio, sr = librosa.load(file_path, sr=16000)
        
        # Create temporary WAV file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        sf.write(temp_file.name, audio, 16000)
        
        return temp_file.name

    def transcribe_with_whisper(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe audio using Whisper"""
        if self.whisper_model is None:
            self.load_models()
        
        print("Transcribing audio with Whisper...")
        result = self.whisper_model.transcribe(
            audio_path,
            word_timestamps=True,
            verbose=False
        )
        
        return result

    def perform_diarization(self, audio_path: str) -> List[Dict[str, Any]]:
        """Perform speaker diarization"""
        if self.diarization_pipeline is None:
            return []
        
        print("Performing speaker diarization...")
        try:
            diarization = self.diarization_pipeline(audio_path)
            
            speakers = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                speakers.append({
                    'speaker': speaker,
                    'start': turn.start,
                    'end': turn.end
                })
            
            return speakers
        except Exception as e:
            print(f"Diarization failed: {e}")
            return []

    def align_transcript_with_speakers(self, transcript: Dict[str, Any], speakers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Align transcript segments with speaker information"""
        if not speakers:
            # No diarization available, return transcript with generic speakers
            segments = []
            for segment in transcript.get('segments', []):
                segments.append({
                    'text': segment['text'].strip(),
                    'start': segment['start'],
                    'end': segment['end'],
                    'speaker': 'Speaker_1',
                    'confidence': segment.get('avg_logprob', 0.0)
                })
            return segments
        
        aligned_segments = []
        
        for segment in transcript.get('segments', []):
            segment_start = segment['start']
            segment_end = segment['end']
            segment_text = segment['text'].strip()
            
            # Find the speaker for this segment
            best_speaker = 'Unknown'
            max_overlap = 0
            
            for speaker_info in speakers:
                # Calculate overlap between segment and speaker turn
                overlap_start = max(segment_start, speaker_info['start'])
                overlap_end = min(segment_end, speaker_info['end'])
                overlap_duration = max(0, overlap_end - overlap_start)
                
                if overlap_duration > max_overlap:
                    max_overlap = overlap_duration
                    best_speaker = speaker_info['speaker']
            
            aligned_segments.append({
                'text': segment_text,
                'start': segment_start,
                'end': segment_end,
                'speaker': best_speaker,
                'confidence': segment.get('avg_logprob', 0.0)
            })
        
        return aligned_segments

    def process_audio_file(self, file_path: str) -> Dict[str, Any]:
        """Complete audio processing pipeline"""
        try:
            # Preprocess audio
            processed_audio_path = self.preprocess_audio(file_path)
            
            # Transcribe with Whisper
            transcript = self.transcribe_with_whisper(processed_audio_path)
            
            # Perform speaker diarization
            speakers = self.perform_diarization(processed_audio_path)
            
            # Align transcript with speakers
            aligned_segments = self.align_transcript_with_speakers(transcript, speakers)
            
            # Get unique speakers
            unique_speakers = list(set([seg['speaker'] for seg in aligned_segments]))
            
            # Clean up temporary file
            os.unlink(processed_audio_path)
            
            return {
                'full_text': transcript.get('text', ''),
                'segments': aligned_segments,
                'speakers': unique_speakers,
                'language': transcript.get('language', 'en'),
                'duration': max([seg['end'] for seg in aligned_segments]) if aligned_segments else 0
            }
            
        except Exception as e:
            print(f"Error processing audio file: {e}")
            raise Exception(f"Audio processing failed: {str(e)}")

# Global ASR service instance
asr_service = ASRService()

async def process_audio_file(file_path: str) -> Dict[str, Any]:
    """Async wrapper for audio processing"""
    return asr_service.process_audio_file(file_path)
