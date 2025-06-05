#!/usr/bin/env python3
"""
Test the PDF text display fix
"""
import os
import sys
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from migrate_pdf_functions import PDFMigrationHelper
import fitz  # PyMuPDF

def test_pdf_text_fix():
    """Test that PDF adaptation now shows actual adapted text instead of markers"""
    
    # Configuration
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        return
    
    config = {
        'anthropic_api_key': api_key,
        'output_folder': '/Users/chris/projects/GitHub/Matcha/test_outputs',
        'upload_folder': '/Users/chris/projects/GitHub/Matcha/uploads'
    }
    
    # Create test output directory
    os.makedirs(config['output_folder'], exist_ok=True)
    
    # Find a test PDF file
    upload_folder = config['upload_folder']
    test_pdf = None
    
    print("=== PDF TEXT DISPLAY FIX TEST ===")
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
    
    # Initialize helper
    pdf_helper = PDFMigrationHelper(config)
    
    # Test adaptation with the fix
    print("Testing PDF adaptation with text display fix:")
    try:
        result = pdf_helper.process_with_pdf_template_system(
            test_pdf, 
            'dyslexia',
            direct_adapt=True,
            preserve_visuals=True,
            translate=False
        )
        
        if result.get('success'):
            output_path = result.get('output_path')
            print(f"   ✅ PDF adaptation completed")
            print(f"   Output: {output_path}")
            
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"   File size: {file_size} bytes ({file_size/1024:.1f} KB)")
                
                # Check the content of the adapted PDF
                print(f"   Checking content...")
                doc = fitz.open(output_path)
                
                pages_with_real_content = 0
                pages_with_markers_only = 0
                total_text_length = 0
                
                for page_num in range(doc.page_count):
                    page = doc[page_num]
                    text = page.get_text().strip()
                    total_text_length += len(text)
                    
                    # Check for placeholder markers
                    markers = ['[DYSLEXIA]', '[Adapted: DYSLEXIA]', 'Adapted for dyslexia']
                    is_marker_only = any(text == marker for marker in markers)
                    
                    if is_marker_only:
                        pages_with_markers_only += 1
                    elif len(text) > 50:  # Substantial content
                        pages_with_real_content += 1
                
                doc.close()
                
                print(f"   Total pages: {doc.page_count}")
                print(f"   Pages with real content: {pages_with_real_content}")
                print(f"   Pages with markers only: {pages_with_markers_only}")
                print(f"   Total text length: {total_text_length} characters")
                
                # Determine if fix worked
                if pages_with_real_content > pages_with_markers_only:
                    print(f"   ✅ FIX SUCCESSFUL: More pages have real content than markers")
                elif pages_with_markers_only == 0:
                    print(f"   ✅ FIX SUCCESSFUL: No marker-only pages found")
                else:
                    print(f"   ⚠ PARTIAL FIX: Still some marker-only pages")
                
                # Check for oversized files (previous issue)
                if file_size > 50 * 1024 * 1024:  # 50MB
                    print(f"   ⚠ WARNING: File is very large ({file_size/1024/1024:.1f}MB)")
                else:
                    print(f"   ✅ File size is reasonable")
                
            else:
                print(f"   ❌ Output file doesn't exist")
        else:
            print(f"   ❌ Adaptation failed: {result.get('error')}")
        
    except Exception as e:
        print(f"   ❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_text_fix()