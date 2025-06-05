#!/usr/bin/env python3
"""
Test script to verify adaptation service is working properly with error handling
"""
import sys
sys.path.append('.')

import os
from dotenv import load_dotenv
from services.adaptations_service import AdaptationsService
import json

# Load environment variables
load_dotenv()


def test_adaptation_service():
    """Test the enhanced adaptation service with better error handling"""
    print("🔧 Testing Enhanced Adaptation Service")
    print("=" * 60)
    
    # Initialize service
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        return
    
    config = {
        'anthropic_api_key': api_key
    }
    
    service = AdaptationsService(config)
    
    # Test texts
    test_texts = [
        {
            'profile': 'dyslexia',
            'text': "The implementation of complex technological solutions requires careful consideration of multiple interdependent factors and systematic analysis of potential outcomes."
        },
        {
            'profile': 'esl',
            'text': "Subsequently, the ramifications of these decisions manifest themselves through various channels, necessitating continuous monitoring and adjustment."
        },
        {
            'profile': 'adhd', 
            'text': "This comprehensive document outlines the various procedures and protocols that must be followed when implementing new systems, including but not limited to the following important considerations that should be taken into account during the planning phase."
        }
    ]
    
    print("\n📋 Running Adaptation Tests:\n")
    
    results = []
    for test in test_texts:
        profile = test['profile']
        text = test['text']
        
        print(f"Testing {profile.upper()} adaptation:")
        print(f"Original ({len(text)} chars): {text[:80]}...")
        
        try:
            # Test adaptation
            adapted = service.adapt_text(text, profile)
            
            # Validate adaptation
            validation = service.validate_adaptation(text, adapted, profile)
            
            print(f"Adapted ({len(adapted)} chars): {adapted[:80]}...")
            print(f"Valid: {validation['is_valid']}")
            
            if validation['metrics']:
                print(f"Metrics: Words {validation['metrics']['original_word_count']} -> {validation['metrics']['adapted_word_count']}")
                print(f"         Avg word length: {validation['metrics'].get('original_avg_word_length', 0):.1f} -> {validation['metrics'].get('adapted_avg_word_length', 0):.1f}")
            
            if validation['issues']:
                print(f"Issues: {', '.join(validation['issues'])}")
            
            results.append({
                'profile': profile,
                'success': validation['is_valid'],
                'validation': validation
            })
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            results.append({
                'profile': profile,
                'success': False,
                'error': str(e)
            })
        
        print("-" * 60)
    
    # Test the built-in test method
    print("\n🧪 Running Built-in Test:")
    for profile in ['dyslexia', 'esl', 'adhd']:
        test_result = service.test_adaptation(profile)
        print(f"\n{profile.upper()}: {'✅ Success' if test_result['success'] else '❌ Failed'}")
        if not test_result['success'] and 'error' in test_result:
            print(f"  Error: {test_result['error']}")
        elif test_result['success']:
            print(f"  Original: {test_result['original'][:60]}...")
            print(f"  Adapted:  {test_result['adapted'][:60]}...")
    
    # Print cache statistics
    print("\n📊 Cache Statistics:")
    cache_stats = service.get_cache_stats()
    print(json.dumps(cache_stats, indent=2))
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    print(f"\n✅ Summary: {successful}/{len(results)} adaptations successful")
    
    # Check for common issues
    print("\n⚠️  Common Issues to Check:")
    print("1. Ensure ANTHROPIC_API_KEY is set in environment or .env file")
    print("2. Check that the API key has sufficient credits")
    print("3. Verify network connectivity to Anthropic API")
    print("4. Look for rate limiting errors in logs")


if __name__ == "__main__":
    test_adaptation_service()