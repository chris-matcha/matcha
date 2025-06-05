#!/usr/bin/env python3
"""
Quick test script to verify current state of Matcha functionality
"""
import os
import glob
from datetime import datetime

def test_current_state():
    print("🔍 Testing Current Matcha State")
    print("=" * 50)
    
    # Check recent outputs
    outputs_dir = "/Users/chris/projects/GitHub/Matcha/outputs"
    recent_files = []
    
    if os.path.exists(outputs_dir):
        all_files = glob.glob(os.path.join(outputs_dir, "*"))
        # Get files from today
        today = datetime.now().strftime("%Y-%m-%d")
        for file in all_files:
            if os.path.isfile(file):
                # Check if file was modified today (rough test)
                mtime = datetime.fromtimestamp(os.path.getmtime(file))
                if mtime.strftime("%Y-%m-%d") == today:
                    recent_files.append(os.path.basename(file))
    
    print(f"📁 Recent output files ({len(recent_files)}):")
    for f in sorted(recent_files)[:10]:  # Show first 10
        file_type = "🔤 Translation" if "translated_" in f else "📄 Adapted"
        print(f"  {file_type}: {f}")
    
    if len(recent_files) > 10:
        print(f"  ... and {len(recent_files) - 10} more")
    
    # Check for translations specifically
    translations = [f for f in recent_files if "translated_" in f]
    print(f"\n🌍 Translation files found: {len(translations)}")
    
    # Check for different profiles
    profiles_found = set()
    for f in recent_files:
        if "dyslexia" in f.lower():
            profiles_found.add("dyslexia")
        elif "adhd" in f.lower():
            profiles_found.add("adhd")
        elif "esl" in f.lower():
            profiles_found.add("esl")
    
    print(f"👥 Profiles tested: {', '.join(profiles_found) if profiles_found else 'Unknown'}")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"  ✅ File generation: {'Working' if recent_files else 'Not working'}")
    print(f"  ✅ Translations: {'Working' if translations else 'Not working'}")
    print(f"  ⚠️  Known issues: UI download visibility, text positioning")
    
    return len(recent_files) > 0, len(translations) > 0

if __name__ == "__main__":
    files_working, translations_working = test_current_state()
    
    print(f"\n🎯 Next Steps:")
    if files_working and translations_working:
        print("  1. Focus on UI download visibility issue")
        print("  2. Test text positioning")
        print("  3. System is mostly functional!")
    elif files_working:
        print("  1. Debug translation creation")
        print("  2. Check form submission")
    else:
        print("  1. Check basic PDF processing")
        print("  2. Review error logs")