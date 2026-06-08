# test_env.py

from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("API key loaded successfully!")
    print(api_key[:10] + "...")
else:
    print("API key NOT found")