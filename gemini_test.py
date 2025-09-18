import os
import google.generativeai as genai

# Load API key from environment
api_key = os.getenv("GEMINI_API_KEY")
print("API KEY FOUND?", bool(api_key))

genai.configure(api_key=api_key)

# Use Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

try:
    response = model.generate_content("Give me 3 tips for staying healthy.")
    print("RAW RESPONSE:", response)   # See full object
    print("TEXT RESPONSE:", response.text)  # Extracted text
except Exception as e:
    print("❌ ERROR:", e)
