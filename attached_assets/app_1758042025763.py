import streamlit as st
import pandas as pd
import numpy as np
from utils.data_loader import DataLoader
from utils.diagnosis_engine import DiagnosisEngine
from utils.medication_recommender import MedicationRecommender
from utils.patient_tracker import PatientTracker
from utils.prescription_scanner import PrescriptionScanner


# Page configuration
st.set_page_config(
    page_title="MedBot - Telemedicine Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_loader' not in st.session_state:
    st.session_state.data_loader = DataLoader()
if 'diagnosis_engine' not in st.session_state:
    st.session_state.diagnosis_engine = DiagnosisEngine(st.session_state.data_loader)
if 'medication_recommender' not in st.session_state:
    st.session_state.medication_recommender = MedicationRecommender(st.session_state.data_loader)
if 'patient_tracker' not in st.session_state:
    st.session_state.patient_tracker = PatientTracker()


def main():
    st.title("🏥 MedBot - Telemedicine Assistant")
    st.markdown("### AI-Powered Medical Consultation & Medication Recommendation System")
    
    # Sidebar for patient information
    st.sidebar.header("👤 Patient Information")
    patient_name = st.sidebar.text_input("Patient Name", placeholder="Enter patient name")
    patient_email = st.sidebar.text_input("Email (Optional)", placeholder="patient@email.com")
    patient_age = st.sidebar.number_input("Age", min_value=1, max_value=120, value=30)
    patient_gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"])
    
    # ML Model Status and Training
    st.sidebar.header("🤖 AI Model Status")
    ml_model = st.session_state.diagnosis_engine.ml_model
    model_info = ml_model.get_model_info()
    
    if model_info['status'] == 'trained':
        st.sidebar.success("✅ AI Model Active")
        st.sidebar.caption(f"Classes: {model_info['n_classes']}")
        
        if st.sidebar.button("🔄 Retrain Model"):
            with st.sidebar:
                with st.spinner("Training AI model..."):
                    try:
                        metrics = ml_model.train_model()
                        st.success(f"Model trained! Accuracy: {metrics['accuracy']:.1%}")
                        st.caption(f"Training samples: {metrics['training_samples']}")
                    except Exception as e:
                        st.error(f"Training failed: {e}")
    else:
        st.sidebar.warning(" AI Model ")
        if st.sidebar.button("🚀 Train AI Model"):
            with st.sidebar:
                with st.spinner("Training AI model..."):
                    try:
                        metrics = ml_model.train_model()

                    # If training returned nothing or failed silently
                        if not metrics:
                            st.warning("")
                        else:
                            st.success(f"Model trained! Accuracy: {metrics['accuracy']:.1%}")
                            st.caption(f"Training samples: {metrics['training_samples']}")
                            st.rerun()

                    except Exception:
                    # Hide all technical errors from the user
                            st.warning("Training")

    
    
    # Main navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🩺 Consultation", "📋 Patient History", "📊 Analytics", "💊 Prescription Scanner"])

    # -------------------------------
    # TAB 1: Consultation
    # -------------------------------
    with tab1:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.header("🔍 Symptom Assessment")
        
        symptom_input_method = st.radio(
            "How would you like to enter symptoms?",
            ["Text Description", "Symptom Checklist"]
        )
        
        symptoms = []
        symptom_severities = {}
        
        if symptom_input_method == "Text Description":
            symptom_text = st.text_area(
                "Describe your symptoms:",
                placeholder="E.g., I have a headache, fever, and feel nauseous...",
                height=100
            )
            if symptom_text:
                symptoms = [symptom_text.strip()]
        else:
            common_symptoms = [
                "Headache", "Fever", "Cough", "Nausea", "Vomiting", "Diarrhea", 
                "Abdominal pain", "Back pain", "Dizziness", "Fatigue", "Rash",
                "Shortness of breath", "Chest pain", "Joint pain", "Muscle pain",
                "Sore throat", "Runny nose", "Loss of appetite", "Weight loss"
            ]
            
            selected_symptoms = st.multiselect(
                "Select your symptoms:",
                common_symptoms,
                help="Select all symptoms you are experiencing"
            )
            symptoms = selected_symptoms
            
            if selected_symptoms:
                st.subheader("📊 Rate Symptom Severity")
                st.markdown("*Rate the severity of each symptom to improve diagnostic accuracy*")
                
                for symptom in selected_symptoms:
                    col_sev, col_dur = st.columns([2, 1])
                    with col_sev:
                        severity = st.selectbox(
                            f"Severity of {symptom}:",
                            ["Mild", "Moderate", "Severe", "Critical"],
                            index=1,
                            key=f"severity_{symptom}",
                            help=f"Rate how severe your {symptom.lower()} is"
                        )
                    with col_dur:
                        duration = st.number_input(
                            f"Days with {symptom}:",
                            min_value=0,
                            max_value=365,
                            value=1,
                            key=f"duration_{symptom}",
                            help=f"How many days have you had {symptom.lower()}?"
                        )
                    symptom_severities[symptom] = {
                        'severity': severity,
                        'duration_days': duration if duration > 0 else None
                    }
        
        if st.button("🔍 Diagnose", type="primary") and symptoms:
            with st.spinner("Analyzing symptoms with severity assessment..."):
                diagnosis_results = st.session_state.diagnosis_engine.diagnose(symptoms, symptom_severities)
                st.session_state.diagnosis_results = diagnosis_results
                st.session_state.current_symptoms = symptoms
                st.session_state.symptom_severities = symptom_severities
    
        with col2:
            st.header("📊 Diagnosis Results")
            
            if hasattr(st.session_state, 'diagnosis_results') and st.session_state.diagnosis_results:
                results = st.session_state.diagnosis_results
                top_diagnosis = results[0]
                
                confidence_color = "success" if top_diagnosis['confidence'] > 0.7 else "warning" if top_diagnosis['confidence'] > 0.5 else "info"
                
                if confidence_color == "success":
                    st.success(f"**{top_diagnosis['disease']}** (Confidence: {top_diagnosis['confidence']:.1%})")
                elif confidence_color == "warning":
                    st.warning(f"**{top_diagnosis['disease']}** (Confidence: {top_diagnosis['confidence']:.1%})")
                else:
                    st.info(f"**{top_diagnosis['disease']}** (Confidence: {top_diagnosis['confidence']:.1%})")
                
                if 'explanation' in top_diagnosis:
                    st.caption(f"📈 {top_diagnosis['explanation']}")
                
                if 'method' in top_diagnosis:
                    method = top_diagnosis['method']
                    method_icons = {
                        'hybrid': '🔬 Hybrid AI + Pattern Analysis',
                        'machine_learning': '🤖 AI Machine Learning',
                        'pattern_matching': '🔍 Pattern Matching'
                    }
                    st.caption(f"Method: {method_icons.get(method, method)}")
                
                if 'symptom_analysis' in top_diagnosis:
                    analysis = top_diagnosis['symptom_analysis']
                    risk_level = analysis['risk_level']
                    risk_colors = {'low': '🟢', 'moderate': '🟡', 'high': '🟠', 'critical': '🔴'}
                    st.markdown(f"**Risk Level:** {risk_colors.get(risk_level, '⚪')} {risk_level.title()}")
                    if risk_level in ['critical', 'high']:
                        st.error("⚠️ **URGENT**: High-risk symptoms detected. Seek immediate medical attention!")
                    elif risk_level == 'moderate':
                        st.warning("⚠️ **ATTENTION**: Moderate symptoms require medical consultation within 24-48 hours.")
                
                if hasattr(st.session_state, 'symptom_severities') and st.session_state.symptom_severities:
                    from utils.symptom_severity import SymptomSeverityEngine
                    severity_engine = SymptomSeverityEngine()
                    st.subheader("🚨 Urgency Recommendations")
                    for symptom, severity_info in st.session_state.symptom_severities.items():
                        severity = severity_info.get('severity', 'moderate')
                        recommendations = severity_engine.get_severity_recommendations(symptom, severity)
                        if recommendations and severity.lower() in ['critical', 'severe']:
                            with st.expander(f"⚠️ {symptom} ({severity}) - Action Required", expanded=True):
                                for rec in recommendations:
                                    st.write(f"• {rec}")
                
                if top_diagnosis['precautions']:
                    st.subheader("⚠️ Precautions")
                    for i, precaution in enumerate(top_diagnosis['precautions'], 1):
                        if precaution.strip():
                            st.write(f"{i}. {precaution}")
                
                if len(results) > 1:
                    st.subheader("🔄 Alternative Possibilities")
                    for result in results[1:3]:
                        st.info(f"**{result['disease']}** (Confidence: {result['confidence']:.1%})")
                
                # Save consultation
                if patient_name and st.button("💾 Save Consultation", type="primary"):
                    try:
                        patient_data = {
                            "name": patient_name,
                            "age": patient_age,
                            "gender": patient_gender,
                            "email": patient_email if patient_email else None
                        }
                        patient_record = st.session_state.patient_tracker.get_or_create_patient(patient_data)

                        if patient_record:
                            consultation_id = st.session_state.patient_tracker.save_consultation(
                                patient_id=str(patient_record["_id"]),
                                symptoms=symptoms,
                                diagnosis_result=results,
                                session_data={
                                    'symptom_severities': st.session_state.symptom_severities if hasattr(st.session_state, 'symptom_severities') else {},
                                    'patient_age': patient_age,
                                    'patient_gender': patient_gender
                                }
                            )
                            if consultation_id:
                                st.success("✅ Consultation saved successfully!")
                                st.session_state['last_consultation_id'] = consultation_id
                            else:
                                st.error("Failed to save consultation")
                        else:
                            st.error("Failed to create/find patient record")
                    except Exception as e:
                        st.error(f"Error saving consultation: {e}")
            else:
                st.info("Enter symptoms above to get a diagnosis")
       # Medication Recommendations Section
        if hasattr(st.session_state, 'diagnosis_results') and st.session_state.diagnosis_results:
            st.header("💊 Medication Recommendations")
            top_diagnosis = st.session_state.diagnosis_results[0]['disease']
            medications = st.session_state.medication_recommender.recommend_medications(
                top_diagnosis, patient_age, patient_gender
            )
            
            if medications:
                col3, col4 = st.columns([1,1])
                with col3:
                    st.subheader("🏥 Recommended Medications")
                    for i, med in enumerate(medications[:3], 1):
                        with st.expander(f"{i}. {med['name']}", expanded=i==1):
                            st.write(f"**Composition:** {med['composition']}")
                            st.write(f"**Uses:** {med['uses']}")
                            st.write(f"**Manufacturer:** {med['manufacturer']}")
                            dosage_info = st.session_state.medication_recommender.get_age_based_dosage(med['name'], patient_age)
                            if dosage_info:
                                st.write(f"**Recommended Dosage:** {dosage_info}")
                            if med['excellent_review'] > 0:
                                st.write(f"**Patient Reviews:** {med['excellent_review']}% Excellent, {med['average_review']}% Average, {med['poor_review']}% Poor")
                with col4:
                    st.subheader("⚠️ Side Effects & Warnings")
                    for i, med in enumerate(medications[:3], 1):
                        with st.expander(f"Side Effects - {med['name']}", expanded=i==1):
                            if med['side_effects']:
                                st.warning(f"**Common Side Effects:** {med['side_effects']}")
                            detailed_effects = st.session_state.medication_recommender.get_detailed_side_effects(med['name'])
                            if detailed_effects:
                                st.error(f"**Detailed Warning:** {str(detailed_effects)[:500]}...")
                
                # Save prescribed medications
                if hasattr(st.session_state, 'last_consultation_id') and st.session_state.last_consultation_id:
                    if st.button("💊 Save Prescribed Medications"):
                        try:
                            medication_data = []
                            for med in medications[:3]:
                                dosage_info = st.session_state.medication_recommender.get_age_based_dosage(med['name'], patient_age)
                                medication_data.append({
                                    'name': med['name'],
                                    'dosage': dosage_info if dosage_info else 'As directed',
                                    'frequency': 'As prescribed',
                                    'duration': '7-14 days',
                                    'side_effects': med['side_effects'] if med['side_effects'] else 'None reported'
                                })
                            success = st.session_state.patient_tracker.save_medications(st.session_state.last_consultation_id, medication_data)
                            if success:
                                st.success("✅ Medications saved to patient record!")
                            else:
                                st.error("Failed to save medications")
                        except Exception as e:
                            st.error(f"Error saving medications: {e}")
            else:
                st.warning("No specific medications found for this condition. Please consult a healthcare provider.")
        
    # -------------------------------
    # TAB 2: Patient History
    # -------------------------------
    with tab2:
        st.header("📋 Patient History & Records")
        if patient_name and patient_name.strip():
            try:
                patient_record = None
                if patient_email:
                    patient_record = st.session_state.patient_tracker.get_patient_by_email(patient_email)
                else:
                    patient_data = {
                        "name": patient_name,
                        "age": patient_age,
                        "gender": patient_gender,
                        "email": patient_email if patient_email else None
                    }
                    patient_record = st.session_state.patient_tracker.get_or_create_patient(patient_data)
                
                if patient_record:
                    st.session_state.patient_tracker.display_patient_history(str(patient_record["_id"]))
                else:
                    st.info(f"No history found for {patient_name}. Complete a consultation to create patient records.")
            except Exception as e:
                st.error(f"Error retrieving patient history: {e}")
        else:
            st.info("Please enter a patient name in the sidebar to view history.")

    # -------------------------------
    # TAB 3: Analytics
    # -------------------------------
    with tab3:
        st.header("📊 Medical Analytics Dashboard")
        try:
            st.session_state.patient_tracker.display_analytics_dashboard()
        except Exception as e:
            st.error(f"Error loading analytics: {e}")
    
    # -------------------------------
    # TAB 4: Prescription Scanner
    # -------------------------------
    with tab4:
        st.header("📷 Prescription Scanner (OCR)")

        # Upload image or paste text
        uploaded_file = st.file_uploader("Upload prescription image", type=["jpg", "jpeg", "png"])
        text_input = st.text_area("Or paste prescription text here:")

        if st.button("Scan Prescription"):
            try:
                # Initialize scanner
                scanner = PrescriptionScanner(tesseract_path=r"C:\Program Files\Tesseract-OCR\tesseract.exe")

                # Process uploaded image
                if uploaded_file:
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    results = scanner.process(temp_path, is_image=True)

                # Process pasted text
                elif text_input.strip():
                    results = scanner.process(text_input, is_image=False)

                # If neither input is provided
                else:
                    st.warning("⚠️ Please upload an image or paste text.")
                    results = None

                # Display results
                if results:
                    st.subheader("📝 Extracted OCR/Text")
                    st.text(results["raw_text"])

                    st.subheader("💊 Extracted Medicines")
                    st.json(results["structured_medicines"])

            except Exception as e:
                st.error(f"❌ Error during OCR/Scanning: {e}")
    # -------------------------------
    # Disclaimer
    # -------------------------------
    st.markdown("---")
    st.error("""
    **Medical Disclaimer**: This tool is for informational purposes only and is not a substitute for professional medical advice, 
    diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions 
    you may have regarding a medical condition. Never disregard professional medical advice or delay in seeking it because 
    of something you have read on this application.
    """)


if __name__ == "__main__":
    main()
