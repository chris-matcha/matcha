"""
Assessments Service

Analyzes content and provides recommendations based on learning profiles.
"""
import re
from typing import Dict, Any, List, Optional, Tuple
from collections import Counter
from .base_service import BaseService
from .profiles_service import LearningProfilesService
from .adaptations_service import AdaptationsService


class AssessmentsService(BaseService):
    """Service for content assessment and analysis"""
    
    def _initialize(self):
        """Initialize assessment service"""
        self.profiles_service = LearningProfilesService(self.config)
        self.adaptations_service = AdaptationsService(self.config)
    
    def assess_content(self, content: Dict[str, Any], profile_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive content assessment
        
        Args:
            content: Content to assess
            profile_id: Optional profile to assess against
            
        Returns:
            Assessment results
        """
        assessment = {
            'readability_metrics': {},
            'content_analysis': {},
            'recommendations': [],
            'profile_suitability': {}
        }
        
        # Extract all text
        all_text = self._extract_all_text(content)
        
        if not all_text:
            assessment['error'] = "No text content found"
            return assessment
        
        # Calculate readability metrics
        assessment['readability_metrics'] = self._calculate_comprehensive_metrics(all_text)
        
        # Analyze content structure
        assessment['content_analysis'] = self._analyze_content_structure(content)
        
        # Check against specific profile or all profiles
        if profile_id:
            assessment['profile_suitability'][profile_id] = self._assess_profile_suitability(
                all_text, profile_id, assessment['readability_metrics']
            )
        else:
            # Check against all profiles
            for pid in ['dyslexia', 'adhd', 'esl']:
                assessment['profile_suitability'][pid] = self._assess_profile_suitability(
                    all_text, pid, assessment['readability_metrics']
                )
        
        # Generate recommendations
        assessment['recommendations'] = self._generate_recommendations(
            assessment['readability_metrics'],
            assessment['profile_suitability']
        )
        
        return assessment
    
    def _extract_all_text(self, content: Dict[str, Any]) -> str:
        """Extract all text from content"""
        text_parts = []
        
        # PDF content
        if 'pages' in content:
            for page in content['pages']:
                if page.get('text'):
                    text_parts.append(page['text'])
        
        # PowerPoint content
        elif 'slides' in content:
            for slide in content['slides']:
                if slide.get('title'):
                    text_parts.append(slide['title'])
                if slide.get('content'):
                    text_parts.append(slide['content'])
                if slide.get('notes'):
                    text_parts.append(slide['notes'])
        
        return '\n\n'.join(text_parts)
    
    def _calculate_comprehensive_metrics(self, text: str) -> Dict[str, Any]:
        """Calculate comprehensive readability metrics"""
        # Use the adaptations service for basic metrics
        basic_metrics = self.adaptations_service.calculate_readability_metrics(text)
        
        # Add additional metrics
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        # Complex word count (3+ syllables)
        complex_words = [w for w in words if self._count_syllables(w) >= 3]
        
        # Average sentence length
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # Passive voice detection (simplified)
        passive_count = len(re.findall(r'\b(was|were|been|being|is|are|am)\s+\w+ed\b', text))
        
        metrics = {
            **basic_metrics,
            'complex_word_count': len(complex_words),
            'complex_word_percentage': (len(complex_words) / len(words) * 100) if words else 0,
            'avg_sentence_length': avg_sentence_length,
            'passive_voice_count': passive_count,
            'paragraph_count': len(text.split('\n\n')),
            'avg_words_per_paragraph': len(words) / len(text.split('\n\n')) if text.split('\n\n') else 0
        }
        
        # Calculate SMOG index
        if len(sentences) >= 30:
            smog = 1.0430 * (30 * len(complex_words) / len(sentences)) ** 0.5 + 3.1291
            metrics['smog_index'] = smog
        else:
            metrics['smog_index'] = None
        
        return metrics
    
    def _analyze_content_structure(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content structure and organization"""
        analysis = {
            'structure_type': 'unknown',
            'organization_score': 0,
            'key_elements': []
        }
        
        # PDF analysis
        if 'pages' in content:
            analysis['structure_type'] = 'document'
            analysis['page_count'] = len(content['pages'])
            
            # Check for headers, lists, etc.
            for page in content['pages']:
                text = page.get('text', '')
                if re.search(r'^#{1,3}\s+.+$', text, re.MULTILINE):
                    analysis['key_elements'].append('headers')
                if re.search(r'^[\*\-]\s+.+$', text, re.MULTILINE):
                    analysis['key_elements'].append('bullet_points')
                if re.search(r'^\d+\.\s+.+$', text, re.MULTILINE):
                    analysis['key_elements'].append('numbered_lists')
        
        # PowerPoint analysis
        elif 'slides' in content:
            analysis['structure_type'] = 'presentation'
            analysis['slide_count'] = len(content['slides'])
            
            # Analyze slide patterns
            title_count = sum(1 for s in content['slides'] if s.get('title'))
            content_count = sum(1 for s in content['slides'] if s.get('content'))
            notes_count = sum(1 for s in content['slides'] if s.get('notes'))
            
            analysis['title_coverage'] = title_count / len(content['slides']) if content['slides'] else 0
            analysis['content_coverage'] = content_count / len(content['slides']) if content['slides'] else 0
            analysis['notes_coverage'] = notes_count / len(content['slides']) if content['slides'] else 0
        
        # Calculate organization score (0-100)
        if analysis['key_elements']:
            analysis['organization_score'] = min(100, len(set(analysis['key_elements'])) * 25)
        
        return analysis
    
    def _assess_profile_suitability(self, text: str, profile_id: str, 
                                   metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess how suitable content is for a specific profile"""
        profile = self.profiles_service.get_profile(profile_id)
        if not profile:
            return {'error': 'Invalid profile'}
        
        thresholds = profile['thresholds']
        suitability = {
            'overall_score': 100,
            'issues': [],
            'strengths': []
        }
        
        # Check each metric against thresholds
        if metrics.get('flesch_ease', 0) < thresholds.get('flesch_ease', 60):
            penalty = (thresholds['flesch_ease'] - metrics['flesch_ease']) / thresholds['flesch_ease'] * 30
            suitability['overall_score'] -= penalty
            suitability['issues'].append(f"Reading ease too low ({metrics['flesch_ease']:.1f} vs {thresholds['flesch_ease']} required)")
        else:
            suitability['strengths'].append("Good reading ease")
        
        if metrics.get('grade_level', 999) > thresholds.get('grade_level', 8):
            penalty = (metrics['grade_level'] - thresholds['grade_level']) / thresholds['grade_level'] * 30
            suitability['overall_score'] -= penalty
            suitability['issues'].append(f"Grade level too high ({metrics['grade_level']:.1f} vs {thresholds['grade_level']} max)")
        else:
            suitability['strengths'].append("Appropriate grade level")
        
        if metrics.get('complex_word_percentage', 100) > thresholds.get('complex_word_threshold', 10):
            penalty = (metrics['complex_word_percentage'] - thresholds['complex_word_threshold']) / thresholds['complex_word_threshold'] * 20
            suitability['overall_score'] -= penalty
            suitability['issues'].append(f"Too many complex words ({metrics['complex_word_percentage']:.1f}%)")
        else:
            suitability['strengths'].append("Good vocabulary complexity")
        
        # Ensure score is between 0 and 100
        suitability['overall_score'] = max(0, min(100, suitability['overall_score']))
        
        # Add recommendation
        if suitability['overall_score'] >= 80:
            suitability['recommendation'] = "Content is well-suited for this profile"
        elif suitability['overall_score'] >= 60:
            suitability['recommendation'] = "Content needs minor adaptations"
        else:
            suitability['recommendation'] = "Content needs significant adaptations"
        
        return suitability
    
    def _generate_recommendations(self, metrics: Dict[str, Any], 
                                 profile_suitability: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # General readability recommendations
        if metrics.get('flesch_ease', 0) < 50:
            recommendations.append("Simplify vocabulary and sentence structure to improve readability")
        
        if metrics.get('avg_sentence_length', 0) > 20:
            recommendations.append("Break long sentences into shorter, clearer statements")
        
        if metrics.get('complex_word_percentage', 0) > 15:
            recommendations.append("Replace complex words with simpler alternatives where possible")
        
        if metrics.get('passive_voice_count', 0) > 5:
            recommendations.append("Convert passive voice to active voice for clearer communication")
        
        # Profile-specific recommendations
        for profile_id, suitability in profile_suitability.items():
            if suitability.get('overall_score', 100) < 60:
                profile_name = self.profiles_service.get_profile(profile_id)['name']
                recommendations.append(f"Consider using 'Direct Adaptation' for {profile_name}")
        
        return recommendations
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word"""
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
    
    def identify_complex_words(self, text: str, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Identify the most complex words in the text
        
        Args:
            text: Text to analyze
            limit: Maximum number of words to return
            
        Returns:
            List of (word, syllable_count) tuples
        """
        words = re.findall(r'\b\w+\b', text.lower())
        word_complexity = []
        
        for word in set(words):
            if len(word) > 3:  # Skip short words
                syllables = self._count_syllables(word)
                if syllables >= 3:
                    word_complexity.append((word, syllables))
        
        # Sort by syllable count and return top N
        word_complexity.sort(key=lambda x: x[1], reverse=True)
        return word_complexity[:limit]