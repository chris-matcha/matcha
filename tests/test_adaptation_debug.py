#!/usr/bin/env python3
"""
Debug script to test if PDF content adaptation is actually happening
"""
import os
import sys
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import services
from services import AdaptationsService, LearningProfilesService

def test_adaptation_service():
    """Test the adaptation service to see if it's actually adapting text"""
    
    # Configuration
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        return
    
    config = {
        'anthropic_api_key': api_key
    }
    
    # Initialize services
    adaptations_service = AdaptationsService(config)
    profiles_service = LearningProfilesService(config)
    
    print("=== ADAPTATION SERVICE DEBUG TEST ===")
    print()
    
    # Test 1: Check if API client is initialized
    print("1. Checking API client initialization:")
    print(f"   Has client: {adaptations_service.client is not None}")
    print(f"   API key present: {config.get('anthropic_api_key') is not None}")
    print()
    
    # Test 2: Test readability metrics calculation
    test_text = "This is a complex sentence with difficult vocabulary that requires substantial adaptation for students who have learning difficulties."
    print("2. Testing readability metrics:")
    print(f"   Original text: {test_text}")
    metrics = adaptations_service.calculate_readability_metrics(test_text)
    print(f"   Metrics: {metrics}")
    print()
    
    # Test 3: Check if adaptation is needed
    print("3. Testing if adaptation is needed:")
    for profile in ['dyslexia', 'esl', 'adhd']:
        needs_adaptation = profiles_service.needs_adaptation(test_text, profile, metrics)
        print(f"   Profile '{profile}': Needs adaptation = {needs_adaptation}")
    print()
    
    # Test 4: Test direct text adaptation
    print("4. Testing direct text adaptation:")
    for profile in ['dyslexia', 'esl', 'adhd']:
        print(f"   Testing profile: {profile}")
        try:
            adapted_text = adaptations_service.adapt_text(test_text, profile)
            print(f"   Original:  {test_text}")
            print(f"   Adapted:   {adapted_text}")
            print(f"   Changed:   {adapted_text != test_text}")
            print()
        except Exception as e:
            print(f"   ERROR adapting text: {str(e)}")
            print()
    
    # Test 5: Test page adaptation (simulating PDF content)
    print("5. Testing page adaptation (PDF simulation):")
    page_content = {
        'page_number': 1,
        'text': test_text,
        'images': []
    }
    
    for profile in ['dyslexia', 'esl', 'adhd']:
        print(f"   Testing profile: {profile}")
        try:
            adapted_page = adaptations_service._adapt_page(page_content, profile, force_adaptation=True)
            original_text = page_content['text']
            adapted_text = adapted_page['text']
            print(f"   Original:  {original_text}")
            print(f"   Adapted:   {adapted_text}")
            print(f"   Changed:   {adapted_text != original_text}")
            print()
        except Exception as e:
            print(f"   ERROR adapting page: {str(e)}")
            print()
    
    # Test 6: Test cache statistics
    print("6. Cache statistics:")
    cache_stats = adaptations_service.get_cache_stats()
    print(f"   Cache stats: {cache_stats}")
    print()
    
    # Test 7: Test rule-based adaptation (without AI)
    print("7. Testing rule-based adaptation (fallback mode):")
    service_no_api = AdaptationsService({})  # No API key
    print(f"   Has client: {service_no_api.client is not None}")
    
    for profile in ['dyslexia', 'esl', 'adhd']:
        try:
            adapted_text = service_no_api.adapt_text(test_text, profile)
            print(f"   Profile '{profile}' (rules): {adapted_text != test_text} (changed)")
        except Exception as e:
            print(f"   ERROR with rules for '{profile}': {str(e)}")
    print()

if __name__ == "__main__":
    test_adaptation_service()