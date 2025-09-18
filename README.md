# AI Health Assistant - SIH 2025 Submission

## 🏥 Project Overview

An intelligent healthcare assistant application developed for Smart India Hackathon 2025. This comprehensive platform combines AI-powered chatbot functionality with prescription checking capabilities to provide accessible healthcare support and medication guidance.

## 🚀 Features

### 🤖 AI Health Chatbot
- Interactive conversational AI for health-related queries
- Symptom assessment and preliminary health guidance
- 24/7 availability for immediate health consultations
- Natural language processing for accurate response generation

### 💊 Prescription Checker
- Medicine verification and interaction checking
- Dosage validation and safety recommendations
- Drug interaction warnings and contraindications
- Prescription authenticity verification

### 📱 User-Friendly Interface
- Intuitive web-based interface built with modern technologies
- Responsive design for mobile and desktop compatibility
- Real-time chat functionality with seamless user experience
- Streamlined navigation for easy access to all features

## 🛠️ Technology Stack

### Backend
- **Python** (93.9%) - Core application logic and AI models
- **FastAPI/Flask** - RESTful API development
- **Machine Learning Libraries** - TensorFlow/PyTorch for AI models
- **Database Integration** - Data storage and retrieval

### Frontend
- **HTML/CSS/JavaScript** - User interface development
- **PLpgSQL** (6.1%) - Database queries and procedures
- **Responsive Web Design** - Cross-platform compatibility

### AI & ML Components
- Natural Language Processing (NLP) models
- Medical knowledge base integration
- Prescription validation algorithms
- Gemini API integration for enhanced AI capabilities

## 📁 Project Structure

```
Chatbot_tele/
├── .local/state/replit/agent/    # Agent state management
├── .streamlit/                   # Streamlit configuration
├── __pycache__/                  # Python cache files
├── attached_assets/              # Static assets and resources
├── backend/                      # Backend API and services
├── services/                     # Core business logic services
├── utils/                        # Utility functions and helpers
├── app.py                        # Main application entry point
├── check_gemini_models.py        # Gemini API model verification
├── data_loader.py                # Data loading and preprocessing
├── embed_api.py                  # Embedding API services
├── gemini_test.py                # Gemini integration testing
├── main.py                       # Application launcher
└── README.md                     # Project documentation
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager
- API keys for Gemini/OpenAI services

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/kuldeep31016/Chatbot_tele.git
   cd Chatbot_tele
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   ```bash
   # Create .env file and add your API keys
   GEMINI_API_KEY=your_gemini_api_key
   OPENAI_API_KEY=your_openai_api_key
   DATABASE_URL=your_database_url
   ```

4. **Run the application**
   ```bash
   # Using Streamlit (recommended)
   streamlit run app.py
   
   # Or using Python directly
   python main.py
   ```

5. **Access the application**
   - Open your browser and navigate to `http://localhost:8501`
   - Start interacting with the AI health assistant

## 📖 Usage Guide

### Health Chatbot
1. Navigate to the chatbot interface
2. Type your health-related questions or symptoms
3. Receive AI-powered responses and recommendations
4. Follow up with additional questions as needed

### Prescription Checker
1. Upload or input prescription details
2. Get instant verification and safety checks
3. Review drug interaction warnings
4. Receive dosage recommendations and safety guidelines

## 🎯 SIH 2025 Problem Statement Alignment

This project addresses critical healthcare challenges by:
- **Improving Healthcare Accessibility**: 24/7 AI assistant for immediate health guidance
- **Enhancing Medication Safety**: Advanced prescription checking and validation
- **Reducing Healthcare Burden**: Preliminary assessment before hospital visits
- **Promoting Health Awareness**: Educational content and preventive care guidance

## 🔧 Key Technical Achievements

- **Advanced NLP Integration**: Sophisticated natural language understanding for medical queries
- **Real-time Processing**: Instant responses and prescription validation
- **Scalable Architecture**: Modular design supporting future enhancements
- **Security Implementation**: Secure handling of sensitive health data
- **Cross-platform Compatibility**: Accessible across various devices and browsers

## 🚀 Future Enhancements

- Integration with hospital management systems
- Telemedicine video consultation features
- Multi-language support for broader accessibility
- Mobile application development
- Advanced analytics and health tracking
- Integration with wearable devices and IoT sensors

## 👥 Team Information

**Developed for Smart India Hackathon 2024**
- Team Leader: Harshal Mandliya 
- Institution: Dayananda Sagar College of Engineering, Bengaluru
- Problem Statement: Telemedicine Chatbot

## 📞 Support & Contact

For technical support or project inquiries:
- Email: iamkulfeepraj55@gmail.com

## 📄 License

This project is developed for Smart India Hackathon 2025. All rights reserved.

---

**⚡ Built with passion for healthcare innovation and powered by AI technology**

*This project represents our commitment to leveraging technology for better healthcare accessibility and medication safety.*
