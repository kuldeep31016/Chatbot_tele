"""
Medication reminder service with SMS notifications and scheduling.
Handles automated reminders for medication adherence.
"""

import os
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Any
import json

class ReminderService:
    """Service for managing medication reminders and SMS notifications"""
    
    def __init__(self, twilio_service, database=None):
        self.twilio_service = twilio_service
        self.database = database
        
        # In-memory storage for reminders when database is not available
        self.active_reminders = {}
        
    def setup_medication_reminder(self, patient_id: int, medicine_name: str,
                                 dosage: str, frequency: str, phone_number: str,
                                 reminder_times: List[str], start_date: datetime.date,
                                 duration_days: int) -> bool:
        """Setup medication reminder with SMS notifications"""
        
        try:
            # Create medication record in database if available
            if self.database:
                # First create a consultation record if it doesn't exist
                consultation_id = self._ensure_consultation_exists(
                    patient_id, medicine_name, frequency
                )
                
                if consultation_id:
                    # Add medication to database
                    medication_id = self.database.add_medication(
                        consultation_id=consultation_id,
                        medicine_name=medicine_name,
                        dosage=dosage,
                        frequency=frequency,
                        duration=f"{duration_days} days"
                    )
                    
                    if medication_id:
                        print(f"✅ Medication {medicine_name} added to database with ID: {medication_id}")
                    else:
                        print("⚠️ Failed to add medication to database")
                else:
                    print("⚠️ Failed to create consultation record")
            
            # Setup SMS reminders
            reminder_data = {
                'patient_id': patient_id,
                'medicine_name': medicine_name,
                'dosage': dosage,
                'frequency': frequency,
                'phone_number': phone_number,
                'reminder_times': reminder_times,
                'start_date': start_date.isoformat(),
                'end_date': (start_date + timedelta(days=duration_days)).isoformat(),
                'active': True
            }
            
            # Store in memory (for immediate testing)
            reminder_key = f"{patient_id}_{medicine_name}_{start_date.isoformat()}"
            self.active_reminders[reminder_key] = reminder_data
            
            # Send immediate confirmation SMS
            confirmation_sent = self._send_reminder_confirmation(
                phone_number, medicine_name, dosage, reminder_times, duration_days
            )
            
            if confirmation_sent:
                print(f"✅ Reminder setup successful for {medicine_name}")
                return True
            else:
                print(f"⚠️ Reminder setup completed but confirmation SMS failed")
                return True  # Still consider successful even if SMS fails
                
        except Exception as e:
            print(f"❌ Failed to setup medication reminder: {e}")
            return False
    
    def _ensure_consultation_exists(self, patient_id: int, medicine_name: str, 
                                  frequency: str) -> Optional[int]:
        """Ensure a consultation record exists for the medication"""
        try:
            if not self.database:
                return None
            
            # Create a consultation record for medication tracking
            consultation_id = self.database.create_consultation(
                patient_id=patient_id,
                symptoms=f"Prescription medication: {medicine_name}",
                diagnosis="Medication management",
                confidence_score=1.0,
                prediction_method="prescription_scan",
                session_data={
                    'source': 'prescription_scanner',
                    'medicine_name': medicine_name,
                    'frequency': frequency
                }
            )
            
            return consultation_id
            
        except Exception as e:
            print(f"Failed to create consultation record: {e}")
            return None
    
    def _send_reminder_confirmation(self, phone_number: str, medicine_name: str,
                                  dosage: str, reminder_times: List[str],
                                  duration_days: int) -> bool:
        """Send SMS confirmation for reminder setup"""
        
        times_str = ', '.join(reminder_times)
        
        message = f"""🏥 Medication Reminder Setup Complete!

💊 Medicine: {medicine_name}
📏 Dosage: {dosage}
⏰ Reminder Times: {times_str}
📅 Duration: {duration_days} days

You will receive SMS reminders at the scheduled times.

Stay healthy! 💙
- AI Health Assistant"""
        
        return self.twilio_service.send_sms(phone_number, message)
    
    def send_immediate_reminder(self, phone_number: str, medicine_name: str,
                              dosage: str) -> bool:
        """Send immediate medication reminder SMS"""
        
        message = f"""⏰ Medication Reminder

Time to take your medicine:
💊 {medicine_name}
📏 {dosage}

Please take your medication as prescribed.

Take care! 💙
- AI Health Assistant"""
        
        return self.twilio_service.send_sms(phone_number, message)
    
    def get_active_reminders(self, patient_id: int) -> List[Dict[str, Any]]:
        """Get all active reminders for a patient"""
        
        active_reminders = []
        
        # Get from database if available
        if self.database:
            try:
                medications = self.database.get_patient_medications(patient_id)
                for med in medications:
                    active_reminders.append({
                        'medicine_name': med['medicine_name'],
                        'dosage': med['dosage'],
                        'frequency': med['frequency'],
                        'duration': med['duration'],
                        'prescribed_date': med['prescribed_date'],
                        'source': 'database'
                    })
            except Exception as e:
                print(f"Failed to get reminders from database: {e}")
        
        # Get from memory storage
        for key, reminder in self.active_reminders.items():
            if reminder['patient_id'] == patient_id and reminder['active']:
                active_reminders.append({
                    'medicine_name': reminder['medicine_name'],
                    'dosage': reminder['dosage'],
                    'frequency': reminder['frequency'],
                    'reminder_times': reminder['reminder_times'],
                    'start_date': reminder['start_date'],
                    'end_date': reminder['end_date'],
                    'source': 'memory'
                })
        
        return active_reminders
    
    def process_scheduled_reminders(self) -> Dict[str, int]:
        """Process and send scheduled reminders (to be called by scheduler)"""
        
        current_time = datetime.now().time()
        current_date = datetime.now().date()
        
        sent_count = 0
        failed_count = 0
        
        for key, reminder in self.active_reminders.items():
            if not reminder['active']:
                continue
            
            # Check if reminder is still valid (within duration)
            end_date = datetime.fromisoformat(reminder['end_date']).date()
            if current_date > end_date:
                reminder['active'] = False
                continue
            
            # Check if current time matches any reminder time
            for reminder_time_str in reminder['reminder_times']:
                try:
                    reminder_time = time.fromisoformat(reminder_time_str)
                    
                    # Check if current time is within 5 minutes of reminder time
                    current_minutes = current_time.hour * 60 + current_time.minute
                    reminder_minutes = reminder_time.hour * 60 + reminder_time.minute
                    
                    if abs(current_minutes - reminder_minutes) <= 5:
                        # Send reminder
                        success = self.send_immediate_reminder(
                            reminder['phone_number'],
                            reminder['medicine_name'],
                            reminder['dosage']
                        )
                        
                        if success:
                            sent_count += 1
                        else:
                            failed_count += 1
                        
                        break  # Only send one reminder per medicine per check
                        
                except Exception as e:
                    print(f"Failed to process reminder {key}: {e}")
                    failed_count += 1
        
        return {
            'sent': sent_count,
            'failed': failed_count,
            'processed_time': datetime.now().isoformat()
        }
    
    def cancel_reminder(self, patient_id: int, medicine_name: str) -> bool:
        """Cancel medication reminder"""
        
        try:
            # Cancel in memory storage
            for key, reminder in self.active_reminders.items():
                if (reminder['patient_id'] == patient_id and 
                    reminder['medicine_name'].lower() == medicine_name.lower()):
                    reminder['active'] = False
                    
                    # Send cancellation SMS
                    phone_number = reminder['phone_number']
                    cancellation_message = f"""📱 Reminder Cancelled

Medication reminders for {medicine_name} have been cancelled.

If you need to restart reminders, please use the app.

- AI Health Assistant"""
                    
                    self.twilio_service.send_sms(phone_number, cancellation_message)
                    return True
            
            return False
            
        except Exception as e:
            print(f"Failed to cancel reminder: {e}")
            return False
    
    def get_reminder_statistics(self, patient_id: int) -> Dict[str, Any]:
        """Get reminder statistics for a patient"""
        
        stats = {
            'total_reminders': 0,
            'active_reminders': 0,
            'medicines_count': 0,
            'next_reminder': None
        }
        
        medicines = set()
        next_reminder_time = None
        
        for key, reminder in self.active_reminders.items():
            if reminder['patient_id'] == patient_id:
                stats['total_reminders'] += 1
                medicines.add(reminder['medicine_name'])
                
                if reminder['active']:
                    stats['active_reminders'] += 1
                    
                    # Find next reminder time
                    for time_str in reminder['reminder_times']:
                        try:
                            reminder_time = datetime.strptime(time_str, '%H:%M').time()
                            current_time = datetime.now().time()
                            
                            # Create datetime for comparison
                            today = datetime.now().date()
                            reminder_datetime = datetime.combine(today, reminder_time)
                            
                            if reminder_datetime.time() > current_time:
                                if not next_reminder_time or reminder_datetime < next_reminder_time:
                                    next_reminder_time = reminder_datetime
                        except:
                            continue
        
        stats['medicines_count'] = len(medicines)
        if next_reminder_time:
            stats['next_reminder'] = next_reminder_time.strftime('%H:%M')
        
        return stats
    
    def send_weekly_adherence_report(self, patient_id: int, phone_number: str) -> bool:
        """Send weekly medication adherence report"""
        
        try:
            if self.database:
                # Get adherence stats from database
                adherence_stats = self.database.get_adherence_stats(patient_id, days=7)
                
                if adherence_stats and adherence_stats['total_doses'] > 0:
                    adherence_percentage = adherence_stats['adherence_percentage']
                    taken_doses = adherence_stats['taken_doses']
                    total_doses = adherence_stats['total_doses']
                    
                    message = f"""📊 Weekly Medication Report

📈 Adherence: {adherence_percentage}%
✅ Taken: {taken_doses}/{total_doses} doses

"""
                    
                    if adherence_percentage >= 90:
                        message += "🌟 Excellent! Keep up the great work!"
                    elif adherence_percentage >= 75:
                        message += "👍 Good progress! Try to improve consistency."
                    else:
                        message += "⚠️ Needs improvement. Please follow your medication schedule."
                    
                    message += "\n\n- AI Health Assistant"
                    
                    return self.twilio_service.send_sms(phone_number, message)
            
            # Fallback message when database is not available
            message = """📊 Weekly Medication Report

We're tracking your medication reminders to help you stay healthy.

Keep taking your medicines as prescribed!

- AI Health Assistant"""
            
            return self.twilio_service.send_sms(phone_number, message)
            
        except Exception as e:
            print(f"Failed to send adherence report: {e}")
            return False
    
    def export_reminder_data(self, patient_id: int) -> Dict[str, Any]:
        """Export reminder data for backup or analysis"""
        
        patient_reminders = []
        
        for key, reminder in self.active_reminders.items():
            if reminder['patient_id'] == patient_id:
                patient_reminders.append(reminder)
        
        return {
            'patient_id': patient_id,
            'export_date': datetime.now().isoformat(),
            'reminders': patient_reminders,
            'total_count': len(patient_reminders)
        }
    
    def import_reminder_data(self, reminder_data: Dict[str, Any]) -> bool:
        """Import reminder data from backup"""
        
        try:
            patient_id = reminder_data['patient_id']
            
            for reminder in reminder_data['reminders']:
                key = f"{patient_id}_{reminder['medicine_name']}_{reminder['start_date']}"
                self.active_reminders[key] = reminder
            
            return True
            
        except Exception as e:
            print(f"Failed to import reminder data: {e}")
            return False
