"""
Patch for anthropic library compatibility issues with httpx
"""

def patch_anthropic_httpx():
    """
    Monkey patch to fix the 'proxies' parameter issue in anthropic library
    when using older versions with newer httpx
    """
    try:
        import httpx
        
        # Store the original Client class
        original_client = httpx.Client
        
        # Create a wrapper that filters out the 'proxies' parameter
        class PatchedClient(original_client):
            def __init__(self, *args, **kwargs):
                # Remove 'proxies' parameter if it exists
                if 'proxies' in kwargs:
                    print("Removing unsupported 'proxies' parameter from httpx.Client")
                    kwargs.pop('proxies')
                
                # Also remove other potentially problematic parameters
                problematic_params = ['proxies', 'proxy', 'mounts']
                for param in problematic_params:
                    if param in kwargs:
                        kwargs.pop(param)
                
                # Call the original constructor
                super().__init__(*args, **kwargs)
        
        # Replace the Client class with our patched version
        httpx.Client = PatchedClient
        print("Successfully patched httpx.Client for anthropic compatibility")
        
    except Exception as e:
        print(f"Warning: Could not patch httpx for anthropic compatibility: {e}")

# Apply the patch when this module is imported
patch_anthropic_httpx()