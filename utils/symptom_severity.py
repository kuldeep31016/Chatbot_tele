import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

class SymptomSeverityEngine:
    """Engine for processing symptom severity and calculating enhanced confidence scores"""
    
    def __init__(self):
        self.severity_weights = {
            'mild': 0.3,
            'moderate': 0.6,
            'severe': 0.9,
            'critical': 1.0
        }
        
        # Symptom importance weights for different conditions
        self.symptom_importance = {
            'fever': {
                'malaria': 0.9, 'dengue': 0.9, 'typhoid': 0.8, 'common cold': 0.6, 'chicken pox': 0.7
            },
            'headache': {
                'migraine': 0.9, 'hypertension': 0.7, 'common cold': 0.4, 'dengue': 0.6
            },
            'chest pain': {
                'heart attack': 0.95, 'gerd': 0.7, 'bronchial asthma': 0.6
            },
            'abdominal pain': {
                'peptic ulcer disease': 0.9, 'gastroenteritis': 0.8, 'gerd': 0.6
            },
            'breathing difficulty': {
                'bronchial asthma': 0.95, 'pneumonia': 0.9, 'heart attack': 0.8
            },
            'nausea': {
                'gastroenteritis': 0.8, 'migraine': 0.7, 'gerd': 0.6, 'hepatitis a': 0.7
            },
            'vomiting': {
                'gastroenteritis': 0.9, 'migraine': 0.8, 'gerd': 0.7
            },
            'diarrhea': {
                'gastroenteritis': 0.9, 'peptic ulcer disease': 0.6
            },
            'cough': {
                'common cold': 0.8, 'bronchial asthma': 0.8, 'pneumonia': 0.8
            },
            'joint pain': {
                'arthritis': 0.9, 'osteoarthritis': 0.9
            },
            'rash': {
                'allergy': 0.9, 'psoriasis': 0.8, 'chicken pox': 0.9, 'impetigo': 0.8
            }
        }
    
    def normalize_symptom_name(self, symptom: str) -> str:
        """Normalize symptom names for consistent matching"""
        symptom_lower = symptom.lower().strip()
        
        # Mapping of user input variations to standardized symptom names
        symptom_map = {
            'head ache': 'headache',
            'stomach pain': 'abdominal pain',
            'belly pain': 'abdominal pain',
            'stomach ache': 'abdominal pain',
            'shortness of breath': 'breathing difficulty',
            'difficulty breathing': 'breathing difficulty',
            'breathlessness': 'breathing difficulty',
            'skin rash': 'rash',
            'joint ache': 'joint pain',
            'muscle pain': 'joint pain',
            'sore throat': 'throat pain',
            'runny nose': 'nasal congestion',
            'stuffy nose': 'nasal congestion'
        }
        
        return symptom_map.get(symptom_lower, symptom_lower)
    
    def calculate_symptom_score(self, symptom: str, severity: str, duration_days: Optional[int] = None) -> float:
        """Calculate weighted score for a single symptom"""
        base_score = self.severity_weights.get(severity.lower(), 0.5)
        
        # Duration factor (symptoms lasting longer are more significant)
        duration_factor = 1.0
        if duration_days:
            if duration_days >= 7:
                duration_factor = 1.2
            elif duration_days >= 3:
                duration_factor = 1.1
            elif duration_days <= 1:
                duration_factor = 0.9
        
        return base_score * duration_factor
    
    def calculate_enhanced_confidence(self, 
                                    base_confidence: float, 
                                    symptom_scores: Dict[str, Dict[str, any]], 
                                    disease: str) -> Tuple[float, str]:
        """
        Calculate enhanced confidence score based on symptom severity
        
        Args:
            base_confidence: Original confidence from pattern matching
            symptom_scores: Dict with symptom info including severity scores
            disease: Disease name being evaluated
            
        Returns:
            Tuple of (enhanced_confidence, explanation)
        """
        normalized_disease = disease.lower()
        symptom_boost = 0.0
        important_symptoms_present = 0
        total_symptom_weight = 0.0
        
        explanation_parts = []
        
        for symptom, info in symptom_scores.items():
            normalized_symptom = self.normalize_symptom_name(symptom)
            symptom_score = info.get('score', 0.5)
            
            # Check if this symptom is important for this disease
            if normalized_symptom in self.symptom_importance:
                normalized_disease = disease.lower()
                disease_relevance = self.symptom_importance[normalized_symptom].get(normalized_disease, 0.0)
                
                if disease_relevance > 0:
                    # Calculate weighted contribution
                    weighted_contribution = symptom_score * disease_relevance
                    symptom_boost += weighted_contribution
                    total_symptom_weight += disease_relevance
                    
                    if disease_relevance > 0.7:  # High importance symptom
                        important_symptoms_present += 1
                        severity_level = info.get('severity', 'moderate')
                        explanation_parts.append(f"{symptom} ({severity_level})")
        
        # Normalize the boost - only boost if we have relevant symptom mappings
        if total_symptom_weight > 0 and symptom_boost > 0:
            # Cap boost at 20% of base confidence or 0.2, whichever is smaller
            max_boost = min(base_confidence * 0.2, 0.2)
            normalized_boost = min((symptom_boost / total_symptom_weight) * 0.3, max_boost)
        else:
            normalized_boost = 0.0  # No boost if no relevant symptom mappings
        
        # Calculate final enhanced confidence
        enhanced_confidence = min(base_confidence + normalized_boost, 1.0)
        
        # Generate explanation
        if important_symptoms_present > 0:
            explanation = f"Enhanced by {important_symptoms_present} key symptom(s): {', '.join(explanation_parts[:3])}"
        else:
            explanation = "Based on symptom pattern matching"
        
        return enhanced_confidence, explanation
    
    def get_severity_recommendations(self, symptom: str, severity: str) -> List[str]:
        """Get specific recommendations based on symptom severity"""
        recommendations = []
        
        if severity.lower() == 'critical':
            recommendations.append("🚨 URGENT: Seek immediate emergency medical care")
            recommendations.append("Call emergency services or go to the nearest emergency room")
            
        elif severity.lower() == 'severe':
            recommendations.append("⚠️ Seek medical attention within 24 hours")
            recommendations.append("Contact your healthcare provider immediately")
            
        elif severity.lower() == 'moderate':
            recommendations.append("📞 Consider consulting a healthcare provider within 2-3 days")
            recommendations.append("Monitor symptoms and seek care if they worsen")
            
        else:  # mild
            recommendations.append("💡 Monitor symptoms and consider home remedies")
            recommendations.append("Consult healthcare provider if symptoms persist > 1 week")
        
        # Add symptom-specific recommendations
        symptom_specific = {
            'chest pain': {
                'critical': ["Call emergency services immediately - possible heart attack"],
                'severe': ["Urgent cardiology consultation required"]
            },
            'breathing difficulty': {
                'critical': ["Emergency treatment required - possible respiratory failure"],
                'severe': ["Immediate pulmonary assessment needed"]
            },
            'fever': {
                'critical': ["High fever >104°F requires emergency care"],
                'severe': ["Persistent fever >101°F needs medical evaluation"]
            }
        }
        
        normalized_symptom = self.normalize_symptom_name(symptom)
        if normalized_symptom in symptom_specific:
            specific_recs = symptom_specific[normalized_symptom].get(severity.lower(), [])
            recommendations.extend(specific_recs)
        
        return recommendations
    
    def analyze_symptom_pattern(self, symptom_scores: Dict[str, Dict[str, any]]) -> Dict[str, any]:
        """Analyze the overall symptom pattern for risk assessment"""
        
        total_severity_score = sum(info.get('score', 0.5) for info in symptom_scores.values())
        avg_severity = total_severity_score / len(symptom_scores) if symptom_scores else 0
        
        critical_symptoms = sum(1 for info in symptom_scores.values() 
                              if info.get('severity', '').lower() == 'critical')
        
        severe_symptoms = sum(1 for info in symptom_scores.values() 
                            if info.get('severity', '').lower() == 'severe')
        
        # Determine risk level
        risk_level = 'low'
        if critical_symptoms > 0 or avg_severity > 0.8:
            risk_level = 'critical'
        elif severe_symptoms > 1 or avg_severity > 0.7:
            risk_level = 'high'
        elif severe_symptoms > 0 or avg_severity > 0.5:
            risk_level = 'moderate'
        
        return {
            'risk_level': risk_level,
            'total_severity_score': total_severity_score,
            'average_severity': avg_severity,
            'critical_symptoms_count': critical_symptoms,
            'severe_symptoms_count': severe_symptoms,
            'symptom_count': len(symptom_scores)
        }
