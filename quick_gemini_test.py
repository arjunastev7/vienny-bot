from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)
def try_model(name):
    try:
        response = client.models.generate_content(
            model=name,
            contents="Hello"
        )
        print(f"Success {name}: {response.text.strip()[:20]}")
    except Exception as e:
        print(f"Error {name}: {e}")

try_model("gemini-flash-latest")
try_model("gemini-2.0-flash-lite")
