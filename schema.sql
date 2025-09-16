-- Database schema for AI-powered telemedicine application
-- Supports PostgreSQL database for production deployment

-- Enable UUID extension for unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Patients table
CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    name VARCHAR(255) NOT NULL,
    age INTEGER CHECK (age >= 0 AND age <= 150),
    gender VARCHAR(20) CHECK (gender IN ('Male', 'Female', 'Other')),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Additional patient information
    emergency_contact VARCHAR(20),
    emergency_contact_name VARCHAR(255),
    address TEXT,
    medical_history TEXT,
    allergies TEXT,
    chronic_conditions TEXT,
    
    -- Metadata
    registration_source VARCHAR(50) DEFAULT 'app',
    last_consultation_date TIMESTAMP WITH TIME ZONE,
    active BOOLEAN DEFAULT true
);

-- Consultations table
CREATE TABLE IF NOT EXISTS consultations (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    
    -- Consultation details
    symptoms TEXT NOT NULL,
    diagnosis VARCHAR(500) NOT NULL,
    confidence_score DECIMAL(5,4) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    prediction_method VARCHAR(50) NOT NULL,
    
    -- Additional consultation data
    urgency_level VARCHAR(20) CHECK (urgency_level IN ('mild', 'moderate', 'urgent', 'emergency')),
    consultation_type VARCHAR(50) DEFAULT 'symptom_checker',
    session_data JSONB,
    ai_recommendations TEXT,
    
    -- Timestamps
    consultation_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    follow_up_date TIMESTAMP WITH TIME ZONE,
    
    -- Doctor information (if applicable)
    doctor_name VARCHAR(255),
    doctor_specialty VARCHAR(100),
    clinic_name VARCHAR(255),
    
    -- Status tracking
    status VARCHAR(20) DEFAULT 'completed' CHECK (status IN ('pending', 'completed', 'follow_up_required')),
    notes TEXT
);

-- Medications table
CREATE TABLE IF NOT EXISTS medications (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    consultation_id INTEGER REFERENCES consultations(id) ON DELETE CASCADE,
    
    -- Medicine details
    medicine_name VARCHAR(255) NOT NULL,
    generic_name VARCHAR(255),
    dosage VARCHAR(100),
    frequency VARCHAR(100),
    duration VARCHAR(100),
    instructions TEXT,
    
    -- Additional medicine information
    side_effects TEXT,
    contraindications TEXT,
    food_interactions TEXT,
    
    -- Prescription details
    prescribed_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    start_date DATE,
    end_date DATE,
    
    -- Status
    active BOOLEAN DEFAULT true,
    discontinued_date TIMESTAMP WITH TIME ZONE,
    discontinuation_reason TEXT
);

-- Medication adherence tracking
CREATE TABLE IF NOT EXISTS medication_adherence (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    medication_id INTEGER REFERENCES medications(id) ON DELETE CASCADE,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    
    -- Adherence details
    taken_date DATE NOT NULL,
    taken BOOLEAN NOT NULL DEFAULT false,
    taken_time TIME,
    scheduled_time TIME,
    
    -- Additional tracking
    notes TEXT,
    side_effects_experienced TEXT,
    missed_reason VARCHAR(255),
    
    -- Timestamps
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure one record per medication per day
    UNIQUE(medication_id, patient_id, taken_date)
);

-- Prescription scans table (for storing OCR results)
CREATE TABLE IF NOT EXISTS prescription_scans (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    consultation_id INTEGER REFERENCES consultations(id) ON DELETE SET NULL,
    
    -- Scan details
    image_path VARCHAR(500),
    image_hash VARCHAR(64), -- For duplicate detection
    
    -- OCR results
    raw_ocr_text TEXT,
    structured_data JSONB,
    extraction_confidence DECIMAL(5,4),
    extraction_method VARCHAR(50) DEFAULT 'openai_vision',
    
    -- Doctor and prescription info
    doctor_name VARCHAR(255),
    doctor_specialty VARCHAR(100),
    clinic_name VARCHAR(255),
    prescription_date DATE,
    
    -- Processing metadata
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processing_status VARCHAR(20) DEFAULT 'completed',
    error_message TEXT,
    
    -- Medicine count extracted
    medicines_extracted INTEGER DEFAULT 0
);

-- SMS reminders table
CREATE TABLE IF NOT EXISTS sms_reminders (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    medication_id INTEGER REFERENCES medications(id) ON DELETE CASCADE,
    
    -- Reminder configuration
    phone_number VARCHAR(20) NOT NULL,
    reminder_times TIME[] NOT NULL, -- Array of reminder times
    active BOOLEAN DEFAULT true,
    
    -- Schedule details
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reminder_frequency VARCHAR(50) DEFAULT 'daily',
    
    -- Message customization
    custom_message TEXT,
    language_code VARCHAR(5) DEFAULT 'en',
    
    -- Tracking
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_sent_at TIMESTAMP WITH TIME ZONE,
    total_sent INTEGER DEFAULT 0,
    total_failed INTEGER DEFAULT 0,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'cancelled'))
);

-- SMS delivery log
CREATE TABLE IF NOT EXISTS sms_delivery_log (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    reminder_id INTEGER REFERENCES sms_reminders(id) ON DELETE CASCADE,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    
    -- Message details
    phone_number VARCHAR(20) NOT NULL,
    message_content TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'medication_reminder',
    
    -- Delivery tracking
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    delivery_status VARCHAR(20) DEFAULT 'sent',
    twilio_sid VARCHAR(100),
    error_message TEXT,
    
    -- Cost tracking
    cost_cents INTEGER,
    
    -- Response tracking
    patient_response TEXT,
    response_received_at TIMESTAMP WITH TIME ZONE
);

-- Chat history table
CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    
    -- Chat details
    session_id VARCHAR(100),
    message_role VARCHAR(20) NOT NULL CHECK (message_role IN ('user', 'assistant', 'system')),
    message_content TEXT NOT NULL,
    
    -- Message metadata
    language_code VARCHAR(5) DEFAULT 'en',
    message_type VARCHAR(50) DEFAULT 'chat',
    intent_detected VARCHAR(100),
    confidence_score DECIMAL(5,4),
    
    -- AI processing
    ai_model_used VARCHAR(50),
    processing_time_ms INTEGER,
    tokens_used INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Emergency detection
    emergency_detected BOOLEAN DEFAULT false,
    emergency_keywords TEXT[]
);

-- Health records summary view
CREATE TABLE IF NOT EXISTS health_records_summary (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    
    -- Summary statistics
    total_consultations INTEGER DEFAULT 0,
    total_medications INTEGER DEFAULT 0,
    total_prescriptions_scanned INTEGER DEFAULT 0,
    
    -- Recent activity
    last_consultation_date TIMESTAMP WITH TIME ZONE,
    last_prescription_date TIMESTAMP WITH TIME ZONE,
    last_chat_date TIMESTAMP WITH TIME ZONE,
    
    -- Health metrics
    medication_adherence_7days DECIMAL(5,2),
    medication_adherence_30days DECIMAL(5,2),
    
    -- Common conditions
    most_common_symptoms TEXT[],
    frequent_diagnoses TEXT[],
    
    -- Risk assessment
    risk_level VARCHAR(20) DEFAULT 'low',
    risk_factors TEXT[],
    
    -- Updated timestamp
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- System configuration table
CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    config_type VARCHAR(20) DEFAULT 'string',
    description TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100)
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone);
CREATE INDEX IF NOT EXISTS idx_patients_email ON patients(email);
CREATE INDEX IF NOT EXISTS idx_patients_active ON patients(active);

CREATE INDEX IF NOT EXISTS idx_consultations_patient_id ON consultations(patient_id);
CREATE INDEX IF NOT EXISTS idx_consultations_date ON consultations(consultation_date);
CREATE INDEX IF NOT EXISTS idx_consultations_urgency ON consultations(urgency_level);

CREATE INDEX IF NOT EXISTS idx_medications_consultation_id ON medications(consultation_id);
CREATE INDEX IF NOT EXISTS idx_medications_patient ON medications(consultation_id, medicine_name);
CREATE INDEX IF NOT EXISTS idx_medications_active ON medications(active);

CREATE INDEX IF NOT EXISTS idx_adherence_patient_date ON medication_adherence(patient_id, taken_date);
CREATE INDEX IF NOT EXISTS idx_adherence_medication ON medication_adherence(medication_id);

CREATE INDEX IF NOT EXISTS idx_sms_reminders_patient ON sms_reminders(patient_id);
CREATE INDEX IF NOT EXISTS idx_sms_reminders_active ON sms_reminders(active);

CREATE INDEX IF NOT EXISTS idx_sms_log_patient ON sms_delivery_log(patient_id);
CREATE INDEX IF NOT EXISTS idx_sms_log_sent_at ON sms_delivery_log(sent_at);

CREATE INDEX IF NOT EXISTS idx_chat_history_patient ON chat_history(patient_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_session ON chat_history(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_emergency ON chat_history(emergency_detected);

-- Triggers for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_health_summary_updated_at BEFORE UPDATE ON health_records_summary
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate medication adherence
CREATE OR REPLACE FUNCTION calculate_medication_adherence(p_patient_id INTEGER, p_days INTEGER DEFAULT 30)
RETURNS DECIMAL(5,2) AS $$
DECLARE
    total_doses INTEGER;
    taken_doses INTEGER;
    adherence_rate DECIMAL(5,2);
BEGIN
    SELECT 
        COUNT(*) INTO total_doses,
        SUM(CASE WHEN taken THEN 1 ELSE 0 END) INTO taken_doses
    FROM medication_adherence ma
    JOIN medications m ON ma.medication_id = m.id
    WHERE ma.patient_id = p_patient_id
    AND ma.taken_date >= CURRENT_DATE - INTERVAL '1 day' * p_days
    AND m.active = true;
    
    IF total_doses = 0 THEN
        RETURN NULL;
    END IF;
    
    adherence_rate := (taken_doses::DECIMAL / total_doses::DECIMAL) * 100;
    RETURN ROUND(adherence_rate, 2);
END;
$$ LANGUAGE plpgsql;

-- Function to update health records summary
CREATE OR REPLACE FUNCTION update_health_summary(p_patient_id INTEGER)
RETURNS VOID AS $$
DECLARE
    consultation_count INTEGER;
    medication_count INTEGER;
    prescription_count INTEGER;
    last_consultation TIMESTAMP WITH TIME ZONE;
    last_prescription TIMESTAMP WITH TIME ZONE;
    last_chat TIMESTAMP WITH TIME ZONE;
    adherence_7days DECIMAL(5,2);
    adherence_30days DECIMAL(5,2);
BEGIN
    -- Count consultations
    SELECT COUNT(*), MAX(consultation_date) INTO consultation_count, last_consultation
    FROM consultations WHERE patient_id = p_patient_id;
    
    -- Count medications
    SELECT COUNT(*) INTO medication_count
    FROM medications m
    JOIN consultations c ON m.consultation_id = c.id
    WHERE c.patient_id = p_patient_id AND m.active = true;
    
    -- Count prescriptions
    SELECT COUNT(*), MAX(processed_at) INTO prescription_count, last_prescription
    FROM prescription_scans WHERE patient_id = p_patient_id;
    
    -- Last chat
    SELECT MAX(created_at) INTO last_chat
    FROM chat_history WHERE patient_id = p_patient_id;
    
    -- Calculate adherence rates
    adherence_7days := calculate_medication_adherence(p_patient_id, 7);
    adherence_30days := calculate_medication_adherence(p_patient_id, 30);
    
    -- Insert or update summary
    INSERT INTO health_records_summary (
        patient_id, total_consultations, total_medications, total_prescriptions_scanned,
        last_consultation_date, last_prescription_date, last_chat_date,
        medication_adherence_7days, medication_adherence_30days
    ) VALUES (
        p_patient_id, consultation_count, medication_count, prescription_count,
        last_consultation, last_prescription, last_chat,
        adherence_7days, adherence_30days
    )
    ON CONFLICT (patient_id) DO UPDATE SET
        total_consultations = EXCLUDED.total_consultations,
        total_medications = EXCLUDED.total_medications,
        total_prescriptions_scanned = EXCLUDED.total_prescriptions_scanned,
        last_consultation_date = EXCLUDED.last_consultation_date,
        last_prescription_date = EXCLUDED.last_prescription_date,
        last_chat_date = EXCLUDED.last_chat_date,
        medication_adherence_7days = EXCLUDED.medication_adherence_7days,
        medication_adherence_30days = EXCLUDED.medication_adherence_30days,
        updated_at = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Insert default system configuration
INSERT INTO system_config (config_key, config_value, config_type, description) VALUES
('app_version', '1.0.0', 'string', 'Current application version'),
('default_language', 'en', 'string', 'Default application language'),
('emergency_phone', '108', 'string', 'Emergency services phone number'),
('sms_enabled', 'true', 'boolean', 'Enable SMS notifications'),
('max_daily_sms', '50', 'integer', 'Maximum SMS messages per patient per day'),
('prescription_retention_days', '365', 'integer', 'Days to retain prescription images'),
('chat_history_retention_days', '90', 'integer', 'Days to retain chat history'),
('ai_confidence_threshold', '0.7', 'decimal', 'Minimum AI confidence for recommendations')
ON CONFLICT (config_key) DO NOTHING;

-- Create views for common queries
CREATE OR REPLACE VIEW patient_medication_view AS
SELECT 
    p.id as patient_id,
    p.name as patient_name,
    p.phone,
    m.id as medication_id,
    m.medicine_name,
    m.dosage,
    m.frequency,
    m.duration,
    m.prescribed_date,
    m.active,
    c.consultation_date,
    c.diagnosis
FROM patients p
JOIN consultations c ON p.id = c.patient_id
JOIN medications m ON c.id = m.consultation_id
WHERE p.active = true;

CREATE OR REPLACE VIEW active_reminders_view AS
SELECT 
    sr.id as reminder_id,
    sr.patient_id,
    p.name as patient_name,
    p.phone,
    sr.medication_id,
    m.medicine_name,
    m.dosage,
    sr.reminder_times,
    sr.start_date,
    sr.end_date,
    sr.status,
    sr.language_code
FROM sms_reminders sr
JOIN patients p ON sr.patient_id = p.id
JOIN medications m ON sr.medication_id = m.id
WHERE sr.active = true 
AND sr.status = 'active'
AND CURRENT_DATE BETWEEN sr.start_date AND sr.end_date;

-- Grant permissions (adjust as needed for your deployment)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
