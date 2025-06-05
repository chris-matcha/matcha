"""
Test PDF Visual Handler

Tests for the migrated PDF visual preservation functionality.
"""
import unittest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.pdf_visual_handler import PDFVisualHandler


class TestPDFVisualHandler(unittest.TestCase):
    """Test cases for PDF Visual Handler"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.handler = PDFVisualHandler()
        self.test_content = {
            'pages': [{
                'page_number': 1,
                'text': 'This is test content for visual preservation.',
                'text_blocks': [{
                    'bbox': [50, 50, 500, 100],
                    'lines': [{
                        'bbox': [50, 50, 500, 70],
                        'spans': [{
                            'text': 'This is test content',
                            'font': 'Arial',
                            'size': 12,
                            'color': 0,
                            'bbox': [50, 50, 200, 70]
                        }]
                    }]
                }]
            }],
            'metadata': {'page_count': 1}
        }
    
    def test_profile_configs(self):
        """Test profile configurations are properly set"""
        self.assertIn('dyslexia', self.handler.profile_configs)
        self.assertIn('adhd', self.handler.profile_configs)
        self.assertIn('esl', self.handler.profile_configs)
        self.assertIn('default', self.handler.profile_configs)
        
        # Check dyslexia config
        dyslexia_config = self.handler.profile_configs['dyslexia']
        self.assertEqual(dyslexia_config['tint_color'], (255, 254, 245, 30))
        self.assertTrue(dyslexia_config['first_word_highlight'])
        self.assertTrue(dyslexia_config['reading_guide'])
    
    @patch('fitz.open')
    def test_extract_content_with_formatting(self, mock_fitz_open):
        """Test content extraction with formatting details"""
        # Mock PyMuPDF document
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.rect = [0, 0, 612, 792]
        mock_page.rotation = 0
        mock_page.get_text.return_value = "Test text"
        mock_page.get_text.return_value = {"blocks": []}  # For dict call
        mock_page.get_images.return_value = []
        
        mock_doc.page_count = 1
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.metadata = {'title': 'Test PDF'}
        
        mock_fitz_open.return_value = mock_doc
        
        # Test extraction
        content = self.handler.extract_content_with_formatting('test.pdf')
        
        self.assertIn('pages', content)
        self.assertIn('metadata', content)
        self.assertEqual(content['metadata']['page_count'], 1)
        self.assertEqual(len(content['pages']), 1)
    
    @patch('fitz.open')
    def test_create_visual_preserved_pdf(self, mock_fitz_open):
        """Test visual preserved PDF creation"""
        # Mock document
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz_open.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            # Test creation
            success = self.handler.create_visual_preserved_pdf(
                'original.pdf', 
                self.test_content,
                output_path,
                'dyslexia'
            )
            
            # Should call save
            mock_doc.save.assert_called_once_with(output_path)
            self.assertTrue(success)
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_update_page_text(self):
        """Test page text update logic"""
        # Create mock page
        mock_page = MagicMock()
        
        # Test text update
        adapted_text = "Simplified text content"
        text_blocks = [{
            'bbox': [50, 50, 500, 100],
            'lines': [{
                'bbox': [50, 50, 500, 70],
                'spans': [{
                    'font': 'Arial',
                    'size': 12
                }]
            }]
        }]
        
        self.handler._update_page_text(mock_page, adapted_text, text_blocks)
        
        # Should clear text areas
        mock_page.draw_rect.assert_called()
        # Should insert new text
        mock_page.insert_textbox.assert_called()
    
    def test_apply_profile_enhancements(self):
        """Test profile enhancement application"""
        mock_page = MagicMock()
        mock_page.rect = MagicMock(height=792)
        
        # Test with dyslexia profile
        dyslexia_config = self.handler.profile_configs['dyslexia']
        self.handler._apply_profile_enhancements(mock_page, dyslexia_config)
        
        # Should add tint
        mock_page.draw_rect.assert_called()
    
    @patch('pdf2image.convert_from_path')
    @patch('fitz.open')
    def test_create_visual_preserved_with_overlay(self, mock_fitz_open, mock_convert):
        """Test overlay-based visual preservation"""
        # Mock image conversion
        mock_img = MagicMock()
        mock_img.width = 612
        mock_img.height = 792
        mock_img.mode = 'RGB'
        mock_img.convert.return_value = mock_img
        mock_convert.return_value = [mock_img]
        
        # Mock output document
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_doc.new_page.return_value = mock_page
        mock_fitz_open.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            success = self.handler.create_visual_preserved_with_overlay(
                'original.pdf',
                self.test_content,
                output_path,
                'adhd'
            )
            
            # Should create new page
            mock_doc.new_page.assert_called()
            # Should save document
            mock_doc.save.assert_called_with(output_path)
            self.assertTrue(success)
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    @patch('pdf2image.convert_from_path')
    def test_create_simple_visual_preserved(self, mock_convert):
        """Test simple visual preservation"""
        # Mock image
        mock_img = MagicMock()
        mock_img.mode = 'RGB'
        mock_img.size = (612, 792)
        mock_img.convert.return_value = mock_img
        mock_convert.return_value = [mock_img]
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            success = self.handler.create_simple_visual_preserved(
                'original.pdf',
                output_path,
                'esl'
            )
            
            # Should save as PDF
            mock_img.save.assert_called()
            self.assertTrue(success)
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_process_image_for_overlay(self):
        """Test image processing for overlay"""
        # Create test image
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='white')
        
        # Process with profile config
        profile_config = self.handler.profile_configs['dyslexia']
        processed = self.handler._process_image_for_overlay(img, profile_config)
        
        # Should return RGBA image
        self.assertEqual(processed.mode, 'RGBA')
    
    def test_add_text_overlay(self):
        """Test text overlay addition"""
        mock_page = MagicMock()
        mock_page.rect = MagicMock(width=612, height=792)
        
        text_blocks = [{
            'bbox': [50, 50, 500, 100]
        }]
        
        self.handler._add_text_overlay(mock_page, "Test overlay text", text_blocks)
        
        # Should clear text areas
        mock_page.draw_rect.assert_called()
        # Should add new text
        mock_page.insert_textbox.assert_called()


if __name__ == '__main__':
    unittest.main()