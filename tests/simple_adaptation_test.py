#!/usr/bin/env python3
"""
Simple test to isolate where PDF adaptation is failing
"""
import os
from dotenv import load_dotenv
from services.adaptations_service import AdaptationsService

load_dotenv()

def test_text_adaptation():
    """Test just the text adaptation component"""
    print("🧪 Testing Text Adaptation Only")
    print("=" * 50)
    
    # Initialize the adaptations service
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ No API key found")
        return
        
    config = {'anthropic_api_key': api_key}
    adaptations_service = AdaptationsService(config)
    
    # Test with sample text that would be found in a PDF
    test_texts = [
        "Total mass of reactants = total mass of products",
        "Iron ore contains iron oxide (Fe2O3). Write a balanced equation for the reaction of iron oxide with carbon monoxide.",
        "Which of the following is an example of a metal oxide?",
        "Potassium, sodium, lithium, calcium, magnesium, zinc, iron and copper can be put in order of their reactivity."
    ]
    
    profile = 'adhd'
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 Test {i}: '{text[:50]}...'")
        print(f"   Original length: {len(text)} chars")
        
        try:
            adapted = adaptations_service.adapt_text(text, profile)
            print(f"   ✅ Adaptation successful!")
            print(f"   Adapted length: {len(adapted)} chars")
            print(f"   Adapted text: '{adapted[:100]}...'")
            
            # Check if it's actually different
            if adapted == text:
                print(f"   ⚠️  WARNING: Adapted text is identical to original")
            elif adapted.strip() in ['[ADHD]', '[Adapted: ADHD]', f'[{profile.upper()}]']:
                print(f"   ❌ ERROR: Got placeholder instead of adapted text")
            else:
                print(f"   ✅ Text was successfully adapted")
                
        except Exception as e:
            print(f"   ❌ Adaptation failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Test cache stats
    print(f"\n📊 Cache stats: {adaptations_service.get_cache_stats()}")

if __name__ == "__main__":
    test_text_adaptation()