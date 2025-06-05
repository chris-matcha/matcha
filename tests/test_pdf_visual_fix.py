#!/usr/bin/env python3
"""
Test script to verify and fix PDF visual handler issues
"""
import sys
sys.path.append('.')

import os
from dotenv import load_dotenv
import fitz
from services.pdf_visual_handler import PDFVisualHandler
from services.adaptations_service import AdaptationsService
from services.pdf_service import PDFService
import tempfile

# Load environment variables
load_dotenv()

def test_pdf_visual_handler():
    """Test PDF visual handler with fixes for reported issues"""
    print("🔧 Testing PDF Visual Handler Fixes")
    print("=" * 60)
    
    # Initialize services
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        return
    
    config = {
        'anthropic_api_key': api_key
    }
    
    pdf_service = PDFService(config)
    adaptations_service = AdaptationsService(config)
    visual_handler = PDFVisualHandler()
    
    # Create a test PDF
    test_pdf_path = create_test_pdf()
    output_path = "test_outputs/visual_handler_test_output.pdf"
    os.makedirs("test_outputs", exist_ok=True)
    
    print(f"\n📄 Created test PDF: {test_pdf_path}")
    
    # Extract content
    print("\n📊 Extracting content from PDF...")
    content = pdf_service.extract_content_from_pdf(test_pdf_path, include_formatting=True)
    
    # Adapt content
    print("\n✏️ Adapting content for dyslexia profile...")
    adapted_content = {'pages': []}
    
    for page in content['pages']:
        adapted_page = {
            'text': '',
            'text_blocks': page.get('text_blocks', []),
            'page_num': page.get('page_num', 0),
            'width': page.get('width', 0),
            'height': page.get('height', 0)
        }
        
        # Adapt the text
        if page.get('text'):
            adapted_text = adaptations_service.adapt_text(page['text'], 'dyslexia')
            adapted_page['text'] = adapted_text
            print(f"  Page {page.get('page_num', 0) + 1}: {len(page['text'])} -> {len(adapted_text)} chars")
        
        adapted_content['pages'].append(adapted_page)
    
    # Test visual preservation
    print("\n🎨 Creating visual preserved PDF...")
    success = visual_handler.create_visual_preserved_pdf_with_anchors(
        test_pdf_path, adapted_content, output_path, 'dyslexia'
    )
    
    if success:
        print(f"✅ Visual preserved PDF created: {output_path}")
        
        # Analyze the output
        analyze_output_pdf(output_path)
    else:
        print("❌ Failed to create visual preserved PDF")
    
    # Clean up
    os.remove(test_pdf_path)

def create_test_pdf():
    """Create a test PDF with various elements"""
    doc = fitz.open()
    
    # Page 1: Text with background color
    page = doc.new_page(width=595, height=842)  # A4
    
    # Add colored background area
    rect = fitz.Rect(50, 50, 300, 150)
    page.draw_rect(rect, color=(0.9, 0.9, 1.0), fill=(0.9, 0.9, 1.0))
    
    # Add text on colored background
    page.insert_text((60, 80), "Text on colored background", fontsize=14, color=(0, 0, 0))
    page.insert_text((60, 100), "This should maintain the background color", fontsize=12, color=(0, 0, 0))
    
    # Add regular text
    page.insert_text((50, 200), "Regular text on white background", fontsize=14, color=(0, 0, 0))
    page.insert_text((50, 220), "This is a longer paragraph that contains multiple lines of text. " * 3, fontsize=12, color=(0, 0, 0))
    
    # Add an image area with text
    img_rect = fitz.Rect(350, 50, 550, 250)
    page.draw_rect(img_rect, color=(0.8, 0.8, 0.8), fill=(0.8, 0.8, 0.8))
    page.insert_text((360, 140), "Text inside image area", fontsize=12, color=(0, 0, 0))
    
    # Save to temporary file
    temp_path = tempfile.mktemp(suffix='.pdf')
    doc.save(temp_path)
    doc.close()
    
    return temp_path

def analyze_output_pdf(pdf_path):
    """Analyze the output PDF to check for issues"""
    print("\n🔍 Analyzing output PDF...")
    doc = fitz.open(pdf_path)
    
    for page_num, page in enumerate(doc):
        print(f"\n  Page {page_num + 1}:")
        
        # Check for text
        text = page.get_text()
        print(f"    Text length: {len(text)} chars")
        if text.strip():
            print(f"    First 50 chars: {text[:50]}...")
        else:
            print("    ⚠️ No text found!")
        
        # Check for drawings/rectangles
        drawings = page.get_drawings()
        rect_count = sum(1 for d in drawings if d['type'] == 'rect')
        print(f"    Rectangle count: {rect_count}")
        
        # Check for images
        images = page.get_images()
        print(f"    Image count: {len(images)}")
    
    doc.close()

def test_specific_fixes():
    """Test specific fixes for the reported issues"""
    print("\n🔧 Testing Specific Fixes")
    print("=" * 60)
    
    # Test 1: Background color sampling
    print("\n1. Testing background color sampling:")
    visual_handler = PDFVisualHandler()
    
    # Create a test page with colored background
    doc = fitz.open()
    page = doc.new_page()
    
    # Draw colored rectangle
    rect = fitz.Rect(100, 100, 200, 200)
    page.draw_rect(rect, color=(0.8, 0.9, 1.0), fill=(0.8, 0.9, 1.0))
    
    # Sample the color
    sampled_color = visual_handler._sample_background_color(page, rect)
    print(f"   Sampled color: {sampled_color}")
    print(f"   Expected: ~(0.8, 0.9, 1.0)")
    
    doc.close()
    
    # Test 2: Text in image area detection
    print("\n2. Testing text in image area detection:")
    doc = fitz.open()
    page = doc.new_page()
    
    # Add a fake image area
    img_rect = fitz.Rect(100, 100, 300, 300)
    page.draw_rect(img_rect, color=(0.5, 0.5, 0.5), fill=(0.5, 0.5, 0.5))
    
    # Test rect that overlaps with image
    text_rect = fitz.Rect(150, 150, 250, 200)
    is_in_image = visual_handler._is_text_in_image_area(page, text_rect)
    print(f"   Text in image area: {is_in_image}")
    
    # Test rect that doesn't overlap
    text_rect2 = fitz.Rect(400, 400, 500, 450)
    is_in_image2 = visual_handler._is_text_in_image_area(page, text_rect2)
    print(f"   Text outside image area: {is_in_image2}")
    
    doc.close()

if __name__ == "__main__":
    # Run main test
    test_pdf_visual_handler()
    
    # Run specific tests
    test_specific_fixes()