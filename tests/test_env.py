
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("CLAUDE_API_KEY")
print(f"API Key loaded: {api_key[:8]}..." if api_key and len(api_key) > 8 else "No API key found")

