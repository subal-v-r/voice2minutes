from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import re
from typing import List, Dict, Any
import spacy

class AssigneeExtractor:
    def __init__(self):
        """Initialize NER model for assignee extraction"""
        self.ner_pipeline = None
        self.nlp = None
        
        # Common name patterns and titles
        self.name_patterns = [
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # First Last
            r'\b[A-Z][a-z]+\b',  # Single name
        ]
        
        self.title_patterns = [
            r'\b(Mr|Mrs|Ms|Dr|Prof|CEO|CTO|VP|Director|Manager|Lead|Senior|Junior)\b\.?\s*',
        ]
        
        # Pronouns and role indicators
        self.assignee_indicators = {
            'pronouns': ['I', 'we', 'you', 'he', 'she', 'they'],
            'roles': ['team', 'developer', 'designer', 'manager', 'analyst', 'engineer'],
            'assignment_phrases': [
                'assigned to', 'responsible for', 'will handle', 'takes care of',
                'in charge of', 'owns', 'leads', 'manages'
            ]
        }
    
    def load_models(self):
        """Load NER model and spaCy"""
        if self.ner_pipeline is None:
            print("Loading NER model...")
            try:
                self.ner_pipeline = pipeline(
                    "ner",
                    model="dslim/bert-base-NER",
                    tokenizer="dslim/bert-base-NER",
                    aggregation_strategy="simple"
                )
            except Exception as e:
                print(f"Warning: Could not load NER model: {e}")
                self.ner_pipeline = None
        
        if self.nlp is None:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("Warning: spaCy model not found.")
                self.nlp = None
    
    def extract_entities_with_bert(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities using BERT NER"""
        if self.ner_pipeline is None:
            return []
        
        try:
            entities = self.ner_pipeline(text)
            
            # Filter for person names
            person_entities = []
            for entity in entities:
                if entity['entity_group'] in ['PER', 'PERSON']:
                    person_entities.append({
                        'text': entity['word'],
                        'label': entity['entity_group'],
                        'confidence': entity['score'],
                        'start': entity['start'],
                        'end': entity['end']
                    })
            
            return person_entities
        except Exception as e:
            print(f"NER extraction failed: {e}")
            return []
    
    def extract_entities_with_spacy(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities using spaCy"""
        if self.nlp is None:
            return []
        
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'confidence': 0.8,  # spaCy doesn't provide confidence scores
                    'start': ent.start_char,
                    'end': ent.end_char
                })
        
        return entities
    
    def extract_names_with_regex(self, text: str) -> List[str]:
        """Extract potential names using regex patterns"""
        names = []
        
        # Remove titles first
        clean_text = text
        for pattern in self.title_patterns:
            clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
        
        # Extract names
        for pattern in self.name_patterns:
            matches = re.findall(pattern, clean_text)
            names.extend(matches)
        
        # Filter out common words that might match name patterns
        common_words = {
            'Action', 'Item', 'Next', 'Step', 'Meeting', 'Team', 'Project',
            'Update', 'Review', 'Send', 'Call', 'Email', 'Follow', 'Complete'
        }
        
        filtered_names = [name for name in names if name not in common_words]
        
        return list(set(filtered_names))  # Remove duplicates
    
    def find_assignment_context(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find assignment context around entities"""
        assignments = []
        text_lower = text.lower()
        
        for entity in entities:
            entity_text = entity['text']
            entity_start = entity.get('start', 0)
            
            # Look for assignment phrases near the entity
            context_window = 50  # characters before and after
            start_pos = max(0, entity_start - context_window)
            end_pos = min(len(text), entity_start + len(entity_text) + context_window)
            context = text[start_pos:end_pos].lower()
            
            # Check for assignment indicators
            is_assigned = False
            assignment_type = 'mentioned'
            
            for phrase in self.assignee_indicators['assignment_phrases']:
                if phrase in context:
                    is_assigned = True
                    assignment_type = 'assigned'
                    break
            
            # Check for action verbs near the name
            action_verbs = ['will', 'should', 'needs to', 'has to', 'responsible']
            for verb in action_verbs:
                if verb in context:
                    is_assigned = True
                    assignment_type = 'action'
                    break
            
            assignments.append({
                'name': entity_text,
                'confidence': entity.get('confidence', 0.5),
                'is_assigned': is_assigned,
                'assignment_type': assignment_type,
                'context': context.strip()
            })
        
        return assignments
    
    def map_to_speakers(self, assignees: List[str], speakers: List[str]) -> List[str]:
        """Map extracted assignees to known speakers"""
        mapped_assignees = []
        
        for assignee in assignees:
            best_match = None
            best_score = 0
            
            # Try exact match first
            for speaker in speakers:
                if assignee.lower() == speaker.lower():
                    best_match = speaker
                    best_score = 1.0
                    break
            
            # Try partial match
            if best_match is None:
                for speaker in speakers:
                    # Check if assignee is part of speaker name or vice versa
                    if (assignee.lower() in speaker.lower() or 
                        speaker.lower() in assignee.lower()):
                        similarity = len(assignee) / max(len(speaker), len(assignee))
                        if similarity > best_score:
                            best_match = speaker
                            best_score = similarity
            
            # Use original assignee if no good match found
            if best_match and best_score > 0.5:
                mapped_assignees.append(best_match)
            else:
                mapped_assignees.append(assignee)
        
        return list(set(mapped_assignees))  # Remove duplicates

# Global extractor instance
assignee_extractor = AssigneeExtractor()

def extract_assignees(text: str, speakers: List[str] = None) -> List[str]:
    """Extract assignees from action item text"""
    if assignee_extractor.ner_pipeline is None and assignee_extractor.nlp is None:
        assignee_extractor.load_models()
    
    all_entities = []
    
    # Try BERT NER first
    bert_entities = assignee_extractor.extract_entities_with_bert(text)
    all_entities.extend(bert_entities)
    
    # Fallback to spaCy if BERT fails
    if not bert_entities:
        spacy_entities = assignee_extractor.extract_entities_with_spacy(text)
        all_entities.extend(spacy_entities)
    
    # Fallback to regex if no entities found
    if not all_entities:
        regex_names = assignee_extractor.extract_names_with_regex(text)
        for name in regex_names:
            all_entities.append({
                'text': name,
                'confidence': 0.6,
                'start': text.find(name),
                'end': text.find(name) + len(name)
            })
    
    # Find assignment context
    assignments = assignee_extractor.find_assignment_context(text, all_entities)
    
    # Extract assignee names
    assignees = [assignment['name'] for assignment in assignments 
                if assignment['is_assigned'] or assignment['confidence'] > 0.7]
    
    # Map to known speakers if provided
    if speakers:
        assignees = assignee_extractor.map_to_speakers(assignees, speakers)
    
    return assignees
