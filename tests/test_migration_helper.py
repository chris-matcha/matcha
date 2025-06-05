"""
Test Migration Helper

Tests for the PDF migration helper functionality.
"""
import unittest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from migrate_pdf_functions import PDFMigrationHelper


class TestPDFMigrationHelper(unittest.TestCase):
    """Test cases for PDF Migration Helper"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.helper = PDFMigrationHelper({
            'output_folder': tempfile.mkdtemp()
        })
    
    @patch.object(PDFMigrationHelper, '__init__', lambda x, config: None)
    def test_helper_initialization(self):
        """Test helper initializes correctly"""
        helper = PDFMigrationHelper({})
        
        # Should have all required services (these would be mocked in real usage)
        self.assertTrue(hasattr(helper, 'formats_service'))
        self.assertTrue(hasattr(helper, 'adaptations_service'))
        self.assertTrue(hasattr(helper, 'profiles_service'))
    
    @patch('services.FormatsService')
    @patch('services.AdaptationsService')
    @patch('services.LearningProfilesService')
    def test_process_with_pdf_template_system(self, mock_profiles, mock_adaptations, mock_formats):
        """Test the main PDF processing function"""
        # Setup mocks
        mock_content = {
            'pages': [{'text': 'Original content'}],
            'metadata': {'page_count': 1}
        }
        
        mock_adapted_content = {
            'pages': [{'text': 'Adapted content'}],
            'metadata': {'page_count': 1}
        }
        
        mock_formats_instance = mock_formats.return_value
        mock_formats_instance.extract_content.return_value = mock_content
        mock_formats_instance.create_file.return_value = True
        
        mock_adaptations_instance = mock_adaptations.return_value
        mock_adaptations_instance.adapt_content.return_value = mock_adapted_content
        
        # Create helper with mocked services
        helper = PDFMigrationHelper({'output_folder': tempfile.mkdtemp()})
        helper.formats_service = mock_formats_instance
        helper.adaptations_service = mock_adaptations_instance
        
        # Test processing
        result = helper.process_with_pdf_template_system(
            'test.pdf', 
            'dyslexia',
            direct_adapt=True,
            preserve_visuals=True
        )
        
        # Should succeed
        self.assertTrue(result['success'])
        self.assertIn('output_path', result)
        self.assertEqual(result['profile'], 'dyslexia')
        
        # Should call extract with formatting
        mock_formats_instance.extract_content.assert_called_with(
            'test.pdf', 'pdf', include_formatting=True
        )
        
        # Should call adapt content
        mock_adaptations_instance.adapt_content.assert_called_with(
            mock_content, 'dyslexia', force_adaptation=True
        )
        
        # Should call create file with visual preservation
        mock_formats_instance.create_file.assert_called_with(
            mock_adapted_content,
            result['output_path'],
            'pdf',
            profile='dyslexia',
            preserve_visuals=True,
            original_path='test.pdf'
        )
    
    @patch('services.FormatsService')
    @patch('services.AdaptationsService')
    @patch('services.LearningProfilesService')
    def test_process_without_visual_preservation(self, mock_profiles, mock_adaptations, mock_formats):
        """Test processing without visual preservation"""
        # Setup mocks
        mock_formats_instance = mock_formats.return_value
        mock_formats_instance.extract_content.return_value = {'pages': []}
        mock_formats_instance.create_file.return_value = True
        
        mock_adaptations_instance = mock_adaptations.return_value
        mock_adaptations_instance.adapt_content.return_value = {'pages': []}
        
        helper = PDFMigrationHelper({'output_folder': tempfile.mkdtemp()})
        helper.formats_service = mock_formats_instance
        helper.adaptations_service = mock_adaptations_instance
        
        # Test without visual preservation
        result = helper.process_with_pdf_template_system(
            'test.pdf',
            'esl',
            preserve_visuals=False
        )
        
        # Should extract without formatting
        mock_formats_instance.extract_content.assert_called_with(
            'test.pdf', 'pdf', include_formatting=False
        )
        
        # Should create file without visual preservation
        mock_formats_instance.create_file.assert_called_with(
            {'pages': []},
            result['output_path'],
            'pdf',
            profile='esl',
            preserve_visuals=False,
            original_path=None
        )
    
    @patch('services.FormatsService')
    def test_direct_visual_preserved_methods(self, mock_formats):
        """Test direct method replacements"""
        mock_formats_instance = mock_formats.return_value
        mock_visual_handler = Mock()
        mock_formats_instance.pdf_visual_handler = mock_visual_handler
        
        helper = PDFMigrationHelper({})
        helper.formats_service = mock_formats_instance
        
        # Test create_visual_preserved_pdf
        mock_visual_handler.create_visual_preserved_pdf.return_value = True
        result = helper.create_visual_preserved_pdf(
            'input.pdf', {'pages': []}, 'output.pdf', 'dyslexia'
        )
        
        self.assertTrue(result)
        mock_visual_handler.create_visual_preserved_pdf.assert_called_with(
            'input.pdf', {'pages': []}, 'output.pdf', 'dyslexia'
        )
        
        # Test create_visual_preserved_with_text_overlay
        mock_visual_handler.create_visual_preserved_with_overlay.return_value = True
        result = helper.create_visual_preserved_with_text_overlay(
            'input.pdf', {'pages': []}, 'output.pdf', 'adhd'
        )
        
        self.assertTrue(result)
        mock_visual_handler.create_visual_preserved_with_overlay.assert_called_with(
            'input.pdf', {'pages': []}, 'output.pdf', 'adhd'
        )
        
        # Test create_visual_preserved_pdf_simple
        mock_visual_handler.create_simple_visual_preserved.return_value = True
        result = helper.create_visual_preserved_pdf_simple(
            'input.pdf', 'output.pdf', 'esl'
        )
        
        self.assertTrue(result)
        mock_visual_handler.create_simple_visual_preserved.assert_called_with(
            'input.pdf', 'output.pdf', 'esl'
        )
    
    @patch('services.FormatsService')
    def test_create_adapted_pdf(self, mock_formats):
        """Test adapted PDF creation"""
        mock_formats_instance = mock_formats.return_value
        mock_formats_instance.create_file.return_value = True
        
        helper = PDFMigrationHelper({})
        helper.formats_service = mock_formats_instance
        
        # Test create_adapted_pdf
        result = helper.create_adapted_pdf(
            {'pages': [{'text': 'content'}]}, 'output.pdf', 'dyslexia'
        )
        
        self.assertTrue(result)
        mock_formats_instance.create_file.assert_called_with(
            {'pages': [{'text': 'content'}]}, 'output.pdf', 'pdf', 'dyslexia', preserve_visuals=False
        )
    
    @patch('services.FormatsService')
    @patch('services.AdaptationsService')
    @patch('services.LearningProfilesService')
    def test_error_handling(self, mock_profiles, mock_adaptations, mock_formats):
        """Test error handling in migration"""
        # Setup mocks to raise exception
        mock_formats_instance = mock_formats.return_value
        mock_formats_instance.extract_content.side_effect = Exception("Test error")
        
        helper = PDFMigrationHelper({'output_folder': tempfile.mkdtemp()})
        helper.formats_service = mock_formats_instance
        
        # Test error handling
        result = helper.process_with_pdf_template_system('test.pdf', 'dyslexia')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Test error')
    
    def test_output_filename_generation(self):
        """Test output filename generation"""
        helper = PDFMigrationHelper({'output_folder': '/tmp/outputs'})
        
        # Test with mock services to avoid actual processing
        with patch.object(helper, 'formats_service'), \
             patch.object(helper, 'adaptations_service'):
            
            helper.formats_service.extract_content.return_value = {'pages': []}
            helper.adaptations_service.adapt_content.return_value = {'pages': []}
            helper.formats_service.create_file.return_value = True
            
            result = helper.process_with_pdf_template_system(
                '/path/to/document.pdf', 'dyslexia'
            )
            
            # Should generate correct filename
            expected_filename = 'adapted_dyslexia_document.pdf'
            self.assertTrue(result['output_path'].endswith(expected_filename))


if __name__ == '__main__':
    unittest.main()