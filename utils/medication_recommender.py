import pandas as pd
from fuzzywuzzy import fuzz, process
import re

class MedicationRecommender:
    def __init__(self, data_loader):
        self.data_loader = data_loader
    
    def recommend_medications(self, disease, age, gender):
        """Recommend medications based on diagnosed disease"""
        medicine_data = self.data_loader.get_medicine_data()
        if medicine_data is None:
            return []
        
        # Find medications that treat the diagnosed condition
        relevant_medications = []
        
        # Method 1: Direct matching in uses field
        for _, row in medicine_data.iterrows():
            uses = str(row.get('Uses', '')).lower()
            medicine_name = row.get('Medicine Name', '')
            
            # Check if disease name appears in uses
            if disease.lower() in uses:
                score = 1.0
            else:
                # Use fuzzy matching for partial matches
                score = fuzz.partial_ratio(disease.lower(), uses) / 100.0
            
            if score > 0.4:  # Threshold for relevance
                medication_info = {
                    'name': medicine_name,
                    'composition': row.get('Composition', 'N/A'),
                    'uses': row.get('Uses', 'N/A'),
                    'side_effects': row.get('Side_effects', 'N/A'),
                    'manufacturer': row.get('Manufacturer', 'N/A'),
                    'excellent_review': row.get('Excellent Review %', 0),
                    'average_review': row.get('Average Review %', 0),
                    'poor_review': row.get('Poor Review %', 0),
                    'relevance_score': score
                }
                relevant_medications.append(medication_info)
        
        # Method 2: Keyword-based matching for common conditions
        disease_keywords = self._get_disease_keywords(disease)
        
        for keyword in disease_keywords:
            for _, row in medicine_data.iterrows():
                uses = str(row.get('Uses', '')).lower()
                medicine_name = row.get('Medicine Name', '')
                
                if keyword.lower() in uses and not any(med['name'] == medicine_name for med in relevant_medications):
                    medication_info = {
                        'name': medicine_name,
                        'composition': row.get('Composition', 'N/A'),
                        'uses': row.get('Uses', 'N/A'),
                        'side_effects': row.get('Side_effects', 'N/A'),
                        'manufacturer': row.get('Manufacturer', 'N/A'),
                        'excellent_review': row.get('Excellent Review %', 0),
                        'average_review': row.get('Average Review %', 0),
                        'poor_review': row.get('Poor Review %', 0),
                        'relevance_score': 0.7
                    }
                    relevant_medications.append(medication_info)
        
        # Sort by relevance score and review quality
        relevant_medications.sort(key=lambda x: (x['relevance_score'], x['excellent_review']), reverse=True)
        
        return relevant_medications[:10]  # Return top 10 recommendations
    
    def _get_disease_keywords(self, disease):
        """Get relevant keywords for a disease to improve medication matching"""
        keyword_map = {
            'Common Cold': ['cold', 'respiratory', 'cough', 'congestion'],
            'Migraine': ['headache', 'pain', 'migraine'],
            'Hypertension': ['blood pressure', 'hypertension', 'cardiac'],
            'GERD': ['acid', 'reflux', 'gastro', 'stomach'],
            'Gastroenteritis': ['gastro', 'stomach', 'diarrhea', 'nausea'],
            'Diabetes': ['diabetes', 'blood sugar', 'glucose'],
            'Asthma': ['asthma', 'respiratory', 'breathing'],
            'Arthritis': ['arthritis', 'joint', 'inflammation', 'pain'],
            'Allergy': ['allergy', 'allergic', 'antihistamine'],
            'Infection': ['infection', 'bacterial', 'antibiotic'],
            'Pain': ['pain', 'analgesic', 'anti-inflammatory']
        }
        
        # Get keywords for the specific disease
        keywords = keyword_map.get(disease, [])
        
        # Add general keywords based on disease name
        disease_words = disease.lower().split()
        keywords.extend(disease_words)
        
        return list(set(keywords))
    
    def get_age_based_dosage(self, medicine_name, age):
        """Get age-appropriate dosage recommendations"""
        adherence_data = self.data_loader.get_adherence_data()
        if adherence_data is None:
            return self._get_generic_dosage_by_age(age)
        
        # Find similar medications in adherence data
        medicine_types = adherence_data['Medication_Type'].unique()
        
        # Try to match medicine name with medication types
        best_match = process.extractOne(medicine_name, medicine_types)
        if best_match and best_match[1] > 60:  # 60% similarity threshold
            med_type = best_match[0]
            
            # Get average dosage for similar age group
            age_group_data = adherence_data[
                (adherence_data['Medication_Type'] == med_type) &
                (adherence_data['Age'] >= age - 5) &
                (adherence_data['Age'] <= age + 5)
            ]
            
            if not age_group_data.empty:
                avg_dosage = age_group_data['Dosage_mg'].mean()
                return f"{avg_dosage:.0f}mg (based on similar patients in your age group)"
        
        return self._get_generic_dosage_by_age(age)
    
    def _get_generic_dosage_by_age(self, age):
        """Provide generic age-based dosage guidelines"""
        if age < 12:
            return "Pediatric dosage - consult pediatrician"
        elif age < 18:
            return "Adolescent dosage - typically 50-75% of adult dose"
        elif age < 65:
            return "Standard adult dosage as per medication guidelines"
        else:
            return "Elderly dosage - may require reduced dose, consult geriatrician"
    
    def get_detailed_side_effects(self, medicine_name):
        """Get detailed side effects from the drugs.com dataset"""
        side_effects_data = self.data_loader.get_side_effects_data()
        if side_effects_data is None:
            return None
        
        # Clean medicine name for matching
        clean_name = self._clean_medicine_name(medicine_name)
        
        # Try direct name matching
        direct_matches = side_effects_data[
            side_effects_data['drug_name'].str.contains(clean_name, case=False, na=False)
        ]
        
        if not direct_matches.empty:
            return direct_matches.iloc[0]['side_effects']
        
        # Try fuzzy matching with drug names
        drug_names = side_effects_data['drug_name'].dropna().unique()
        best_match = process.extractOne(clean_name, drug_names)
        
        if best_match and best_match[1] > 70:  # 70% similarity threshold
            matched_drug = best_match[0]
            side_effects = side_effects_data[
                side_effects_data['drug_name'] == matched_drug
            ]['side_effects'].iloc[0]
            return side_effects
        
        # Try matching with generic names
        if 'generic_name' in side_effects_data.columns:
            generic_matches = side_effects_data[
                side_effects_data['generic_name'].str.contains(clean_name, case=False, na=False)
            ]
            if not generic_matches.empty:
                return generic_matches.iloc[0]['side_effects']
        
        return None
    
    def _clean_medicine_name(self, name):
        """Clean medicine name for better matching"""
        if not name:
            return ""
        
        # Remove dosage information (e.g., "400mg", "25 Tablet")
        clean_name = re.sub(r'\d+\s*(mg|mcg|g|ml|tablet|capsule|injection|syrup|cream)', '', name, flags=re.IGNORECASE)
        
        # Remove brand-specific suffixes
        clean_name = re.sub(r'\s+(tablet|capsule|injection|syrup|cream|gel|ointment).*$', '', clean_name, flags=re.IGNORECASE)
        
        # Extract main drug name (usually the first word or two)
        words = clean_name.strip().split()
        if words:
            # Take first 1-2 significant words
            main_name = ' '.join(words[:2]) if len(words) > 1 else words[0]
            return main_name.strip()
        
        return clean_name.strip()
    
    def get_drug_interactions(self, medicine_list):
        """Check for potential drug interactions (basic implementation)"""
        # This is a simplified implementation
        # In a real system, you'd have a comprehensive drug interaction database
        
        interactions = []
        
        # Basic interaction patterns based on drug classes
        interaction_patterns = {
            'blood_pressure': ['lisinopril', 'amlodipine', 'metoprolol', 'losartan'],
            'blood_thinners': ['warfarin', 'aspirin', 'clopidogrel'],
            'antibiotics': ['amoxicillin', 'azithromycin', 'ciprofloxacin'],
            'nsaids': ['ibuprofen', 'naproxen', 'diclofenac']
        }
        
        # Check for potential interactions within the same class
        for category, drugs in interaction_patterns.items():
            category_matches = []
            for medicine in medicine_list:
                clean_name = self._clean_medicine_name(medicine).lower()
                for drug in drugs:
                    if drug in clean_name or fuzz.partial_ratio(drug, clean_name) > 80:
                        category_matches.append(medicine)
                        break
            
            if len(category_matches) > 1:
                interactions.append({
                    'type': f'{category.replace("_", " ").title()} Interaction',
                    'drugs': category_matches,
                    'warning': f'Multiple {category.replace("_", " ")} medications detected. Monitor for enhanced effects.'
                })
        
        return interactions
