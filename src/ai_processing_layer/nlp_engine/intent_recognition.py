"""
Intent Recognition Engine for KSSEM Virtual AI Assistant
Uses BERT/DistilBERT for understanding user queries and extracting intents
"""

import json
import numpy as np
import pickle
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import re

# NLP Libraries
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# ML Libraries
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import torch
from transformers import DistilBertTokenizer, DistilBertModel

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

@dataclass
class IntentResult:
    intent: str
    confidence: float
    entities: Dict[str, str]
    response_template: str
    context: List[str]

class KSSEMIntentRecognizer:
    """
    Intent Recognition Engine specifically designed for KSSEM campus queries
    Uses both traditional ML and transformer models for high accuracy
    """
    
    def __init__(self, intents_file: str = "/workspace/data/training_data/intents.json"):
        """Initialize the intent recognition engine"""
        self.intents_file = intents_file
        self.intents_data = None
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
        # BERT model for advanced understanding
        self.tokenizer = None
        self.bert_model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Training data
        self.patterns = []
        self.tags = []
        self.responses = {}
        self.contexts = {}
        
        # Load and prepare data
        self.load_intents()
        self.prepare_training_data()
        self.initialize_bert()
        
    def load_intents(self) -> None:
        """Load KSSEM-specific intents from JSON file"""
        try:
            with open(self.intents_file, 'r') as f:
                self.intents_data = json.load(f)
            print(f"✓ Loaded {len(self.intents_data['intents'])} intent categories")
        except FileNotFoundError:
            print(f"⚠ Warning: Intents file not found at {self.intents_file}")
            self.intents_data = self._create_default_intents()
    
    def _create_default_intents(self) -> Dict:
        """Create basic default intents if file is not available"""
        return {
            "intents": [
                {
                    "tag": "greeting",
                    "patterns": ["hello", "hi", "good morning"],
                    "responses": ["Hello! How can I help you with KSSEM information?"],
                    "context": ["greeting"]
                },
                {
                    "tag": "navigation",
                    "patterns": ["where is", "how to reach", "direction to"],
                    "responses": ["I'll help you navigate to your destination."],
                    "context": ["location_search"]
                }
            ]
        }
    
    def prepare_training_data(self) -> None:
        """Prepare training data from intents"""
        self.patterns = []
        self.tags = []
        self.responses = {}
        self.contexts = {}
        
        for intent in self.intents_data['intents']:
            tag = intent['tag']
            
            # Store responses and contexts
            self.responses[tag] = intent['responses']
            self.contexts[tag] = intent.get('context', [])
            
            # Prepare patterns for training
            for pattern in intent['patterns']:
                processed_pattern = self._preprocess_text(pattern)
                self.patterns.append(processed_pattern)
                self.tags.append(tag)
        
        # Train TF-IDF vectorizer
        if self.patterns:
            self.vectorizer.fit(self.patterns)
            print(f"✓ Prepared {len(self.patterns)} training patterns")
    
    def initialize_bert(self) -> None:
        """Initialize BERT model for advanced NLP understanding"""
        try:
            model_name = 'distilbert-base-uncased'
            self.tokenizer = DistilBertTokenizer.from_pretrained(model_name)
            self.bert_model = DistilBertModel.from_pretrained(model_name)
            self.bert_model.to(self.device)
            self.bert_model.eval()
            print("✓ BERT model initialized successfully")
        except Exception as e:
            print(f"⚠ Warning: Could not initialize BERT model: {e}")
            self.tokenizer = None
            self.bert_model = None
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better understanding"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters except spaces and common punctuation
        text = re.sub(r'[^a-zA-Z0-9\s\?\!\.]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and stem (optional for BERT, but useful for TF-IDF)
        processed_tokens = []
        for token in tokens:
            if token not in self.stop_words and len(token) > 1:
                processed_tokens.append(self.stemmer.stem(token))
        
        return ' '.join(processed_tokens)
    
    def extract_entities(self, text: str, intent: str) -> Dict[str, str]:
        """Extract entities from user input based on intent"""
        entities = {}
        text_lower = text.lower()
        
        # KSSEM-specific entity extraction
        if intent == "navigation":
            # Extract location entities
            locations = [
                "library", "cafeteria", "auditorium", "gymnasium", "medical center",
                "block a", "block b", "block c", "block d", "block e", "block f",
                "block g", "block h", "block i", "block j", "admin block",
                "computer science", "cse", "electronics", "ece", "mechanical", "civil",
                "mba", "placement cell", "research center", "principal office"
            ]
            
            for location in locations:
                if location in text_lower:
                    entities["location"] = location
                    break
            
            # Extract room numbers
            room_pattern = r'([a-z]\s*[-]?\s*\d{3})|(\d{3})'
            room_match = re.search(room_pattern, text_lower)
            if room_match:
                entities["room"] = room_match.group().replace(' ', '').replace('-', '')
        
        elif intent == "department_info":
            departments = ["cse", "ece", "mechanical", "civil", "mba", 
                          "computer science", "electronics", "communication"]
            for dept in departments:
                if dept in text_lower:
                    entities["department"] = dept
                    break
        
        elif intent == "faculty_info":
            # Extract faculty names or designations
            faculty_names = ["rajesh kumar", "priya sharma", "suresh reddy", 
                           "lakshmi devi", "vikram singh", "principal", "head"]
            for name in faculty_names:
                if name in text_lower:
                    entities["faculty"] = name
                    break
        
        elif intent == "facility_info":
            facilities = ["library", "cafeteria", "hostel", "wifi", "parking",
                         "sports", "medical", "auditorium", "gymnasium"]
            for facility in facilities:
                if facility in text_lower:
                    entities["facility"] = facility
                    break
        
        return entities
    
    def get_bert_similarity(self, query: str, patterns: List[str]) -> List[float]:
        """Calculate semantic similarity using BERT embeddings"""
        if not self.bert_model or not self.tokenizer:
            return [0.0] * len(patterns)
        
        try:
            # Encode query
            query_tokens = self.tokenizer(query, return_tensors='pt', 
                                        padding=True, truncation=True, max_length=128)
            query_tokens = {k: v.to(self.device) for k, v in query_tokens.items()}
            
            with torch.no_grad():
                query_embedding = self.bert_model(**query_tokens).last_hidden_state.mean(dim=1)
            
            similarities = []
            
            for pattern in patterns:
                # Encode pattern
                pattern_tokens = self.tokenizer(pattern, return_tensors='pt',
                                              padding=True, truncation=True, max_length=128)
                pattern_tokens = {k: v.to(self.device) for k, v in pattern_tokens.items()}
                
                with torch.no_grad():
                    pattern_embedding = self.bert_model(**pattern_tokens).last_hidden_state.mean(dim=1)
                
                # Calculate cosine similarity
                similarity = torch.cosine_similarity(query_embedding, pattern_embedding).item()
                similarities.append(similarity)
            
            return similarities
        
        except Exception as e:
            print(f"⚠ BERT similarity calculation failed: {e}")
            return [0.0] * len(patterns)
    
    def recognize_intent(self, query: str, use_bert: bool = True) -> IntentResult:
        """
        Recognize intent from user query using hybrid approach
        Combines TF-IDF and BERT for better accuracy
        """
        if not query.strip():
            return IntentResult("unknown", 0.0, {}, "I didn't understand. Could you please rephrase?", [])
        
        processed_query = self._preprocess_text(query)
        
        # Method 1: TF-IDF similarity
        tfidf_scores = self._calculate_tfidf_similarity(processed_query)
        
        # Method 2: BERT similarity (if available)
        bert_scores = []
        if use_bert and self.bert_model:
            original_patterns = [intent['patterns'][0] for intent in self.intents_data['intents']
                               for _ in intent['patterns']]
            bert_scores = self.get_bert_similarity(query, self.patterns)
        
        # Combine scores
        final_scores = []
        for i, (tfidf_score, bert_score) in enumerate(zip(tfidf_scores, bert_scores or [0] * len(tfidf_scores))):
            # Weighted combination: 60% BERT, 40% TF-IDF
            if bert_scores:
                combined_score = 0.6 * bert_score + 0.4 * tfidf_score
            else:
                combined_score = tfidf_score
            final_scores.append(combined_score)
        
        # Find best match
        if not final_scores:
            return IntentResult("unknown", 0.0, {}, "I'm not sure how to help with that.", [])
        
        best_match_idx = np.argmax(final_scores)
        confidence = final_scores[best_match_idx]
        predicted_intent = self.tags[best_match_idx]
        
        # Set confidence threshold
        if confidence < 0.3:
            predicted_intent = "unknown"
            confidence = 0.0
        
        # Extract entities
        entities = self.extract_entities(query, predicted_intent)
        
        # Get response template
        response_template = self._get_response_template(predicted_intent)
        
        # Get context
        context = self.contexts.get(predicted_intent, [])
        
        return IntentResult(
            intent=predicted_intent,
            confidence=confidence,
            entities=entities,
            response_template=response_template,
            context=context
        )
    
    def _calculate_tfidf_similarity(self, query: str) -> List[float]:
        """Calculate TF-IDF similarity scores"""
        if not self.patterns:
            return []
        
        try:
            # Transform query and patterns
            query_vector = self.vectorizer.transform([query])
            pattern_vectors = self.vectorizer.transform(self.patterns)
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_vector, pattern_vectors).flatten()
            return similarities.tolist()
        
        except Exception as e:
            print(f"⚠ TF-IDF similarity calculation failed: {e}")
            return [0.0] * len(self.patterns)
    
    def _get_response_template(self, intent: str) -> str:
        """Get appropriate response template for intent"""
        if intent in self.responses:
            return random.choice(self.responses[intent])
        else:
            return "I'm here to help! Could you please be more specific?"
    
    def add_training_data(self, patterns: List[str], intent: str, responses: List[str]) -> None:
        """Add new training data dynamically"""
        # Add to intents data
        existing_intent = None
        for intent_obj in self.intents_data['intents']:
            if intent_obj['tag'] == intent:
                existing_intent = intent_obj
                break
        
        if existing_intent:
            existing_intent['patterns'].extend(patterns)
            existing_intent['responses'].extend(responses)
        else:
            new_intent = {
                "tag": intent,
                "patterns": patterns,
                "responses": responses,
                "context": [intent]
            }
            self.intents_data['intents'].append(new_intent)
        
        # Re-prepare training data
        self.prepare_training_data()
        print(f"✓ Added {len(patterns)} new patterns for intent '{intent}'")
    
    def get_intent_statistics(self) -> Dict:
        """Get statistics about the intent recognition system"""
        if not self.intents_data:
            return {}
        
        intent_counts = {}
        total_patterns = 0
        
        for intent in self.intents_data['intents']:
            tag = intent['tag']
            pattern_count = len(intent['patterns'])
            intent_counts[tag] = pattern_count
            total_patterns += pattern_count
        
        return {
            "total_intents": len(self.intents_data['intents']),
            "total_patterns": total_patterns,
            "intent_distribution": intent_counts,
            "bert_available": self.bert_model is not None,
            "vectorizer_vocabulary_size": len(self.vectorizer.vocabulary_) if hasattr(self.vectorizer, 'vocabulary_') else 0
        }
    
    def test_queries(self, test_queries: List[str]) -> None:
        """Test the intent recognition system with sample queries"""
        print("\n=== Testing KSSEM Intent Recognition ===")
        
        for query in test_queries:
            result = self.recognize_intent(query)
            print(f"\nQuery: '{query}'")
            print(f"Intent: {result.intent} (confidence: {result.confidence:.3f})")
            print(f"Entities: {result.entities}")
            print(f"Response: {result.response_template}")

# Example usage and testing
if __name__ == "__main__":
    # Initialize intent recognizer
    intent_recognizer = KSSEMIntentRecognizer()
    
    # Test queries
    test_queries = [
        "Hello, I need help",
        "Where is the library?",
        "How do I get to the Computer Science department?",
        "What are the library timings?",
        "Tell me about Dr. Rajesh Kumar",
        "What is the fee structure for CSE?",
        "Which companies visit for placements?",
        "How to reach Block A Room 201?",
        "Is there Wi-Fi on campus?",
        "I need medical help",
        "Thank you, goodbye"
    ]
    
    # Run tests
    intent_recognizer.test_queries(test_queries)
    
    # Show statistics
    stats = intent_recognizer.get_intent_statistics()
    print(f"\n=== System Statistics ===")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Interactive testing
    print("\n=== Interactive Testing ===")
    print("Type 'quit' to exit")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            break
        
        result = intent_recognizer.recognize_intent(user_input)
        print(f"Assistant: {result.response_template}")
        if result.entities:
            print(f"Detected entities: {result.entities}")
        print(f"Intent: {result.intent} (confidence: {result.confidence:.3f})")