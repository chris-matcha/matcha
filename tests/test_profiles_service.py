"""
Test Learning Profiles Service

Example tests showing how services can be tested in isolation.
"""
import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import LearningProfilesService


class TestLearningProfilesService(unittest.TestCase):
    """Test cases for Learning Profiles Service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = LearningProfilesService({})
    
    def test_list_profiles(self):
        """Test listing all profiles"""
        profiles = self.service.list_profiles()
        
        # Should have 3 default profiles
        self.assertEqual(len(profiles), 3)
        
        # Check profile IDs
        profile_ids = [p['id'] for p in profiles]
        self.assertIn('dyslexia', profile_ids)
        self.assertIn('adhd', profile_ids)
        self.assertIn('esl', profile_ids)
    
    def test_get_profile(self):
        """Test getting a specific profile"""
        profile = self.service.get_profile('dyslexia')
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile['name'], 'Dyslexia Support')
        self.assertIn('thresholds', profile)
        self.assertIn('formatting', profile)
        self.assertIn('adaptations', profile)
    
    def test_get_invalid_profile(self):
        """Test getting non-existent profile"""
        profile = self.service.get_profile('invalid')
        self.assertIsNone(profile)
    
    def test_validate_profile(self):
        """Test profile validation"""
        self.assertTrue(self.service.validate_profile('dyslexia'))
        self.assertTrue(self.service.validate_profile('adhd'))
        self.assertTrue(self.service.validate_profile('esl'))
        self.assertFalse(self.service.validate_profile('invalid'))
    
    def test_get_thresholds(self):
        """Test getting profile thresholds"""
        thresholds = self.service.get_thresholds('dyslexia')
        
        self.assertIn('flesch_ease', thresholds)
        self.assertIn('grade_level', thresholds)
        self.assertEqual(thresholds['flesch_ease'], 60)
        self.assertEqual(thresholds['grade_level'], 8)
    
    def test_get_formatting(self):
        """Test getting profile formatting"""
        formatting = self.service.get_formatting('adhd')
        
        self.assertIn('font', formatting)
        self.assertIn('font_size', formatting)
        self.assertIn('background_color', formatting)
        self.assertEqual(formatting['font'], 'Verdana')
    
    def test_get_adaptations(self):
        """Test getting profile adaptations"""
        adaptations = self.service.get_adaptations('esl')
        
        self.assertIn('simplify_idioms', adaptations)
        self.assertIn('support_translation', adaptations)
        self.assertTrue(adaptations['simplify_idioms'])
        self.assertTrue(adaptations['support_translation'])
    
    def test_needs_adaptation(self):
        """Test adaptation need detection"""
        # Text with good readability
        good_metrics = {
            'flesch_ease': 70,
            'grade_level': 6
        }
        self.assertFalse(self.service.needs_adaptation("Simple text", 'dyslexia', good_metrics))
        
        # Text with poor readability
        poor_metrics = {
            'flesch_ease': 30,
            'grade_level': 12
        }
        self.assertTrue(self.service.needs_adaptation("Complex text", 'dyslexia', poor_metrics))
    
    def test_get_profile_colors(self):
        """Test getting profile color scheme"""
        colors = self.service.get_profile_colors('dyslexia')
        
        self.assertIn('background', colors)
        self.assertIn('text', colors)
        self.assertIn('highlight', colors)
        self.assertEqual(colors['background'], '#FFFEF5')
        self.assertEqual(colors['text'], '#000080')
    
    def test_custom_profile_config(self):
        """Test service with custom profile configuration"""
        custom_config = {
            'profiles': {
                'dyslexia': {
                    'thresholds': {
                        'flesch_ease': 65  # Override default
                    }
                }
            }
        }
        
        custom_service = LearningProfilesService(custom_config)
        thresholds = custom_service.get_thresholds('dyslexia')
        
        # Should have custom threshold
        self.assertEqual(thresholds['flesch_ease'], 65)


if __name__ == '__main__':
    unittest.main()