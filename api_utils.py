"""
API utilities for working with the Claude API.
Contains functions for checking API connectivity and efficient API calls.
"""

import time
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

# This would be imported from your main file
# from app import api_key

class ApiUtils:
    def __init__(self, api_key):
        """Initialize with the API key from the main application"""
        self.api_key = api_key
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def check_connection(self):
        """Test the Claude API connection and return status details"""
        try:
            # Simple short prompt to test connectivity
            test_prompt = "Respond with 'OK' if you can read this message."
            
            # Start timer to measure response time
            start_time = time.time()
            
            # Call the API with a short timeout
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=10,
                messages=[{"role": "user", "content": test_prompt}]
            )
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Check if we got a valid response
            content = response.content[0].text.strip() if response.content else "No content"
            
            # Return success status with details
            return {
                "status": "connected",
                "response_time": f"{response_time:.2f}s",
                "model": "claude-3-5-sonnet-20240620",
                "content": content,
                "message": f"Claude API is responding (in {response_time:.2f}s)"
            }
        
        except Exception as e:
            # Check for specific error types
            error_message = str(e)
            if "timeout" in error_message.lower():
                status = "timeout"
                message = "Claude API connection timed out. The service may be experiencing high load."
            elif "unauthorized" in error_message.lower() or "authentication" in error_message.lower():
                status = "auth_error"
                message = "API key authentication failed. Please check your API key."
            elif "rate limit" in error_message.lower():
                status = "rate_limited"
                message = "Rate limit exceeded. Please try again later."
            else:
                status = "error"
                message = f"Connection error: {error_message}"
            
            return {
                "status": status,
                "message": message,
                "error": error_message
            }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    def call_with_retry(self, prompt, model="claude-3-5-sonnet-20240620", max_tokens=1024, timeout=20):
        """Call Claude API with reduced timeout and retry wait time"""
        try:
            # Use a shorter timeout
            client_with_timeout = anthropic.Anthropic(
                api_key=self.api_key,
                timeout=timeout  # Reduced from default
            )
            
            response = client_with_timeout.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response
        except Exception as e:
            if "timeout" in str(e).lower():
                print(f"API timeout after {timeout}s. Retrying...")
            elif "rate limit" in str(e).lower():
                print("Rate limit hit. Waiting before retry...")
                time.sleep(2)  # Extra wait for rate limits
            raise  # Re-raise for retry mechanism


# HTML Templates for the API check page
API_CHECK_SUCCESS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>API Connection Check</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        .container { max-width: 800px; margin: 0 auto; }
        .success { color: #28a745; }
        .error { color: #dc3545; }
        .info { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .btn { display: inline-block; background: #4CAF50; color: white; text-decoration: none; 
               padding: 10px 15px; margin-top: 20px; border: none; cursor: pointer; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="success">✓ Claude API Connection Successful</h1>
        
        <div class="info">
            <p><strong>Status:</strong> Connected</p>
            <p><strong>Response Time:</strong> {{ result.response_time }}</p>
            <p><strong>Model:</strong> {{ result.model }}</p>
            <p><strong>API Response:</strong> {{ result.content }}</p>
        </div>
        
        <p>The API connection is working properly. You can now use the application to adapt presentations.</p>
        
        <a href="/" class="btn">Back to Home</a>
    </div>
</body>
</html>
"""

API_CHECK_ERROR_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>API Connection Error</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        .container { max-width: 800px; margin: 0 auto; }
        .success { color: #28a745; }
        .error { color: #dc3545; }
        .info { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .troubleshooting { background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .btn { display: inline-block; background: #4CAF50; color: white; text-decoration: none; 
               padding: 10px 15px; margin-top: 20px; border: none; cursor: pointer; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="error">✗ Claude API Connection Failed</h1>
        
        <div class="info">
            <p><strong>Status:</strong> {{ result.status }}</p>
            <p><strong>Message:</strong> {{ result.message }}</p>
        </div>
        
        <div class="troubleshooting">
            <h3>Troubleshooting Steps:</h3>
            <ol>
                <li>Check that your API key is correct and has not expired</li>
                <li>Verify your internet connection is stable</li>
                <li>Ensure you are not hitting rate limits (check usage on your Anthropic dashboard)</li>
                <li>Try again in a few minutes if the service might be experiencing temporary issues</li>
            </ol>
        </div>
        
        <p>You will not be able to adapt presentations until the API connection is restored.</p>
        
        <a href="/check_api" class="btn">Try Again</a>
        <a href="/" class="btn" style="background: #6c757d; margin-left: 10px;">Back to Home</a>
    </div>
</body>
</html>
"""