"""
Example: Using Matcha Services Independently

This example demonstrates how each service can be used in isolation,
showing the benefits of the service-oriented architecture.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import (
    LearningProfilesService,
    AdaptationsService,
    TranslationsService,
    AssessmentsService,
    FormatsService
)


def example_1_profile_exploration():
    """Example 1: Explore learning profiles"""
    print("=== Example 1: Learning Profiles ===")
    
    profiles_service = LearningProfilesService({})
    
    # List all profiles
    profiles = profiles_service.list_profiles()
    for profile in profiles:
        print(f"\nProfile: {profile['name']} ({profile['id']})")
        print(f"Description: {profile['description']}")
        
        # Get detailed settings
        thresholds = profiles_service.get_thresholds(profile['id'])
        print(f"Flesch Ease Threshold: {thresholds.get('flesch_ease', 'N/A')}")
        print(f"Grade Level Maximum: {thresholds.get('grade_level', 'N/A')}")


def example_2_content_assessment():
    """Example 2: Assess content readability"""
    print("\n=== Example 2: Content Assessment ===")
    
    adaptations_service = AdaptationsService({})
    assessments_service = AssessmentsService({})
    
    # Sample text
    complex_text = """
    The implementation of sophisticated algorithmic solutions necessitates 
    a comprehensive understanding of computational complexity theory and 
    its practical applications in modern software engineering paradigms.
    """
    
    simple_text = """
    To write good code, you need to understand how computers work.
    Learn the basics first. Then practice every day.
    """
    
    # Calculate metrics
    complex_metrics = adaptations_service.calculate_readability_metrics(complex_text)
    simple_metrics = adaptations_service.calculate_readability_metrics(simple_text)
    
    print("\nComplex Text Metrics:")
    print(f"  Flesch Ease: {complex_metrics['flesch_ease']:.1f}")
    print(f"  Grade Level: {complex_metrics['grade_level']:.1f}")
    
    print("\nSimple Text Metrics:")
    print(f"  Flesch Ease: {simple_metrics['flesch_ease']:.1f}")
    print(f"  Grade Level: {simple_metrics['grade_level']:.1f}")
    
    # Assess against profiles
    content = {'pages': [{'text': complex_text}]}
    assessment = assessments_service.assess_content(content)
    
    print("\nProfile Suitability for Complex Text:")
    for profile_id, suitability in assessment['profile_suitability'].items():
        print(f"  {profile_id}: {suitability['overall_score']:.0f}% - {suitability['recommendation']}")


def example_3_text_adaptation():
    """Example 3: Adapt text for different profiles"""
    print("\n=== Example 3: Text Adaptation ===")
    
    adaptations_service = AdaptationsService({})
    
    original_text = """
    Subsequently, the utilization of advanced methodologies will facilitate 
    enhanced comprehension of the subject matter, thereby demonstrating 
    the efficacy of our pedagogical approach.
    """
    
    print(f"Original: {original_text.strip()}")
    
    # Adapt for each profile (using rule-based since no API key)
    for profile_id in ['dyslexia', 'adhd', 'esl']:
        adapted = adaptations_service._adapt_text_rules(original_text, profile_id)
        print(f"\nAdapted for {profile_id}:")
        print(f"  {adapted.strip()}")


def example_4_language_support():
    """Example 4: Check translation support"""
    print("\n=== Example 4: Translation Support ===")
    
    translations_service = TranslationsService({})
    
    # List supported languages
    languages = translations_service.get_supported_languages()
    print("Supported Languages:")
    for i, lang in enumerate(languages):
        print(f"  {i+1}. {lang['name']} ({lang['code']})")
    
    # Example translation (will show placeholder without API key)
    sample_text = "Welcome to our learning platform!"
    for lang_code in ['spanish', 'french', 'chinese']:
        translated = translations_service.translate_text(sample_text, lang_code)
        print(f"\n{lang_code.title()}: {translated}")


def example_5_complex_workflow():
    """Example 5: Complex workflow combining services"""
    print("\n=== Example 5: Complex Workflow ===")
    
    # Initialize services
    profiles_service = LearningProfilesService({})
    adaptations_service = AdaptationsService({})
    assessments_service = AssessmentsService({})
    translations_service = TranslationsService({})
    
    # Sample educational content
    content = {
        'pages': [{
            'page_number': 1,
            'text': """
            Photosynthesis is the process by which plants utilize sunlight 
            to synthesize nutrients from carbon dioxide and water. This 
            complex biochemical mechanism is fundamental to life on Earth.
            """
        }]
    }
    
    print("Original Content:")
    print(content['pages'][0]['text'].strip())
    
    # Step 1: Assess the content
    assessment = assessments_service.assess_content(content)
    print("\nReadability Assessment:")
    print(f"  Flesch Ease: {assessment['readability_metrics']['flesch_ease']:.1f}")
    print(f"  Recommendations: {', '.join(assessment['recommendations'])}")
    
    # Step 2: Adapt for ESL learners
    adapted_content = adaptations_service.adapt_content(content, 'esl', force_adaptation=True)
    print("\nAdapted for ESL:")
    print(adapted_content['pages'][0]['text'].strip())
    
    # Step 3: Prepare for translation
    target_language = 'spanish'
    if translations_service.is_language_supported(target_language):
        print(f"\n✓ {target_language.title()} translation is supported")
    
    # Step 4: Get formatting preferences
    formatting = profiles_service.get_formatting('esl')
    print(f"\nESL Formatting Preferences:")
    print(f"  Font: {formatting['font']}")
    print(f"  Font Size: {formatting['font_size']}pt")
    print(f"  Background: {formatting['background_color']}")


def main():
    """Run all examples"""
    print("Matcha Service-Oriented Architecture Examples")
    print("=" * 50)
    
    try:
        example_1_profile_exploration()
        example_2_content_assessment()
        example_3_text_adaptation()
        example_4_language_support()
        example_5_complex_workflow()
        
        print("\n" + "=" * 50)
        print("✓ All examples completed successfully!")
        print("\nThese examples demonstrate how each service can be:")
        print("- Used independently")
        print("- Tested in isolation")
        print("- Combined for complex workflows")
        print("- Extended with new functionality")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # Create examples directory if it doesn't exist
    os.makedirs('examples', exist_ok=True)
    main()