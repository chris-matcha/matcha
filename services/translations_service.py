"""
Translations Service

Handles content translation for multilingual support.
"""
from typing import Dict, Any, List, Optional
from .base_service import BaseService
import anthropic


class TranslationsService(BaseService):
    """Service for content translation"""
    
    SUPPORTED_LANGUAGES = {
        'spanish': 'Spanish',
        'french': 'French',
        'german': 'German',
        'italian': 'Italian',
        'portuguese': 'Portuguese',
        'dutch': 'Dutch',
        'polish': 'Polish',
        'ukrainian': 'Ukrainian',
        'russian': 'Russian',
        'japanese': 'Japanese',
        'korean': 'Korean',
        'chinese': 'Chinese (Simplified)',
        'arabic': 'Arabic',
        'hindi': 'Hindi'
    }
    
    def _initialize(self):
        """Initialize translation service"""
        self.api_key = self.config.get('anthropic_api_key')
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
            self.logger.warning("No Anthropic API key provided")
    
    def translate_content(self, content: Dict[str, Any], target_language: str) -> Dict[str, Any]:
        """
        Translate content to target language
        
        Args:
            content: Content to translate (pages or slides)
            target_language: Target language code
            
        Returns:
            Translated content
        """
        if not self.is_language_supported(target_language):
            raise ValueError(f"Unsupported language: {target_language}")
        
        translated_content = {
            'metadata': content.get('metadata', {}).copy()
        }
        translated_content['metadata']['language'] = target_language
        
        # Handle PDF content
        if 'pages' in content:
            translated_content['pages'] = []
            for page in content['pages']:
                translated_page = self._translate_page(page, target_language)
                translated_content['pages'].append(translated_page)
        
        # Handle PowerPoint content
        elif 'slides' in content:
            translated_content['slides'] = []
            for slide in content['slides']:
                translated_slide = self._translate_slide(slide, target_language)
                translated_content['slides'].append(translated_slide)
        
        return translated_content
    
    def _translate_page(self, page: Dict[str, Any], target_language: str) -> Dict[str, Any]:
        """Translate a single page"""
        translated_page = page.copy()
        
        text = page.get('text', '')
        if text and len(text.strip()) > 0:
            translated_page['text'] = self.translate_text(text, target_language)
        
        return translated_page
    
    def _translate_slide(self, slide: Dict[str, Any], target_language: str) -> Dict[str, Any]:
        """Translate a single slide"""
        translated_slide = slide.copy()
        
        # Translate title
        if slide.get('title'):
            translated_slide['title'] = self.translate_text(slide['title'], target_language)
        
        # Translate content
        if slide.get('content'):
            translated_slide['content'] = self.translate_text(slide['content'], target_language)
        
        # Translate notes
        if slide.get('notes'):
            translated_slide['notes'] = self.translate_text(slide['notes'], target_language)
        
        return translated_slide
    
    def translate_text(self, text: str, target_language: str) -> str:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language code
            
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text
        
        if self.client:
            return self._translate_with_ai(text, target_language)
        else:
            # Fallback: return original text with language marker
            return f"[{target_language.upper()}] {text}"
    
    def _translate_with_ai(self, text: str, target_language: str) -> str:
        """Translate using AI with language-specific optimizations"""
        language_name = self.SUPPORTED_LANGUAGES.get(target_language, target_language)
        
        try:
            # Add language-specific instructions
            special_instructions = self._get_language_instructions(target_language)
            
            prompt = f"""Translate the following text to {language_name}.
Maintain the original formatting, including line breaks and bullet points.
Ensure the translation sounds natural and conversational.
If there are technical terms, provide the translation followed by the original in parentheses.
{special_instructions}

IMPORTANT: Provide ONLY the translated text. Do not include prefixes like "Here's the translation", "The translation is", or explanatory notes. Return only the direct translation.

Original text:
{text}

Translated text:"""
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=4000,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            translated_text = response.content[0].text
            
            # Clean up any conversational prefixes that might still appear
            cleaned_text = self._clean_translation_response(translated_text)
            
            return cleaned_text
            
        except Exception as e:
            self.logger.error(f"Translation failed: {str(e)}")
            return text
    
    def _clean_translation_response(self, text: str) -> str:
        """
        Clean up conversational prefixes from translation responses
        
        Args:
            text: Raw translation response
            
        Returns:
            Cleaned translation text
        """
        if not text or not text.strip():
            return text
        
        lines = text.strip().split('\n')
        cleaned_lines = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Skip lines that are conversational prefixes
            conversational_prefixes = [
                "here's the translation",
                "here is the translation", 
                "the translation is",
                "translation:",
                "translated text:",
                "translation follows:",
                "maintaining the original formatting",
                "following the guidelines you provided"
            ]
            
            # Check if the line starts with any conversational prefix
            is_prefix = False
            for prefix in conversational_prefixes:
                if line_lower.startswith(prefix):
                    is_prefix = True
                    break
            
            # Skip prefix lines, keep content
            if not is_prefix and line.strip():
                cleaned_lines.append(line)
        
        # Join the cleaned lines
        cleaned_text = '\n'.join(cleaned_lines).strip()
        
        # If we cleaned everything away, return the original (safety fallback)
        if not cleaned_text:
            return text
        
        return cleaned_text
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if a language is supported"""
        return language_code in self.SUPPORTED_LANGUAGES
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages"""
        languages = []
        for code, name in self.SUPPORTED_LANGUAGES.items():
            languages.append({
                'code': code,
                'name': name
            })
        return languages
    
    def detect_language(self, text: str) -> Optional[str]:
        """Detect the language of text (if AI available)"""
        if not self.client or not text:
            return None
        
        try:
            prompt = f"""Detect the language of this text and return only the language code 
(e.g., 'english', 'spanish', 'french', etc.):

{text[:500]}"""
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=50,
                temperature=0,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            detected = response.content[0].text.strip().lower()
            return detected if detected in self.SUPPORTED_LANGUAGES else None
            
        except Exception as e:
            self.logger.error(f"Language detection failed: {str(e)}")
            return None
    
    def _get_language_instructions(self, target_language: str) -> str:
        """Get language-specific translation instructions"""
        target_language_lower = target_language.lower()
        
        if target_language_lower == "polish":
            return """
When translating to Polish:
- Maintain proper Polish diacritical marks (ą, ć, ę, ł, ń, ó, ś, ź, ż)
- Pay attention to grammatical cases and gender agreement
- For technical terms, consider including the English original in parentheses first time
"""
        elif target_language_lower == "ukrainian":
            return """
When translating to Ukrainian:
- Use modern Ukrainian vocabulary rather than Russified terms where possible
- Properly handle Ukrainian specific characters (є, і, ї, ґ)
- For technical/scientific terms, consider providing the English original in parentheses on first occurrence
"""
        elif target_language_lower in ["german", "deutsch"]:
            return """
When translating to German:
- Use proper German compound word formation
- Maintain formal/informal distinction appropriately
- Pay attention to German word order in complex sentences
"""
        elif target_language_lower in ["french", "français"]:
            return """
When translating to French:
- Use appropriate formality level (tu/vous)
- Maintain proper French accent marks and cedillas
- Follow French syntax for complex constructions
"""
        elif target_language_lower in ["spanish", "español"]:
            return """
When translating to Spanish:
- Use appropriate formality (tú/usted) for the context
- Maintain proper Spanish accent marks and special characters (ñ)
- Consider regional variations if context suggests a specific variant
"""
        
        return ""  # No special instructions for other languages