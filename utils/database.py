"""
Database utilities for the telemedicine application.
Handles patient records, consultation history, and medication tracking.
"""

import os
import json
from datetime import datetime, date
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Optional, Any


class MedicalDatabase:
    def __init__(self):
        self.connection_string = os.getenv('DATABASE_URL')
        if not self.connection_string:
            raise Exception("DATABASE_URL environment variable not set")
        self._connection_healthy = True

    def _check_connection_health(self):
        """Check if database connection is healthy"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
            self._connection_healthy = True
            return True
        except Exception:
            self._connection_healthy = False
            return False

    def get_connection(self):
        """Get a database connection"""
        return psycopg2.connect(self.connection_string)

    # ---------------- Patient management ----------------
    def create_patient(self, name: str, age: int, gender: str,
                       email: Optional[str] = None, phone: Optional[str] = None) -> int:
        """Create a new patient record and return patient ID"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO patients (name, age, gender, email, phone)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (name, age, gender, email, phone))
                return cursor.fetchone()[0]

    def get_patient(self, patient_id: int) -> Optional[Dict]:
        """Get patient information by ID"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
                result = cursor.fetchone()
                return dict(result) if result else None

    def find_patient_by_email(self, email: str) -> Optional[Dict]:
        """Find patient by email address"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM patients WHERE email = %s", (email,))
                result = cursor.fetchone()
                return dict(result) if result else None

    # ---------------- Consultation management ----------------
    def create_consultation(self, patient_id: int, symptoms: str, diagnosis: str,
                            confidence_score: float, prediction_method: str,
                            session_data: Optional[Dict] = None) -> int:
        """Create a new consultation record"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO consultations 
                    (patient_id, symptoms, diagnosis, confidence_score, prediction_method, session_data)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (patient_id, symptoms, diagnosis, confidence_score,
                      prediction_method, json.dumps(session_data) if session_data else None))
                return cursor.fetchone()[0]

    def get_patient_consultations(self, patient_id: int, limit: int = 10) -> List[Dict]:
        """Get consultation history for a patient"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT c.*, p.name as patient_name
                    FROM consultations c
                    JOIN patients p ON c.patient_id = p.id
                    WHERE c.patient_id = %s
                    ORDER BY c.consultation_date DESC
                    LIMIT %s
                """, (patient_id, limit))
                return [dict(row) for row in cursor.fetchall()]

    def get_consultation(self, consultation_id: int) -> Optional[Dict]:
        """Get consultation details by ID"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT c.*, p.name as patient_name, p.age, p.gender
                    FROM consultations c
                    JOIN patients p ON c.patient_id = p.id
                    WHERE c.id = %s
                """, (consultation_id,))
                result = cursor.fetchone()
                return dict(result) if result else None

    # ---------------- Medication management ----------------
    def add_medication(self, consultation_id: int, medicine_name: str,
                       dosage: str, frequency: str, duration: str,
                       side_effects: Optional[str] = None) -> int:
        """Add a prescribed medication to a consultation"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO medications 
                    (consultation_id, medicine_name, dosage, frequency, duration, side_effects)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (consultation_id, medicine_name, dosage, frequency, duration, side_effects))
                return cursor.fetchone()[0]

    def get_consultation_medications(self, consultation_id: int) -> List[Dict]:
        """Get all medications for a consultation"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM medications 
                    WHERE consultation_id = %s
                    ORDER BY prescribed_date DESC
                """, (consultation_id,))
                return [dict(row) for row in cursor.fetchall()]

    def get_patient_medications(self, patient_id: int) -> List[Dict]:
        """Get all medications prescribed to a patient"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT m.*, c.diagnosis, c.consultation_date
                    FROM medications m
                    JOIN consultations c ON m.consultation_id = c.id
                    WHERE c.patient_id = %s
                    ORDER BY m.prescribed_date DESC
                """, (patient_id,))
                return [dict(row) for row in cursor.fetchall()]

    # ---------------- Medication adherence tracking ----------------
    def record_medication_taken(self, medication_id: int, patient_id: int,
                                taken_date: date, taken: bool = True,
                                notes: Optional[str] = None) -> int:
        """Record when a patient takes medication"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id FROM medication_adherence 
                    WHERE medication_id = %s AND patient_id = %s AND taken_date = %s
                """, (medication_id, patient_id, taken_date))

                existing = cursor.fetchone()
                if existing:
                    cursor.execute("""
                        UPDATE medication_adherence 
                        SET taken = %s, notes = %s 
                        WHERE id = %s
                        RETURNING id
                    """, (taken, notes, existing[0]))
                else:
                    cursor.execute("""
                        INSERT INTO medication_adherence 
                        (medication_id, patient_id, taken_date, taken, notes)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                    """, (medication_id, patient_id, taken_date, taken, notes))

                result = cursor.fetchone()
                return result[0] if result else 0

    def get_adherence_stats(self, patient_id: int, days: int = 30) -> Dict:
        """Get medication adherence statistics for a patient"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_doses,
                        SUM(CASE WHEN taken THEN 1 ELSE 0 END) as taken_doses,
                        ROUND(AVG(CASE WHEN taken THEN 1.0 ELSE 0.0 END) * 100, 1) as adherence_percentage
                    FROM medication_adherence 
                    WHERE patient_id = %s 
                    AND taken_date >= CURRENT_DATE - make_interval(days => %s)
                """, (patient_id, days))
                result = cursor.fetchone()
                return dict(result) if result else {
                    'total_doses': 0,
                    'taken_doses': 0,
                    'adherence_percentage': 0
                }

    # ---------------- Analytics and reporting ----------------
    def get_diagnosis_statistics(self, days: int = 30) -> List[Dict]:
        """Get diagnosis statistics for the last N days"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        diagnosis,
                        COUNT(*) as count,
                        AVG(confidence_score) as avg_confidence,
                        prediction_method
                    FROM consultations 
                    WHERE consultation_date >= CURRENT_DATE - make_interval(days => %s)
                    GROUP BY diagnosis, prediction_method
                    ORDER BY count DESC
                """, (days,))
                return [dict(row) for row in cursor.fetchall()]

    def get_most_common_symptoms(self, limit: int = 10) -> List[Dict]:
        """Get the most commonly reported symptoms"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        unnest(string_to_array(lower(symptoms), ',')) as symptom,
                        COUNT(*) as frequency
                    FROM consultations
                    WHERE consultation_date >= CURRENT_DATE - INTERVAL '90 days'
                    GROUP BY symptom
                    HAVING LENGTH(TRIM(unnest(string_to_array(lower(symptoms), ',')))) > 2
                    ORDER BY frequency DESC
                    LIMIT %s
                """, (limit,))
                return [dict(row) for row in cursor.fetchall()]

    def close(self):
        """Close database connection"""
        pass  # Connections auto-close with context managers


# ✅ Provide a global `db` instance so other modules can import it
try:
    db = MedicalDatabase()
except Exception as e:
    db = None
    print("❌ Could not initialize database:", e)
