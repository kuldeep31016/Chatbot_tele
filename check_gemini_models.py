import google.generativeai as genai
genai.configure(api_key="YOUR_API_KEY")  # Replace with your actual key
print([m.name for m in genai.list_models()])