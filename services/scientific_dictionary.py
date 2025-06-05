"""
Scientific and Technical Terms Dictionary

A growing dictionary system for adapting scientific and technical terms
based on learning profiles (dyslexia, ADHD, ESL).
"""
import json
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime


class ScientificDictionary:
    """Dictionary system for scientific and technical term adaptations"""
    
    def __init__(self, dictionary_path: str = "services/data/scientific_dictionary.json"):
        self.dictionary_path = dictionary_path
        self.logger = logging.getLogger(self.__class__.__name__)
        self.dictionary = self._load_dictionary()
        self.usage_stats = {}
        
    def _load_dictionary(self) -> Dict[str, Any]:
        """Load the dictionary from file or create with initial terms"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.dictionary_path), exist_ok=True)
            
            if os.path.exists(self.dictionary_path):
                with open(self.dictionary_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Create initial dictionary with core scientific terms
                initial_dict = self._create_initial_dictionary()
                self._save_dictionary(initial_dict)
                return initial_dict
                
        except Exception as e:
            self.logger.error(f"Error loading dictionary: {e}")
            return self._create_initial_dictionary()
    
    def _create_initial_dictionary(self) -> Dict[str, Any]:
        """Create initial dictionary with common scientific terms"""
        return {
            "metadata": {
                "version": "1.0",
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_terms": 0
            },
            "terms": {
                # Chemistry - Chemical formulas and compounds
                "Fe2O3": {
                    "category": "chemistry",
                    "type": "chemical_formula",
                    "adaptations": {
                        "dyslexia": "Iron oxide (Fe2O3) - rust compound",
                        "adhd": "Fe2O3 = Iron rust",
                        "esl": "Fe2O3 (iron oxide - a rust compound made of iron and oxygen)"
                    },
                    "definition": "Iron(III) oxide, commonly known as rust",
                    "usage_count": 0
                },
                "CO2": {
                    "category": "chemistry", 
                    "type": "chemical_formula",
                    "adaptations": {
                        "dyslexia": "Carbon dioxide (CO2) - gas we breathe out",
                        "adhd": "CO2 = Gas from breathing",
                        "esl": "CO2 (carbon dioxide - the gas humans breathe out)"
                    },
                    "definition": "Carbon dioxide, a greenhouse gas",
                    "usage_count": 0
                },
                "H2O": {
                    "category": "chemistry",
                    "type": "chemical_formula", 
                    "adaptations": {
                        "dyslexia": "Water (H2O) - two hydrogen, one oxygen",
                        "adhd": "H2O = Water",
                        "esl": "H2O (water - made of hydrogen and oxygen atoms)"
                    },
                    "definition": "Water molecule",
                    "usage_count": 0
                },
                "NaCl": {
                    "category": "chemistry",
                    "type": "chemical_formula",
                    "adaptations": {
                        "dyslexia": "Salt (NaCl) - table salt",
                        "adhd": "NaCl = Table salt", 
                        "esl": "NaCl (sodium chloride - common table salt)"
                    },
                    "definition": "Sodium chloride, table salt",
                    "usage_count": 0
                },
                "H2SO4": {
                    "category": "chemistry",
                    "type": "chemical_formula",
                    "adaptations": {
                        "dyslexia": "Sulfuric acid (H2SO4) - strong acid",
                        "adhd": "H2SO4 = Powerful acid",
                        "esl": "H2SO4 (sulfuric acid - a very strong and dangerous acid)"
                    },
                    "definition": "Sulfuric acid, a strong mineral acid",
                    "usage_count": 0
                },
                
                # Biology - Genetic and cellular terms
                "DNA": {
                    "category": "biology",
                    "type": "abbreviation",
                    "adaptations": {
                        "dyslexia": "DNA - genetic code in cells",
                        "adhd": "DNA = Your genetic blueprint",
                        "esl": "DNA (genetic material that controls how living things grow)"
                    },
                    "definition": "Deoxyribonucleic acid, genetic material",
                    "usage_count": 0
                },
                "RNA": {
                    "category": "biology",
                    "type": "abbreviation", 
                    "adaptations": {
                        "dyslexia": "RNA - helps make proteins",
                        "adhd": "RNA = Protein maker",
                        "esl": "RNA (ribonucleic acid - helps cells make proteins)"
                    },
                    "definition": "Ribonucleic acid, involved in protein synthesis",
                    "usage_count": 0
                },
                "ATP": {
                    "category": "biology",
                    "type": "abbreviation",
                    "adaptations": {
                        "dyslexia": "ATP - cell energy",
                        "adhd": "ATP = Cell battery",
                        "esl": "ATP (cell energy - like a battery for living cells)"
                    },
                    "definition": "Adenosine triphosphate, cellular energy currency",
                    "usage_count": 0
                },
                
                # Physics - Units and concepts
                "pH": {
                    "category": "chemistry",
                    "type": "measurement",
                    "adaptations": {
                        "dyslexia": "pH - acid level (0-14 scale)",
                        "adhd": "pH = Acid strength",
                        "esl": "pH (acidity level - scale from 0 to 14)"
                    },
                    "definition": "Measure of acidity or alkalinity",
                    "usage_count": 0
                },
                "MHz": {
                    "category": "physics",
                    "type": "unit",
                    "adaptations": {
                        "dyslexia": "MHz - radio wave speed",
                        "adhd": "MHz = Radio frequency",
                        "esl": "MHz (megahertz - how fast radio waves vibrate)"
                    },
                    "definition": "Megahertz, unit of frequency",
                    "usage_count": 0
                },
                "UV": {
                    "category": "physics",
                    "type": "abbreviation",
                    "adaptations": {
                        "dyslexia": "UV light - invisible sun rays",
                        "adhd": "UV = Invisible sunlight",
                        "esl": "UV (ultraviolet light - invisible rays from the sun)"
                    },
                    "definition": "Ultraviolet radiation",
                    "usage_count": 0
                },
                
                # Mathematics
                "log": {
                    "category": "mathematics",
                    "type": "function",
                    "adaptations": {
                        "dyslexia": "log - math function for big numbers",
                        "adhd": "log = Special math operation",
                        "esl": "log (logarithm - mathematical operation for large numbers)"
                    },
                    "definition": "Logarithm, mathematical function",
                    "usage_count": 0
                },
                "sin": {
                    "category": "mathematics", 
                    "type": "function",
                    "adaptations": {
                        "dyslexia": "sin - triangle math",
                        "adhd": "sin = Triangle function",
                        "esl": "sin (sine - mathematical function used with triangles)"
                    },
                    "definition": "Sine, trigonometric function",
                    "usage_count": 0
                },
                
                # Medical/Health
                "BMI": {
                    "category": "medical",
                    "type": "abbreviation",
                    "adaptations": {
                        "dyslexia": "BMI - body weight measure",
                        "adhd": "BMI = Health weight index",
                        "esl": "BMI (body mass index - measures if weight is healthy)"
                    },
                    "definition": "Body Mass Index, health metric",
                    "usage_count": 0
                },
                "ECG": {
                    "category": "medical",
                    "type": "abbreviation",
                    "adaptations": {
                        "dyslexia": "ECG - heart test",
                        "adhd": "ECG = Heart monitor",
                        "esl": "ECG (electrocardiogram - test that shows heart rhythm)"
                    },
                    "definition": "Electrocardiogram, heart rhythm test",
                    "usage_count": 0
                }
            }
        }
    
    def _save_dictionary(self, dictionary: Dict[str, Any]) -> None:
        """Save dictionary to file"""
        try:
            # Update metadata
            dictionary["metadata"]["last_updated"] = datetime.now().isoformat()
            dictionary["metadata"]["total_terms"] = len(dictionary.get("terms", {}))
            
            with open(self.dictionary_path, 'w', encoding='utf-8') as f:
                json.dump(dictionary, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Error saving dictionary: {e}")
    
    def get_adaptation(self, term: str, profile: str) -> Optional[str]:
        """Get adaptation for a term based on learning profile"""
        try:
            term_lower = term.lower()
            
            # Try exact match first
            if term in self.dictionary.get("terms", {}):
                term_data = self.dictionary["terms"][term]
            elif term_lower in self.dictionary.get("terms", {}):
                term_data = self.dictionary["terms"][term_lower]
            else:
                # Try case-insensitive search
                term_data = None
                for dict_term, data in self.dictionary.get("terms", {}).items():
                    if dict_term.lower() == term_lower:
                        term_data = data
                        break
                
                if not term_data:
                    return None
            
            # Update usage statistics
            self._update_usage_stats(term)
            
            # Get profile-specific adaptation
            adaptations = term_data.get("adaptations", {})
            profile_lower = profile.lower()
            
            if profile_lower in adaptations:
                return adaptations[profile_lower]
            elif "default" in adaptations:
                return adaptations["default"]
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting adaptation for {term}: {e}")
            return None
    
    def add_term(self, term: str, category: str, term_type: str, 
                 adaptations: Dict[str, str], definition: str = "") -> bool:
        """Add a new term to the dictionary"""
        try:
            if "terms" not in self.dictionary:
                self.dictionary["terms"] = {}
            
            self.dictionary["terms"][term] = {
                "category": category,
                "type": term_type,
                "adaptations": adaptations,
                "definition": definition,
                "usage_count": 0,
                "added_date": datetime.now().isoformat()
            }
            
            self._save_dictionary(self.dictionary)
            self.logger.info(f"Added new term: {term}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding term {term}: {e}")
            return False
    
    def update_term(self, term: str, updates: Dict[str, Any]) -> bool:
        """Update an existing term"""
        try:
            if term not in self.dictionary.get("terms", {}):
                return False
            
            for key, value in updates.items():
                if key in ["adaptations", "definition", "category", "type"]:
                    self.dictionary["terms"][term][key] = value
            
            self.dictionary["terms"][term]["last_updated"] = datetime.now().isoformat()
            self._save_dictionary(self.dictionary)
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating term {term}: {e}")
            return False
    
    def _update_usage_stats(self, term: str) -> None:
        """Update usage statistics for a term"""
        try:
            if term in self.dictionary.get("terms", {}):
                self.dictionary["terms"][term]["usage_count"] += 1
                
                # Update session stats
                if term not in self.usage_stats:
                    self.usage_stats[term] = 0
                self.usage_stats[term] += 1
                
        except Exception as e:
            self.logger.error(f"Error updating usage stats for {term}: {e}")
    
    def get_terms_by_category(self, category: str) -> Dict[str, Any]:
        """Get all terms in a specific category"""
        terms = {}
        for term, data in self.dictionary.get("terms", {}).items():
            if data.get("category", "").lower() == category.lower():
                terms[term] = data
        return terms
    
    def search_terms(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for terms containing the query string"""
        results = []
        query_lower = query.lower()
        
        for term, data in self.dictionary.get("terms", {}).items():
            if (query_lower in term.lower() or 
                query_lower in data.get("definition", "").lower()):
                results.append({
                    "term": term,
                    "category": data.get("category", ""),
                    "definition": data.get("definition", ""),
                    "adaptations": data.get("adaptations", {})
                })
                
                if len(results) >= limit:
                    break
        
        return results
    
    def get_most_used_terms(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get the most frequently used terms"""
        terms_with_usage = []
        
        for term, data in self.dictionary.get("terms", {}).items():
            usage_count = data.get("usage_count", 0)
            terms_with_usage.append({
                "term": term,
                "usage_count": usage_count,
                "category": data.get("category", ""),
                "adaptations": data.get("adaptations", {})
            })
        
        # Sort by usage count
        terms_with_usage.sort(key=lambda x: x["usage_count"], reverse=True)
        
        return terms_with_usage[:limit]
    
    def export_dictionary(self, export_path: str) -> bool:
        """Export dictionary to a different file"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.dictionary, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Error exporting dictionary: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get dictionary statistics"""
        terms = self.dictionary.get("terms", {})
        
        # Count by category
        category_counts = {}
        for term_data in terms.values():
            category = term_data.get("category", "unknown")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Count by type
        type_counts = {}
        for term_data in terms.values():
            term_type = term_data.get("type", "unknown")
            type_counts[term_type] = type_counts.get(term_type, 0) + 1
        
        total_usage = sum(data.get("usage_count", 0) for data in terms.values())
        
        return {
            "total_terms": len(terms),
            "categories": category_counts,
            "types": type_counts,
            "total_usage": total_usage,
            "session_usage": len(self.usage_stats),
            "metadata": self.dictionary.get("metadata", {})
        }
    
    def suggest_missing_terms(self, text: str) -> List[str]:
        """Analyze text and suggest terms that might need dictionary entries"""
        import re
        
        suggestions = []
        
        # Common patterns for scientific terms
        patterns = [
            r'\b[A-Z][a-z]*\d+[A-Z][a-z]*\d*\b',  # Chemical formulas like Fe2O3
            r'\b[A-Z]{2,5}\b',                      # Abbreviations like DNA, RNA
            r'\b\w+pH\b|\bpH\w*\b',                # pH related terms
            r'\b\d+[A-Za-z]+\b',                   # Units like 5mL, 10kg
            r'\b[A-Z][a-z]*-\d+\b',                # Isotopes like Carbon-14
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if (match not in self.dictionary.get("terms", {}) and 
                    match not in suggestions and
                    len(match) >= 2):
                    suggestions.append(match)
        
        return suggestions[:10]  # Return top 10 suggestions