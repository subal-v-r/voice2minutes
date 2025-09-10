import re
import dateparser
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

class DeadlineExtractor:
    def __init__(self):
        """Initialize deadline extractor"""
        self.date_patterns = [
            # Explicit dates
            r'\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b',  # MM/DD/YYYY
            r'\b(\d{1,2})-(\d{1,2})-(\d{2,4})\b',  # MM-DD-YYYY
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})\b',
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})\b',
            
            # Relative dates
            r'\b(today|tomorrow|yesterday)\b',
            r'\b(next|this)\s+(week|month|year|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(end of|beginning of)\s+(week|month|year|quarter)\b',
            r'\bin\s+(\d+)\s+(days?|weeks?|months?)\b',
            r'\bwithin\s+(\d+)\s+(days?|weeks?|months?)\b',
            
            # Deadline indicators with time
            r'\bby\s+(.*?)(?:\.|,|$)',
            r'\bbefore\s+(.*?)(?:\.|,|$)',
            r'\buntil\s+(.*?)(?:\.|,|$)',
            r'\bdue\s+(.*?)(?:\.|,|$)',
            r'\bdeadline\s*:?\s*(.*?)(?:\.|,|$)',
            
            # Quarter and fiscal periods
            r'\b(Q1|Q2|Q3|Q4)\s*(\d{4})?\b',
            r'\b(first|second|third|fourth)\s+quarter\b',
            
            # Time of day
            r'\b(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)\b',
            r'\b(\d{1,2})\s*(AM|PM|am|pm)\b',
        ]
        
        self.urgency_indicators = {
            'asap': 0,  # Immediate
            'urgent': 1,  # Within 1 day
            'high priority': 2,  # Within 3 days
            'soon': 7,  # Within 1 week
            'eventually': 30  # Within 1 month
        }
    
    def extract_date_mentions(self, text: str) -> List[Dict[str, Any]]:
        """Extract all date mentions from text"""
        mentions = []
        text_lower = text.lower()
        
        for pattern in self.date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                mentions.append({
                    'text': match.group(0),
                    'start': match.start(),
                    'end': match.end(),
                    'full_match': match.groups() if match.groups() else None
                })
        
        return mentions
    
    def parse_relative_date(self, text: str) -> Optional[datetime]:
        """Parse relative date expressions"""
        text_lower = text.lower().strip()
        now = datetime.now()
        
        # Handle urgency indicators
        for indicator, days in self.urgency_indicators.items():
            if indicator in text_lower:
                return now + timedelta(days=days)
        
        # Handle specific relative expressions
        if 'today' in text_lower:
            return now
        elif 'tomorrow' in text_lower:
            return now + timedelta(days=1)
        elif 'yesterday' in text_lower:
            return now - timedelta(days=1)
        elif 'next week' in text_lower:
            return now + timedelta(weeks=1)
        elif 'this week' in text_lower:
            # End of this week (Friday)
            days_until_friday = (4 - now.weekday()) % 7
            return now + timedelta(days=days_until_friday)
        elif 'next month' in text_lower:
            return now + timedelta(days=30)
        elif 'end of month' in text_lower:
            # Last day of current month
            if now.month == 12:
                return datetime(now.year + 1, 1, 1) - timedelta(days=1)
            else:
                return datetime(now.year, now.month + 1, 1) - timedelta(days=1)
        
        # Handle "in X days/weeks/months"
        in_match = re.search(r'in\s+(\d+)\s+(days?|weeks?|months?)', text_lower)
        if in_match:
            number = int(in_match.group(1))
            unit = in_match.group(2)
            
            if 'day' in unit:
                return now + timedelta(days=number)
            elif 'week' in unit:
                return now + timedelta(weeks=number)
            elif 'month' in unit:
                return now + timedelta(days=number * 30)
        
        # Handle "within X days/weeks/months"
        within_match = re.search(r'within\s+(\d+)\s+(days?|weeks?|months?)', text_lower)
        if within_match:
            number = int(within_match.group(1))
            unit = within_match.group(2)
            
            if 'day' in unit:
                return now + timedelta(days=number)
            elif 'week' in unit:
                return now + timedelta(weeks=number)
            elif 'month' in unit:
                return now + timedelta(days=number * 30)
        
        return None
    
    def parse_with_dateparser(self, text: str) -> Optional[datetime]:
        """Parse date using dateparser library"""
        try:
            # Clean the text
            cleaned_text = re.sub(r'[^\w\s/\-:,]', '', text)
            
            # Try to parse with dateparser
            parsed_date = dateparser.parse(
                cleaned_text,
                settings={
                    'PREFER_DATES_FROM': 'future',
                    'RELATIVE_BASE': datetime.now()
                }
            )
            
            return parsed_date
        except Exception:
            return None
    
    def extract_deadline_from_text(self, text: str) -> Optional[str]:
        """Extract deadline from action item text"""
        text_lower = text.lower()
        
        # Look for deadline indicators
        deadline_patterns = [
            r'\bby\s+(.*?)(?:\.|,|;|$)',
            r'\bbefore\s+(.*?)(?:\.|,|;|$)',
            r'\buntil\s+(.*?)(?:\.|,|;|$)',
            r'\bdue\s+(.*?)(?:\.|,|;|$)',
            r'\bdeadline\s*:?\s*(.*?)(?:\.|,|;|$)',
        ]
        
        for pattern in deadline_patterns:
            match = re.search(pattern, text_lower)
            if match:
                deadline_text = match.group(1).strip()
                
                # Try relative parsing first
                relative_date = self.parse_relative_date(deadline_text)
                if relative_date:
                    return relative_date.isoformat()
                
                # Try dateparser
                parsed_date = self.parse_with_dateparser(deadline_text)
                if parsed_date:
                    return parsed_date.isoformat()
        
        # Look for any date mentions in the text
        date_mentions = self.extract_date_mentions(text)
        for mention in date_mentions:
            # Try relative parsing
            relative_date = self.parse_relative_date(mention['text'])
            if relative_date:
                return relative_date.isoformat()
            
            # Try dateparser
            parsed_date = self.parse_with_dateparser(mention['text'])
            if parsed_date:
                return parsed_date.isoformat()
        
        # Check for urgency indicators without specific dates
        for indicator, days in self.urgency_indicators.items():
            if indicator in text_lower:
                deadline = datetime.now() + timedelta(days=days)
                return deadline.isoformat()
        
        return None
    
    def classify_urgency(self, deadline_str: Optional[str]) -> str:
        """Classify urgency based on deadline"""
        if not deadline_str:
            return 'low'
        
        try:
            deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
            now = datetime.now()
            
            if deadline.tzinfo:
                # Make now timezone aware if deadline is
                from datetime import timezone
                now = now.replace(tzinfo=timezone.utc)
            
            days_until = (deadline - now).days
            
            if days_until < 0:
                return 'overdue'
            elif days_until == 0:
                return 'urgent'
            elif days_until <= 3:
                return 'high'
            elif days_until <= 7:
                return 'medium'
            else:
                return 'low'
        
        except Exception:
            return 'low'

# Global extractor instance
deadline_extractor = DeadlineExtractor()

def extract_deadlines(text: str) -> Optional[str]:
    """Extract deadline from action item text"""
    return deadline_extractor.extract_deadline_from_text(text)

def get_deadline_urgency(deadline_str: Optional[str]) -> str:
    """Get urgency classification for deadline"""
    return deadline_extractor.classify_urgency(deadline_str)
