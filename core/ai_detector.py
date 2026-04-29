import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os
from config import MODEL_DIR, AI_CONFIDENCE_THRESHOLD

class AIDetector:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.model_path = os.path.join(MODEL_DIR, "vuln_detector.pkl")
        self.vectorizer_path = os.path.join(MODEL_DIR, "vectorizer.pkl")
        self.load_or_train_model()
    
    def extract_features(self, response_text):
        """Extract features from response"""
        features = {
            'length': min(len(response_text), 10000),
            'sql_errors': sum(1 for word in ['mysql', 'sql', 'syntax', 'oracle', 'postgresql', 
                                             'mariadb', 'mongodb', 'query'] 
                             if word in response_text.lower()),
            'xss_indicators': sum(1 for word in ['script', 'alert', 'onerror', 'javascript', 
                                                 'onload', 'iframe', 'svg'] 
                                 if word in response_text.lower()),
            'special_chars': response_text.count("'") + response_text.count('"') + 
                            response_text.count(';') + response_text.count('--') +
                            response_text.count('<') + response_text.count('>'),
            'error_messages': sum(1 for word in ['error', 'warning', 'fatal', 'exception',
                                                 'stack trace', 'debug'] 
                                 if word in response_text.lower()),
        }
        return features
    
    def load_or_train_model(self):
        """Load pre-trained model or train a simple one"""
        if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
            try:
                self.model = joblib.load(self.model_path)
                self.vectorizer = joblib.load(self.vectorizer_path)
                print("[AI] Loaded pre-trained model successfully")
                return
            except Exception as e:
                print(f"[AI] Could not load model: {e}")
        
        # Train a simple model
        print("[AI] Training new model...")
        self.train_simple_model()
    
    def train_simple_model(self):
        """Train a simple classification model"""
        # Extended training data
        X_train = [
            # Vulnerable patterns (1)
            "error in your SQL syntax near",
            "mysql_fetch_array() expects parameter",
            "You have an error in your SQL syntax",
            "<script>alert('XSS')</script>",
            "onerror=alert(1) javascript:",
            "Warning: include(../../../etc/passwd)",
            "Division by zero in /var/www/",
            "unexpected T_STRING in",
            "Syntax error in SQL statement",
            "Cross-site scripting vulnerability",
            
            # Normal patterns (0)
            "Welcome to our website",
            "Page not found - 404",
            "Invalid request",
            "Please login to continue",
            "Your session has expired",
            "Thank you for your submission",
            "Operation completed successfully",
            "Internal server error",
            "Access denied",
            "Bad request"
        ]
        
        y_train = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # Vulnerable
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0]   # Normal
        
        self.vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2))
        X_vectorized = self.vectorizer.fit_transform(X_train)
        
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_vectorized, y_train)
        
        # Save the model
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.vectorizer, self.vectorizer_path)
        
        print("[AI] Model trained and saved successfully")
    
    def predict(self, response_text, confidence_threshold=None):
        """Predict if response indicates a vulnerability"""
        if confidence_threshold is None:
            confidence_threshold = AI_CONFIDENCE_THRESHOLD
            
        if not self.model or not self.vectorizer:
            return False, 0.0
        
        try:
            # Truncate long responses
            if len(response_text) > 5000:
                response_text = response_text[:5000]
            
            X_test = self.vectorizer.transform([response_text])
            proba = self.model.predict_proba(X_test)[0]
            confidence = max(proba)
            prediction = self.model.predict(X_test)[0]
            
            return bool(prediction), float(confidence)
        except Exception as e:
            print(f"[AI] Prediction error: {e}")
            return False, 0.0