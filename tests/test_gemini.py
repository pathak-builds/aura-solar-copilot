import google.generativeai as genai

# Replace with your actual Gemini API key
API_KEY = "API Key here"

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

response = model.generate_content("Hello! Tell me a joke.")

print(response.text)