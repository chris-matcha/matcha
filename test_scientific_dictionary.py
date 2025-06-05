#!/usr/bin/env python3
"""
Test the Scientific Dictionary system
"""
import os
from dotenv import load_dotenv
from services.adaptations_service import AdaptationsService

load_dotenv()

def test_scientific_dictionary_integration():
    """Test the scientific dictionary integration with adaptations service"""
    print("🧪 Testing Scientific Dictionary Integration")
    print("=" * 60)
    
    # Initialize adaptations service (which loads the dictionary)
    config = {}  # No API key for this test
    adaptations_service = AdaptationsService(config)
    
    # Test scientific terms that should be in the dictionary
    test_terms = [
        ("Fe2O3", "dyslexia"),
        ("CO2", "adhd"), 
        ("DNA", "esl"),
        ("pH", "dyslexia"),
        ("H2O", "adhd"),
        ("NaCl", "esl"),
        ("ATP", "dyslexia"),
        ("RNA", "adhd"),
        ("UV", "esl"),
        ("BMI", "dyslexia")
    ]
    
    dictionary_hits = 0
    total_tests = len(test_terms)
    
    for term, profile in test_terms:
        print(f"\n📝 Testing: '{term}' (profile: {profile})")
        
        try:
            adapted = adaptations_service.adapt_text(term, profile)
            
            if adapted != term:  # Adaptation occurred
                print(f"   ✅ Dictionary hit: '{term}' -> '{adapted}'")
                dictionary_hits += 1
            else:
                print(f"   ⚠️ No adaptation: '{term}' (might need AI or not in dictionary)")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Dictionary Performance:")
    print(f"   Total terms tested: {total_tests}")
    print(f"   Dictionary hits: {dictionary_hits}")
    print(f"   Hit rate: {(dictionary_hits/total_tests)*100:.1f}%")
    
    return dictionary_hits

def test_dictionary_statistics():
    """Test dictionary statistics and management functions"""
    print("\n🧪 Testing Dictionary Statistics")
    print("=" * 60)
    
    config = {}
    adaptations_service = AdaptationsService(config)
    
    # Get dictionary statistics
    stats = adaptations_service.get_dictionary_stats()
    print(f"📊 Dictionary Statistics:")
    print(f"   Total terms: {stats.get('total_terms', 0)}")
    print(f"   Categories: {stats.get('categories', {})}")
    print(f"   Types: {stats.get('types', {})}")
    print(f"   Total usage: {stats.get('total_usage', 0)}")
    
    # Test search functionality
    search_results = adaptations_service.search_scientific_terms("Fe", limit=5)
    print(f"\n🔍 Search results for 'Fe': {len(search_results)} found")
    for result in search_results[:3]:
        print(f"   - {result['term']}: {result['definition']}")
    
    return len(stats.get('categories', {})) > 0

def test_term_suggestions():
    """Test automatic term suggestion from text"""
    print("\n🧪 Testing Term Suggestion")
    print("=" * 60)
    
    config = {}
    adaptations_service = AdaptationsService(config)
    
    # Sample scientific text with potential new terms
    sample_texts = [
        "The reaction between HCl and NaOH produces salt and water.",
        "Mitochondria produce ATP through cellular respiration involving O2.",
        "The pH of blood must remain between 7.35 and 7.45 for proper function.",
        "DNA replication involves enzymes like helicase and polymerase.",
        "Calculate the molarity using the formula: M = n/V where n is moles."
    ]
    
    all_suggestions = set()
    
    for text in sample_texts:
        print(f"\n📄 Analyzing: '{text[:50]}...'")
        suggestions = adaptations_service.suggest_missing_terms(text)
        
        if suggestions:
            print(f"   💡 Suggested terms: {', '.join(suggestions)}")
            all_suggestions.update(suggestions)
        else:
            print(f"   ℹ️ No new terms suggested")
    
    print(f"\n💡 Total unique suggestions: {len(all_suggestions)}")
    print(f"   Terms: {', '.join(sorted(all_suggestions))}")
    
    return len(all_suggestions)

def test_adding_new_terms():
    """Test adding new terms to the dictionary"""
    print("\n🧪 Testing Adding New Terms")
    print("=" * 60)
    
    config = {}
    adaptations_service = AdaptationsService(config)
    
    # Test adding a new term
    new_term_data = {
        "term": "mRNA",
        "category": "biology",
        "type": "abbreviation",
        "adaptations": {
            "dyslexia": "mRNA - messenger RNA, carries genetic info",
            "adhd": "mRNA = Genetic messenger",
            "esl": "mRNA (messenger RNA - carries genetic instructions)"
        },
        "definition": "Messenger RNA, carries genetic information from DNA"
    }
    
    print(f"📝 Adding new term: {new_term_data['term']}")
    
    success = adaptations_service.add_scientific_term(
        new_term_data["term"],
        new_term_data["category"], 
        new_term_data["type"],
        new_term_data["adaptations"],
        new_term_data["definition"]
    )
    
    if success:
        print(f"   ✅ Successfully added '{new_term_data['term']}'")
        
        # Test that the new term works
        adapted = adaptations_service.adapt_text("mRNA", "dyslexia")
        print(f"   🧪 Test adaptation: 'mRNA' -> '{adapted}'")
        
        if adapted != "mRNA":
            print(f"   ✅ New term adaptation working!")
            return True
        else:
            print(f"   ⚠️ New term not being used for adaptation")
            return False
    else:
        print(f"   ❌ Failed to add new term")
        return False

def demonstrate_profile_differences():
    """Demonstrate how different profiles get different adaptations"""
    print("\n🧪 Demonstrating Profile-Specific Adaptations")
    print("=" * 60)
    
    config = {}
    adaptations_service = AdaptationsService(config)
    
    test_terms = ["DNA", "Fe2O3", "pH", "ATP"]
    profiles = ["dyslexia", "adhd", "esl"]
    
    for term in test_terms:
        print(f"\n🧬 Term: '{term}'")
        for profile in profiles:
            adapted = adaptations_service.adapt_text(term, profile)
            print(f"   {profile.upper()}: '{adapted}'")
    
    return True

if __name__ == "__main__":
    print("🚀 Testing Scientific Dictionary System")
    print("=" * 70)
    
    # Run all tests
    integration_hits = test_scientific_dictionary_integration()
    stats_working = test_dictionary_statistics()
    suggestions_count = test_term_suggestions()
    new_term_success = test_adding_new_terms()
    profile_demo = demonstrate_profile_differences()
    
    print("\n" + "=" * 70)
    print("📋 SCIENTIFIC DICTIONARY TEST RESULTS:")
    print(f"   📖 Dictionary integration: {'✅ Working' if integration_hits > 5 else '❌ Issues'} ({integration_hits} hits)")
    print(f"   📊 Statistics system: {'✅ Working' if stats_working else '❌ Failed'}")
    print(f"   💡 Term suggestions: {'✅ Working' if suggestions_count > 0 else '❌ No suggestions'} ({suggestions_count} terms)")
    print(f"   ➕ Adding new terms: {'✅ Working' if new_term_success else '❌ Failed'}")
    print(f"   🎯 Profile differences: {'✅ Working' if profile_demo else '❌ Failed'}")
    
    total_score = sum([
        integration_hits > 5,
        stats_working,
        suggestions_count > 0, 
        new_term_success,
        profile_demo
    ])
    
    print(f"\n🎯 Overall Score: {total_score}/5 systems working")
    
    if total_score >= 4:
        print("🎉 Scientific Dictionary system is working excellently!")
        print("📚 Benefits:")
        print("   • Instant, consistent adaptations for scientific terms")
        print("   • Profile-specific explanations (dyslexia, ADHD, ESL)")
        print("   • Growing database that learns from usage")
        print("   • Automatic detection of new terms to add")
        print("   • Fast lookup without API calls")
    else:
        print("⚠️ Scientific Dictionary system needs attention")