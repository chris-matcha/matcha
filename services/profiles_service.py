"""
Learning Profiles Service

Manages learning profiles (Dyslexia, ADHD, ESL) and their configurations.
"""
from typing import Dict, Any, List, Optional
from .base_service import BaseService


class LearningProfilesService(BaseService):
    """Service for managing learning profiles"""
    
    # Default profile configurations
    PROFILES = {
        'dyslexia': {
            'name': 'Dyslexia Support',
            'description': 'Optimized for learners with dyslexia',
            'thresholds': {
                'flesch_ease': 60,
                'grade_level': 8,
                'smog_index': 8,
                'complex_word_threshold': 10
            },
            'formatting': {
                'font': 'Arial',
                'font_size': 14,
                'line_spacing': 1.5,
                'background_color': '#FFFEF5',  # Light yellow
                'text_color': '#000080',  # Dark blue
                'highlight_color': '#0066CC'
            },
            'adaptations': {
                'simplify_vocabulary': True,
                'shorten_sentences': True,
                'increase_spacing': True,
                'use_bullet_points': True
            }
        },
        'adhd': {
            'name': 'ADHD Support',
            'description': 'Designed for learners with ADHD',
            'thresholds': {
                'flesch_ease': 70,
                'grade_level': 7,
                'smog_index': 7,
                'complex_word_threshold': 8
            },
            'formatting': {
                'font': 'Verdana',
                'font_size': 13,
                'line_spacing': 1.4,
                'background_color': '#F0FFF0',  # Light green
                'text_color': '#004D00',  # Dark green
                'highlight_color': '#2E8B57'
            },
            'adaptations': {
                'break_into_chunks': True,
                'add_visual_breaks': True,
                'highlight_key_points': True,
                'reduce_distractions': True
            }
        },
        'esl': {
            'name': 'English Language Learners',
            'description': 'Adapted for non-native English speakers',
            'thresholds': {
                'flesch_ease': 80,
                'grade_level': 6,
                'smog_index': 6,
                'complex_word_threshold': 5
            },
            'formatting': {
                'font': 'Calibri',
                'font_size': 13,
                'line_spacing': 1.3,
                'background_color': '#FAF5FF',  # Light purple
                'text_color': '#4B0082',  # Indigo
                'highlight_color': '#9400D3'
            },
            'adaptations': {
                'simplify_idioms': True,
                'explain_complex_terms': True,
                'add_context_clues': True,
                'support_translation': True
            }
        }
    }
    
    def _initialize(self):
        """Initialize profiles with custom configurations if provided"""
        # Merge custom profiles with defaults
        custom_profiles = self.config.get('profiles', {})
        for profile_id, custom_config in custom_profiles.items():
            if profile_id in self.PROFILES:
                self.PROFILES[profile_id].update(custom_config)
            else:
                self.PROFILES[profile_id] = custom_config
    
    def get_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific profile configuration
        
        Args:
            profile_id: Profile identifier (dyslexia, adhd, esl)
            
        Returns:
            Profile configuration or None if not found
        """
        return self.PROFILES.get(profile_id)
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """
        List all available profiles
        
        Returns:
            List of profile summaries
        """
        profiles = []
        for profile_id, config in self.PROFILES.items():
            profiles.append({
                'id': profile_id,
                'name': config['name'],
                'description': config['description']
            })
        return profiles
    
    def get_thresholds(self, profile_id: str) -> Dict[str, Any]:
        """Get readability thresholds for a profile"""
        profile = self.get_profile(profile_id)
        if not profile:
            return {}
        return profile.get('thresholds', {})
    
    def get_formatting(self, profile_id: str) -> Dict[str, Any]:
        """Get formatting preferences for a profile"""
        profile = self.get_profile(profile_id)
        if not profile:
            return {}
        return profile.get('formatting', {})
    
    def get_adaptations(self, profile_id: str) -> Dict[str, Any]:
        """Get adaptation settings for a profile"""
        profile = self.get_profile(profile_id)
        if not profile:
            return {}
        return profile.get('adaptations', {})
    
    def needs_adaptation(self, text: str, profile_id: str, metrics: Dict[str, float]) -> bool:
        """
        Check if text needs adaptation based on profile thresholds
        
        Args:
            text: Text to check
            profile_id: Profile to check against
            metrics: Pre-calculated readability metrics
            
        Returns:
            bool: True if adaptation is needed
        """
        thresholds = self.get_thresholds(profile_id)
        if not thresholds:
            return False
        
        # Check each metric against thresholds
        needs_adapt = False
        
        if 'flesch_ease' in metrics and 'flesch_ease' in thresholds:
            if metrics['flesch_ease'] < thresholds['flesch_ease']:
                needs_adapt = True
                
        if 'grade_level' in metrics and 'grade_level' in thresholds:
            if metrics['grade_level'] > thresholds['grade_level']:
                needs_adapt = True
                
        if 'smog_index' in metrics and 'smog_index' in thresholds:
            if metrics['smog_index'] > thresholds['smog_index']:
                needs_adapt = True
        
        return needs_adapt
    
    def get_profile_colors(self, profile_id: str) -> Dict[str, str]:
        """Get color scheme for a profile"""
        formatting = self.get_formatting(profile_id)
        return {
            'background': formatting.get('background_color', '#FFFFFF'),
            'text': formatting.get('text_color', '#000000'),
            'highlight': formatting.get('highlight_color', '#0000FF')
        }
    
    def validate_profile(self, profile_id: str) -> bool:
        """Check if a profile ID is valid"""
        return profile_id in self.PROFILES