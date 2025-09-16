"""
Data loader for medical datasets used in the telemedicine application.
Handles loading and caching of medicine data, disease information, and other medical datasets.
"""

import pandas as pd
import os
from typing import Optional, Dict, Any, List
import json

class DataLoader:
    """Loader for medical datasets with caching and fallback mechanisms"""
    
    def __init__(self):
        self.data_cache = {}
        
        # Dataset file paths (these would be actual dataset files in production)
        self.dataset_paths = {
            'medicine_data': 'data/medicine_dataset.csv',
            'precaution_data': 'data/disease_precautions.csv', 
            'side_effects_data': 'data/drug_side_effects.csv',
            'adherence_data': 'data/medication_adherence.csv',
            'symptoms_data': 'data/symptoms_dataset.csv'
        }
        
        # Initialize with synthetic data for demonstration
        self._initialize_synthetic_data()
    
    def _initialize_synthetic_data(self):
        """Initialize with synthetic medical data for demonstration purposes"""
        
        # Create synthetic medicine data
        medicine_data = {
            'Medicine Name': [
                'Paracetamol 500mg', 'Ibuprofen 400mg', 'Amoxicillin 250mg',
                'Omeprazole 20mg', 'Metformin 500mg', 'Aspirin 75mg',
                'Atorvastatin 10mg', 'Lisinopril 5mg', 'Amlodipine 5mg',
                'Levothyroxine 50mcg', 'Azithromycin 500mg', 'Prednisone 5mg'
            ],
            'Composition': [
                'Paracetamol', 'Ibuprofen', 'Amoxicillin',
                'Omeprazole', 'Metformin', 'Aspirin',
                'Atorvastatin', 'Lisinopril', 'Amlodipine',
                'Levothyroxine', 'Azithromycin', 'Prednisone'
            ],
            'Uses': [
                'Pain relief and fever reduction',
                'Pain, inflammation, and fever reduction',
                'Treatment of bacterial infections',
                'Treatment of acid reflux and gastric ulcers',
                'Treatment of type 2 diabetes',
                'Prevention of heart attack and stroke',
                'Treatment of high cholesterol',
                'Treatment of hypertension',
                'Treatment of hypertension and angina',
                'Treatment of hypothyroidism',
                'Treatment of bacterial infections',
                'Treatment of inflammation and autoimmune conditions'
            ],
            'Side_effects': [
                'Nausea, stomach upset, rare liver damage',
                'Stomach upset, heartburn, drowsiness',
                'Nausea, diarrhea, allergic reactions',
                'Headache, nausea, stomach pain',
                'Nausea, diarrhea, stomach upset',
                'Stomach upset, bleeding risk',
                'Muscle pain, liver problems',
                'Dry cough, dizziness, fatigue',
                'Swelling, dizziness, flushing',
                'Heart palpitations, insomnia',
                'Nausea, diarrhea, stomach pain',
                'Weight gain, mood changes, high blood sugar'
            ],
            'Manufacturer': [
                'Generic Pharma', 'MediCorp', 'BioHealth',
                'PharmaTech', 'DiabetCare', 'CardioMed',
                'LipidCare', 'HeartHealth', 'CardioMed',
                'ThyroidCare', 'InfectMed', 'InflammaControl'
            ],
            'Excellent Review %': [85, 78, 92, 88, 79, 82, 86, 91, 89, 87, 84, 76],
            'Average Review %': [12, 18, 7, 10, 16, 15, 11, 8, 9, 11, 13, 19],
            'Poor Review %': [3, 4, 1, 2, 5, 3, 3, 1, 2, 2, 3, 5]
        }
        
        self.data_cache['medicine_data'] = pd.DataFrame(medicine_data)
        
        # Create synthetic disease precautions data
        precaution_data = {
            'Disease': [
                'Common Cold', 'Migraine', 'Hypertension', 'GERD', 'Gastroenteritis',
                'Bronchial Asthma', 'Arthritis', 'Heart Attack', 'Pneumonia', 'Diabetes'
            ],
            'Precaution_1': [
                'Rest and hydration', 'Avoid triggers', 'Monitor blood pressure', 
                'Avoid spicy foods', 'Stay hydrated', 'Avoid allergens',
                'Gentle exercise', 'Immediate medical care', 'Rest and fluids', 'Monitor blood sugar'
            ],
            'Precaution_2': [
                'Warm liquids', 'Dark quiet room', 'Low sodium diet',
                'Eat smaller meals', 'BRAT diet', 'Use inhaler as prescribed',
                'Apply heat/cold', 'Take prescribed medications', 'Avoid smoking', 'Healthy diet'
            ],
            'Precaution_3': [
                'Avoid cold air', 'Stress management', 'Regular exercise',
                'Elevate head while sleeping', 'Wash hands frequently', 'Monitor peak flow',
                'Maintain healthy weight', 'Cardiac rehabilitation', 'Get vaccinated', 'Regular exercise'
            ],
            'Precaution_4': [
                'Vitamin C', 'Regular sleep', 'Take medications as prescribed',
                'Avoid late night eating', 'Probiotics', 'Emergency action plan',
                'Physical therapy', 'Follow-up care', 'Complete antibiotic course', 'Foot care'
            ]
        }
        
        self.data_cache['precaution_data'] = pd.DataFrame(precaution_data)
        
        # Create synthetic side effects data
        side_effects_data = {
            'drug_name': [
                'Paracetamol', 'Ibuprofen', 'Amoxicillin', 'Omeprazole', 'Metformin',
                'Aspirin', 'Atorvastatin', 'Lisinopril', 'Amlodipine', 'Levothyroxine'
            ],
            'generic_name': [
                'Acetaminophen', 'Ibuprofen', 'Amoxicillin', 'Omeprazole', 'Metformin',
                'Aspirin', 'Atorvastatin', 'Lisinopril', 'Amlodipine', 'Levothyroxine'
            ],
            'medical_condition': [
                'Pain and fever', 'Pain and inflammation', 'Bacterial infections', 
                'Acid reflux', 'Type 2 diabetes', 'Cardiovascular prevention',
                'High cholesterol', 'Hypertension', 'Hypertension', 'Hypothyroidism'
            ],
            'side_effects': [
                'Nausea, vomiting, constipation, loss of appetite, stomach pain',
                'Nausea, vomiting, heartburn, stomach pain, diarrhea, constipation',
                'Nausea, vomiting, diarrhea, stomach pain, skin rash, allergic reactions',
                'Headache, nausea, stomach pain, gas, diarrhea, constipation',
                'Nausea, vomiting, stomach pain, diarrhea, metallic taste, loss of appetite',
                'Stomach upset, heartburn, nausea, vomiting, increased bleeding risk',
                'Muscle pain, weakness, nausea, stomach pain, constipation, liver problems',
                'Dry cough, dizziness, fatigue, headache, nausea, high potassium levels',
                'Dizziness, fatigue, nausea, stomach pain, swelling of ankles, flushing',
                'Heart palpitations, insomnia, nervousness, tremors, headache, nausea'
            ]
        }
        
        self.data_cache['side_effects_data'] = pd.DataFrame(side_effects_data)
        
        # Create synthetic adherence data
        adherence_data = {
            'Patient_ID': list(range(1, 101)),
            'Age': [25 + (i % 50) for i in range(100)],
            'Medication_Type': ['Paracetamol', 'Ibuprofen', 'Metformin', 'Omeprazole', 'Aspirin'] * 20,
            'Dosage_mg': [500, 400, 500, 20, 75] * 20,
            'Adherence_Rate': [0.7 + (i % 30) * 0.01 for i in range(100)]
        }
        
        self.data_cache['adherence_data'] = pd.DataFrame(adherence_data)
    
    def get_medicine_data(self) -> Optional[pd.DataFrame]:
        """Get medicine dataset"""
        return self._load_dataset('medicine_data')
    
    def get_precaution_data(self) -> Optional[pd.DataFrame]:
        """Get disease precautions dataset"""
        return self._load_dataset('precaution_data')
    
    def get_side_effects_data(self) -> Optional[pd.DataFrame]:
        """Get drug side effects dataset"""
        return self._load_dataset('side_effects_data')
    
    def get_adherence_data(self) -> Optional[pd.DataFrame]:
        """Get medication adherence dataset"""
        return self._load_dataset('adherence_data')
    
    def get_symptoms_data(self) -> Optional[pd.DataFrame]:
        """Get symptoms dataset"""
        return self._load_dataset('symptoms_data')
    
    def _load_dataset(self, dataset_name: str) -> Optional[pd.DataFrame]:
        """Load dataset with caching"""
        
        # Return from cache if available
        if dataset_name in self.data_cache:
            return self.data_cache[dataset_name]
        
        # Try to load from file
        file_path = self.dataset_paths.get(dataset_name)
        if file_path and os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                self.data_cache[dataset_name] = df
                return df
            except Exception as e:
                print(f"Failed to load {dataset_name} from {file_path}: {e}")
        
        # Return None if not found
        return None
    
    def search_medicines(self, query: str, limit: int = 10) -> Optional[pd.DataFrame]:
        """Search medicines by name or composition"""
        medicine_data = self.get_medicine_data()
        if medicine_data is None:
            return None
        
        # Search in medicine name and composition
        mask = (
            medicine_data['Medicine Name'].str.contains(query, case=False, na=False) |
            medicine_data['Composition'].str.contains(query, case=False, na=False) |
            medicine_data['Uses'].str.contains(query, case=False, na=False)
        )
        
        results = medicine_data[mask].head(limit)
        return results if not results.empty else None
    
    def get_medicine_by_condition(self, condition: str) -> Optional[pd.DataFrame]:
        """Get medicines that treat a specific condition"""
        medicine_data = self.get_medicine_data()
        if medicine_data is None:
            return None
        
        mask = medicine_data['Uses'].str.contains(condition, case=False, na=False)
        results = medicine_data[mask]
        
        return results if not results.empty else None
    
    def get_disease_info(self, disease_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive information about a disease"""
        precaution_data = self.get_precaution_data()
        
        if precaution_data is None:
            return None
        
        # Find disease in precautions data
        mask = precaution_data['Disease'].str.contains(disease_name, case=False, na=False)
        disease_rows = precaution_data[mask]
        
        if disease_rows.empty:
            return None
        
        disease_row = disease_rows.iloc[0]
        
        # Get related medicines
        related_medicines = self.get_medicine_by_condition(disease_name)
        
        # Compile disease information
        disease_info = {
            'name': disease_row['Disease'],
            'precautions': [
                disease_row.get('Precaution_1', ''),
                disease_row.get('Precaution_2', ''),
                disease_row.get('Precaution_3', ''),
                disease_row.get('Precaution_4', '')
            ],
            'related_medicines': related_medicines.to_dict('records') if related_medicines is not None else []
        }
        
        # Remove empty precautions
        disease_info['precautions'] = [p for p in disease_info['precautions'] if p.strip()]
        
        return disease_info
    
    def get_medicine_interactions(self, medicine_name: str) -> List[Dict[str, Any]]:
        """Get potential drug interactions for a medicine"""
        # This is a simplified implementation
        # In production, you'd have a comprehensive drug interaction database
        
        interactions = []
        
        # Basic interaction warnings based on medicine type
        interaction_warnings = {
            'aspirin': [
                {
                    'interacting_drug': 'Warfarin',
                    'severity': 'high',
                    'description': 'Increased bleeding risk'
                }
            ],
            'metformin': [
                {
                    'interacting_drug': 'Alcohol',
                    'severity': 'moderate',
                    'description': 'Risk of lactic acidosis'
                }
            ],
            'lisinopril': [
                {
                    'interacting_drug': 'Potassium supplements',
                    'severity': 'moderate',
                    'description': 'Risk of hyperkalemia'
                }
            ]
        }
        
        medicine_lower = medicine_name.lower()
        for drug, drug_interactions in interaction_warnings.items():
            if drug in medicine_lower:
                interactions.extend(drug_interactions)
        
        return interactions
    
    def get_dataset_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded datasets"""
        stats = {}
        
        for dataset_name in self.dataset_paths.keys():
            data = self._load_dataset(dataset_name)
            if data is not None:
                stats[dataset_name] = {
                    'rows': len(data),
                    'columns': len(data.columns),
                    'memory_usage': data.memory_usage(deep=True).sum(),
                    'loaded': True
                }
            else:
                stats[dataset_name] = {
                    'loaded': False,
                    'error': 'Dataset not available'
                }
        
        return stats
    
    def refresh_cache(self):
        """Clear cache and reload all datasets"""
        self.data_cache.clear()
        print("Dataset cache cleared")
        
        # Reload synthetic data
        self._initialize_synthetic_data()
        print("Synthetic data reloaded")
    
    def export_dataset(self, dataset_name: str, file_path: str) -> bool:
        """Export dataset to CSV file"""
        try:
            data = self._load_dataset(dataset_name)
            if data is not None:
                data.to_csv(file_path, index=False)
                return True
            return False
        except Exception as e:
            print(f"Failed to export {dataset_name}: {e}")
            return False
    
    def validate_datasets(self) -> Dict[str, bool]:
        """Validate all datasets for required columns and data quality"""
        validation_results = {}
        
        # Required columns for each dataset
        required_columns = {
            'medicine_data': ['Medicine Name', 'Composition', 'Uses', 'Side_effects'],
            'precaution_data': ['Disease', 'Precaution_1'],
            'side_effects_data': ['drug_name', 'side_effects'],
            'adherence_data': ['Patient_ID', 'Medication_Type', 'Adherence_Rate']
        }
        
        for dataset_name, required_cols in required_columns.items():
            data = self._load_dataset(dataset_name)
            
            if data is None:
                validation_results[dataset_name] = False
                continue
            
            # Check if required columns exist
            missing_cols = [col for col in required_cols if col not in data.columns]
            
            if missing_cols:
                print(f"Dataset {dataset_name} missing columns: {missing_cols}")
                validation_results[dataset_name] = False
            else:
                # Check for empty data
                if len(data) == 0:
                    print(f"Dataset {dataset_name} is empty")
                    validation_results[dataset_name] = False
                else:
                    validation_results[dataset_name] = True
        
        return validation_results
