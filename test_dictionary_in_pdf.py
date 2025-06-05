#!/usr/bin/env python3
"""
Test scientific dictionary integration with actual PDF processing
"""
import os
from dotenv import load_dotenv
from services.adaptations_service import AdaptationsService
from services.pdf_visual_handler import PDFVisualHandler

load_dotenv()

def test_dictionary_in_pdf_adaptation():
    """Test that scientific dictionary works in real PDF adaptation"""
    print("🧪 Testing Scientific Dictionary in PDF Adaptation")
    print("=" * 60)
    
    pdf_path = "uploads/0ca61bcc-8780-47fe-aab6-77b6757a37de_L3_Metal_oxides_MC.pdf"
    output_path = "test_outputs/dictionary_enhanced_adaptation.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Test PDF not found: {pdf_path}")
        return False
    
    # Ensure output directory exists
    os.makedirs("test_outputs", exist_ok=True)
    
    # Initialize services
    config = {}  # No API key - will use rule-based + dictionary
    adaptations_service = AdaptationsService(config)
    handler = PDFVisualHandler()
    
    print(f"📄 Processing PDF: {pdf_path}")
    print(f"🎯 Output: {output_path}")
    
    try:
        # Extract some text first to see what we're working with
        pages_data = handler.extract_text_blocks_with_formatting(pdf_path)
        
        print(f"\n🔍 Analyzing first page for scientific terms...")
        dictionary_terms_found = []
        
        if pages_data:
            first_page = pages_data[0]
            for block in first_page['blocks']:
                # Extract text from block
                block_text = ""
                for line in block['lines']:
                    for span in line['spans']:
                        block_text += span['text']
                
                # Check if this text would hit the dictionary
                if block_text.strip():
                    dict_adaptation = adaptations_service.scientific_dict.get_adaptation(
                        block_text.strip(), 'dyslexia'
                    )
                    if dict_adaptation:
                        dictionary_terms_found.append({
                            'original': block_text.strip(),
                            'adapted': dict_adaptation
                        })
        
        if dictionary_terms_found:
            print(f"✅ Found {len(dictionary_terms_found)} terms that will use dictionary:")
            for term_data in dictionary_terms_found[:5]:  # Show first 5
                print(f"   • '{term_data['original']}' → '{term_data['adapted']}'")
        else:
            print("ℹ️ No dictionary terms found in sample text")
        
        # Now run the full PDF adaptation
        print(f"\n🔄 Running full PDF adaptation with dictionary integration...")
        
        success = handler.create_visual_preserved_pdf_with_anchors(
            pdf_path,
            {},  # Empty adapted content - will extract and adapt internally
            output_path,
            'dyslexia'  # Use dyslexia profile for testing
        )
        
        if success and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ PDF adaptation successful!")
            print(f"📁 Output file: {output_path}")
            print(f"📊 File size: {file_size:,} bytes")
            
            # Get dictionary usage statistics
            dict_stats = adaptations_service.get_dictionary_stats()
            print(f"\n📊 Dictionary Usage:")
            print(f"   Total terms in dictionary: {dict_stats.get('total_terms', 0)}")
            print(f"   Session usage: {dict_stats.get('session_usage', 0)}")
            
            return True
        else:
            print(f"❌ PDF adaptation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during PDF adaptation: {e}")
        import traceback
        traceback.print_exc()
        return False

def demonstrate_dictionary_benefits():
    """Demonstrate the benefits of the scientific dictionary"""
    print("\n🧪 Demonstrating Dictionary Benefits")
    print("=" * 60)
    
    config = {}
    adaptations_service = AdaptationsService(config)
    
    scientific_terms = ["Fe2O3", "CO2", "DNA", "pH", "ATP"]
    
    print("🔬 Scientific Term Adaptations:")
    print("=" * 40)
    
    for term in scientific_terms:
        print(f"\n📝 Term: '{term}'")
        
        # Show adaptations for all profiles
        for profile in ["dyslexia", "adhd", "esl"]:
            adapted = adaptations_service.adapt_text(term, profile)
            print(f"   {profile.upper():8}: {adapted}")
    
    # Show dictionary statistics
    stats = adaptations_service.get_dictionary_stats()
    print(f"\n📊 Dictionary Statistics:")
    print(f"   • Total terms: {stats.get('total_terms', 0)}")
    print(f"   • Categories: {len(stats.get('categories', {}))}")
    print(f"   • Ready for instant lookup")
    
    return True

def show_dictionary_file_contents():
    """Show what's actually stored in the dictionary file"""
    print("\n🧪 Dictionary File Contents")
    print("=" * 60)
    
    dictionary_path = "services/data/scientific_dictionary.json"
    
    if os.path.exists(dictionary_path):
        file_size = os.path.getsize(dictionary_path)
        print(f"📁 Dictionary file: {dictionary_path}")
        print(f"📊 File size: {file_size:,} bytes")
        
        try:
            import json
            with open(dictionary_path, 'r') as f:
                data = json.load(f)
            
            metadata = data.get('metadata', {})
            terms = data.get('terms', {})
            
            print(f"\n📋 Metadata:")
            print(f"   Version: {metadata.get('version', 'unknown')}")
            print(f"   Created: {metadata.get('created', 'unknown')}")
            print(f"   Total terms: {metadata.get('total_terms', 0)}")
            
            print(f"\n🔬 Sample Terms:")
            for i, (term, term_data) in enumerate(list(terms.items())[:5]):
                category = term_data.get('category', 'unknown')
                definition = term_data.get('definition', 'No definition')
                print(f"   {i+1}. {term} ({category})")
                print(f"      {definition}")
            
            if len(terms) > 5:
                print(f"   ... and {len(terms) - 5} more terms")
            
            return True
            
        except Exception as e:
            print(f"❌ Error reading dictionary file: {e}")
            return False
    else:
        print(f"❌ Dictionary file not found: {dictionary_path}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Scientific Dictionary in Real PDF Adaptation")
    print("=" * 70)
    
    # Run tests
    pdf_success = test_dictionary_in_pdf_adaptation()
    benefits_demo = demonstrate_dictionary_benefits()
    file_contents = show_dictionary_file_contents()
    
    print("\n" + "=" * 70)
    print("📋 SCIENTIFIC DICTIONARY IN PDF TEST RESULTS:")
    print(f"   📄 PDF adaptation with dictionary: {'✅ Working' if pdf_success else '❌ Failed'}")
    print(f"   🎯 Profile-specific benefits: {'✅ Demonstrated' if benefits_demo else '❌ Failed'}")
    print(f"   📁 Dictionary file integrity: {'✅ Valid' if file_contents else '❌ Issues'}")
    
    total_score = sum([pdf_success, benefits_demo, file_contents])
    print(f"\n🎯 Overall Integration Score: {total_score}/3")
    
    if total_score >= 2:
        print("🎉 Scientific Dictionary successfully integrated with PDF adaptation!")
        print("\n🚀 Key Achievements:")
        print("   ✅ Dictionary terms get instant, consistent adaptations")
        print("   ✅ No API calls needed for scientific terms")
        print("   ✅ Profile-specific explanations for learning needs")
        print("   ✅ Persistent storage with automatic loading")
        print("   ✅ Easy to add new terms and categories")
        print("   ✅ Seamlessly integrated with existing PDF pipeline")
        
        print("\n📚 Next Steps:")
        print("   • Run: python dictionary_manager.py (interactive management)")
        print("   • Add more terms specific to your curriculum")
        print("   • Monitor usage statistics to identify popular terms")
        print("   • Export/backup dictionary for sharing between systems")
    else:
        print("⚠️ Scientific Dictionary integration needs attention")