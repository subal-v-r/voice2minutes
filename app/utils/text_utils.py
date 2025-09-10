import re
from typing import List, Dict, Any
from datetime import datetime, timedelta
import dateparser

def extract_time_mentions(text: str) -> List[Dict[str, Any]]:
    """Extract time mentions from text"""
    time_patterns = [
        r'\b(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)\b',
        r'\b(\d{1,2})\s*(AM|PM|am|pm)\b',
        r'\b(morning|afternoon|evening|night)\b',
        r'\b(today|tomorrow|yesterday)\b',
        r'\b(next|this)\s+(week|month|year)\b'
    ]
    
    time_mentions = []
    for pattern in time_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            time_mentions.append({
                'text': match.group(0),
                'start': match.start(),
                'end': match.end()
            })
    
    return time_mentions

def extract_email_addresses(text: str) -> List[str]:
    """Extract email addresses from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)

def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers from text"""
    phone_patterns = [
        r'\b\d{3}-\d{3}-\d{4}\b',
        r'\b$$\d{3}$$\s*\d{3}-\d{4}\b',
        r'\b\d{3}\.\d{3}\.\d{4}\b',
        r'\b\d{10}\b'
    ]
    
    phone_numbers = []
    for pattern in phone_patterns:
        phone_numbers.extend(re.findall(pattern, text))
    
    return phone_numbers

def calculate_speaking_time(segments: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate speaking time for each speaker"""
    speaker_time = {}
    
    for segment in segments:
        speaker = segment.get('speaker', 'Unknown')
        duration = segment.get('end', 0) - segment.get('start', 0)
        
        if speaker in speaker_time:
            speaker_time[speaker] += duration
        else:
            speaker_time[speaker] = duration
    
    return speaker_time

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

def clean_speaker_name(speaker: str) -> str:
    """Clean and standardize speaker names"""
    # Remove common prefixes/suffixes
    speaker = re.sub(r'^(SPEAKER_|Speaker_)', '', speaker)
    
    # Capitalize first letter of each word
    speaker = ' '.join(word.capitalize() for word in speaker.split())
    
    return speaker

def merge_consecutive_segments(segments: List[Dict[str, Any]], max_gap: float = 2.0) -> List[Dict[str, Any]]:
    """Merge consecutive segments from the same speaker"""
    if not segments:
        return segments
    
    merged = []
    current_segment = segments[0].copy()
    
    for i in range(1, len(segments)):
        next_segment = segments[i]
        
        # Check if same speaker and small gap
        if (current_segment['speaker'] == next_segment['speaker'] and 
            next_segment['start'] - current_segment['end'] <= max_gap):
            
            # Merge segments
            current_segment['text'] += ' ' + next_segment['text']
            current_segment['end'] = next_segment['end']
        else:
            # Add current segment and start new one
            merged.append(current_segment)
            current_segment = next_segment.copy()
    
    # Add the last segment
    merged.append(current_segment)
    
    return merged
