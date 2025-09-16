# AI-Powered Telemedicine Application

## Overview

This is a comprehensive AI-powered telemedicine assistant built with Streamlit that provides healthcare services primarily for rural and underserved areas. The application combines multiple AI technologies including OpenAI's GPT-5, computer vision for prescription scanning, and machine learning for symptom diagnosis. Key features include multilingual support (English, Hindi, Punjabi), voice input capabilities, automated medication reminders via SMS, and intelligent health chatbot functionality.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application providing an intuitive user interface
- **Component Structure**: Service-oriented architecture with clear separation of concerns
- **State Management**: Session-based state management for patient data and service initialization
- **Multilingual Support**: Language detection and translation services for accessibility

### Backend Architecture
- **AI Services Layer**: OpenAI GPT-5 integration for medical consultation and prescription OCR
- **Medical Intelligence**: Custom ML models using scikit-learn for diagnosis prediction with TF-IDF vectorization and Random Forest classification
- **Data Processing**: Pandas-based medical dataset management with fuzzy string matching for symptom analysis
- **Communication Services**: Twilio integration for SMS-based medication reminders

### Data Storage Solutions
- **Primary Database**: PostgreSQL with psycopg2 for patient records, consultations, and medical history
- **Document Storage**: MongoDB Atlas for patient tracking and consultation logs
- **In-Memory Caching**: Session-based caching for medical datasets and ML model states
- **File Storage**: Local CSV datasets for medicine information, disease precautions, and side effects data

### Authentication and Authorization
- **Environment-Based Security**: API keys and database credentials managed through environment variables
- **Service Authentication**: Individual service authentication for OpenAI, Twilio, and MongoDB connections
- **Data Privacy**: Patient information handled with healthcare data privacy considerations

### Medical Intelligence Components
- **Diagnosis Engine**: Multi-layered diagnosis system combining rule-based symptom matching with ML predictions
- **Medication Recommender**: Fuzzy matching algorithms for medicine suggestions based on diagnosed conditions
- **Symptom Severity Engine**: Weighted scoring system for urgency classification (emergency, urgent, moderate, mild)
- **Prescription OCR**: AI vision-powered prescription scanning using OpenAI's vision capabilities

## External Dependencies

### AI and Machine Learning Services
- **OpenAI API**: GPT-5 model for medical consultation, symptom analysis, and vision-based prescription scanning
- **Speech Recognition**: Google Speech Recognition API for voice input functionality
- **Language Detection**: langdetect library for automatic language identification

### Communication Services
- **Twilio**: SMS notification service for medication reminders and patient alerts
- **SMTP**: Email services for patient communication (configured but not explicitly implemented)

### Database Systems
- **PostgreSQL**: Primary relational database for structured medical data and patient records
- **MongoDB Atlas**: NoSQL database for document storage and patient tracking with TLS security

### Data Processing Libraries
- **pandas**: Medical dataset manipulation and analysis
- **scikit-learn**: Machine learning models for diagnosis prediction
- **fuzzywuzzy**: Fuzzy string matching for symptom and medicine name matching
- **OpenCV**: Image processing for prescription scanning

### UI and Media Processing
- **Streamlit**: Web application framework with built-in components
- **PIL (Pillow)**: Image processing for uploaded prescriptions
- **pytesseract**: OCR capabilities for text extraction from images

### Development and Deployment
- **python-dotenv**: Environment variable management for secure configuration
- **certifi**: SSL certificate handling for secure database connections
- **psycopg2**: PostgreSQL database adapter with connection pooling