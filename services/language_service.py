"""
Language service for multilingual support in the telemedicine application.
Supports English, Hindi, and Punjabi with automatic language detection.
"""

import os
from typing import Dict, Optional
from langdetect import detect

class LanguageService:
    """Service for handling multilingual content and translations"""
    
    def __init__(self):
        self.supported_languages = ['en', 'hi', 'pa']
        
        # Predefined translations for common UI elements
        self.ui_translations = {
            'en': {
                'welcome_title': '🏥 AI Health Assistant - Your Digital Healthcare Companion',
                'welcome_description': '''
                Welcome to your AI-powered health assistant! This application provides:
                - 🤖 Intelligent health chatbot with voice support
                - 📱 Smart prescription scanner using AI vision
                - 🩺 Advanced symptom checker with urgency classification
                - ⏰ Automated medication reminders via SMS
                - 📋 Digital health records management
                - 🔗 Medicine purchase assistance
                
                **Designed for rural healthcare accessibility with offline capabilities.**
                ''',
                'symptoms_placeholder': 'Describe your symptoms in detail...',
                'medicine_search_placeholder': 'Enter medicine name to search...',
                'chat_placeholder': 'Ask your health question...',
                'voice_button': '🎤 Voice Input',
                'scan_button': '🔍 Scan Prescription',
                'analyze_button': '🔍 Analyze Symptoms',
                'setup_reminders': '📱 Setup SMS Reminders',
                'emergency_warning': '🚨 EMERGENCY: Seek immediate medical attention!',
                'urgent_warning': '⚠️ URGENT: Consult a doctor within 24 hours',
                'moderate_warning': '📞 MODERATE: Schedule a doctor visit within a few days',
                'mild_info': '💡 MILD: Monitor symptoms, self-care may be sufficient'
            },
            'hi': {
                'welcome_title': '🏥 AI स्वास्थ्य सहायक - आपका डिजिटल स्वास्थ्य साथी',
                'welcome_description': '''
                आपके AI-संचालित स्वास्थ्य सहायक में आपका स्वागत है! यह एप्लिकेशन प्रदान करता है:
                - 🤖 आवाज समर्थन के साथ बुद्धिमान स्वास्थ्य चैटबॉट
                - 📱 AI दृष्टि का उपयोग करते हुए स्मार्ट प्रिस्क्रिप्शन स्कैनर
                - 🩺 तात्कालिकता वर्गीकरण के साथ उन्नत लक्षण जांचकर्ता
                - ⏰ SMS के माध्यम से स्वचालित दवा अनुस्मारक
                - 📋 डिजिटल स्वास्थ्य रिकॉर्ड प्रबंधन
                - 🔗 दवा खरीदारी सहायता
                
                **ऑफलाइन क्षमताओं के साथ ग्रामीण स्वास्थ्य सेवा पहुंच के लिए डिज़ाइन किया गया।**
                ''',
                'symptoms_placeholder': 'अपने लक्षणों का विस्तार से वर्णन करें...',
                'medicine_search_placeholder': 'खोजने के लिए दवा का नाम दर्ज करें...',
                'chat_placeholder': 'अपना स्वास्थ्य प्रश्न पूछें...',
                'voice_button': '🎤 आवाज इनपुट',
                'scan_button': '🔍 प्रिस्क्रिप्शन स्कैन करें',
                'analyze_button': '🔍 लक्षणों का विश्लेषण करें',
                'setup_reminders': '📱 SMS अनुस्मारक सेटअप करें',
                'emergency_warning': '🚨 आपातकाल: तुरंत चिकित्सा सहायता लें!',
                'urgent_warning': '⚠️ तत्काल: 24 घंटे के भीतर डॉक्टर से सलाह लें',
                'moderate_warning': '📞 मध्यम: कुछ दिनों के भीतर डॉक्टर की नियुक्ति लें',
                'mild_info': '💡 हल्का: लक्षणों की निगरानी करें, स्व-देखभाल पर्याप्त हो सकती है'
            },
            'pa': {
                'welcome_title': '🏥 AI ਸਿਹਤ ਸਹਾਇਕ - ਤੁਹਾਡਾ ਡਿਜੀਟਲ ਸਿਹਤ ਸਾਥੀ',
                'welcome_description': '''
                ਤੁਹਾਡੇ AI-ਸੰਚਾਲਿਤ ਸਿਹਤ ਸਹਾਇਕ ਵਿੱਚ ਤੁਹਾਡਾ ਸੁਆਗਤ ਹੈ! ਇਹ ਐਪਲੀਕੇਸ਼ਨ ਪ੍ਰਦਾਨ ਕਰਦੀ ਹੈ:
                - 🤖 ਆਵਾਜ਼ ਸਮਰਥਨ ਦੇ ਨਾਲ ਬੁੱਧੀਮਾਨ ਸਿਹਤ ਚੈਟਬੋਟ
                - 📱 AI ਦ੍ਰਿਸ਼ਟੀ ਦੀ ਵਰਤੋਂ ਕਰਦੇ ਹੋਏ ਸਮਾਰਟ ਪ੍ਰਿਸਕ੍ਰਿਪਸ਼ਨ ਸਕੈਨਰ
                - 🩺 ਤਤਕਾਲਤਾ ਵਰਗੀਕਰਨ ਦੇ ਨਾਲ ਉੱਨਤ ਲੱਛਣ ਜਾਂਚਕਰਤਾ
                - ⏰ SMS ਦੁਆਰਾ ਸਵੈਚਲਿਤ ਦਵਾਈ ਯਾਦਦਿਹਾਨੀ
                - 📋 ਡਿਜੀਟਲ ਸਿਹਤ ਰਿਕਾਰਡ ਪ੍ਰਬੰਧਨ
                - 🔗 ਦਵਾਈ ਖਰੀਦਦਾਰੀ ਸਹਾਇਤਾ
                
                **ਔਫਲਾਈਨ ਸਮਰੱਥਾਵਾਂ ਦੇ ਨਾਲ ਪੇਂਡੂ ਸਿਹਤ ਸੇਵਾ ਪਹੁੰਚ ਲਈ ਡਿਜ਼ਾਈਨ ਕੀਤਾ ਗਿਆ।**
                ''',
                'symptoms_placeholder': 'ਆਪਣੇ ਲੱਛਣਾਂ ਦਾ ਵਿਸਤਾਰ ਨਾਲ ਵਰਣਨ ਕਰੋ...',
                'medicine_search_placeholder': 'ਖੋਜਣ ਲਈ ਦਵਾਈ ਦਾ ਨਾਮ ਦਾਖਲ ਕਰੋ...',
                'chat_placeholder': 'ਆਪਣਾ ਸਿਹਤ ਸਵਾਲ ਪੁੱਛੋ...',
                'voice_button': '🎤 ਆਵਾਜ਼ ਇਨਪੁੱਟ',
                'scan_button': '🔍 ਪ੍ਰਿਸਕ੍ਰਿਪਸ਼ਨ ਸਕੈਨ ਕਰੋ',
                'analyze_button': '🔍 ਲੱਛਣਾਂ ਦਾ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰੋ',
                'setup_reminders': '📱 SMS ਯਾਦਦਿਹਾਨੀ ਸੈਟਅਪ ਕਰੋ',
                'emergency_warning': '🚨 ਐਮਰਜੈਂਸੀ: ਤੁਰੰਤ ਡਾਕਟਰੀ ਸਹਾਇਤਾ ਲਵੋ!',
                'urgent_warning': '⚠️ ਤਤਕਾਲ: 24 ਘੰਟਿਆਂ ਵਿੱਚ ਡਾਕਟਰ ਨਾਲ ਸਲਾਹ ਕਰੋ',
                'moderate_warning': '📞 ਦਰਮਿਆਨਾ: ਕੁਝ ਦਿਨਾਂ ਵਿੱਚ ਡਾਕਟਰ ਦੀ ਮੁਲਾਕਾਤ ਤੈਅ ਕਰੋ',
                'mild_info': '💡 ਹਲਕਾ: ਲੱਛਣਾਂ ਦੀ ਨਿਗਰਾਨੀ ਕਰੋ, ਸਵੈ-ਦੇਖਭਾਲ ਕਾਫੀ ਹੋ ਸਕਦੀ ਹੈ'
            }
        }
    
    def detect_language(self, text: str) -> str:
        """Detect language of input text"""
        try:
            detected = detect(text)
            # Map detected languages to supported languages
            if detected in self.supported_languages:
                return detected
            elif detected in ['hi', 'mr', 'bn']:  # Indian languages
                return 'hi'
            else:
                return 'en'  # Default to English
        except:
            return 'en'  # Default to English if detection fails
    
    def get_text(self, key: str, language: str = 'en') -> str:
        """Get translated text for a given key and language"""
        if language not in self.supported_languages:
            language = 'en'
        
        return self.ui_translations.get(language, {}).get(key, 
               self.ui_translations['en'].get(key, key))
    
    def translate_text(self, text: str, target_language: str, 
                      source_language: str = 'auto') -> str:
        """Basic translation support - OpenAI handles complex translation in the app"""
        if target_language not in self.supported_languages:
            return text
        
        if target_language == 'en' and source_language == 'en':
            return text
        
        # For basic translation, return original text
        # Complex medical translation is handled by OpenAI service in the app
        return text
    
    def get_language_name(self, language_code: str) -> str:
        """Get human-readable language name"""
        language_names = {
            'en': 'English',
            'hi': 'हिंदी (Hindi)',
            'pa': 'ਪੰਜਾਬੀ (Punjabi)'
        }
        return language_names.get(language_code, language_code)
    
    def format_medical_text(self, text: str, language: str) -> str:
        """Format medical text appropriately for the target language"""
        if language == 'hi':
            # Add Devanagari formatting considerations
            return text
        elif language == 'pa':
            # Add Gurmukhi formatting considerations  
            return text
        else:
            # English formatting
            return text
    
    def get_emergency_keywords(self, language: str) -> list:
        """Get emergency keywords for the specified language"""
        emergency_keywords = {
            'en': [
                'emergency', 'urgent', 'severe pain', 'chest pain', 
                'difficulty breathing', 'unconscious', 'bleeding',
                'heart attack', 'stroke', 'seizure', 'overdose'
            ],
            'hi': [
                'आपातकाल', 'तत्काल', 'गंभीर दर्द', 'छाती में दर्द',
                'सांस लेने में कठिनाई', 'बेहोश', 'खून बह रहा',
                'दिल का दौरा', 'लकवा', 'दौरा', 'ओवरडोज'
            ],
            'pa': [
                'ਐਮਰਜੈਂਸੀ', 'ਤਤਕਾਲ', 'ਗੰਭੀਰ ਦਰਦ', 'ਛਾਤੀ ਵਿੱਚ ਦਰਦ',
                'ਸਾਹ ਲੈਣ ਵਿੱਚ ਮੁਸ਼ਕਲ', 'ਬੇਹੋਸ਼', 'ਖੂਨ ਵਗ ਰਿਹਾ',
                'ਦਿਲ ਦਾ ਦੌਰਾ', 'ਅਧਰੰਗ', 'ਦੌਰਾ', 'ਓਵਰਡੋਜ਼'
            ]
        }
        return emergency_keywords.get(language, emergency_keywords['en'])
    
    def check_emergency_content(self, text: str, language: str) -> bool:
        """Check if text contains emergency-related content"""
        text_lower = text.lower()
        emergency_keywords = self.get_emergency_keywords(language)
        
        for keyword in emergency_keywords:
            if keyword.lower() in text_lower:
                return True
        return False
    
    def get_medication_instructions(self, language: str) -> Dict[str, str]:
        """Get common medication instruction translations"""
        instructions = {
            'en': {
                'before_food': 'Take before food',
                'after_food': 'Take after food',
                'with_food': 'Take with food',
                'empty_stomach': 'Take on empty stomach',
                'bedtime': 'Take at bedtime',
                'morning': 'Take in the morning',
                'evening': 'Take in the evening',
                'twice_daily': 'Take twice daily',
                'thrice_daily': 'Take three times daily',
                'as_needed': 'Take as needed'
            },
            'hi': {
                'before_food': 'खाने से पहले लें',
                'after_food': 'खाने के बाद लें',
                'with_food': 'खाने के साथ लें',
                'empty_stomach': 'खाली पेट लें',
                'bedtime': 'सोते समय लें',
                'morning': 'सुबह लें',
                'evening': 'शाम को लें',
                'twice_daily': 'दिन में दो बार लें',
                'thrice_daily': 'दिन में तीन बार लें',
                'as_needed': 'आवश्यकता अनुसार लें'
            },
            'pa': {
                'before_food': 'ਖਾਣੇ ਤੋਂ ਪਹਿਲਾਂ ਲਵੋ',
                'after_food': 'ਖਾਣੇ ਤੋਂ ਬਾਅਦ ਲਵੋ',
                'with_food': 'ਖਾਣੇ ਨਾਲ ਲਵੋ',
                'empty_stomach': 'ਖਾਲੀ ਪੇਟ ਲਵੋ',
                'bedtime': 'ਸੌਣ ਸਮੇਂ ਲਵੋ',
                'morning': 'ਸਵੇਰੇ ਲਵੋ',
                'evening': 'ਸ਼ਾਮ ਨੂੰ ਲਵੋ',
                'twice_daily': 'ਦਿਨ ਵਿੱਚ ਦੋ ਵਾਰ ਲਵੋ',
                'thrice_daily': 'ਦਿਨ ਵਿੱਚ ਤਿੰਨ ਵਾਰ ਲਵੋ',
                'as_needed': 'ਲੋੜ ਅਨੁਸਾਰ ਲਵੋ'
            }
        }
        return instructions.get(language, instructions['en'])
