import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

# Use environment variable for API key
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    
client = anthropic.Anthropic(api_key=api_key)

try:
    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=100,
        messages=[{"role": "user", "content": "Hello, Claude!"}]
    )
    print("Success! Response:", response.content[0].text)
except Exception as e:
    print("Error:", e)