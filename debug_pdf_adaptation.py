#!/usr/bin/env python3
"""
Debug script to trace through PDF adaptation pipeline
"""
import sys
sys.path.append('.')

import os
from dotenv import load_dotenv
from migrate_pdf_functions import PDFMigrationHelper

# Load environment variables
load_dotenv()

def debug_pdf_adaptation():
    """Debug the PDF adaptation pipeline step by step"""
    print("🔧 Debugging PDF Adaptation Pipeline")
    print("=" * 60)
    
    # Setup
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        return
    
    config = {
        'output_folder': 'outputs',
        'upload_folder': 'uploads',
        'anthropic_api_key': api_key
    }
    
    # Find a PDF to test with
    test_pdf = None
    uploads_dir = 'uploads'
    if os.path.exists(uploads_dir):
        for file in os.listdir(uploads_dir):
            if file.endswith('.pdf'):
                test_pdf = os.path.join(uploads_dir, file)
                break
    
    if not test_pdf:
        print("❌ No PDF found in uploads directory")
        return
    
    print(f"📄 Testing with: {test_pdf}")
    
    # Initialize the migration helper
    try:
        pdf_helper = PDFMigrationHelper(config)
        print("✅ PDFMigrationHelper initialized")
    except Exception as e:
        print(f"❌ Error initializing PDFMigrationHelper: {e}")
        return
    
    # Step 1: Test content extraction
    print("\n🔍 Step 1: Testing content extraction...")
    try:
        content = pdf_helper.formats_service.extract_content(
            test_pdf, 'pdf', include_formatting=True
        )
        print(f"✅ Content extracted successfully")
        print(f"   - Pages: {len(content.get('pages', []))}")
        
        # Check first few pages
        for i, page in enumerate(content.get('pages', [])[:3]):
            text = page.get('text', '')
            text_blocks = page.get('text_blocks', [])
            print(f"   - Page {i+1}: {len(text)} chars, {len(text_blocks)} text blocks")
            if text.strip():
                print(f"     Sample: {text[:100]}...")
            else:
                print(f"     ⚠️  No text content")
                
    except Exception as e:
        print(f"❌ Content extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 2: Test content adaptation  
    print("\n🎯 Step 2: Testing content adaptation...")
    try:
        adapted_content = pdf_helper.adaptations_service.adapt_content(
            content, 'adhd', force_adaptation=True
        )
        print(f"✅ Content adapted successfully")
        print(f"   - Adapted pages: {len(adapted_content.get('pages', []))}")
        
        # Check adaptation results
        for i, (original_page, adapted_page) in enumerate(zip(content.get('pages', [])[:3], adapted_content.get('pages', [])[:3])):
            orig_text = original_page.get('text', '')
            adapt_text = adapted_page.get('text', '')
            print(f"   - Page {i+1}: {len(orig_text)} -> {len(adapt_text)} chars")
            if adapt_text.strip():
                print(f"     Adapted sample: {adapt_text[:100]}...")
            else:
                print(f"     ⚠️  No adapted text")
                
    except Exception as e:
        print(f"❌ Content adaptation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3: Test PDF creation
    print("\n📝 Step 3: Testing PDF creation...")
    try:
        output_path = os.path.join(config['output_folder'], 'debug_test_output.pdf')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        success = pdf_helper.formats_service.create_file(
            adapted_content,
            output_path,
            'pdf',
            profile='adhd',
            preserve_visuals=True,
            original_path=test_pdf
        )
        
        if success:
            print(f"✅ PDF created successfully: {output_path}")
            
            # Quick content check
            if os.path.exists(output_path):
                import PyPDF2
                with open(output_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    print(f"   - Created PDF has {len(reader.pages)} pages")
                    
                    # Check first page content
                    if len(reader.pages) > 0:
                        first_page_text = reader.pages[0].extract_text()
                        print(f"   - First page text: {len(first_page_text)} chars")
                        if first_page_text.strip():
                            print(f"     Sample: {first_page_text[:100]}...")
        else:
            print(f"❌ PDF creation failed")
            
    except Exception as e:
        print(f"❌ PDF creation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n✅ Debug complete!")

if __name__ == "__main__":
    debug_pdf_adaptation()