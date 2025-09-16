"""
Enhanced prescription OCR service using OpenAI Vision API (GPT-5) for accurate medicine extraction.
This service replaces basic OCR with AI-powered vision analysis for better accuracy.
"""

import base64
import json
import re
from typing import Dict, List, Any, Optional
from PIL import Image
import io

class PrescriptionOCR:
    """Advanced prescription scanner using OpenAI Vision API"""
    
    def __init__(self, openai_service):
        self.openai_service = openai_service
        
        # Common medicine name patterns for validation
        self.medicine_patterns = [
            r'paracetamol|acetaminophen',
            r'ibuprofen',
            r'aspirin',
            r'amoxicillin',
            r'azithromycin',
            r'metformin',
            r'omeprazole',
            r'lisinopril',
            r'atorvastatin',
            r'amlodipine',
            r'levothyroxine',
            r'gabapentin',
            r'prednisone',
            r'tramadol',
            r'losartan'
        ]
        
        # Dosage and frequency patterns for validation
        self.dosage_patterns = [
            r'\d+\s*mg',
            r'\d+\s*g',
            r'\d+\s*ml',
            r'\d+\s*tablet[s]?',
            r'\d+\s*cap[s]?',
            r'\d+\s*injection[s]?'
        ]
        
        self.frequency_patterns = [
            r'once\s+daily|OD|1\s*x\s*daily',
            r'twice\s+daily|BD|2\s*x\s*daily',
            r'thrice\s+daily|TDS|3\s*x\s*daily',
            r'four\s+times\s+daily|QDS|4\s*x\s*daily',
            r'morning|evening|night',
            r'before\s+meals?|after\s+meals?',
            r'as\s+needed|PRN|SOS'
        ]
    
    def extract_prescription_data(self, image_base64: str) -> Dict[str, Any]:
        """
        Extract comprehensive prescription data using OpenAI Vision API
        """
        try:
            # Use OpenAI Vision API for advanced extraction
            result = self.openai_service.extract_prescription_data(image_base64)
            
            # Validate and enhance the extracted data
            validated_result = self._validate_and_enhance_extraction(result)
            
            # Add confidence scores and additional metadata
            enhanced_result = self._add_metadata(validated_result)
            
            return enhanced_result
            
        except Exception as e:
            print(f"Prescription extraction failed: {e}")
            return self._get_fallback_result()
    
    def _validate_and_enhance_extraction(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance the raw extraction results"""
        
        # Validate medicine information
        if 'medicines' in raw_result and raw_result['medicines']:
            validated_medicines = []
            
            for medicine in raw_result['medicines']:
                validated_medicine = self._validate_medicine_data(medicine)
                if validated_medicine:
                    validated_medicines.append(validated_medicine)
            
            raw_result['medicines'] = validated_medicines
        
        # Validate doctor information
        if 'doctor_info' in raw_result:
            raw_result['doctor_info'] = self._validate_doctor_info(raw_result['doctor_info'])
        
        # Validate patient information
        if 'patient_info' in raw_result:
            raw_result['patient_info'] = self._validate_patient_info(raw_result['patient_info'])
        
        return raw_result
    
    def _validate_medicine_data(self, medicine: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate and clean medicine data"""
        if not medicine.get('name') or medicine['name'].lower() in ['not visible', 'unclear', 'not extracted']:
            return None
        
        # Clean and validate medicine name
        medicine_name = self._clean_medicine_name(medicine.get('name', ''))
        if not medicine_name:
            return None
        
        # Clean and validate dosage
        dosage = self._clean_dosage(medicine.get('dosage', ''))
        
        # Clean and validate frequency
        frequency = self._clean_frequency(medicine.get('frequency', ''))
        
        # Clean and validate duration
        duration = self._clean_duration(medicine.get('duration', ''))
        
        return {
            'name': medicine_name,
            'dosage': dosage or 'As prescribed',
            'frequency': frequency or 'As prescribed',
            'duration': duration or 'As prescribed',
            'instructions': medicine.get('instructions', ''),
            'generic_name': medicine.get('generic_name', ''),
            'confidence_score': self._calculate_medicine_confidence(medicine)
        }
    
    def _clean_medicine_name(self, name: str) -> str:
        """Clean and validate medicine name"""
        if not name or name.lower() in ['not visible', 'unclear', 'not extracted']:
            return ''
        
        # Remove common prefixes/suffixes
        cleaned = re.sub(r'^(tab|cap|inj|syr)\.?\s*', '', name, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*(tablet|capsule|injection|syrup|mg|ml|g).*$', '', cleaned, flags=re.IGNORECASE)
        
        # Validate against known medicine patterns
        cleaned = cleaned.strip()
        
        # Basic validation - medicine name should be at least 3 characters
        if len(cleaned) >= 3 and cleaned.isalpha() or any(char.isalpha() for char in cleaned):
            return cleaned.title()
        
        return ''
    
    def _clean_dosage(self, dosage: str) -> str:
        """Clean and validate dosage information"""
        if not dosage or dosage.lower() in ['not visible', 'unclear', 'not extracted']:
            return ''
        
        # Extract dosage using regex
        dosage_match = re.search(r'(\d+\.?\d*)\s*(mg|g|ml|mcg|iu|units?)', dosage, re.IGNORECASE)
        if dosage_match:
            amount = dosage_match.group(1)
            unit = dosage_match.group(2).lower()
            return f"{amount}{unit}"
        
        # Extract tablet/capsule count
        tablet_match = re.search(r'(\d+)\s*(tablet[s]?|cap[s]?|pill[s]?)', dosage, re.IGNORECASE)
        if tablet_match:
            count = tablet_match.group(1)
            unit = 'tablet' if 'tablet' in dosage.lower() else 'capsule'
            return f"{count} {unit}"
        
        return dosage.strip()
    
    def _clean_frequency(self, frequency: str) -> str:
        """Clean and validate frequency information"""
        if not frequency or frequency.lower() in ['not visible', 'unclear', 'not extracted']:
            return ''
        
        freq_lower = frequency.lower()
        
        # Standardize common frequency patterns
        if any(pattern in freq_lower for pattern in ['once daily', 'od', '1 x daily', '1x daily']):
            return 'Once daily'
        elif any(pattern in freq_lower for pattern in ['twice daily', 'bd', '2 x daily', '2x daily']):
            return 'Twice daily'
        elif any(pattern in freq_lower for pattern in ['thrice daily', 'tds', '3 x daily', '3x daily']):
            return 'Three times daily'
        elif any(pattern in freq_lower for pattern in ['four times', 'qds', '4 x daily', '4x daily']):
            return 'Four times daily'
        elif 'morning' in freq_lower:
            return 'Morning'
        elif 'evening' in freq_lower:
            return 'Evening'
        elif 'night' in freq_lower:
            return 'At bedtime'
        elif any(pattern in freq_lower for pattern in ['as needed', 'prn', 'sos']):
            return 'As needed'
        
        return frequency.strip()
    
    def _clean_duration(self, duration: str) -> str:
        """Clean and validate duration information"""
        if not duration or duration.lower() in ['not visible', 'unclear', 'not extracted']:
            return ''
        
        # Extract duration using regex
        duration_match = re.search(r'(\d+)\s*(day[s]?|week[s]?|month[s]?)', duration, re.IGNORECASE)
        if duration_match:
            amount = duration_match.group(1)
            unit = duration_match.group(2).lower()
            return f"{amount} {unit}"
        
        return duration.strip()
    
    def _calculate_medicine_confidence(self, medicine: Dict[str, Any]) -> float:
        """Calculate confidence score for medicine extraction"""
        confidence = 0.0
        
        # Base confidence for having a name
        if medicine.get('name') and len(medicine['name']) > 2:
            confidence += 0.4
        
        # Additional confidence for dosage
        if medicine.get('dosage') and any(pattern in medicine['dosage'].lower() 
                                        for pattern in ['mg', 'g', 'ml', 'tablet']):
            confidence += 0.3
        
        # Additional confidence for frequency
        if medicine.get('frequency') and any(pattern in medicine['frequency'].lower() 
                                           for pattern in ['daily', 'morning', 'evening', 'times']):
            confidence += 0.2
        
        # Additional confidence for duration
        if medicine.get('duration') and any(pattern in medicine['duration'].lower() 
                                          for pattern in ['day', 'week', 'month']):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _validate_doctor_info(self, doctor_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean doctor information"""
        if not doctor_info:
            return {}
        
        # Clean doctor name
        name = doctor_info.get('name', '')
        if name and name.lower() not in ['not extracted', 'not visible', 'unclear']:
            # Remove common prefixes
            name = re.sub(r'^(dr\.?|doctor)\s*', '', name, flags=re.IGNORECASE)
            doctor_info['name'] = name.strip().title()
        else:
            doctor_info['name'] = 'Not extracted'
        
        return doctor_info
    
    def _validate_patient_info(self, patient_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean patient information"""
        if not patient_info:
            return {}
        
        # Clean patient name
        name = patient_info.get('name', '')
        if name and name.lower() not in ['not extracted', 'not visible', 'unclear']:
            patient_info['name'] = name.strip().title()
        else:
            patient_info['name'] = 'Not extracted'
        
        # Validate age
        age = patient_info.get('age', '')
        if age:
            age_match = re.search(r'(\d+)', str(age))
            if age_match:
                patient_info['age'] = age_match.group(1)
            else:
                patient_info['age'] = 'Not extracted'
        
        return patient_info
    
    def _add_metadata(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Add metadata and confidence scores to the result"""
        
        # Calculate overall extraction confidence
        medicine_count = len(result.get('medicines', []))
        doctor_extracted = bool(result.get('doctor_info', {}).get('name') and 
                              result['doctor_info']['name'] != 'Not extracted')
        patient_extracted = bool(result.get('patient_info', {}).get('name') and 
                               result['patient_info']['name'] != 'Not extracted')
        
        overall_confidence = 0.0
        if medicine_count > 0:
            overall_confidence += 0.6
        if doctor_extracted:
            overall_confidence += 0.2
        if patient_extracted:
            overall_confidence += 0.2
        
        # Add metadata
        result['extraction_metadata'] = {
            'medicine_count': medicine_count,
            'overall_confidence': overall_confidence,
            'extraction_method': 'openai_vision',
            'doctor_info_extracted': doctor_extracted,
            'patient_info_extracted': patient_extracted
        }
        
        return result
    
    def _get_fallback_result(self) -> Dict[str, Any]:
        """Return fallback result when extraction fails"""
        return {
            'doctor_info': {'name': 'Extraction failed'},
            'patient_info': {'name': 'Extraction failed'},
            'prescription_date': 'Not available',
            'medicines': [],
            'diagnosis': 'Extraction failed',
            'notes': 'Failed to process prescription image',
            'follow_up': 'Not available',
            'extraction_metadata': {
                'medicine_count': 0,
                'overall_confidence': 0.0,
                'extraction_method': 'failed',
                'doctor_info_extracted': False,
                'patient_info_extracted': False
            }
        }
    
    def validate_prescription_image(self, image_base64: str) -> bool:
        """Validate if the uploaded image is likely a prescription"""
        try:
            # Decode base64 image
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # Basic image validation
            if image.size[0] < 100 or image.size[1] < 100:
                return False
            
            # Check aspect ratio (prescriptions are usually portrait or square)
            aspect_ratio = image.size[0] / image.size[1]
            if aspect_ratio > 2 or aspect_ratio < 0.5:
                return False
            
            return True
            
        except Exception as e:
            print(f"Image validation failed: {e}")
            return False
    
    def extract_specific_medicine(self, image_base64: str, medicine_name: str) -> Optional[Dict[str, Any]]:
        """Extract information for a specific medicine from prescription"""
        try:
            full_result = self.extract_prescription_data(image_base64)
            
            if 'medicines' in full_result:
                for medicine in full_result['medicines']:
                    if medicine_name.lower() in medicine.get('name', '').lower():
                        return medicine
            
            return None
            
        except Exception as e:
            print(f"Specific medicine extraction failed: {e}")
            return None
    
    def get_extraction_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of the extraction results"""
        metadata = result.get('extraction_metadata', {})
        
        return {
            'success': metadata.get('medicine_count', 0) > 0,
            'medicine_count': metadata.get('medicine_count', 0),
            'confidence': metadata.get('overall_confidence', 0.0),
            'doctor_identified': metadata.get('doctor_info_extracted', False),
            'patient_identified': metadata.get('patient_info_extracted', False),
            'method': metadata.get('extraction_method', 'unknown')
        }
