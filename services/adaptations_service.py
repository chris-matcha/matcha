"""
Adaptations Service

Core service for adapting content based on learning profiles.
"""
import re
import hashlib
import time
from typing import Dict, Any, List, Optional
from .base_service import BaseService
from .profiles_service import LearningProfilesService
import anthropic


class AdaptationCache:
    """Enhanced cache for storing text adaptation results with better hit rate"""
    def __init__(self, max_size=2000):
        self.cache = {}
        self.max_size = max_size
        self.access_times = {}
        self.hit_count = 0
        self.miss_count = 0
    
    def get_key(self, text, profile):
        """Generate a cache key based on text content and profile"""
        text_to_hash = self._normalize_text(text)
        text_hash = hashlib.md5(text_to_hash.encode()).hexdigest()
        profile_key = profile.lower() if profile else "default"
        return f"{text_hash}-{profile_key}"
    
    def _normalize_text(self, text):
        """Normalize text to improve cache hit rates"""
        if not text:
            return ""
        
        # Truncate very long texts for hashing
        text_to_process = text[:2000] if len(text) > 2000 else text
        
        # Normalize whitespace
        normalized = ' '.join(text_to_process.split())
        
        # Convert to lowercase for case-insensitive matching
        normalized = normalized.lower()
        
        return normalized
    
    def get(self, text, profile):
        """Get adaptation from cache if available with metrics tracking"""
        key = self.get_key(text, profile)
        
        if key in self.cache:
            self.hit_count += 1
            self.access_times[key] = time.time()
            return self.cache[key]
        
        self.miss_count += 1
        return None
    
    def set(self, text, profile, adapted_text):
        """Store adaptation in cache with cache eviction logic"""
        key = self.get_key(text, profile)
        
        # If cache is full, remove least recently used items
        if len(self.cache) >= self.max_size:
            # Find LRU key
            lru_key = min(self.access_times.items(), key=lambda x: x[1])[0]
            del self.cache[lru_key]
            del self.access_times[lru_key]
        
        self.cache[key] = adapted_text
        self.access_times[key] = time.time()
    
    def get_stats(self):
        """Get cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': f"{hit_rate:.1f}%",
            'cache_size': len(self.cache),
            'max_size': self.max_size
        }
    
    def clear(self):
        """Clear the cache"""
        self.cache.clear()
        self.access_times.clear()
        self.hit_count = 0
        self.miss_count = 0


class AdaptationsService(BaseService):
    """Service for content adaptation"""
    
    def _initialize(self):
        """Initialize adaptation service"""
        self.profiles_service = LearningProfilesService(self.config)
        self.api_key = self.config.get('anthropic_api_key')
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
            self.logger.warning("No Anthropic API key provided")
        
        # Initialize adaptation cache
        self.cache = AdaptationCache(max_size=2000)
        
        # Initialize scientific dictionary
        try:
            from .scientific_dictionary import ScientificDictionary
            self.scientific_dict = ScientificDictionary()
            self.logger.info("Scientific dictionary loaded successfully")
        except Exception as e:
            self.logger.warning(f"Scientific dictionary failed to load: {e}")
            self.scientific_dict = None
    
    def adapt_content(self, content: Dict[str, Any], profile_id: str, 
                     force_adaptation: bool = False) -> Dict[str, Any]:
        """
        Adapt content based on learning profile
        
        Args:
            content: Content to adapt (pages or slides)
            profile_id: Learning profile ID
            force_adaptation: Force adaptation even if metrics are acceptable
            
        Returns:
            Adapted content
        """
        if not self.profiles_service.validate_profile(profile_id):
            raise ValueError(f"Invalid profile: {profile_id}")
        
        adapted_content = {
            'metadata': content.get('metadata', {}).copy()
        }
        
        # Handle PDF content
        if 'pages' in content:
            adapted_content['pages'] = []
            for page in content['pages']:
                adapted_page = self._adapt_page(page, profile_id, force_adaptation)
                adapted_content['pages'].append(adapted_page)
        
        # Handle PowerPoint content
        elif 'slides' in content:
            adapted_content['slides'] = []
            for slide in content['slides']:
                adapted_slide = self._adapt_slide(slide, profile_id, force_adaptation)
                adapted_content['slides'].append(adapted_slide)
        
        return adapted_content
    
    def adapt_text(self, text: str, profile_id: str) -> str:
        """
        Simple text adaptation method for direct use
        
        Args:
            text: Text to adapt
            profile_id: Learning profile ID
            
        Returns:
            Adapted text
        """
        return self._adapt_text(text, profile_id)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache.get_stats()
    
    def get_dictionary_stats(self) -> Dict[str, Any]:
        """Get scientific dictionary statistics"""
        if self.scientific_dict:
            return self.scientific_dict.get_statistics()
        else:
            return {"error": "Scientific dictionary not available"}
    
    def add_scientific_term(self, term: str, category: str, term_type: str,
                           adaptations: Dict[str, str], definition: str = "") -> bool:
        """Add a new scientific term to the dictionary"""
        if self.scientific_dict:
            return self.scientific_dict.add_term(term, category, term_type, adaptations, definition)
        return False
    
    def search_scientific_terms(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for scientific terms"""
        if self.scientific_dict:
            return self.scientific_dict.search_terms(query, limit)
        return []
    
    def suggest_missing_terms(self, text: str) -> List[str]:
        """Suggest scientific terms that might need dictionary entries"""
        if self.scientific_dict:
            return self.scientific_dict.suggest_missing_terms(text)
        return []
    
    def get_most_used_scientific_terms(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get the most frequently used scientific terms"""
        if self.scientific_dict:
            return self.scientific_dict.get_most_used_terms(limit)
        return []
    
    def validate_adaptation(self, original_text: str, adapted_text: str, profile_id: str) -> Dict[str, Any]:
        """
        Validate that adaptation was successful
        
        Args:
            original_text: Original text before adaptation
            adapted_text: Text after adaptation
            profile_id: Learning profile used
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            'is_valid': True,
            'issues': [],
            'metrics': {}
        }
        
        # Check if text is identical
        if original_text == adapted_text and len(original_text.strip()) > 10:
            validation['is_valid'] = False
            validation['issues'].append('Adapted text is identical to original')
        
        # Check for empty or too short
        if not adapted_text or len(adapted_text.strip()) < 2:
            validation['is_valid'] = False
            validation['issues'].append('Adapted text is empty or too short')
        
        # Check for error messages
        error_indicators = [
            "I cannot", "I'm sorry", "I can't", "Unable to", 
            "Error:", "Failed to", "Not possible", "Cannot process"
        ]
        
        for indicator in error_indicators:
            if indicator in adapted_text[:100]:
                validation['is_valid'] = False
                validation['issues'].append(f'Adapted text contains error indicator: "{indicator}"')
                break
        
        # Calculate metrics
        if original_text and adapted_text:
            validation['metrics']['length_ratio'] = len(adapted_text) / len(original_text)
            validation['metrics']['original_length'] = len(original_text)
            validation['metrics']['adapted_length'] = len(adapted_text)
            
            # Word-level metrics
            original_words = original_text.split()
            adapted_words = adapted_text.split()
            validation['metrics']['original_word_count'] = len(original_words)
            validation['metrics']['adapted_word_count'] = len(adapted_words)
            
            # Average word length
            if original_words:
                validation['metrics']['original_avg_word_length'] = sum(len(w) for w in original_words) / len(original_words)
            if adapted_words:
                validation['metrics']['adapted_avg_word_length'] = sum(len(w) for w in adapted_words) / len(adapted_words)
            
            # Check extreme length ratios
            if validation['metrics']['length_ratio'] > 10.0 or validation['metrics']['length_ratio'] < 0.1:
                validation['is_valid'] = False
                validation['issues'].append(f"Extreme length ratio: {validation['metrics']['length_ratio']:.2f}")
        
        return validation
    
    def test_adaptation(self, profile_id: str = 'dyslexia') -> Dict[str, Any]:
        """
        Test if adaptation is working properly
        
        Args:
            profile_id: Profile to test
            
        Returns:
            Test results
        """
        test_text = "The implementation of complex technological solutions requires careful consideration of multiple interdependent factors and systematic analysis."
        
        try:
            adapted = self.adapt_text(test_text, profile_id)
            validation = self.validate_adaptation(test_text, adapted, profile_id)
            
            return {
                'success': validation['is_valid'],
                'original': test_text,
                'adapted': adapted,
                'validation': validation,
                'profile': profile_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'profile': profile_id
            }
    
    def _adapt_page(self, page: Dict[str, Any], profile_id: str, 
                   force_adaptation: bool) -> Dict[str, Any]:
        """Adapt a single page"""
        adapted_page = page.copy()
        
        text = page.get('text', '')
        if not text or len(text.strip()) < 2:
            return adapted_page
        
        # Check if adaptation is needed
        if not force_adaptation:
            metrics = self.calculate_readability_metrics(text)
            if not self.profiles_service.needs_adaptation(text, profile_id, metrics):
                return adapted_page
        
        # Adapt the text
        adapted_text = self._adapt_text(text, profile_id)
        adapted_page['text'] = adapted_text
        
        return adapted_page
    
    def _adapt_slide(self, slide: Dict[str, Any], profile_id: str,
                    force_adaptation: bool) -> Dict[str, Any]:
        """Adapt a single slide"""
        adapted_slide = slide.copy()
        
        # Adapt title
        if slide.get('title'):
            adapted_slide['title'] = self._adapt_text(slide['title'], profile_id)
        
        # Adapt content
        if slide.get('content'):
            adapted_slide['content'] = self._adapt_text(slide['content'], profile_id)
        
        # Adapt notes
        if slide.get('notes'):
            adapted_slide['notes'] = self._adapt_text(slide['notes'], profile_id)
        
        return adapted_slide
    
    def _adapt_text(self, text: str, profile_id: str, raise_on_failure: bool = False) -> str:
        """
        Adapt text using AI or rule-based methods
        
        Args:
            text: Text to adapt
            profile_id: Learning profile
            raise_on_failure: If True, raise exception on adaptation failure instead of returning original
            
        Returns:
            Adapted text
            
        Raises:
            RuntimeError: If adaptation fails and raise_on_failure is True
        """
        try:
            # First, try scientific dictionary for exact matches
            if self.scientific_dict:
                dict_adaptation = self.scientific_dict.get_adaptation(text.strip(), profile_id)
                if dict_adaptation:
                    self.logger.info(f"Scientific dictionary hit for '{text.strip()}' -> '{dict_adaptation}'")
                    return dict_adaptation
            
            # If no dictionary match, proceed with AI or rule-based adaptation
            if self.client:
                adapted = self._adapt_text_ai(text, profile_id)
            else:
                adapted = self._adapt_text_rules(text, profile_id)
            
            # Validate adaptation actually happened
            if adapted == text and len(text.strip()) > 10:
                # Check if this looks like a failed adaptation
                if raise_on_failure:
                    raise RuntimeError(f"Adaptation failed - output identical to input for profile {profile_id}")
                else:
                    self.logger.warning(f"Adaptation may have failed - output identical to input")
            
            return adapted
            
        except Exception as e:
            if raise_on_failure:
                raise RuntimeError(f"Adaptation failed: {str(e)}")
            else:
                self.logger.error(f"Adaptation failed, returning original: {str(e)}")
                return text
    
    def _adapt_text_ai(self, text: str, profile_id: str) -> str:
        """Adapt text using AI with caching"""
        # Skip processing very short text
        if len(text.strip()) < 2:
            return text
        
        # Normalize the profile to prevent case issues
        profile_id = profile_id.lower() if profile_id else "dyslexia"
        
        # Check cache first
        cached_result = self.cache.get(text, profile_id)
        if cached_result:
            self.logger.debug(f"Cache hit for {profile_id} adaptation")
            return cached_result
        
        try:
            # Build adaptation prompt using efficient format
            prompt = self._build_efficient_prompt(text, profile_id)
            
            self.logger.info(f"Calling AI for {profile_id} adaptation of {len(text)} chars")
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=4000,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            adapted_text = response.content[0].text.strip()
            
            # Validate the adapted text - ensure it's not just a placeholder or error
            if not adapted_text or len(adapted_text) < 5:
                self.logger.error(f"AI returned very short adapted text ({len(adapted_text)} chars)")
                raise ValueError(f"AI adaptation returned insufficient content")
            
            # Check for common AI errors or refusals
            error_indicators = [
                "I cannot", "I'm sorry", "I can't", "Unable to", 
                "Error:", "Failed to", "Not possible", "Cannot process",
                "I don't have", "I am not able"
            ]
            
            if any(indicator in adapted_text[:100] for indicator in error_indicators):
                self.logger.error(f"AI returned error/refusal response")
                raise ValueError(f"AI refused to adapt content")
            
            # Check if adaptation just returned the original text
            if adapted_text == text or adapted_text == f"Original:\n{text}\n\nAdapted:":
                self.logger.error(f"AI returned unmodified text")
                raise ValueError(f"AI failed to adapt content - returned original")
            
            # Ensure adapted text maintains reasonable length relationship to original
            # Educational adaptations can legitimately expand content significantly
            # Only flag extreme ratios that likely indicate errors
            length_ratio = len(adapted_text) / len(text)
            if length_ratio > 15.0 or length_ratio < 0.05:  # More lenient bounds
                self.logger.warning(f"Adapted text length ratio extreme ({length_ratio:.2f}) - may indicate adaptation issue")
                # Don't raise error, just log warning for very extreme cases
            
            # Additional validation: Check if the text was actually simplified/adapted
            # Count average word length as a rough proxy for simplification
            original_avg_word_len = sum(len(word) for word in text.split()) / max(1, len(text.split()))
            adapted_avg_word_len = sum(len(word) for word in adapted_text.split()) / max(1, len(adapted_text.split()))
            
            # For dyslexia and ESL, we expect simpler (shorter) words
            if profile_id in ['dyslexia', 'esl'] and adapted_avg_word_len > original_avg_word_len * 1.1:
                self.logger.warning(f"Adapted text may not be simplified (avg word length: {original_avg_word_len:.1f} -> {adapted_avg_word_len:.1f})")
            
            # Store in cache for future use
            self.cache.set(text, profile_id, adapted_text)
            
            self.logger.info(f"AI adaptation successful: {len(text)} -> {len(adapted_text)} chars")
            return adapted_text
            
        except Exception as e:
            self.logger.error(f"AI adaptation failed: {str(e)}")
            raise  # Re-raise the exception instead of silently returning original
    
    def _adapt_text_rules(self, text: str, profile_id: str) -> str:
        """Adapt text using rule-based methods"""
        adaptations = self.profiles_service.get_adaptations(profile_id)
        
        if adaptations.get('simplify_vocabulary'):
            text = self._simplify_vocabulary(text)
        
        if adaptations.get('shorten_sentences'):
            text = self._shorten_sentences(text)
        
        if adaptations.get('use_bullet_points'):
            text = self._convert_to_bullets(text)
        
        return text
    
    def _build_efficient_prompt(self, text: str, profile_id: str) -> str:
        """Build efficient prompt for AI adaptation"""
        # First line contains essential instructions, rest is just the content
        if profile_id == "dyslexia":
            instructions = "Adapt for dyslexia: short sentences (max 15 words), simple words, active voice, bullet points where appropriate. Keep meaning intact."
        elif profile_id == "adhd":
            instructions = "Adapt for ADHD: clear structure, short chunks, bullet points, highlight key info, remove unnecessary details. Keep meaning intact."
        else:  # ESL
            instructions = "Adapt for English learners: simpler words (original in parentheses), short sentences, explain idioms, consistent terms. Keep meaning intact."
        
        # Minimal format with clear sections
        prompt = f"{instructions}\n\nOriginal:\n{text}\n\nAdapted:"
        return prompt
    
    def _simplify_vocabulary(self, text: str) -> str:
        """Simple rule-based vocabulary simplification"""
        # Basic word replacements
        replacements = {
            'utilize': 'use',
            'implement': 'do',
            'demonstrate': 'show',
            'facilitate': 'help',
            'subsequently': 'then',
            'additional': 'more',
            'numerous': 'many'
        }
        
        for old, new in replacements.items():
            text = re.sub(rf'\b{old}\b', new, text, flags=re.IGNORECASE)
        
        return text
    
    def _shorten_sentences(self, text: str) -> str:
        """Break long sentences into shorter ones"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        shortened = []
        
        for sentence in sentences:
            if len(sentence) > 150:  # Long sentence
                # Try to break at conjunctions
                parts = re.split(r',\s*(?:and|but|or)\s*', sentence)
                shortened.extend(parts)
            else:
                shortened.append(sentence)
        
        return ' '.join(shortened)
    
    def _convert_to_bullets(self, text: str) -> str:
        """Convert paragraph text to bullet points"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        if len(sentences) > 3:
            # Convert to bullet points
            bullets = ['• ' + s.strip() for s in sentences if s.strip()]
            return '\n'.join(bullets)
        return text
    
    def calculate_readability_metrics(self, text: str) -> Dict[str, float]:
        """Calculate readability metrics for text"""
        # Simple implementations - in production, use proper libraries
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        syllables = sum(self._count_syllables(word) for word in words)
        
        # Flesch Reading Ease
        if len(sentences) > 0 and len(words) > 0:
            flesch = 206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (syllables / len(words))
        else:
            flesch = 0
        
        # Grade Level (simplified)
        grade_level = 0.39 * (len(words) / len(sentences)) + 11.8 * (syllables / len(words)) - 15.59
        
        return {
            'flesch_ease': max(0, min(100, flesch)),
            'grade_level': max(0, grade_level),
            'word_count': len(words),
            'sentence_count': len(sentences)
        }
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)"""
        word = word.lower()
        count = 0
        vowels = 'aeiouy'
        if word[0] in vowels:
            count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        if word.endswith('e'):
            count -= 1
        if word.endswith('le'):
            count += 1
        if count == 0:
            count += 1
        return count
    
    def process_text_batch(self, texts: List[str], profile_id: str, 
                          max_batch_size: int = 5, max_tokens_per_batch: int = 4000) -> List[str]:
        """
        Process multiple text elements in efficient batches
        
        Args:
            texts: List of texts to adapt
            profile_id: Learning profile ID
            max_batch_size: Maximum texts per batch
            max_tokens_per_batch: Maximum estimated tokens per batch
            
        Returns:
            List of adapted texts
        """
        results = []
        current_batch = []
        current_batch_tokens = 0
        
        def estimate_tokens(text: str) -> int:
            """Roughly estimate token count based on character count"""
            return len(text) // 4  # Approximation: ~4 chars per token
        
        # Group texts into efficient batches
        for text in texts:
            text_tokens = estimate_tokens(text)
            
            # If this text would make the batch too large, process the current batch first
            if (len(current_batch) >= max_batch_size or 
                (current_batch_tokens + text_tokens > max_tokens_per_batch and current_batch)):
                # Process the current batch
                batch_results = self._process_single_batch(current_batch, profile_id)
                results.extend(batch_results)
                current_batch = []
                current_batch_tokens = 0
            
            # Add this text to the current batch
            current_batch.append(text)
            current_batch_tokens += text_tokens
        
        # Process any remaining texts in the final batch
        if current_batch:
            batch_results = self._process_single_batch(current_batch, profile_id)
            results.extend(batch_results)
        
        return results
    
    def _process_single_batch(self, texts: List[str], profile_id: str) -> List[str]:
        """
        Process a single batch of texts using one API call
        
        Args:
            texts: List of texts in the batch
            profile_id: Learning profile ID
            
        Returns:
            List of adapted texts
        """
        # For very small batches, process individually
        if len(texts) <= 1:
            return [self._adapt_text(texts[0], profile_id)] if texts else []
        
        # Skip if no AI client available
        if not self.client:
            # Fallback to rule-based processing
            return [self._adapt_text_rules(text, profile_id) for text in texts]
        
        # Create a single prompt with multiple texts
        profile_name = profile_id.title()
        instructions = self._get_batch_instructions(profile_id)
        
        combined_prompt = f"{instructions}\n\nFormat your response using exactly '### TEXT N ###' before each adapted text (where N is the text number).\n\n"
        
        for i, text in enumerate(texts):
            combined_prompt += f"### TEXT {i+1} ###\n{text}\n\n"
        
        try:
            # Call API with the combined prompt
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=8000,  # Larger token limit for batch processing
                temperature=0.3,
                messages=[
                    {"role": "user", "content": combined_prompt}
                ]
            )
            
            # Parse the response to extract individual adapted texts
            content = response.content[0].text
            
            # Parse using regex
            import re
            pattern = r'###\s*TEXT\s*(\d+)\s*###\s*(.*?)(?=###\s*TEXT\s*\d+\s*###|$)'
            matches = re.findall(pattern, content, re.DOTALL)
            
            # Create a dictionary to maintain order
            text_dict = {}
            for match in matches:
                text_num = int(match[0])
                if 1 <= text_num <= len(texts):  # Ensure valid text number
                    text_dict[text_num] = match[1].strip()
            
            # If we don't have matches for all texts, fall back to individual processing
            if len(text_dict) != len(texts):
                self.logger.warning("Batch processing response parsing failed. Falling back to individual processing.")
                return [self._adapt_text(text, profile_id) for text in texts]
            
            # Convert dictionary to ordered list
            adapted_texts = []
            for i in range(1, len(texts) + 1):
                if i in text_dict:
                    adapted_texts.append(text_dict[i])
                else:
                    # If missing a specific text, adapt it individually
                    adapted_texts.append(self._adapt_text(texts[i-1], profile_id))
            
            return adapted_texts
            
        except Exception as e:
            self.logger.error(f"Error in batch processing: {str(e)}")
            # Fall back to individual processing
            return [self._adapt_text(text, profile_id) for text in texts]
    
    def _get_batch_instructions(self, profile_id: str) -> str:
        """Get batch processing instructions for a profile"""
        if profile_id == "dyslexia":
            return "Adapt the following texts for dyslexia users: short sentences (max 15 words), simple words, active voice, bullet points where appropriate. Keep meaning intact."
        elif profile_id == "adhd":
            return "Adapt the following texts for ADHD users: clear structure, short chunks, bullet points, highlight key info, remove unnecessary details. Keep meaning intact."
        else:  # ESL
            return "Adapt the following texts for English learners: simpler words (original in parentheses), short sentences, explain idioms, consistent terms. Keep meaning intact."