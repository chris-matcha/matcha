#!/usr/bin/env python3
"""
Test the complete PDF adaptation flow to see where text might be getting lost
"""
import os
import sys
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from migrate_pdf_functions import PDFMigrationHelper
from services import FormatsService, AdaptationsService

def test_pdf_adaptation_flow():
    """Test the complete PDF adaptation pipeline"""
    
    # Configuration
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        return
    
    config = {
        'anthropic_api_key': api_key,
        'output_folder': '/Users/chris/projects/GitHub/Matcha/outputs',
        'upload_folder': '/Users/chris/projects/GitHub/Matcha/uploads'
    }
    
    # Find a test PDF file
    upload_folder = config['upload_folder']
    test_pdf = None
    
    print("=== PDF ADAPTATION FLOW TEST ===")
    print()
    
    # Look for any PDF file in uploads
    if os.path.exists(upload_folder):
        for file in os.listdir(upload_folder):
            if file.endswith('.pdf'):
                test_pdf = os.path.join(upload_folder, file)
                break
    
    if not test_pdf:
        print("❌ No PDF files found in uploads folder")
        return
    
    print(f"✅ Found test PDF: {os.path.basename(test_pdf)}")
    print()
    
    # Initialize services
    formats_service = FormatsService(config)
    adaptations_service = AdaptationsService(config)
    pdf_helper = PDFMigrationHelper(config)
    
    # Test 1: Extract content
    print("1. Testing content extraction:")
    try:
        content = formats_service.extract_content(test_pdf, 'pdf', include_formatting=False)
        print(f"   ✅ Content extracted successfully")
        print(f"   Pages found: {len(content.get('pages', []))}")
        
        if content.get('pages'):
            first_page = content['pages'][0]
            text_sample = first_page.get('text', '')[:100]
            print(f"   First page text sample: '{text_sample}...'")
            print(f"   First page text length: {len(first_page.get('text', ''))}")
        print()
    except Exception as e:
        print(f"   ❌ Content extraction failed: {str(e)}")
        return
    
    # Test 2: Test adaptation
    print("2. Testing content adaptation:")
    profile = 'dyslexia'
    try:
        adapted_content = adaptations_service.adapt_content(
            content, profile, force_adaptation=True
        )
        print(f"   ✅ Content adapted successfully")
        print(f"   Adapted pages: {len(adapted_content.get('pages', []))}")
        
        if adapted_content.get('pages'):
            original_text = content['pages'][0].get('text', '')
            adapted_text = adapted_content['pages'][0].get('text', '')
            
            print(f"   Original text length: {len(original_text)}")
            print(f"   Adapted text length: {len(adapted_text)}")
            print(f"   Text changed: {original_text != adapted_text}")
            
            if original_text != adapted_text:
                print(f"   Original sample: '{original_text[:100]}...'")
                print(f"   Adapted sample: '{adapted_text[:100]}...'")
        print()
    except Exception as e:
        print(f"   ❌ Content adaptation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 3: Test PDF creation
    print("3. Testing PDF creation:")
    try:
        test_output = os.path.join(config['output_folder'], 'test_adaptation.pdf')
        success = formats_service.create_file(
            adapted_content,
            test_output,
            'pdf',
            profile=profile,
            preserve_visuals=False
        )
        
        if success and os.path.exists(test_output):
            print(f"   ✅ PDF created successfully: {test_output}")
            print(f"   File size: {os.path.getsize(test_output)} bytes")
            
            # Clean up test file
            os.remove(test_output)
        else:
            print(f"   ❌ PDF creation failed or file doesn't exist")
        print()
    except Exception as e:
        print(f"   ❌ PDF creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 4: Test complete pipeline
    print("4. Testing complete pipeline (PDFMigrationHelper):")
    try:
        result = pdf_helper.process_with_pdf_template_system(
            test_pdf, 
            profile,
            direct_adapt=True,
            preserve_visuals=False,
            translate=False
        )
        
        if result.get('success'):
            print(f"   ✅ Pipeline completed successfully")
            print(f"   Output path: {result.get('output_path')}")
            
            if os.path.exists(result.get('output_path', '')):
                print(f"   Output file exists: Yes")
                print(f"   Output file size: {os.path.getsize(result['output_path'])} bytes")
            else:
                print(f"   ❌ Output file doesn't exist!")
        else:
            print(f"   ❌ Pipeline failed: {result.get('error')}")
        print()
    except Exception as e:
        print(f"   ❌ Pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 5: Test with visual preservation
    print("5. Testing with visual preservation:")
    try:
        result = pdf_helper.process_with_pdf_template_system(
            test_pdf, 
            profile,
            direct_adapt=True,
            preserve_visuals=True,
            translate=False
        )
        
        if result.get('success'):
            print(f"   ✅ Visual preservation pipeline completed successfully")
            print(f"   Output path: {result.get('output_path')}")
            
            if os.path.exists(result.get('output_path', '')):
                print(f"   Output file exists: Yes")
                print(f"   Output file size: {os.path.getsize(result['output_path'])} bytes")
            else:
                print(f"   ❌ Output file doesn't exist!")
        else:
            print(f"   ❌ Visual preservation pipeline failed: {result.get('error')}")
        print()
    except Exception as e:
        print(f"   ❌ Visual preservation pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    test_pdf_adaptation_flow()