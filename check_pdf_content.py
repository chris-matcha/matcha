#!/usr/bin/env python3
"""
Quick script to check PDF content
"""
import PyPDF2
import os

def check_pdf_content(pdf_path):
    """Check if PDF has text content"""
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return False
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            print(f"📄 PDF Info:")
            print(f"   - File: {os.path.basename(pdf_path)}")
            print(f"   - Size: {os.path.getsize(pdf_path)} bytes")
            print(f"   - Pages: {len(pdf_reader.pages)}")
            
            # Check text content
            total_text = ""
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                total_text += page_text
                print(f"   - Page {i+1}: {len(page_text)} characters")
                if len(page_text) > 0:
                    print(f"     Sample: {page_text[:100]}...")
            
            if len(total_text.strip()) > 0:
                print(f"✅ PDF has content: {len(total_text)} total characters")
                return True
            else:
                print("❌ PDF appears to have no text content")
                return False
                
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        return False

if __name__ == "__main__":
    # Check the ADHD PDF that was mentioned
    pdf_path = "/Users/chris/projects/GitHub/Matcha/outputs/adapted_adhd_652d4be8-aa32-47d2-b7be-6dfbed1b7156_L3_Metal_oxides_MC.pdf"
    check_pdf_content(pdf_path)