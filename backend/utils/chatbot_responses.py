def get_bot_response(message):
    message = message.lower()
    if 'fever' in message:
        return 'Fever can be caused by many things. Stay hydrated and monitor your temperature. If it persists, consult a doctor.'
    if 'headache' in message:
        return 'Headaches are common. Rest, drink water, and avoid screen time. If severe, seek medical advice.'
    if 'covid' in message:
        return 'For COVID-19 concerns, follow local guidelines and consult a healthcare provider.'
    if 'pain' in message:
        return 'Pain should not be ignored. If it is severe or persistent, consult a healthcare professional.'
    return 'I am here to help with health questions. For serious symptoms, please consult a doctor.'
