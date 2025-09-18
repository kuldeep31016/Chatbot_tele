import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.chatbot_responses import get_bot_response
from utils.prescription_data import get_prescription_suggestion
from utils.health_checker import assess_health
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Logging setup
logging.basicConfig(level=logging.INFO)

DISCLAIMER = "This is for informational purposes only. Always consult a healthcare professional for serious symptoms."

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Missing message field', 'disclaimer': DISCLAIMER}), 400
    user_message = data['message']
    response = get_bot_response(user_message)
    return jsonify({
        'response': response,
        'timestamp': datetime.now().isoformat(),
        'disclaimer': DISCLAIMER
    })

@app.route('/api/prescription', methods=['POST'])
def prescription():
    data = request.get_json()
    if not data or 'symptoms' not in data or 'age' not in data:
        return jsonify({'error': 'Missing required fields', 'disclaimer': DISCLAIMER}), 400
    result = get_prescription_suggestion(data['symptoms'], data['age'], data.get('medical_history', ''))
    return jsonify({**result, 'disclaimer': DISCLAIMER})

@app.route('/api/health_check', methods=['POST'])
def health_check():
    data = request.get_json()
    if not data or 'symptoms' not in data or 'duration' not in data or 'severity' not in data:
        return jsonify({'error': 'Missing required fields', 'disclaimer': DISCLAIMER}), 400
    result = assess_health(data['symptoms'], data['duration'], data['severity'])
    return jsonify({**result, 'disclaimer': DISCLAIMER})

@app.route('/api/log_symptoms', methods=['POST'])
def log_symptoms():
    data = request.get_json()
    if not data or 'symptoms' not in data:
        return jsonify({'error': 'Missing symptoms field', 'disclaimer': DISCLAIMER}), 400
    # Simulate saving symptoms
    logging.info(f"Logged symptoms: {data['symptoms']}")
    return jsonify({'status': 'success', 'logged': data['symptoms'], 'disclaimer': DISCLAIMER})

@app.route('/api/set_reminder', methods=['POST'])
def set_reminder():
    data = request.get_json()
    if not data or 'medicine' not in data or 'time' not in data:
        return jsonify({'error': 'Missing medicine or time field', 'disclaimer': DISCLAIMER}), 400
    # Simulate setting reminder
    logging.info(f"Set reminder for {data['medicine']} at {data['time']}")
    return jsonify({'status': 'reminder set', 'medicine': data['medicine'], 'time': data['time'], 'disclaimer': DISCLAIMER})

@app.route('/api/emergency', methods=['GET'])
def emergency():
    # Sample emergency contacts
    contacts = {
        'ambulance': '108',
        'police': '100',
        'fire': '101',
        'nearest_hospital': 'City Hospital, Main Road'
    }
    return jsonify({'contacts': contacts, 'disclaimer': DISCLAIMER})

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found', 'disclaimer': DISCLAIMER}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error', 'disclaimer': DISCLAIMER}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
