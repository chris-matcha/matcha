#!/usr/bin/env python3
"""
Scientific Dictionary Management Tool

Interactive tool for managing the scientific terms dictionary.
"""
import json
import sys
from services.scientific_dictionary import ScientificDictionary

def print_header():
    print("🔬 Scientific Dictionary Manager")
    print("=" * 50)

def show_menu():
    print("\n📋 Available Actions:")
    print("1. View dictionary statistics")
    print("2. Search terms")
    print("3. Add new term")
    print("4. View terms by category")
    print("5. Show most used terms")
    print("6. Suggest missing terms from text")
    print("7. Export dictionary")
    print("8. View sample terms")
    print("9. Exit")
    print()

def view_statistics(dictionary):
    """Display dictionary statistics"""
    stats = dictionary.get_statistics()
    
    print("\n📊 Dictionary Statistics:")
    print(f"   Total terms: {stats['total_terms']}")
    print(f"   Total usage: {stats['total_usage']}")
    print(f"   Session usage: {stats['session_usage']}")
    
    print(f"\n📂 Categories:")
    for category, count in stats['categories'].items():
        print(f"   • {category}: {count} terms")
    
    print(f"\n🏷️ Types:")
    for term_type, count in stats['types'].items():
        print(f"   • {term_type}: {count} terms")

def search_terms(dictionary):
    """Search for terms"""
    query = input("🔍 Enter search term: ").strip()
    if not query:
        return
    
    results = dictionary.search_terms(query, limit=10)
    
    if results:
        print(f"\n📋 Search results for '{query}' ({len(results)} found):")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['term']} ({result['category']})")
            print(f"   Definition: {result['definition']}")
            print(f"   Adaptations:")
            for profile, adaptation in result['adaptations'].items():
                print(f"      {profile}: {adaptation}")
    else:
        print(f"❌ No terms found for '{query}'")

def add_new_term(dictionary):
    """Add a new term to the dictionary"""
    print("\n➕ Adding New Term")
    print("-" * 30)
    
    term = input("Term: ").strip()
    if not term:
        print("❌ Term cannot be empty")
        return
    
    category = input("Category (chemistry/biology/physics/medical/mathematics): ").strip()
    term_type = input("Type (chemical_formula/abbreviation/unit/function): ").strip()
    definition = input("Definition: ").strip()
    
    print("\n📝 Enter adaptations for each profile:")
    adaptations = {}
    
    for profile in ["dyslexia", "adhd", "esl"]:
        adaptation = input(f"  {profile}: ").strip()
        if adaptation:
            adaptations[profile] = adaptation
    
    if adaptations:
        success = dictionary.add_term(term, category, term_type, adaptations, definition)
        if success:
            print(f"✅ Successfully added '{term}' to dictionary")
        else:
            print(f"❌ Failed to add '{term}'")
    else:
        print("❌ At least one adaptation is required")

def view_by_category(dictionary):
    """View terms by category"""
    category = input("📂 Enter category (chemistry/biology/physics/medical/mathematics): ").strip()
    
    terms = dictionary.get_terms_by_category(category)
    
    if terms:
        print(f"\n📋 Terms in '{category}' category ({len(terms)} found):")
        for term, data in terms.items():
            print(f"\n• {term} ({data.get('type', 'unknown')})")
            print(f"  Definition: {data.get('definition', 'No definition')}")
            print(f"  Usage: {data.get('usage_count', 0)} times")
    else:
        print(f"❌ No terms found in '{category}' category")

def show_most_used(dictionary):
    """Show most frequently used terms"""
    limit = 20
    terms = dictionary.get_most_used_terms(limit)
    
    if terms:
        print(f"\n🔥 Most Used Terms (Top {len(terms)}):")
        for i, term_data in enumerate(terms, 1):
            usage = term_data['usage_count']
            if usage > 0:
                print(f"{i:2d}. {term_data['term']} - {usage} uses ({term_data['category']})")
        
        if not any(t['usage_count'] > 0 for t in terms):
            print("ℹ️ No terms have been used yet")
    else:
        print("❌ No usage data available")

def suggest_missing_terms(dictionary):
    """Suggest missing terms from text analysis"""
    print("\n💡 Text Analysis for Missing Terms")
    print("Enter text to analyze (press Enter twice to finish):")
    
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    
    if not lines:
        return
    
    text = " ".join(lines)
    suggestions = dictionary.suggest_missing_terms(text)
    
    if suggestions:
        print(f"\n💡 Suggested terms to add ({len(suggestions)} found):")
        for term in suggestions:
            print(f"   • {term}")
        
        # Ask if user wants to add any
        add_term = input("\n❓ Would you like to add any of these terms? (y/n): ").strip().lower()
        if add_term == 'y':
            for term in suggestions[:3]:  # Limit to first 3
                response = input(f"Add '{term}'? (y/n): ").strip().lower()
                if response == 'y':
                    print(f"\n➕ Adding '{term}':")
                    add_new_term(dictionary)
                    break
    else:
        print("ℹ️ No new terms suggested from this text")

def export_dictionary(dictionary):
    """Export dictionary to file"""
    filename = input("📤 Enter export filename (e.g., dictionary_backup.json): ").strip()
    if not filename:
        filename = "scientific_dictionary_export.json"
    
    if not filename.endswith('.json'):
        filename += '.json'
    
    success = dictionary.export_dictionary(filename)
    if success:
        print(f"✅ Dictionary exported to '{filename}'")
    else:
        print(f"❌ Failed to export dictionary")

def show_sample_terms(dictionary):
    """Show sample terms from each category"""
    stats = dictionary.get_statistics()
    categories = stats.get('categories', {})
    
    print("\n📚 Sample Terms by Category:")
    
    for category in categories:
        terms = dictionary.get_terms_by_category(category)
        if terms:
            print(f"\n📂 {category.title()}:")
            # Show first 3 terms in category
            for i, (term, data) in enumerate(list(terms.items())[:3]):
                adaptations = data.get('adaptations', {})
                sample_adaptation = next(iter(adaptations.values())) if adaptations else "No adaptation"
                print(f"   {i+1}. {term} → {sample_adaptation}")
            
            if len(terms) > 3:
                print(f"   ... and {len(terms) - 3} more")

def main():
    """Main interactive loop"""
    print_header()
    
    # Initialize dictionary
    try:
        dictionary = ScientificDictionary()
        print("✅ Scientific dictionary loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load dictionary: {e}")
        return
    
    while True:
        show_menu()
        
        try:
            choice = input("Select an option (1-9): ").strip()
            
            if choice == '1':
                view_statistics(dictionary)
            elif choice == '2':
                search_terms(dictionary)
            elif choice == '3':
                add_new_term(dictionary)
            elif choice == '4':
                view_by_category(dictionary)
            elif choice == '5':
                show_most_used(dictionary)
            elif choice == '6':
                suggest_missing_terms(dictionary)
            elif choice == '7':
                export_dictionary(dictionary)
            elif choice == '8':
                show_sample_terms(dictionary)
            elif choice == '9':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid option. Please choose 1-9.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()