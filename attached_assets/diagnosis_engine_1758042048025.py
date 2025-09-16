import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re
import streamlit as st
from .symptom_severity import SymptomSeverityEngine
from .ml_diagnosis import MLDiagnosisModel

class DiagnosisEngine:
    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.symptom_disease_mapping = self._build_symptom_mapping()
        self.severity_engine = SymptomSeverityEngine()
        self.ml_model = MLDiagnosisModel(data_loader)
    
    def _build_symptom_mapping(self):
        """Build symptom to disease mapping from medicine data"""
        mapping = {}
        medicine_data = self.data_loader.get_medicine_data()
        
        if medicine_data is not None:
            for _, row in medicine_data.iterrows():
                uses = str(row.get('Uses', '')).lower()
                side_effects = str(row.get('Side_effects', '')).lower()
                
                # Extract potential conditions/symptoms from uses
                conditions = self._extract_conditions_from_text(uses)
                for condition in conditions:
                    if condition not in mapping:
                        mapping[condition] = []
                    mapping[condition].append({
                        'source': 'medicine_use',
                        'medicine': row.get('Medicine Name', ''),
                        'confidence': 0.7
                    })
        
        # Add disease-specific mappings from precaution data
        precaution_data = self.data_loader.get_precaution_data()
        if precaution_data is not None:
            for _, row in precaution_data.iterrows():
                disease = str(row.get('Disease', '')).lower().strip()
                if disease:
                    # Map disease name to itself
                    mapping[disease] = mapping.get(disease, [])
                    mapping[disease].append({
                        'source': 'direct_disease',
                        'disease': row.get('Disease', ''),
                        'confidence': 1.0
                    })
        
        return mapping
    
    def _extract_conditions_from_text(self, text):
        """Extract medical conditions from text"""
        if not text or text == 'nan':
            return []
        
        # Common medical condition patterns
        conditions = []
        
        # Look for "Treatment of" patterns
        treatment_matches = re.findall(r'treatment of ([^,\n]+)', text, re.IGNORECASE)
        conditions.extend([match.strip() for match in treatment_matches])
        
        # Look for specific condition keywords
        condition_keywords = [
            'cancer', 'infection', 'pain', 'fever', 'headache', 'nausea', 'vomiting',
            'diarrhea', 'constipation', 'cough', 'cold', 'flu', 'asthma', 'allergy',
            'diabetes', 'hypertension', 'depression', 'anxiety', 'arthritis'
        ]
        
        for keyword in condition_keywords:
            if keyword in text:
                conditions.append(keyword)
        
        return list(set(conditions))
    
    def diagnose(self, symptoms, symptom_severities=None):
        """Diagnose based on input symptoms with optional severity information"""
        if not symptoms:
            return []
        
        # Handle severity information
        symptom_scores = {}
        if symptom_severities:
            for symptom in symptoms:
                severity_info = symptom_severities.get(symptom, {})
                severity = severity_info.get('severity', 'moderate')
                duration = severity_info.get('duration_days', None)
                score = self.severity_engine.calculate_symptom_score(symptom, severity, duration)
                
                symptom_scores[symptom] = {
                    'severity': severity,
                    'duration_days': duration,
                    'score': score
                }
        else:
            # Default severity scoring for backward compatibility
            for symptom in symptoms:
                symptom_scores[symptom] = {
                    'severity': 'moderate',
                    'duration_days': None,
                    'score': 0.5
                }
        
        # Combine all symptoms into a single text if multiple
        symptom_text = ' '.join(symptoms).lower()
        
        # Find matching diseases
        disease_scores = {}
        
        # Method 1: Direct symptom matching
        for symptom_key, disease_info in self.symptom_disease_mapping.items():
            # Use fuzzy matching for symptom keywords
            for symptom in symptoms:
                similarity = fuzz.partial_ratio(symptom.lower(), symptom_key)
                if similarity > 60:  # Threshold for matching
                    for info in disease_info:
                        if info['source'] == 'direct_disease':
                            disease = info['disease']
                            score = (similarity / 100) * info['confidence']
                            disease_scores[disease] = disease_scores.get(disease, 0) + score
        
        # Method 2: Keyword-based matching
        keyword_disease_map = {
            'headache': ['Migraine', 'Hypertension', 'Common Cold'],
            'fever': ['Malaria', 'Dengue', 'Typhoid', 'Common Cold', 'Chicken pox'],
            'nausea': ['GERD', 'Gastroenteritis', 'Migraine', 'Hepatitis A'],
            'vomiting': ['Gastroenteritis', 'GERD', 'Migraine'],
            'diarrhea': ['Gastroenteritis', 'Peptic ulcer disease'],
            'cough': ['Common Cold', 'Bronchial Asthma', 'Pneumonia'],
            'pain': ['Arthritis', 'Peptic ulcer disease'],
            'rash': ['Allergy', 'Psoriasis', 'Chicken pox', 'Impetigo'],
            'breathing': ['Bronchial Asthma', 'Pneumonia', 'Heart attack'],
            'chest pain': ['Heart attack', 'GERD'],
            'joint pain': ['Arthritis', 'Osteoarthritis'],
            'abdominal pain': ['Peptic ulcer disease', 'Gastroenteritis'],
            'back pain': ['Osteoarthritis', 'Cervical spondylosis']
        }
        
        for keyword, diseases in keyword_disease_map.items():
            if any(keyword in symptom.lower() for symptom in symptoms):
                for disease in diseases:
                    disease_scores[disease] = disease_scores.get(disease, 0) + 0.8
        
        # Method 3: Side effects reverse mapping
        medicine_data = self.data_loader.get_medicine_data()
        if medicine_data is not None:
            for _, row in medicine_data.iterrows():
                side_effects = str(row.get('Side_effects', '')).lower()
                uses = str(row.get('Uses', '')).lower()
                
                # If symptoms match side effects, suggest the condition the medicine treats
                symptom_match_score = 0
                for symptom in symptoms:
                    if symptom.lower() in side_effects:
                        symptom_match_score += 0.3
                
                if symptom_match_score > 0:
                    # Extract diseases from uses
                    diseases_treated = self._extract_diseases_from_uses(uses)
                    for disease in diseases_treated:
                        disease_scores[disease] = disease_scores.get(disease, 0) + symptom_match_score
        
        # Get ML predictions
        try:
            ml_predictions = self.ml_model.predict_disease(symptoms, top_k=5)
        except Exception as e:
            print(f"ML model prediction failed: {e}")
            ml_predictions = []
        
        # Canonicalize disease names for consistent merging
        canonical_scores = {}
        display_names = {}  # Map canonical -> display name
        
        # Disease name synonyms and canonicalization
        disease_synonyms = {
            'gerd': 'gastroesophageal reflux disease',
            'copd': 'chronic obstructive pulmonary disease',
            'htn': 'hypertension',
            'dm': 'diabetes mellitus',
            'mi': 'myocardial infarction',
            'peptic ulcer diseae': 'peptic ulcer disease',  # Fix typo
            'osteoarthristis': 'osteoarthritis'  # Fix typo
        }
        
        def canonicalize_disease(disease_name):
            """Convert disease name to canonical lowercase form"""
            canonical = disease_name.lower().strip()
            return disease_synonyms.get(canonical, canonical)
        
        # Canonicalize pattern matching results
        for disease, score in disease_scores.items():
            canonical = canonicalize_disease(disease)
            # Normalize pattern scores to [0,1] range before combining
            normalized_score = min(score, 1.0)
            
            canonical_scores[canonical] = canonical_scores.get(canonical, 0) + normalized_score
            display_names[canonical] = disease  # Keep original display name
        
        # Add ML predictions with weight
        ml_weight = 0.6  # ML predictions get 60% weight
        pattern_weight = 0.4  # Pattern matching gets 40% weight
        
        for pred in ml_predictions:
            canonical = canonicalize_disease(pred['disease'])
            ml_confidence = pred['confidence']
            
            if canonical in canonical_scores:
                # Weighted combination of pattern matching and ML
                canonical_scores[canonical] = (pattern_weight * canonical_scores[canonical] + 
                                             ml_weight * ml_confidence)
            else:
                # New disease from ML model
                canonical_scores[canonical] = ml_weight * ml_confidence
                display_names[canonical] = pred['disease']
        
        # Sort diseases by canonical score
        sorted_diseases = sorted(canonical_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Format results with enhanced confidence scoring
        results = []
        for canonical_disease, score in sorted_diseases[:7]:  # Top 7 results to account for ML additions
            display_disease = display_names.get(canonical_disease, canonical_disease.title())
            precautions = self._get_disease_precautions(display_disease)
            
            # Determine prediction method
            ml_canonical_names = [canonicalize_disease(pred['disease']) for pred in ml_predictions]
            pattern_canonical_names = [canonicalize_disease(d) for d in disease_scores.keys()]
            
            if canonical_disease in ml_canonical_names and canonical_disease in pattern_canonical_names:
                method = 'hybrid'
            elif canonical_disease in ml_canonical_names:
                method = 'machine_learning'
            else:
                method = 'pattern_matching'
            
            # Calculate enhanced confidence using severity information
            enhanced_confidence, explanation = self.severity_engine.calculate_enhanced_confidence(
                min(score, 1.0), symptom_scores, display_disease
            )
            
            results.append({
                'disease': display_disease,
                'confidence': enhanced_confidence,
                'base_confidence': min(score, 1.0),
                'explanation': explanation,
                'method': method,
                'precautions': precautions,
                'symptom_analysis': self.severity_engine.analyze_symptom_pattern(symptom_scores)
            })
        
        # Keep only top 5 for final results
        results = results[:5]
        
        # If no matches found, provide generic results
        if not results:
            results = self._get_generic_diagnosis(symptoms)
        
        return results
    
    def _extract_diseases_from_uses(self, uses_text):
        """Extract disease names from medicine uses text"""
        if not uses_text or uses_text == 'nan':
            return []
        
        diseases = []
        
        # Pattern matching for common disease formats
        patterns = [
            r'treatment of ([^,\n]+)',
            r'([a-zA-Z\s]+) treatment',
            r'prevention of ([^,\n]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, uses_text, re.IGNORECASE)
            diseases.extend([match.strip() for match in matches])
        
        # Clean and filter diseases
        cleaned_diseases = []
        for disease in diseases:
            if len(disease) > 3 and len(disease) < 50:  # Filter reasonable length
                cleaned_diseases.append(disease.title())
        
        return list(set(cleaned_diseases))
    
    def _get_disease_precautions(self, disease):
        """Get precautions for a specific disease"""
        precaution_data = self.data_loader.get_precaution_data()
        if precaution_data is not None:
            # Try exact match first
            exact_match = precaution_data[precaution_data['Disease'].str.lower() == disease.lower()]
            if not exact_match.empty:
                row = exact_match.iloc[0]
                precautions = []
                for col in ['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']:
                    if col in row and pd.notna(row[col]) and str(row[col]).strip():
                        precautions.append(str(row[col]).strip())
                return precautions
            
            # Try fuzzy match
            disease_list = precaution_data['Disease'].tolist()
            best_match = process.extractOne(disease, disease_list)
            if best_match and best_match[1] > 80:  # 80% similarity threshold
                matched_disease = best_match[0]
                row = precaution_data[precaution_data['Disease'] == matched_disease].iloc[0]
                precautions = []
                for col in ['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']:
                    if col in row and pd.notna(row[col]) and str(row[col]).strip():
                        precautions.append(str(row[col]).strip())
                return precautions
        
        return []
    
    def _get_generic_diagnosis(self, symptoms):
        """Provide generic diagnosis when no specific match is found"""
        generic_results = []
        
        # Analyze symptoms for common patterns
        symptom_text = ' '.join(symptoms).lower()
        
        if any(word in symptom_text for word in ['fever', 'headache', 'body ache']):
            generic_results.append({
                'disease': 'Common Cold',
                'confidence': 0.6,
                'precautions': ['rest', 'drink plenty of fluids', 'consult doctor if symptoms persist']
            })
        
        if any(word in symptom_text for word in ['stomach', 'abdominal', 'nausea', 'vomiting']):
            generic_results.append({
                'disease': 'Gastroenteritis',
                'confidence': 0.5,
                'precautions': ['stay hydrated', 'eat light foods', 'rest', 'consult doctor']
            })
        
        if any(word in symptom_text for word in ['pain', 'ache']):
            generic_results.append({
                'disease': 'General Pain/Inflammation',
                'confidence': 0.4,
                'precautions': ['rest', 'apply ice/heat', 'consult doctor', 'avoid strenuous activity']
            })
        
        if not generic_results:
            generic_results.append({
                'disease': 'Unspecified Condition',
                'confidence': 0.3,
                'precautions': ['consult a healthcare provider', 'monitor symptoms', 'rest', 'stay hydrated']
            })
        
        return generic_results
