from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from typing import Dict, List, Any
import re

class MeetingSummarizer:
    def __init__(self):
        """Initialize meeting summarizer with flan-t5-small model"""
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.max_input_length = 512
        self.max_output_length = 256
    
    def load_model(self):
        """Load flan-t5-small model and tokenizer"""
        if self.model is None:
            print("Loading flan-t5-small model...")
            model_name = "google/flan-t5-small"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            self.model.to(self.device)
    
    def chunk_text(self, text: str, max_length: int = 400) -> List[str]:
        """Split text into chunks that fit model input limits"""
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) < max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def generate_summary(self, text: str, prompt: str) -> str:
        """Generate summary using flan-t5 with specific prompt"""
        if self.model is None:
            self.load_model()
        
        # Prepare input
        input_text = f"{prompt}\n\nText: {text}"
        
        # Tokenize
        inputs = self.tokenizer(
            input_text,
            max_length=self.max_input_length,
            truncation=True,
            return_tensors="pt"
        ).to(self.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=self.max_output_length,
                num_beams=4,
                temperature=0.7,
                do_sample=True,
                early_stopping=True
            )
        
        # Decode
        summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return summary.strip()
    
    def extract_agenda_items(self, text: str) -> List[str]:
        """Extract agenda items from meeting transcript"""
        prompt = "Extract the main agenda items or topics discussed in this meeting. List them as bullet points:"
        
        chunks = self.chunk_text(text)
        all_items = []
        
        for chunk in chunks:
            summary = self.generate_summary(chunk, prompt)
            # Parse bullet points
            items = re.findall(r'[•\-\*]\s*(.+)', summary)
            all_items.extend(items)
        
        # Remove duplicates and clean up
        unique_items = []
        for item in all_items:
            item = item.strip()
            if item and item not in unique_items:
                unique_items.append(item)
        
        return unique_items[:10]  # Limit to top 10 items
    
    def extract_decisions(self, text: str) -> List[str]:
        """Extract decisions made during the meeting"""
        prompt = "Identify the key decisions made in this meeting. List each decision clearly:"
        
        chunks = self.chunk_text(text)
        all_decisions = []
        
        for chunk in chunks:
            summary = self.generate_summary(chunk, prompt)
            # Look for decision indicators
            decisions = re.findall(r'(?:decided|agreed|resolved|concluded)\s+(?:to\s+)?(.+?)(?:\.|$)', summary, re.IGNORECASE)
            all_decisions.extend(decisions)
        
        # Clean up decisions
        unique_decisions = []
        for decision in all_decisions:
            decision = decision.strip()
            if decision and len(decision) > 10 and decision not in unique_decisions:
                unique_decisions.append(decision)
        
        return unique_decisions[:8]  # Limit to top 8 decisions
    
    def identify_risks(self, text: str) -> List[str]:
        """Identify risks mentioned in the meeting"""
        prompt = "Identify any risks, concerns, or potential issues mentioned in this meeting:"
        
        chunks = self.chunk_text(text)
        all_risks = []
        
        for chunk in chunks:
            summary = self.generate_summary(chunk, prompt)
            # Look for risk indicators
            risks = re.findall(r'(?:risk|concern|issue|problem|challenge)\s*:?\s*(.+?)(?:\.|$)', summary, re.IGNORECASE)
            all_risks.extend(risks)
        
        # Clean up risks
        unique_risks = []
        for risk in all_risks:
            risk = risk.strip()
            if risk and len(risk) > 10 and risk not in unique_risks:
                unique_risks.append(risk)
        
        return unique_risks[:6]  # Limit to top 6 risks
    
    def extract_next_steps(self, text: str) -> List[str]:
        """Extract next steps from the meeting"""
        prompt = "Identify the next steps, follow-up actions, or future plans mentioned in this meeting:"
        
        chunks = self.chunk_text(text)
        all_steps = []
        
        for chunk in chunks:
            summary = self.generate_summary(chunk, prompt)
            # Look for action indicators
            steps = re.findall(r'(?:will|should|need to|must|plan to)\s+(.+?)(?:\.|$)', summary, re.IGNORECASE)
            all_steps.extend(steps)
        
        # Clean up steps
        unique_steps = []
        for step in all_steps:
            step = step.strip()
            if step and len(step) > 5 and step not in unique_steps:
                unique_steps.append(step)
        
        return unique_steps[:10]  # Limit to top 10 steps
    
    def generate_executive_summary(self, text: str) -> str:
        """Generate an executive summary of the meeting"""
        prompt = "Provide a concise executive summary of this meeting, highlighting the most important points:"
        
        # Use first chunk for executive summary
        chunks = self.chunk_text(text, max_length=600)
        if chunks:
            return self.generate_summary(chunks[0], prompt)
        return "No content available for summary."

# Global summarizer instance
summarizer = MeetingSummarizer()

def generate_meeting_summary(transcript_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive meeting summary"""
    full_text = transcript_data.get('full_text', '')
    
    if not full_text:
        return {
            'executive_summary': 'No transcript available',
            'agenda_items': [],
            'decisions': [],
            'risks': [],
            'next_steps': []
        }
    
    print("Generating meeting summary...")
    
    # Generate all summary components
    summary = {
        'executive_summary': summarizer.generate_executive_summary(full_text),
        'agenda_items': summarizer.extract_agenda_items(full_text),
        'decisions': summarizer.extract_decisions(full_text),
        'risks': summarizer.identify_risks(full_text),
        'next_steps': summarizer.extract_next_steps(full_text)
    }
    
    return summary
