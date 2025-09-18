def assess_health(symptoms, duration, severity):
    risk = 'low'
    urgent_care = False
    recommendations = ['rest', 'hydration']
    consult = 'Not required unless symptoms worsen.'
    if severity == 'severe' or 'chest pain' in ' '.join(symptoms).lower():
        risk = 'high'
        urgent_care = True
        consult = 'Immediate doctor consultation recommended.'
    elif severity == 'moderate':
        risk = 'medium'
        consult = 'Doctor consultation recommended.'
    return {
        'risk_level': risk,
        'recommendations': recommendations,
        'urgent_care': urgent_care,
        'doctor_consultation': consult
    }
