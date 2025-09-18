from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os

# Get your API key (make sure it's set in environment)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="Health Assistant API")


# --- Models for other endpoints ---
from typing import List, Dict

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

class PrescriptionResponse(BaseModel):
    doctor: str
    patient: str
    medicines: List[Dict]

class SymptomRequest(BaseModel):
    symptoms: List[str]
    severity: str
    duration: int
    age: int

class SymptomResponse(BaseModel):
    risk: str
    advice: str
    possible_conditions: List[Dict]

class ReminderRequest(BaseModel):
    user_id: str
    medicine: str
    time: str

class ReminderResponse(BaseModel):
    status: str
    medicine: str
    time: str

class RecordRequest(BaseModel):
    user_id: str
    record: Dict

class RecordResponse(BaseModel):
    status: str

class PurchaseRequest(BaseModel):
    user_id: str
    medicine: str
    quantity: int

class PurchaseResponse(BaseModel):
    status: str
    medicine: str
    quantity: int


# --- Chatbot Endpoint ---
@app.post("/chat", response_model=ChatResponse)
async def chat_with_bot(req: ChatRequest):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful health assistant. Provide symptom checks and basic health advice. Do not replace a doctor."},
                {"role": "user", "content": req.message}
            ]
        )
        reply = response.choices[0].message.content
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Prescription Scanner Endpoint ---
@app.post("/prescription", response_model=PrescriptionResponse)
async def prescription_scanner():
    # TODO: Integrate with your PrescriptionOCR logic
    return PrescriptionResponse(
        doctor="Dr. Singh",
        patient="Aman",
        medicines=[
            {"name": "Paracetamol", "dosage": "500mg", "frequency": "Twice daily"},
            {"name": "Ibuprofen", "dosage": "200mg", "frequency": "Once daily"}
        ]
    )

# --- Symptom Checker Endpoint ---
@app.post("/symptoms", response_model=SymptomResponse)
async def symptom_checker(req: SymptomRequest):
    # TODO: Integrate with your DiagnosisEngine and OpenAI logic
    return SymptomResponse(
        risk="Low",
        advice="Drink fluids and rest",
        possible_conditions=[
            {"condition": "Common Cold", "confidence": 0.8},
            {"condition": "Flu", "confidence": 0.2}
        ]
    )

# --- Medication Reminders Endpoint ---
@app.post("/reminder", response_model=ReminderResponse)
async def medication_reminder(req: ReminderRequest):
    # TODO: Integrate with your ReminderService logic
    return ReminderResponse(
        status="Reminder set",
        medicine=req.medicine,
        time=req.time
    )

# --- Health Records Endpoints ---
@app.post("/records", response_model=RecordResponse)
async def add_health_record(req: RecordRequest):
    # TODO: Save health record to DB
    return RecordResponse(status="Record added")

@app.get("/records")
async def get_health_records(user_id: str):
    # TODO: Fetch health records from DB
    return {"records": []}

# --- Medicine Purchase Endpoint ---
@app.post("/purchase", response_model=PurchaseResponse)
async def medicine_purchase(req: PurchaseRequest):
    # TODO: Integrate with pharmacy/order logic
    return PurchaseResponse(
        status="Order placed",
        medicine=req.medicine,
        quantity=req.quantity
    )

@app.get("/")
async def root():
    return {"message": "Health Assistant API is running. Use /chat, /prescription, /symptoms, /reminder, /records, /purchase endpoints."}
