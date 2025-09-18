import streamlit as st
import base64
import os
import io
import json
import pandas as pd
from datetime import datetime, timedelta
from PIL import Image
import speech_recognition as sr
from langdetect import detect
from dotenv import load_dotenv
load_dotenv()

import os




# Import our services and utilities
from services.twilio_service import TwilioService
from services.language_service import LanguageService
from services.prescription_ocr import PrescriptionOCR
from services.reminder_service import ReminderService
from data_loader import DataLoader
from utils.database import db
from utils.diagnosis_engine import DiagnosisEngine
from utils.medication_recommender import MedicationRecommender

import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-pro")

# Initialize services
@st.cache_resource
@st.cache_resource
def initialize_services():
    try:
        data_loader = DataLoader()

        twilio_service = TwilioService()
        language_service = LanguageService()
        prescription_ocr = PrescriptionOCR()
        reminder_service = ReminderService(twilio_service, db)
        diagnosis_engine = DiagnosisEngine(data_loader)
        medication_recommender = MedicationRecommender(data_loader)
        return {
            'data_loader': data_loader,
            'twilio_service': twilio_service,
            'language_service': language_service,
            'prescription_ocr': prescription_ocr,
            'reminder_service': reminder_service,
            'diagnosis_engine': diagnosis_engine,
            'medication_recommender': medication_recommender
        }
    except Exception as e:
        st.error(f"Failed to initialize services: {str(e)}")
        return None
def get_ai_response(user_input, patient_data, language, chat_history):
    prompt = f"You are a helpful health assistant. Patient info: {patient_data}. Language: {language}. Chat history: {chat_history}. User: {user_input}"
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini chat response failed: {str(e)}"

def get_ai_symptom_analysis(symptoms_text, severity, duration, age, language):
    prompt = f"Analyze these symptoms: {symptoms_text}. Severity: {severity}. Duration: {duration} days. Age: {age}. Language: {language}."
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini symptom analysis failed: {str(e)}"


def main():
    st.set_page_config(
        page_title="AI Health Assistant",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    services = initialize_services()
    if not services:
        st.error("Failed to initialize application services. Please check your configuration.")
        return
    
    # Initialize session state
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_language' not in st.session_state:
        st.session_state.current_language = 'en'
    if 'patient_data' not in st.session_state:
        st.session_state.patient_data = {}
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🏥 AI Health Assistant")
        
        # Language selection
        language_options = {
            'en': '🇺🇸 English',
            'hi': '🇮🇳 हिंदी (Hindi)',
            'pa': '🇮🇳 ਪੰਜਾਬੀ (Punjabi)'
        }
        
        selected_lang = st.selectbox(
            "Select Language / भाषा चुनें / ਭਾਸ਼ਾ ਚੁਣੋ",
            options=list(language_options.keys()),
            format_func=lambda x: language_options[x],
            key='language_selector'
        )
        
        if selected_lang != st.session_state.current_language:
            st.session_state.current_language = selected_lang
            st.rerun()
        
        st.divider()
        
        # Navigation menu
        menu_options = [
            "🏠 Home",
            "💬 Health Chatbot",
            "📄 Prescription Scanner",
            "🩺 Symptom Checker",
            "💊 Medication Reminders",
            "📋 Health Records",
            "🔗 Medicine Purchase"
        ]
        
        selected_menu = st.selectbox("Navigation", menu_options)
    
    # Main content area
    if selected_menu == "🏠 Home":
        show_home_page(services)
    elif selected_menu == "💬 Health Chatbot":
        show_chatbot_page(services)
    elif selected_menu == "📄 Prescription Scanner":
        show_prescription_scanner(services)
    elif selected_menu == "🩺 Symptom Checker":
        show_symptom_checker(services)
    elif selected_menu == "💊 Medication Reminders":
        show_medication_reminders(services)
    elif selected_menu == "📋 Health Records":
        st.info("Health Records feature is not yet implemented.")
    elif selected_menu == "🔗 Medicine Purchase":
        show_medicine_purchase(services)

def show_home_page(services):
    lang_service = services['language_service']
    current_lang = st.session_state.current_language
    
    # Welcome message
    welcome_text = lang_service.get_text('welcome_title', current_lang)
    st.title(welcome_text)
    
    description = lang_service.get_text('welcome_description', current_lang)
    st.markdown(description)
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        🤖 **AI-Powered Chatbot**
        - Multilingual support
        - Voice input enabled
        - Medical guidance
        """)
    
    with col2:
        st.success("""
        📱 **Smart Scanner**
        - OCR prescription reading
        - Medicine extraction
        - Dosage recommendations
        """)
    
    with col3:
        st.warning("""
        ⏰ **Smart Reminders**
        - SMS notifications
        - Automated scheduling
        - Rural connectivity
        """)
    
    # Quick patient registration
    st.subheader("🆔 Patient Registration")
    
    with st.form("patient_registration"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name / पूरा नाम / ਪੂਰਾ ਨਾਮ")
            age = st.number_input("Age / उम्र / ਉਮਰ", min_value=0, max_value=120, value=25)
            phone = st.text_input("Phone Number / फोन नंबर / ਫੋਨ ਨੰਬਰ")
        
        with col2:
            gender = st.selectbox("Gender / लिंग / ਲਿੰਗ", ["Male", "Female", "Other"])
            email = st.text_input("Email (Optional)")
            
        submitted = st.form_submit_button("Register / पंजीकरण करें / ਰਜਿਸਟਰ ਕਰੋ")
        
        if submitted and name and phone:
            try:
                if db:
                    patient_id = db.create_patient(name, age, gender, email, phone)
                    st.session_state.user_id = patient_id
                    st.session_state.patient_data = {
                        'id': patient_id,
                        'name': name,
                        'age': age,
                        'gender': gender,
                        'email': email,
                        'phone': phone
                    }
                    st.success(f"Registration successful! Patient ID: {patient_id}")
                else:
                    # Fallback without database
                    st.session_state.user_id = hash(phone)  # Simple ID generation
                    st.session_state.patient_data = {
                        'name': name,
                        'age': age,
                        'gender': gender,
                        'email': email,
                        'phone': phone
                    }
                    st.success("Registration successful! (Running in offline mode)")
            except Exception as e:
                st.error(f"Registration failed: {str(e)}")
def show_chatbot_page(services):
    st.title("💬 AI Health Chatbot")
    current_lang = st.session_state.current_language

    col1, col2 = st.columns([3,1])
    with col2:
        if st.button("🎤 Voice Input"):
            try:
                r = sr.Recognizer()
                with sr.Microphone() as source:
                    st.info("Listening...")
                    audio = r.listen(source, timeout=5)
                    text = r.recognize_google(audio)
                    try:
                        detected_lang = detect(text)
                        if detected_lang in ['hi','pa']:
                            st.session_state.current_language = detected_lang
                    except Exception:
                        pass
                    st.session_state.voice_input = text
                    st.success(f"Voice captured: {text}")
            except Exception as e:
                st.error(f"Voice input failed: {str(e)}")

    with col1:
        user_input = st.text_input("Ask your health question", value=st.session_state.get('voice_input',''), key='chat_input')

    if user_input:
        st.session_state.chat_history.append({'role':'user','content':user_input,'timestamp':datetime.now(),'language':current_lang})
        try:
            with st.spinner("AI is thinking..."):
                response = get_ai_response(user_input, st.session_state.patient_data, current_lang, st.session_state.chat_history[-5:])
                st.session_state.chat_history.append({'role':'assistant','content':response,'timestamp':datetime.now(),'language':current_lang})
            st.session_state.voice_input = ''
        except Exception as e:
            st.error(f"Chat service unavailable: {str(e)}")

    st.subheader("Chat History")
    for message in st.session_state.chat_history[-10:]:
        with st.chat_message(message['role']):
            st.write(message['content'])
            st.caption(f"🕐 {message['timestamp'].strftime('%H:%M:%S')}")

def show_prescription_scanner(services):
    st.title("📄 Prescription Scanner")
    
    prescription_ocr = services['prescription_ocr']  # instance of PrescriptionOCR
    reminder_service = services['reminder_service']
    
    st.markdown("Upload a prescription image to extract medicine information automatically.")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose prescription image / प्रिस्क्रिप्शन इमेज चुनें / ਪਿਰਸਕ੍ਰਿਪਸ਼ਨ ਚਿੱਤਰ ਚੁਣੋ",
        type=['png', 'jpg', 'jpeg'],
        help="Upload clear image of prescription"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        col1, col2 = st.columns([1, 2])
        
        with col1:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Prescription", use_container_width=True)
        
        with col2:
            if st.button("🔍 Scan Prescription"):
                try:
                    with st.spinner("Scanning prescription... / प्रिस्क्रिप्शन स्कैन कर रहे हैं..."):
                        # Corrected: use extract_prescription_data instead of process
                        extraction_result = prescription_ocr.extract_prescription_data(image)
                        
                        # Save to session state
                        st.session_state.scanned_prescription = extraction_result
                        st.success("✅ Prescription scanned successfully!")
                        
                        # Debug: show raw OCR output
                        st.write("Raw OCR Output:", extraction_result)
                        
                except Exception as e:
                    st.error(f"Scanning failed: {str(e)}")
    
    # Display extracted prescription data
    if 'scanned_prescription' in st.session_state:
        prescription_data = st.session_state.scanned_prescription
        
        st.subheader("📋 Extracted Medicines")
        medicines = prescription_data.get('medicines', [])
        
        if medicines:
            medicines_df = pd.DataFrame(medicines)
            st.dataframe(medicines_df, use_container_width=True)
            
            # Medication reminder setup
            st.subheader("")
            
            if st.session_state.get('user_id') and st.session_state.get('patient_data', {}).get('phone'):
                with st.form("reminder_setup"):
                    st.write("Configure SMS reminders for your medications:")
                    
                    selected_medicines = st.multiselect(
                        "Select medicines for reminders:",
                        options=[med.get('name', f"Medicine {i+1}") for i, med in enumerate(medicines)]
                    )
                    
                    reminder_times = st.multiselect(
                        "Select reminder times:",
                        options=['08:00', '12:00', '16:00', '20:00'],
                        default=['08:00', '20:00']
                    )
                    
                    start_date = st.date_input("Start date:", value=datetime.now().date())
                    duration_days = st.number_input("Duration (days):", min_value=1, max_value=365, value=7)
                    
                    if st.form_submit_button("📱 Setup SMS Reminders"):
                        phone_number = st.session_state.patient_data['phone']
                        
                        for medicine_name in selected_medicines:
                            medicine_details = next(
                                (med for med in medicines if med.get('name') == medicine_name),
                                {}
                            )
                            
                            success = reminder_service.setup_medication_reminder(
                                patient_id=st.session_state.user_id,
                                medicine_name=medicine_name,
                                dosage=medicine_details.get('dosage', 'As prescribed'),
                                frequency=medicine_details.get('frequency', 'As prescribed'),
                                phone_number=phone_number,
                                reminder_times=reminder_times,
                                start_date=start_date,
                                duration_days=duration_days
                            )
                        
                        st.success("✅ SMS reminders set successfully!")
        else:
            st.info("⚠️ No medicines found in the prescription. Check OCR output above.")


def show_symptom_checker(services):
    st.title("🩺 AI Symptom Checker")
    
    diagnosis_engine = services['diagnosis_engine']
    
    st.markdown("Describe your symptoms to get AI-powered health guidance.")
    
    with st.form("symptom_checker"):
        # Symptom input
        symptoms_text = st.text_area(
            "Describe your symptoms / अपने लक्षण बताएं / ਆਪਣੇ ਲੱਛਣ ਦੱਸੋ",
            height=100,
            help="Describe all your symptoms in detail"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            severity = st.selectbox(
                "Overall Severity / गंभीरता / ਗੰਭੀਰਤਾ",
                options=['mild', 'moderate', 'severe', 'critical'],
                index=1
            )
        
        with col2:
            duration = st.number_input(
                "Duration (days) / अवधि (दिन) / ਮਿਆਦ (ਦਿਨ)",
                min_value=0,
                max_value=365,
                value=1
            )
        
        with col3:
            age = st.number_input(
                "Age / उम्र / ਉਮਰ",
                min_value=0,
                max_value=120,
                value=st.session_state.get('patient_data', {}).get('age', 25)
            )
        
        submitted = st.form_submit_button("🔍 Analyze Symptoms", type="primary")
        
        if submitted and symptoms_text.strip():
            try:
                with st.spinner("Analyzing symptoms with AI... / AI से लक्षणों का विश्लेषण..."):
                    ai_analysis = get_ai_symptom_analysis(
                        symptoms_text,
                        severity,
                        duration,
                        age,
                        st.session_state.current_language
                    )
                    
                    # Also get traditional diagnosis engine results
                    symptoms_list = [s.strip() for s in symptoms_text.replace(',', '\n').split('\n') if s.strip()]
                    traditional_results = diagnosis_engine.diagnose(symptoms_list)
                    
                    # Display AI analysis
                    st.subheader("🤖 AI Analysis Results")
                    
                    if 'urgency_level' in ai_analysis:
                        urgency = ai_analysis['urgency_level']
                        if urgency == 'emergency':
                            st.error("🚨 **EMERGENCY**: Seek immediate medical attention!")
                        elif urgency == 'urgent':
                            st.warning("⚠️ **URGENT**: Consult a doctor within 24 hours")
                        elif urgency == 'moderate':
                            st.info("📞 **MODERATE**: Schedule a doctor visit within a few days")
                        else:
                            st.success("💡 **MILD**: Monitor symptoms, self-care may be sufficient")
                    
                    if 'possible_conditions' in ai_analysis:
                        st.subheader("🎯 Possible Conditions")
                        for condition in ai_analysis['possible_conditions'][:5]:
                            confidence = condition.get('confidence', 0) * 100
                            st.write(f"• **{condition['condition']}** - Confidence: {confidence:.1f}%")
                            if 'explanation' in condition:
                                st.write(f"  *{condition['explanation']}*")
                    
                    if 'recommendations' in ai_analysis:
                        st.subheader("💡 AI Recommendations")
                        for rec in ai_analysis['recommendations']:
                            st.write(f"• {rec}")
                    
                    # Traditional analysis
                    if traditional_results:
                        st.subheader("📊 Traditional Analysis")
                        for result in traditional_results[:3]:
                            confidence = result.get('confidence', 0) * 100
                            st.write(f"• **{result['disease']}** - {confidence:.1f}%")
                            if 'precautions' in result and result['precautions']:
                                with st.expander("View Precautions"):
                                    for precaution in result['precautions']:
                                        st.write(f"- {precaution}")
                    
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                
                # Fallback to traditional diagnosis
                try:
                    symptoms_list = [s.strip() for s in symptoms_text.replace(',', '\n').split('\n') if s.strip()]
                    results = diagnosis_engine.diagnose(symptoms_list)
                    
                    if results:
                        st.subheader("📊 Analysis Results (Fallback)")
                        for result in results[:5]:
                            confidence = result.get('confidence', 0) * 100
                            st.write(f"• **{result['disease']}** - {confidence:.1f}%")
                except Exception as fallback_error:
                    st.error(f"Fallback analysis also failed: {str(fallback_error)}")

def show_medication_reminders(services):
    reminder_service = services['reminder_service']
    diagnosis_engine = services.get('diagnosis_engine')

    if not st.session_state.get('user_id'):
        st.warning("⚠️ Please register as a patient from the Home page to use this feature.")
        return

    st.subheader("📱 Active Reminders")

    try:
        if db:
            with st.form("symptom_checker"):
                symptoms_text = st.text_area(
                    "Describe your symptoms / अपने लक्षण बताएं / ਆਪਣੇ ਲੱਛਣ ਦੱਸੋ",
                    height=100,
                    help="Describe all your symptoms in detail"
                )
                col1, col2, col3 = st.columns(3)
                with col1:
                    severity = st.selectbox(
                        "Overall Severity / गंभीरता / ਗੰਭੀਰਤਾ",
                        options=['mild', 'moderate', 'severe', 'critical'],
                        index=1
                    )
                with col2:
                    duration = st.number_input(
                        "Duration (days) / अवधि (दिन) / ਮਿਆਦ (ਦਿਨ)",
                        min_value=0,
                        max_value=365,
                        value=1
                    )
                with col3:
                    age = st.number_input(
                        "Age / उम्र / ਉਮਰ",
                        min_value=0,
                        max_value=120,
                        value=st.session_state.get('patient_data', {}).get('age', 25)
                    )
                submitted = st.form_submit_button("🔍 Analyze Symptoms", type="primary")
                if submitted and symptoms_text.strip():
                    try:
                        with st.spinner("Analyzing symptoms with AI... / AI से लक्षणों का विश्लेषण..."):
                            ai_analysis = get_ai_symptom_analysis(
                                symptoms_text,
                                severity,
                                duration,
                                age,
                                st.session_state.current_language
                            )
                            st.subheader("🤖 AI Analysis Results")
                            st.write(ai_analysis)
                            symptoms_list = [s.strip() for s in symptoms_text.replace(',', '\n').split('\n') if s.strip()]
                            if diagnosis_engine:
                                traditional_results = diagnosis_engine.diagnose(symptoms_list)
                                if traditional_results:
                                    st.subheader("📊 Traditional Analysis")
                                    for result in traditional_results[:3]:
                                        confidence = result.get('confidence', 0) * 100
                                        st.write(f"• **{result['disease']}** - {confidence:.1f}%")
                                        if 'precautions' in result and result['precautions']:
                                            with st.expander("View Precautions"):
                                                for precaution in result['precautions']:
                                                    st.write(f"- {precaution}")
                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")
                        try:
                            symptoms_list = [s.strip() for s in symptoms_text.replace(',', '\n').split('\n') if s.strip()]
                            if diagnosis_engine:
                                results = diagnosis_engine.diagnose(symptoms_list)
                                if results:
                                    st.subheader("📊 Analysis Results (Fallback)")
                                    for result in results[:5]:
                                        confidence = result.get('confidence', 0) * 100
                                        st.write(f"• **{result['disease']}** - {confidence:.1f}%")
                        except Exception as fallback_error:
                            st.error(f"Fallback analysis also failed: {str(fallback_error)}")
                adherence_stats = db.get_adherence_stats(st.session_state.user_id, days=30)
                if adherence_stats and adherence_stats['total_doses'] > 0:
                    st.subheader("📈 Medication Adherence (Last 30 days)")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Doses", adherence_stats['total_doses'])
                    with col2:
                        st.metric("Taken", adherence_stats['taken_doses'])
                    with col3:
                        st.metric("Adherence %", f"{adherence_stats['adherence_percentage']}%")
        else:
            st.info("Database not available. Health records are not accessible in offline mode.")
            if st.session_state.chat_history:
                st.subheader("💬 Chat History (Session)")
                for message in st.session_state.chat_history:
                    with st.chat_message(message['role']):
                        st.write(message['content'])
                        st.caption(f"🕐 {message['timestamp'].strftime('%H:%M:%S')}")
    except Exception as e:
        st.error(f"Failed to load health records: {str(e)}")

def show_medicine_purchase(services):
    st.title("🔗 Medicine Purchase Links")
    
    st.markdown("Find and purchase your prescribed medicines from trusted pharmacies.")
    
    # Medicine search
    search_medicine = st.text_input(
        "Search Medicine / दवा खोजें / ਦਵਾਈ ਖੋਜੋ",
        placeholder="Enter medicine name..."
    )
    
    if search_medicine:
        st.subheader(f"🔍 Search Results for: {search_medicine}")
        
        # Popular pharmacy links
        pharmacy_links = [
            {
                'name': '1mg',
                'url': f'https://1mg.com/search/all?name={search_medicine}',
                'description': 'Leading online pharmacy with home delivery'
            },
            {
                'name': 'PharmEasy',
                'url': f'https://pharmeasy.in/search/all?name={search_medicine}',
                'description': 'Trusted online pharmacy with quick delivery'
            },
            {
                'name': 'Netmeds',
                'url': f'https://netmeds.com/catalogsearch/result?q={search_medicine}',
                'description': 'Reliable online medicine ordering'
            },
            {
                'name': 'Apollo Pharmacy',
                'url': f'https://apollopharmacy.in/search-medicines/{search_medicine}',
                'description': 'Apollo hospitals pharmacy chain'
            },
            {
                'name': 'MediBuddy',
                'url': f'https://medibuddy.in/medicines?search={search_medicine}',
                'description': 'Healthcare platform with medicine delivery'
            }
        ]
        
        for pharmacy in pharmacy_links:
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**{pharmacy['name']}**")
                    st.write(pharmacy['description'])
                
                with col2:
                    st.link_button("🛒 Visit Store", pharmacy['url'])
                
                st.divider()
    
    # Local pharmacy finder
    st.subheader("📍 Find Local Pharmacies")
    
    location = st.text_input(
        "Enter your location / अपना स्थान दर्ज करें / ਆਪਣਾ ਸਥਾਨ ਦਾਖਲ ਕਰੋ",
        placeholder="City, State or PIN code"
    )
    
    if location:
        st.info("💡 **Google Maps Search Links:**")
        
        google_maps_url = f"https://www.google.com/maps/search/pharmacy+near+{location.replace(' ', '+')}"
        st.link_button("🗺️ Find Pharmacies on Google Maps", google_maps_url)
        
        # Additional helpful links
        st.markdown("**Other helpful resources:**")
        st.markdown(f"• [Justdial Pharmacy Search](https://www.justdial.com/search/?q=pharmacy&city={location})")
        st.markdown(f"• [Practo Pharmacy Finder](https://www.practo.com/search/doctors?city={location}&specialization=Pharmacy)")
    
    # Emergency medicine information
    st.subheader("🚨 Emergency Medicine Information")
    
    with st.expander("Emergency Contacts & Information"):
        st.markdown("""
        **Emergency Numbers:**
        - 🚑 Ambulance: 108 (All India)
        - 🏥 Medical Emergency: 102
        - 🚨 General Emergency: 112
        
        **24x7 Pharmacy Chains:**
        - Apollo Pharmacy (Many locations)
        - Guardian Pharmacy
        - MedPlus (South India)
        - Local hospital pharmacies
        
        **Medicine Safety Tips:**
        - Always check expiry dates
        - Verify medicine names and dosages
        - Keep medicines in cool, dry places
        - Never share prescription medicines
        """)

if __name__ == "__main__":
    main()
