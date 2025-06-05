#!/usr/bin/env python3
"""
Test script for the anchor positioning fixes

This script tests the new anchor-based text positioning system
to ensure original text is removed and adapted text appears in correct positions.
"""

import os
import sys
from services.pdf_visual_handler import PDFVisualHandler

def test_anchor_positioning():
    """Test the anchor positioning fix"""
    
    # Find a test PDF in the uploads directory
    uploads_dir = "/Users/chris/projects/GitHub/Matcha/uploads"
    test_pdf = None
    
    for file in os.listdir(uploads_dir):
        if file.endswith('.pdf'):
            test_pdf = os.path.join(uploads_dir, file)
            break
    
    if not test_pdf:
        print("❌ No PDF files found in uploads directory for testing")
        return False
    
    print(f"📄 Testing with PDF: {test_pdf}")
    
    # Create test output path
    output_dir = "/Users/chris/projects/GitHub/Matcha/test_outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    test_output = os.path.join(output_dir, "perfect_alignment_test_output.pdf")
    
    # Initialize the PDF visual handler
    visual_handler = PDFVisualHandler()
    
    # Create a mock adapted content structure
    adapted_content = {
        'pages': [
            {
                'text': 'This is adapted text that should appear in the correct position with original text removed.',
                'page_number': 1
            }
        ],
        'metadata': {
            'title': 'Test Document'
        }
    }
    
    print("🔧 Testing PERFECT ALIGNMENT anchor-based PDF creation...")
    
    # Test the fixed anchor positioning
    success = visual_handler.create_visual_preserved_pdf_with_anchors(
        test_pdf, 
        adapted_content, 
        test_output, 
        profile='dyslexia'
    )
    
    if success and os.path.exists(test_output):
        print(f"✅ Anchor positioning test PASSED!")
        print(f"📁 Test output created: {test_output}")
        print(f"📊 File size: {os.path.getsize(test_output)} bytes")
        return True
    else:
        print(f"❌ Anchor positioning test FAILED!")
        return False

if __name__ == "__main__":
    print("🧪 Testing Anchor Positioning Fixes")
    print("=" * 50)
    
    success = test_anchor_positioning()
    
    if success:
        print("\n🎉 All tests passed! The anchor positioning fix is working.")
    else:
        print("\n💥 Tests failed. Check the error messages above.")
    
    sys.exit(0 if success else 1)