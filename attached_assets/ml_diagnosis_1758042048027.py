import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
from typing import List, Dict, Tuple, Optional
import re

class MLDiagnosisModel:
    """Machine Learning model for improved diagnosis prediction"""
    
    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=10
        )
        self.label_encoder = LabelEncoder()
        self.is_trained = False
        self.model_path = 'models/'
        
        # Create models directory if it doesn't exist
        os.makedirs(self.model_path, exist_ok=True)
    
    def prepare_training_data(self) -> Tuple[List[str], List[str]]:
        """Prepare training data from medical datasets"""
        symptoms_text = []
        diseases = []
        
        # Extract data from medicine dataset (uses field indicates what conditions it treats)
        medicine_data = self.data_loader.get_medicine_data()
        if medicine_data is not None:
            for _, row in medicine_data.iterrows():
                uses = str(row.get('Uses', ''))
                side_effects = str(row.get('Side_effects', ''))
                
                # Extract diseases from uses field
                extracted_diseases = self._extract_diseases_from_uses(uses)
                
                for disease in extracted_diseases:
                    if len(disease) > 3 and len(disease) < 50:  # Filter reasonable disease names
                        # Create symptom-like text from side effects (reverse mapping)
                        symptom_features = self._extract_symptom_features(side_effects)
                        if symptom_features:
                            symptoms_text.append(symptom_features)
                            diseases.append(disease)
        
        # Add data from drug side effects dataset
        side_effects_data = self.data_loader.get_side_effects_data()
        if side_effects_data is not None:
            for _, row in side_effects_data.iterrows():
                condition = str(row.get('medical_condition', ''))
                side_effects = str(row.get('side_effects', ''))
                
                if condition and condition != 'nan' and side_effects and side_effects != 'nan':
                    # Clean condition name
                    clean_condition = self._clean_condition_name(condition)
                    if clean_condition:
                        # Extract symptom features from side effects
                        symptom_features = self._extract_symptom_features(side_effects)
                        if symptom_features:
                            symptoms_text.append(symptom_features)
                            diseases.append(clean_condition)
        
        # Add synthetic symptom-disease mappings for common conditions
        synthetic_data = self._generate_synthetic_training_data()
        symptoms_text.extend(synthetic_data[0])
        diseases.extend(synthetic_data[1])
        
        return symptoms_text, diseases
    
    def _extract_diseases_from_uses(self, uses_text: str) -> List[str]:
        """Extract disease names from medicine uses text"""
        if not uses_text or uses_text == 'nan':
            return []
        
        diseases = []
        
        # Pattern matching for common disease formats
        patterns = [
            r'treatment of ([^,\n.]+)',
            r'treating ([^,\n.]+)',
            r'prevention of ([^,\n.]+)',
            r'([a-zA-Z\s]+) treatment',
            r'([a-zA-Z\s]+) therapy'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, uses_text, re.IGNORECASE)
            for match in matches:
                clean_match = match.strip().lower()
                if len(clean_match) > 3 and len(clean_match) < 50:
                    diseases.append(clean_match)
        
        return list(set(diseases))
    
    def _extract_symptom_features(self, text: str) -> str:
        """Extract symptom-related features from text"""
        if not text or text == 'nan':
            return ""
        
        # Common symptom keywords
        symptom_keywords = [
            'pain', 'ache', 'fever', 'headache', 'nausea', 'vomiting', 'diarrhea',
            'cough', 'breathing', 'chest pain', 'abdominal pain', 'joint pain',
            'muscle pain', 'back pain', 'dizziness', 'fatigue', 'weakness',
            'rash', 'itching', 'swelling', 'bleeding', 'inflammation',
            'difficulty', 'shortness', 'burning', 'stinging', 'cramping'
        ]
        
        # Extract relevant symptom words
        extracted_symptoms = []
        text_lower = text.lower()
        
        for keyword in symptom_keywords:
            if keyword in text_lower:
                extracted_symptoms.append(keyword)
        
        # Also extract medical terms
        medical_patterns = [
            r'([a-z]+ache)',
            r'([a-z]+pain)',
            r'difficulty ([a-z]+ing)',
            r'loss of ([a-z]+)'
        ]
        
        for pattern in medical_patterns:
            matches = re.findall(pattern, text_lower)
            extracted_symptoms.extend(matches)
        
        return ' '.join(set(extracted_symptoms))
    
    def _clean_condition_name(self, condition: str) -> str:
        """Clean and standardize condition names"""
        if not condition or condition == 'nan':
            return ""
        
        # Remove common prefixes/suffixes
        clean_name = re.sub(r'^(treatment of|treating|prevention of)\s+', '', condition, flags=re.IGNORECASE)
        clean_name = re.sub(r'\s+(treatment|therapy|disease|disorder|condition)$', '', clean_name, flags=re.IGNORECASE)
        
        # Standardize common conditions
        standardizations = {
            'gerd': 'gastroesophageal reflux disease',
            'copd': 'chronic obstructive pulmonary disease',
            'htn': 'hypertension',
            'dm': 'diabetes mellitus',
            'mi': 'myocardial infarction'
        }
        
        clean_lower = clean_name.lower().strip()
        return standardizations.get(clean_lower, clean_lower)
    
    def _generate_synthetic_training_data(self) -> Tuple[List[str], List[str]]:
        """Generate synthetic training data for common symptom-disease patterns"""
        synthetic_symptoms = []
        synthetic_diseases = []
        
        # Common symptom-disease patterns
        patterns = {
            'common cold': [
                'fever headache cough', 'runny nose sore throat', 'congestion fatigue',
                'cough fever', 'headache fatigue', 'sore throat runny nose'
            ],
            'gastroenteritis': [
                'nausea vomiting diarrhea', 'abdominal pain diarrhea', 'vomiting stomach pain',
                'diarrhea cramping', 'nausea abdominal pain', 'stomach pain vomiting'
            ],
            'migraine': [
                'severe headache nausea', 'headache sensitivity light', 'throbbing headache',
                'headache vomiting', 'severe head pain', 'headache nausea dizziness'
            ],
            'hypertension': [
                'headache dizziness', 'chest pain shortness breath', 'dizziness fatigue',
                'headache fatigue', 'chest discomfort', 'dizziness headache'
            ],
            'bronchial asthma': [
                'shortness breath cough', 'difficulty breathing', 'wheezing cough',
                'chest tightness', 'breathing difficulty cough', 'shortness breath wheezing'
            ],
            'arthritis': [
                'joint pain stiffness', 'muscle pain joint swelling', 'joint ache',
                'joint pain morning stiffness', 'swollen joints pain', 'joint stiffness pain'
            ],
            'heart attack': [
                'severe chest pain', 'chest pain shortness breath', 'chest pressure',
                'chest pain arm pain', 'severe chest discomfort', 'chest pain nausea'
            ],
            'pneumonia': [
                'fever cough breathing difficulty', 'chest pain cough fever',
                'shortness breath fever', 'cough fever chest pain', 'breathing difficulty cough'
            ]
        }
        
        for disease, symptom_combinations in patterns.items():
            for symptoms in symptom_combinations:
                synthetic_symptoms.append(symptoms)
                synthetic_diseases.append(disease)
        
        return synthetic_symptoms, synthetic_diseases
    
    def train_model(self, save_model: bool = True) -> Dict[str, float]:
        """Train the ML diagnosis model"""
        print("Preparing training data...")
        symptoms_text, diseases = self.prepare_training_data()
        
        if len(symptoms_text) == 0:
            raise ValueError("No training data available")
        
        print(f"Training with {len(symptoms_text)} samples...")
        
        # Convert text to features
        X = self.vectorizer.fit_transform(symptoms_text)
        
        # Encode disease labels
        y = self.label_encoder.fit_transform(diseases)
        
        # Split data for evaluation
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train the model
        print("Training Random Forest classifier...")
        self.classifier.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model accuracy: {accuracy:.3f}")
        
        # Mark as trained
        self.is_trained = True
        
        # Save model if requested
        if save_model:
            self.save_model()
        
        return {
            'accuracy': accuracy,
            'training_samples': len(symptoms_text),
            'unique_diseases': len(set(diseases))
        }
    
    def predict_disease(self, symptoms: List[str], top_k: int = 5) -> List[Dict[str, any]]:
        """Predict diseases based on symptoms using ML model"""
        if not self.is_trained:
            if not self.load_model():
                # If model doesn't exist, train it
                print("Training new ML model...")
                self.train_model()
        
        # Combine symptoms into text
        symptom_text = ' '.join(symptoms).lower()
        
        # Enhance symptom text with related terms
        enhanced_text = self._enhance_symptom_text(symptom_text)
        
        # Transform to features
        X = self.vectorizer.transform([enhanced_text])
        
        # Get prediction probabilities
        probabilities = self.classifier.predict_proba(X)[0]
        
        # Get top predictions
        top_indices = np.argsort(probabilities)[-top_k:][::-1]
        
        predictions = []
        for idx in top_indices:
            disease = self.label_encoder.inverse_transform([idx])[0]
            confidence = probabilities[idx]
            
            # Only include predictions with reasonable confidence
            if confidence > 0.05:  # 5% minimum confidence
                predictions.append({
                    'disease': disease.title(),
                    'confidence': confidence,
                    'method': 'machine_learning'
                })
        
        return predictions
    
    def _enhance_symptom_text(self, symptom_text: str) -> str:
        """Enhance symptom text with related medical terms"""
        # Add related terms for better matching
        enhancements = {
            'headache': 'head pain cephalgia',
            'stomach pain': 'abdominal pain gastric pain',
            'chest pain': 'thoracic pain cardiac pain',
            'breathing': 'respiratory dyspnea',
            'fever': 'pyrexia temperature',
            'nausea': 'sick stomach queasy',
            'joint pain': 'arthralgia joint ache',
            'muscle pain': 'myalgia muscle ache'
        }
        
        enhanced_parts = [symptom_text]
        
        for key, enhancement in enhancements.items():
            if key in symptom_text:
                enhanced_parts.append(enhancement)
        
        return ' '.join(enhanced_parts)
    
    def save_model(self):
        """Save the trained model to disk"""
        if not self.is_trained:
            print("Model not trained yet, cannot save")
            return
        
        try:
            # Save vectorizer
            joblib.dump(self.vectorizer, os.path.join(self.model_path, 'vectorizer.pkl'))
            # Save classifier
            joblib.dump(self.classifier, os.path.join(self.model_path, 'classifier.pkl'))
            # Save label encoder
            joblib.dump(self.label_encoder, os.path.join(self.model_path, 'label_encoder.pkl'))
            
            print("Model saved successfully")
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def load_model(self) -> bool:
        """Load a pre-trained model from disk"""
        try:
            vectorizer_path = os.path.join(self.model_path, 'vectorizer.pkl')
            classifier_path = os.path.join(self.model_path, 'classifier.pkl')
            encoder_path = os.path.join(self.model_path, 'label_encoder.pkl')
            
            if not all(os.path.exists(p) for p in [vectorizer_path, classifier_path, encoder_path]):
                return False
            
            self.vectorizer = joblib.load(vectorizer_path)
            self.classifier = joblib.load(classifier_path)
            self.label_encoder = joblib.load(encoder_path)
            
            self.is_trained = True
            print("Model loaded successfully")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, any]:
        """Get information about the current model"""
        if not self.is_trained:
            return {'status': 'not_trained'}
        
        try:
            return {
                'status': 'trained',
                'n_features': self.vectorizer.vocabulary_.__len__() if hasattr(self.vectorizer, 'vocabulary_') else 0,
                'n_classes': len(self.label_encoder.classes_) if hasattr(self.label_encoder, 'classes_') else 0,
                'classes': self.label_encoder.classes_.tolist() if hasattr(self.label_encoder, 'classes_') else [],
                'model_type': 'RandomForestClassifier'
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}