import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model_name = "gemini-2.0-flash"
print(f"Testing {model_name}...")
try:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Hi")
    print(f"Success! Response: {response.text}")
except Exception as e:
    print(f"Failed {model_name}: {e}")

model_name_2 = "models/gemini-2.0-flash"
print(f"Testing {model_name_2}...")
try:
    model = genai.GenerativeModel(model_name_2)
    response = model.generate_content("Hi")
    print(f"Success! Response: {response.text}")
except Exception as e:
    print(f"Failed {model_name_2}: {e}")
