#!/usr/bin/env python3
"""Test the improved anchor-based PDF visual preservation"""

import os
from services.pdf_visual_handler import PDFVisualHandler

def test_improved_anchor():
    # Initialize service
    pdf_handler = PDFVisualHandler()
    
    # Test file path
    test_pdf = "/Users/chris/projects/GitHub/Matcha/uploads/1d98e302-c037-481b-b7cd-ecdaed2f5f0b_L3_Metal_oxides_MC.pdf"
    
    if not os.path.exists(test_pdf):
        print(f"Test PDF not found: {test_pdf}")
        # Try to find any PDF in uploads
        for f in os.listdir("/Users/chris/projects/GitHub/Matcha/uploads"):
            if f.endswith('.pdf'):
                test_pdf = os.path.join("/Users/chris/projects/GitHub/Matcha/uploads", f)
                break
        else:
            print("No PDF files found in uploads folder")
            return
    
    print(f"Testing improved anchor approach with: {test_pdf}")
    
    # Test with the improved anchor-based approach
    # This time, it will extract original text, adapt each block individually,
    # and place adapted text at correct positions
    
    output_path = "test_improved_anchor_output.pdf"
    print(f"Creating improved anchor-based PDF: {output_path}")
    
    # The new method doesn't need pre-adapted content - it will:
    # 1. Extract text blocks from original PDF
    # 2. Adapt each block individually 
    # 3. Place adapted text at original positions
    success = pdf_handler.create_visual_preserved_pdf_with_anchors(
        test_pdf, 
        {},  # Empty adapted content - method will adapt directly
        output_path, 
        'dyslexia'
    )
    
    if success:
        print(f"\n✓ Success! Improved anchor-based PDF created: {output_path}")
        print("\nThe improved approach should now:")
        print("1. Extract all original text blocks with positions")
        print("2. Adapt each text block individually using AI/rules")
        print("3. Replace ALL original text with adapted versions")
        print("4. Preserve backgrounds and visual elements")
        print("5. Position adapted text exactly where original text was")
        
        # Check file size to verify it was created
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"\nOutput file size: {size:,} bytes")
        
    else:
        print("\n✗ Failed to create improved anchor-based PDF")

if __name__ == "__main__":
    test_improved_anchor()