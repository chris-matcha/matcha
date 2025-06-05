"""
Test Adaptations Service

Example tests for the adaptations service showing mocking and isolation.
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import AdaptationsService


class TestAdaptationsService(unittest.TestCase):
    """Test cases for Adaptations Service"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create service without API key to test rule-based adaptation
        self.service = AdaptationsService({})
    
    def test_calculate_readability_metrics(self):
        """Test readability calculation"""
        text = "This is a simple sentence. It is easy to read."
        metrics = self.service.calculate_readability_metrics(text)
        
        self.assertIn('flesch_ease', metrics)
        self.assertIn('grade_level', metrics)
        self.assertIn('word_count', metrics)
        self.assertIn('sentence_count', metrics)
        
        # Check reasonable values
        self.assertGreater(metrics['flesch_ease'], 0)
        self.assertLess(metrics['flesch_ease'], 100)
        self.assertEqual(metrics['word_count'], 10)
        self.assertEqual(metrics['sentence_count'], 2)
    
    def test_simplify_vocabulary(self):
        """Test vocabulary simplification"""
        text = "We need to utilize this tool to facilitate the process."
        simplified = self.service._simplify_vocabulary(text)
        
        self.assertIn("use", simplified)
        self.assertIn("help", simplified)
        self.assertNotIn("utilize", simplified)
        self.assertNotIn("facilitate", simplified)
    
    def test_shorten_sentences(self):
        """Test sentence shortening"""
        long_text = "This is a very long sentence with many clauses, and it continues with more information, but it should be broken down."
        shortened = self.service._shorten_sentences(long_text)
        
        # Should have broken the sentence
        sentences = shortened.split('.')
        self.assertGreater(len(sentences), 1)
    
    def test_convert_to_bullets(self):
        """Test bullet point conversion"""
        text = "First point. Second point. Third point. Fourth point."
        bulleted = self.service._convert_to_bullets(text)
        
        self.assertIn("•", bulleted)
        lines = bulleted.split('\n')
        self.assertEqual(len(lines), 4)
    
    def test_adapt_text_rules(self):
        """Test rule-based text adaptation"""
        text = "We need to utilize complex terminology to demonstrate the functionality."
        adapted = self.service._adapt_text_rules(text, 'dyslexia')
        
        # Should be simplified
        self.assertIn("use", adapted)
        self.assertNotIn("utilize", adapted)
    
    def test_adapt_page(self):
        """Test page adaptation"""
        page = {
            'page_number': 1,
            'text': 'This is a complex sentence with difficult vocabulary that needs simplification.',
            'images': []
        }
        
        adapted_page = self.service._adapt_page(page, 'esl', force_adaptation=True)
        
        self.assertEqual(adapted_page['page_number'], 1)
        self.assertNotEqual(adapted_page['text'], page['text'])
    
    def test_adapt_slide(self):
        """Test slide adaptation"""
        slide = {
            'slide_number': 1,
            'title': 'Complex Terminology',
            'content': 'Utilize these mechanisms to facilitate learning.',
            'notes': 'Additional complex notes.'
        }
        
        adapted_slide = self.service._adapt_slide(slide, 'esl', force_adaptation=True)
        
        # All text fields should be adapted
        self.assertIn('use', adapted_slide['content'].lower())
        self.assertNotIn('utilize', adapted_slide['content'].lower())
    
    @patch('anthropic.Anthropic')
    def test_adapt_text_ai(self, mock_anthropic):
        """Test AI-based adaptation with mocking"""
        # Mock the API response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="This is simplified text.")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        # Create service with mocked API
        service = AdaptationsService({'anthropic_api_key': 'test-key'})
        
        text = "Complex text that needs adaptation."
        adapted = service._adapt_text(text, 'dyslexia')
        
        self.assertEqual(adapted, "This is simplified text.")
        mock_client.messages.create.assert_called_once()
    
    def test_adapt_content_pdf(self):
        """Test adapting PDF content"""
        content = {
            'pages': [
                {'page_number': 1, 'text': 'Page 1 text.'},
                {'page_number': 2, 'text': 'Page 2 text.'}
            ],
            'metadata': {'title': 'Test PDF'}
        }
        
        adapted = self.service.adapt_content(content, 'dyslexia', force_adaptation=True)
        
        self.assertIn('pages', adapted)
        self.assertEqual(len(adapted['pages']), 2)
        self.assertIn('metadata', adapted)
    
    def test_adapt_content_powerpoint(self):
        """Test adapting PowerPoint content"""
        content = {
            'slides': [
                {
                    'slide_number': 1,
                    'title': 'First Slide',
                    'content': 'Slide content'
                }
            ],
            'metadata': {'slide_count': 1}
        }
        
        adapted = self.service.adapt_content(content, 'adhd', force_adaptation=True)
        
        self.assertIn('slides', adapted)
        self.assertEqual(len(adapted['slides']), 1)
    
    def test_invalid_profile(self):
        """Test adaptation with invalid profile"""
        content = {'pages': [{'text': 'Test'}]}
        
        with self.assertRaises(ValueError):
            self.service.adapt_content(content, 'invalid_profile')
    
    def test_syllable_counting(self):
        """Test syllable counting algorithm"""
        test_words = {
            'hello': 2,
            'beautiful': 4,
            'the': 1,
            'extraordinary': 5
        }
        
        for word, expected in test_words.items():
            count = self.service._count_syllables(word)
            self.assertEqual(count, expected, f"Syllable count for '{word}' should be {expected}")


if __name__ == '__main__':
    unittest.main()