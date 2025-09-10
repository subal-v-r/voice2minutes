import re
import spacy
from typing import List, Dict, Any
from datetime import datetime
import dateparser

class TextPreprocessor:
    def __init__(self):
        """Initialize text preprocessor with spaCy model"""
        self.nlp = None
        self.filler_words = {
            'um', 'uh', 'er', 'ah', 'like', 'you know', 'i mean', 'sort of', 
            'kind of', 'basically', 'actually', 'literally', 'obviously',
            'well', 'so', 'right', 'okay', 'alright', 'yeah', 'yes', 'no'
        }
        
        self.contractions = {
            "won't": "will not", "can't": "cannot", "n't": " not",
            "'re": " are", "'ve": " have", "'ll": " will", "'d": " would",
            "'m": " am", "let's": "let us", "that's": "that is",
            "there's": "there is", "here's": "here is", "what's": "what is",
            "where's": "where is", "how's": "how is", "it's": "it is",
            "he's": "he is", "she's": "she is", "we're": "we are",
            "they're": "they are", "i'm": "i am", "you're": "you are",
            "don't": "do not", "doesn't": "does not", "didn't": "did not",
            "haven't": "have not", "hasn't": "has not", "hadn't": "had not",
            "won't": "will not", "wouldn't": "would not", "shouldn't": "should not",
            "couldn't": "could not", "mustn't": "must not"
        }
    
    def load_spacy_model(self):
        """Load spaCy model for sentence segmentation"""
        if self.nlp is None:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("Warning: spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
                print("Using basic sentence splitting as fallback.")
                self.nlp = None
    
    def remove_filler_words(self, text: str) -> str:
        """Remove filler words from text"""
        words = text.lower().split()
        filtered_words = []
        
        i = 0
        while i < len(words):
            word = words[i].strip('.,!?;:')
            
            # Check for multi-word fillers
            if i < len(words) - 1:
                two_word = f"{word} {words[i+1].strip('.,!?;:')}"
                if two_word in self.filler_words:
                    i += 2
                    continue
            
            if word not in self.filler_words:
                filtered_words.append(words[i])
            
            i += 1
        
        return ' '.join(filtered_words)
    
    def expand_contractions(self, text: str) -> str:
        """Expand contractions in text"""
        for contraction, expansion in self.contractions.items():
            text = re.sub(re.escape(contraction), expansion, text, flags=re.IGNORECASE)
        return text
    
    def standardize_dates(self, text: str) -> str:
        """Standardize dates to ISO 8601 format"""
        # Common date patterns
        date_patterns = [
            r'\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b',  # MM/DD/YYYY or MM/DD/YY
            r'\b(\d{1,2})-(\d{1,2})-(\d{2,4})\b',  # MM-DD-YYYY or MM-DD-YY
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})\b',
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})\b',
            r'\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b',
            r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\b'
        ]
        
        def replace_date(match):
            try:
                date_str = match.group(0)
                parsed_date = dateparser.parse(date_str)
                if parsed_date:
                    return parsed_date.strftime('%Y-%m-%d')
                return date_str
            except:
                return match.group(0)
        
        for pattern in date_patterns:
            text = re.sub(pattern, replace_date, text, flags=re.IGNORECASE)
        
        return text
    
    def segment_sentences(self, text: str) -> List[str]:
        """Segment text into sentences using spaCy"""
        if self.nlp is None:
            self.load_spacy_model()
        
        if self.nlp is not None:
            doc = self.nlp(text)
            return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        else:
            # Fallback: simple sentence splitting
            sentences = re.split(r'[.!?]+', text)
            return [sent.strip() for sent in sentences if sent.strip()]
    
    def clean_text(self, text: str) -> str:
        """General text cleaning"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove repeated punctuation
        text = re.sub(r'[.]{2,}', '.', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.!?,:;])', r'\1', text)
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)
        
        return text.strip()
    
    def process_transcript_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process individual transcript segments"""
        processed_segments = []
        
        for segment in segments:
            text = segment.get('text', '')
            
            # Apply preprocessing steps
            text = self.remove_filler_words(text)
            text = self.expand_contractions(text)
            text = self.standardize_dates(text)
            text = self.clean_text(text)
            
            # Skip empty segments
            if not text:
                continue
            
            processed_segment = segment.copy()
            processed_segment['text'] = text
            processed_segment['sentences'] = self.segment_sentences(text)
            
            processed_segments.append(processed_segment)
        
        return processed_segments

# Global preprocessor instance
preprocessor = TextPreprocessor()

def preprocess_transcript(transcript_data: Dict[str, Any]) -> Dict[str, Any]:
    """Preprocess complete transcript data"""
    processed_data = transcript_data.copy()
    
    # Process segments
    if 'segments' in transcript_data:
        processed_data['segments'] = preprocessor.process_transcript_segments(transcript_data['segments'])
    
    # Process full text
    if 'full_text' in transcript_data:
        full_text = transcript_data['full_text']
        full_text = preprocessor.remove_filler_words(full_text)
        full_text = preprocessor.expand_contractions(full_text)
        full_text = preprocessor.standardize_dates(full_text)
        full_text = preprocessor.clean_text(full_text)
        processed_data['full_text'] = full_text
        processed_data['sentences'] = preprocessor.segment_sentences(full_text)
    
    return processed_data
