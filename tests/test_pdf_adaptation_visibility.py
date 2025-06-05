#!/usr/bin/env python3
"""
Test script to verify that adapted text is visible in visual PDFs
"""
import os
import sys
import fitz  # PyMuPDF

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.pdf_service import PDFService

def test_pdf_adaptation_visibility():
    """Test that adapted text is properly shown in visual PDFs"""
    
    # Setup
    config = {
        'output_folder': 'test_outputs',
        'anthropic_api_key': None  # Will test with mock adaptation
    }
    
    pdf_service = PDFService(config)
    
    # Create a simple test PDF
    test_pdf_path = "test_input.pdf"
    doc = fitz.open()
    page = doc.new_page()
    
    # Add some test text
    original_text = "This is a complex sentence with sophisticated vocabulary that should be simplified."
    page.insert_text((50, 50), original_text, fontsize=12)
    
    doc.save(test_pdf_path)
    doc.close()
    
    # Extract content with formatting
    print("1. Extracting content from test PDF...")
    content = pdf_service.extract_content_from_pdf(test_pdf_path, include_formatting=True)
    print(f"   - Extracted {len(content['pages'])} pages")
    
    # Mock adapted content (since we don't have API key in test)
    adapted_content = content.copy()
    adapted_text = "This is a simple sentence with easy words."
    
    if adapted_content['pages']:
        adapted_content['pages'][0]['text'] = adapted_text
        print(f"   - Original text: {original_text}")
        print(f"   - Adapted text: {adapted_text}")
    
    # Create visual preserved PDF
    output_path = "test_output_visual.pdf"
    print("\n2. Creating visual preserved PDF...")
    success = pdf_service.create_visual_preserved_pdf(
        test_pdf_path, 
        adapted_content, 
        output_path, 
        'dyslexia'
    )
    
    if success and os.path.exists(output_path):
        print("   ✓ Visual PDF created successfully")
        
        # Verify the output
        print("\n3. Verifying output PDF...")
        verify_doc = fitz.open(output_path)
        verify_page = verify_doc[0]
        extracted_text = verify_page.get_text()
        
        print(f"   - Extracted text from output: {extracted_text.strip()}")
        
        # Check if adapted text is present
        if adapted_text in extracted_text:
            print("   ✓ Adapted text is present in output")
        else:
            print("   ✗ Adapted text NOT found in output")
            
        # Check if original text is still visible
        if original_text in extracted_text:
            print("   ⚠ Original text is still visible (overlay issue)")
        else:
            print("   ✓ Original text is properly covered")
            
        # Check for adaptation indicator
        if "Adapted for dyslexia" in extracted_text:
            print("   ✓ Adaptation indicator is present")
        else:
            print("   ✗ Adaptation indicator NOT found")
            
        verify_doc.close()
    else:
        print("   ✗ Failed to create visual PDF")
    
    # Cleanup
    if os.path.exists(test_pdf_path):
        os.remove(test_pdf_path)
    if os.path.exists(output_path):
        os.remove(output_path)
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_pdf_adaptation_visibility()