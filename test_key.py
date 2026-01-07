import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env file.")
else:
    # Print masked key for debugging format (first 4 chars)
    print(f"Read Key starting with: {api_key[:4]}...")
    
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content("Say 'Hello' if this works.")
        print(f"API Success! Response: {response.text}")
    except Exception as e:
        print(f"API Failed. Error: {e}")
