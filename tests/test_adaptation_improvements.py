#!/usr/bin/env python3
"""
Test script to verify the PDF adaptation improvements
"""
import os
from dotenv import load_dotenv
from services.adaptations_service import AdaptationsService

load_dotenv()

def test_short_text_adaptation():
    """Test that short text (2+ chars) now gets adapted"""
    print("🧪 Testing Short Text Adaptation Improvements")
    print("=" * 60)
    
    # Initialize the adaptations service
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ No API key found")
        return
        
    config = {'anthropic_api_key': api_key}
    adaptations_service = AdaptationsService(config)
    
    # Test with very short text that should now be processed
    short_texts = [
        "Fe2O3",  # Chemical formula
        "CO2",    # Chemical formula  
        "pH = 7", # Scientific notation
        "H2SO4",  # Chemical formula
        "NaCl",   # Chemical formula
        "DNA",    # Abbreviation
        "RNA",    # Abbreviation
        "O2",     # Chemical formula
        "Be",     # Single element
        "Au",     # Single element
    ]
    
    profile = 'dyslexia'
    
    success_count = 0
    for i, text in enumerate(short_texts, 1):
        print(f"\n📝 Test {i}: '{text}'")
        print(f"   Original length: {len(text)} chars")
        
        try:
            adapted = adaptations_service.adapt_text(text, profile)
            print(f"   ✅ Adaptation completed")
            print(f"   Adapted text: '{adapted}'")
            print(f"   Adapted length: {len(adapted)} chars")
            
            # Validate the adaptation
            validation = adaptations_service.validate_adaptation(text, adapted, profile)
            if validation['is_valid']:
                print(f"   ✅ Validation passed")
                success_count += 1
            else:
                print(f"   ⚠️ Validation issues: {validation['issues']}")
                
        except Exception as e:
            print(f"   ❌ Adaptation failed: {e}")
    
    print(f"\n📊 Summary: {success_count}/{len(short_texts)} short texts successfully adapted")
    print(f"🗂️ Cache stats: {adaptations_service.get_cache_stats()}")
    
    return success_count

def test_improved_validation():
    """Test that validation is more lenient now"""
    print("\n🧪 Testing Improved Validation")
    print("=" * 60)
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ No API key found")
        return
        
    config = {'anthropic_api_key': api_key}
    adaptations_service = AdaptationsService(config)
    
    # Test cases for validation improvements
    test_cases = [
        {
            'original': 'Fe2O3',
            'adapted': 'Iron oxide (Fe2O3)',
            'should_pass': True,
            'description': 'Chemical formula expansion'
        },
        {
            'original': 'DNA',
            'adapted': 'DNA (genetic material)',
            'should_pass': True,
            'description': 'Abbreviation explanation'
        },
        {
            'original': 'pH',
            'adapted': 'pH (acid level)',
            'should_pass': True,
            'description': 'Scientific term explanation'
        }
    ]
    
    validation_passes = 0
    for i, case in enumerate(test_cases, 1):
        print(f"\n🔍 Validation Test {i}: {case['description']}")
        print(f"   Original: '{case['original']}'")
        print(f"   Adapted: '{case['adapted']}'")
        
        validation = adaptations_service.validate_adaptation(
            case['original'], case['adapted'], 'dyslexia'
        )
        
        if validation['is_valid'] == case['should_pass']:
            print(f"   ✅ Validation result as expected: {validation['is_valid']}")
            validation_passes += 1
        else:
            print(f"   ❌ Validation unexpected: got {validation['is_valid']}, expected {case['should_pass']}")
            print(f"      Issues: {validation['issues']}")
        
        print(f"   Metrics: {validation['metrics']}")
    
    print(f"\n📊 Validation Summary: {validation_passes}/{len(test_cases)} validation tests passed")
    
    return validation_passes

if __name__ == "__main__":
    print("🚀 Testing PDF Adaptation System Improvements")
    print("=" * 70)
    
    # Test short text adaptation
    short_text_successes = test_short_text_adaptation()
    
    # Test improved validation  
    validation_successes = test_improved_validation()
    
    print("\n" + "=" * 70)
    print("📋 FINAL RESULTS:")
    print(f"   Short text adaptations working: {short_text_successes > 5}")
    print(f"   Improved validation working: {validation_successes >= 2}")
    
    if short_text_successes > 5 and validation_successes >= 2:
        print("   ✅ All improvements working correctly!")
    else:
        print("   ⚠️ Some improvements need attention")