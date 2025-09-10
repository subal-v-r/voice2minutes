from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import numpy as np
import re
import pickle
import os
from typing import List, Dict, Any
import spacy

class ActionItemDetector:
    def __init__(self):
        """Initialize action item detector"""
        self.embedding_model = None
        self.classifier = None
        self.nlp = None
        self.model_path = "models/action_classifier.pkl"
        
        # Action indicators - words/phrases that suggest action items
        self.action_indicators = {
            'imperative_verbs': [
                'schedule', 'send', 'create', 'update', 'review', 'complete', 'finish',
                'prepare', 'organize', 'contact', 'call', 'email', 'follow up',
                'implement', 'develop', 'design', 'test', 'deploy', 'launch',
                'analyze', 'research', 'investigate', 'document', 'write',
                'submit', 'approve', 'sign', 'deliver', 'present', 'share'
            ],
            'modal_phrases': [
                'need to', 'should', 'must', 'have to', 'will', 'going to',
                'plan to', 'intend to', 'responsible for', 'assigned to',
                'action item', 'todo', 'to do', 'next step', 'follow up'
            ],
            'time_indicators': [
                'by', 'before', 'after', 'until', 'deadline', 'due',
                'next week', 'next month', 'tomorrow', 'today', 'asap',
                'end of week', 'end of month', 'Q1', 'Q2', 'Q3', 'Q4'
            ]
        }
    
    def load_models(self):
        """Load embedding model and classifier"""
        if self.embedding_model is None:
            print("Loading sentence transformer model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        if self.nlp is None:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("Warning: spaCy model not found. Some features may be limited.")
                self.nlp = None
        
        # Load or train classifier
        if os.path.exists(self.model_path):
            self.load_classifier()
        else:
            self.train_classifier()
    
    def create_training_data(self) -> tuple:
        """Create training data for action item classification"""
        # Positive examples (action items)
        positive_examples = [
            "John will send the report by Friday",
            "We need to schedule a follow-up meeting",
            "Sarah should review the proposal",
            "Please update the documentation",
            "Action item: Contact the vendor",
            "I'll prepare the presentation for next week",
            "We must complete this by the deadline",
            "Someone needs to call the client",
            "Let's organize a team meeting",
            "The team will implement the new feature",
            "We should test this thoroughly",
            "Please send me the updated files",
            "I need to finish the analysis",
            "We have to approve the budget",
            "Action: Review and sign the contract",
            "Next step is to deploy to production",
            "We need to follow up on this issue",
            "Please create a ticket for this bug",
            "I will document the process",
            "We should schedule training sessions",
            "The manager needs to approve this",
            "Please prepare the quarterly report",
            "We must investigate this problem",
            "Action item: Update the website",
            "I'll contact the stakeholders"
        ]
        
        # Negative examples (not action items)
        negative_examples = [
            "The weather is nice today",
            "We discussed the quarterly results",
            "The meeting was productive",
            "Everyone agreed on the proposal",
            "The project is going well",
            "We talked about the new policy",
            "The team shared their thoughts",
            "It was mentioned in the presentation",
            "The data shows interesting trends",
            "We reviewed the current status",
            "The client was satisfied",
            "The budget looks reasonable",
            "We had a good discussion",
            "The timeline seems realistic",
            "Everyone was present at the meeting",
            "The presentation was informative",
            "We covered all the topics",
            "The feedback was positive",
            "The results were as expected",
            "We went through the agenda",
            "The team is working hard",
            "The project started last month",
            "We have been making progress",
            "The system is working fine",
            "The meeting ended on time"
        ]
        
        # Combine and create labels
        texts = positive_examples + negative_examples
        labels = [1] * len(positive_examples) + [0] * len(negative_examples)
        
        return texts, labels
    
    def extract_features(self, text: str) -> Dict[str, float]:
        """Extract linguistic features for action detection"""
        features = {}
        text_lower = text.lower()
        
        # Count action indicators
        features['imperative_count'] = sum(1 for verb in self.action_indicators['imperative_verbs'] 
                                         if verb in text_lower)
        features['modal_count'] = sum(1 for phrase in self.action_indicators['modal_phrases'] 
                                    if phrase in text_lower)
        features['time_count'] = sum(1 for indicator in self.action_indicators['time_indicators'] 
                                   if indicator in text_lower)
        
        # Sentence structure features
        features['starts_with_verb'] = 1 if re.match(r'^[A-Z][a-z]*\s+', text) else 0
        features['has_modal'] = 1 if re.search(r'\b(will|should|must|need|have to)\b', text_lower) else 0
        features['has_person'] = 1 if re.search(r'\b(I|we|you|he|she|they|someone|team)\b', text_lower) else 0
        
        # Length and complexity
        features['word_count'] = len(text.split())
        features['has_deadline'] = 1 if re.search(r'\b(by|before|until|deadline|due)\b', text_lower) else 0
        
        return features
    
    def train_classifier(self):
        """Train the action item classifier"""
        print("Training action item classifier...")
        
        # Get training data
        texts, labels = self.create_training_data()
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts)
        
        # Extract additional features
        feature_vectors = []
        for text in texts:
            features = self.extract_features(text)
            feature_vector = list(features.values())
            feature_vectors.append(feature_vector)
        
        # Combine embeddings with features
        combined_features = np.hstack([embeddings, np.array(feature_vectors)])
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            combined_features, labels, test_size=0.2, random_state=42
        )
        
        # Train classifier
        self.classifier = LogisticRegression(random_state=42)
        self.classifier.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.classifier.predict(X_test)
        print("Classifier performance:")
        print(classification_report(y_test, y_pred))
        
        # Save model
        os.makedirs("models", exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.classifier, f)
    
    def load_classifier(self):
        """Load pre-trained classifier"""
        with open(self.model_path, 'rb') as f:
            self.classifier = pickle.load(f)
    
    def predict_action_item(self, text: str) -> Dict[str, Any]:
        """Predict if text is an action item"""
        if self.embedding_model is None or self.classifier is None:
            self.load_models()
        
        # Generate embedding
        embedding = self.embedding_model.encode([text])
        
        # Extract features
        features = self.extract_features(text)
        feature_vector = np.array([list(features.values())])
        
        # Combine features
        combined_features = np.hstack([embedding, feature_vector])
        
        # Predict
        probability = self.classifier.predict_proba(combined_features)[0][1]
        is_action = probability > 0.5
        
        return {
            'is_action': is_action,
            'confidence': probability,
            'features': features
        }
    
    def extract_action_items_from_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract action items from transcript segments"""
        action_items = []
        
        for segment in segments:
            text = segment.get('text', '')
            sentences = segment.get('sentences', [text])
            
            for sentence in sentences:
                if len(sentence.strip()) < 10:  # Skip very short sentences
                    continue
                
                prediction = self.predict_action_item(sentence)
                
                if prediction['is_action'] and prediction['confidence'] > 0.6:
                    action_item = {
                        'text': sentence.strip(),
                        'speaker': segment.get('speaker', 'Unknown'),
                        'start_time': segment.get('start', 0),
                        'end_time': segment.get('end', 0),
                        'confidence': prediction['confidence'],
                        'features': prediction['features']
                    }
                    action_items.append(action_item)
        
        return action_items

# Global detector instance
action_detector = ActionItemDetector()

def detect_action_items(transcript_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Detect action items from transcript data"""
    segments = transcript_data.get('segments', [])
    
    if not segments:
        return []
    
    print("Detecting action items...")
    action_items = action_detector.extract_action_items_from_segments(segments)
    
    # Sort by confidence
    action_items.sort(key=lambda x: x['confidence'], reverse=True)
    
    return action_items
