"""
Enhanced PDF Service

Consolidates all PDF processing functionality from app.py
"""
import os
import fitz  # PyMuPDF
import tempfile
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
import io
import re
from .base_service import BaseService
from .pdf_visual_handler_enhanced import PDFVisualHandlerEnhanced
from .adaptations_service import AdaptationsService
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.colors import HexColor
import anthropic


class PDFService(BaseService):
    """Enhanced PDF service with all PDF processing capabilities"""
    
    def _initialize(self):
        """Initialize PDF service resources"""
        self.visual_handler = PDFVisualHandlerEnhanced()
        self.adaptations_service = AdaptationsService(self.config)
        self.api_key = self.config.get('anthropic_api_key')
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
        
        # Profile-specific styling
        self.PROFILE_STYLES = {
            'dyslexia': {
                'fontName': 'Helvetica',
                'fontSize': 14,
                'leading': 20,
                'textColor': HexColor('#000080'),
                'backColor': HexColor('#FFFEF5'),
                'spaceAfter': 18
            },
            'adhd': {
                'fontName': 'Helvetica',
                'fontSize': 13,
                'leading': 18,
                'textColor': HexColor('#004D00'),
                'backColor': HexColor('#F0FFF0'),
                'spaceAfter': 16
            },
            'esl': {
                'fontName': 'Helvetica',
                'fontSize': 13,
                'leading': 17,
                'textColor': HexColor('#4B0082'),
                'backColor': HexColor('#FAF5FF'),
                'spaceAfter': 15
            },
            'default': {
                'fontName': 'Helvetica',
                'fontSize': 12,
                'leading': 14,
                'textColor': HexColor('#000000'),
                'backColor': HexColor('#FFFFFF'),
                'spaceAfter': 12
            }
        }
    
    def extract_content_from_pdf(self, pdf_path: str, include_formatting: bool = False) -> Dict[str, Any]:
        """
        Extract content from PDF file
        
        Args:
            pdf_path: Path to PDF file
            include_formatting: Whether to include formatting information
            
        Returns:
            Dict containing pages with text and metadata
        """
        if include_formatting:
            return self.visual_handler.extract_content_with_formatting(pdf_path)
        
        content = {
            'pages': [],
            'metadata': {},
            'original_path': pdf_path
        }
        
        try:
            doc = fitz.open(pdf_path)
            
            # Extract metadata
            content['metadata'] = {
                'page_count': doc.page_count,
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'subject': doc.metadata.get('subject', '')
            }
            
            # Extract pages
            for page_num, page in enumerate(doc):
                page_content = {
                    'page_number': page_num + 1,
                    'text': page.get_text(),
                    'images': [],
                    'tables': []
                }
                
                # Extract images
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    page_content['images'].append({
                        'index': img_index,
                        'width': img[2] if len(img) > 2 else 0,
                        'height': img[3] if len(img) > 3 else 0
                    })
                
                content['pages'].append(page_content)
            
            doc.close()
            
        except Exception as e:
            self.logger.error(f"Error extracting PDF content: {str(e)}")
            raise Exception(f"Error extracting PDF content: {str(e)}")
        
        return content
    
    def create_adapted_pdf(self, content: Dict[str, Any], output_path: str, 
                          profile: str = 'default') -> bool:
        """
        Create an adapted PDF with profile-specific formatting
        
        Args:
            content: Content to write to PDF
            output_path: Path for output file
            profile: Learning profile for formatting
            
        Returns:
            bool: Success status
        """
        try:
            # Get profile style settings
            profile_style = self.PROFILE_STYLES.get(profile, self.PROFILE_STYLES['default'])
            
            # Create document with background color
            doc = SimpleDocTemplate(
                output_path, 
                pagesize=A4,
                leftMargin=inch,
                rightMargin=inch,
                topMargin=inch,
                bottomMargin=inch
            )
            
            # Create custom style based on profile
            styles = getSampleStyleSheet()
            profile_para_style = ParagraphStyle(
                'ProfileStyle',
                parent=styles['Normal'],
                fontName=profile_style['fontName'],
                fontSize=profile_style['fontSize'],
                leading=profile_style['leading'],
                textColor=profile_style['textColor'],
                alignment=TA_JUSTIFY,
                spaceAfter=profile_style['spaceAfter']
            )
            
            story = []
            
            # Add content with profile formatting
            for page in content.get('pages', []):
                text = page.get('text', '')
                if text:
                    # Split into paragraphs
                    paragraphs = text.split('\n\n')
                    for para_text in paragraphs:
                        if para_text.strip():
                            para = Paragraph(para_text.strip(), profile_para_style)
                            story.append(para)
                            story.append(Spacer(1, profile_style['spaceAfter']))
                    
                    # Add page break between pages
                    if page != content['pages'][-1]:
                        story.append(PageBreak())
            
            # Build document
            doc.build(story)
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating adapted PDF: {str(e)}")
            return False
    
    def diagnose_pdf_content(self, pdf_path: str) -> Dict[str, Any]:
        """
        Diagnose PDF content for debugging
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dict with diagnostic information
        """
        diagnosis = {
            'file': pdf_path,
            'pages': [],
            'has_images': False,
            'has_text': False,
            'total_text_length': 0,
            'errors': []
        }
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num, page in enumerate(doc):
                page_info = {
                    'page_number': page_num + 1,
                    'text_length': 0,
                    'image_count': 0,
                    'text_blocks': 0,
                    'rect': list(page.rect)
                }
                
                # Get text
                text = page.get_text()
                page_info['text_length'] = len(text)
                diagnosis['total_text_length'] += len(text)
                if text.strip():
                    diagnosis['has_text'] = True
                
                # Get text blocks
                text_dict = page.get_text("dict")
                page_info['text_blocks'] = len(text_dict.get('blocks', []))
                
                # Get images
                images = page.get_images()
                page_info['image_count'] = len(images)
                if images:
                    diagnosis['has_images'] = True
                
                diagnosis['pages'].append(page_info)
            
            doc.close()
            
        except Exception as e:
            diagnosis['errors'].append(str(e))
        
        return diagnosis
    
    def create_visual_preserved_pdf(self, original_path: str, adapted_content: Dict[str, Any],
                                  output_path: str, profile: str = 'default') -> bool:
        """
        Create PDF with visual preservation
        
        Args:
            original_path: Path to original PDF
            adapted_content: Adapted content
            output_path: Output path
            profile: Learning profile
            
        Returns:
            bool: Success status
        """
        return self.visual_handler.create_visual_preserved_pdf(
            original_path, adapted_content, output_path, profile
        )
    
    def adapt_pdf_content(self, pdf_content: Dict[str, Any], profile: str,
                         target_language: Optional[str] = None,
                         force_adaptation: bool = True) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Adapt PDF content based on learning profile
        
        Args:
            pdf_content: Extracted PDF content
            profile: Learning profile
            target_language: Target language for translation
            force_adaptation: Force adaptation even if not needed
            
        Returns:
            Tuple of (adapted_content, translated_content)
        """
        self.logger.info(f"Starting PDF adaptation for profile: {profile}, force: {force_adaptation}")
        
        # Check if adaptations service is available
        if not hasattr(self, 'adaptations_service') or not self.adaptations_service:
            self.logger.error("AdaptationsService not initialized!")
            if not self.client:
                self.logger.warning("No API client available for adaptation")
                return pdf_content, None
        
        adapted_content = {
            'pages': [],
            'metadata': pdf_content.get('metadata', {}).copy()
        }
        
        translated_content = None
        if target_language:
            translated_content = {
                'pages': [],
                'metadata': pdf_content.get('metadata', {}).copy()
            }
        
        # Collect all page texts for batch processing
        pages_to_adapt = []
        page_texts = []
        
        for page in pdf_content.get('pages', []):
            text = page.get('text', '')
            if text and len(text.strip()) > 10:
                pages_to_adapt.append(page)
                page_texts.append(text)
        
        # Batch adapt all page texts at once for better efficiency
        adapted_texts = []
        if page_texts:
            try:
                self.logger.info(f"🚀 Batch adapting {len(page_texts)} pages for profile '{profile}'")
                adapted_texts = self.adaptations_service.process_text_batch(page_texts, profile)
                self.logger.info(f"✅ Batch adaptation completed: {len(adapted_texts)} pages processed")
            except Exception as batch_error:
                self.logger.warning(f"⚠️ Batch adaptation failed: {batch_error}. Falling back to individual processing.")
                # Fallback to individual processing
                adapted_texts = []
                for text in page_texts:
                    try:
                        adapted_text = self.adaptations_service.adapt_text(text, profile)
                        adapted_texts.append(adapted_text)
                    except Exception as e:
                        self.logger.error(f"Individual adaptation failed: {e}")
                        adapted_texts.append(text)  # Use original on failure
        
        # Apply adapted texts to pages
        adapted_text_idx = 0
        
        for page in pdf_content.get('pages', []):
            adapted_page = page.copy()
            text = page.get('text', '')
            
            if text and len(text.strip()) > 10 and adapted_text_idx < len(adapted_texts):
                adapted_text = adapted_texts[adapted_text_idx]
                adapted_text_idx += 1
                
                try:
                    # Validate adaptation
                    validation = self.adaptations_service.validate_adaptation(text, adapted_text, profile)
                    
                    if not validation['is_valid']:
                        self.logger.warning(f"Adaptation validation failed for page {page.get('page_number', '?')}: {validation['issues']}")
                        if force_adaptation:
                            # Try one more time with explicit error raising
                            try:
                                adapted_text = self.adaptations_service._adapt_text(text, profile, raise_on_failure=True)
                            except Exception as retry_error:
                                self.logger.error(f"Forced adaptation failed: {retry_error}")
                                raise ValueError(f"PDF adaptation failed for page {page.get('page_number', '?')}: {retry_error}")
                    
                    adapted_page['text'] = adapted_text
                    
                    # Log successful adaptation metrics
                    if 'metrics' in validation:
                        self.logger.info(f"Page {page.get('page_number', '?')} adapted: "
                                       f"{validation['metrics'].get('original_word_count', 0)} -> "
                                       f"{validation['metrics'].get('adapted_word_count', 0)} words")
                    
                    # Translate if requested
                    if target_language and translated_content is not None:
                        translated_page = page.copy()
                        
                        # Use translation service if available
                        try:
                            from .translations_service import TranslationsService
                            translations_service = TranslationsService(self.config)
                            translated_text = translations_service.translate_text(adapted_text, target_language)
                            translated_page['text'] = translated_text
                            translated_content['pages'].append(translated_page)
                        except Exception as trans_error:
                            self.logger.error(f"Translation failed for page {page.get('page_number', '?')}: {trans_error}")
                            # Don't fail the whole adaptation if translation fails
                    
                except Exception as e:
                    self.logger.error(f"Error adapting page {page.get('page_number', '?')}: {str(e)}")
                    if force_adaptation:
                        raise  # Re-raise if forced adaptation is required
                    adapted_page['text'] = text  # Keep original on error only if not forced
            
            adapted_content['pages'].append(adapted_page)
        
        return adapted_content, translated_content
    
    def _create_adaptation_prompt(self, text: str, profile: str) -> str:
        """Create profile-specific adaptation prompt"""
        base_prompt = f"Adapt the following text for a {profile} learner. "
        
        profile_instructions = {
            'dyslexia': "Use simple sentence structures, clear language, and break complex ideas into smaller chunks. Use active voice and avoid complex words.",
            'adhd': "Use short paragraphs, bullet points where appropriate, and clear headings. Keep sentences concise and engaging.",
            'esl': "Use simple vocabulary, define technical terms, and ensure clear sentence structure. Avoid idioms and complex grammar."
        }
        
        instruction = profile_instructions.get(profile, "Simplify the text while maintaining accuracy.")
        
        return f"{base_prompt}{instruction}\n\nText to adapt:\n{text}"
    
    def cleanup_temp_images(self) -> None:
        """Clean up temporary image files"""
        temp_pattern = os.path.join(tempfile.gettempdir(), "temp_page_*")
        import glob
        for file in glob.glob(temp_pattern):
            try:
                os.remove(file)
            except:
                pass
    
    def estimate_text_width(self, text: str, font_size: int = 12) -> float:
        """
        Estimate text width for layout calculations
        
        Args:
            text: Text to measure
            font_size: Font size in points
            
        Returns:
            Estimated width in points
        """
        # Rough estimation: average character width is about 0.5 * font_size
        avg_char_width = font_size * 0.5
        return len(text) * avg_char_width
    
    def process_with_template_system(self, file_path: str, file_id: str, filename: str, 
                                   profile: str, export_format: str = 'pdf', 
                                   target_language: Optional[str] = None,
                                   processing_callback: Optional[callable] = None,
                                   output_path_callback: Optional[callable] = None) -> Optional[str]:
        """
        Main PDF processing function with template system support
        
        Args:
            file_path: Path to input PDF
            file_id: Unique file identifier
            filename: Original filename
            profile: Learning profile
            export_format: Output format ('pdf' or 'pptx')
            target_language: Target language for translation
            processing_callback: Callback for progress updates
            output_path_callback: Callback to generate output paths
            
        Returns:
            Path to created file or None on error
        """
        self.logger.info(f"Starting PDF template processing for {filename} with export format: {export_format}")
        print(f"DEBUG: PDFService.process_with_template_system called with file_path: {file_path}, profile: {profile}, export_format: {export_format}")
        
        try:
            # Update progress
            if processing_callback:
                processing_callback(file_id, 'Extracting content from PDF...', 10)
            
            # Step 1: Extract content from PDF
            pdf_content = self.extract_content_from_pdf(file_path)
            
            if not pdf_content['pages']:
                raise Exception("No content could be extracted from the PDF")
            
            if processing_callback:
                processing_callback(file_id, 'Adapting PDF content...', 30)
            
            # Step 2: Adapt content (with optional translation)
            self.logger.info(f"Adapting with profile: {profile}, language: {target_language}")
            
            result = self.adapt_pdf_content(pdf_content, profile, target_language, force_adaptation=True)
            if isinstance(result, tuple):
                adapted_content, translated_content = result
            else:
                adapted_content = result
                translated_content = None
            
            if processing_callback:
                processing_callback(file_id, f'Creating adapted {export_format.upper()}...', 70)
            
            # Step 3: Create output based on requested format
            output_path = None
            translated_path = None
            
            if export_format.lower() == 'pdf':
                output_path = self._create_pdf_output(
                    file_path, file_id, filename, profile, 
                    adapted_content, translated_content, target_language,
                    output_path_callback
                )
            elif export_format.lower() == 'pptx':
                output_path = self._create_pptx_output(
                    file_id, filename, profile, adapted_content
                )
            else:
                raise Exception(f"Unsupported export format: {export_format}")
            
            if not output_path:
                raise Exception(f"Failed to create adapted {export_format}")
            
            # Verify the file was created
            if not os.path.exists(output_path):
                raise Exception(f"File creation reported success but file not found")
            
            if processing_callback:
                processing_callback(file_id, f'PDF content successfully adapted to {export_format.upper()}', 100)
            
            self.logger.info(f"Successfully created file at: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error in PDF processing: {str(e)}")
            if processing_callback:
                processing_callback(file_id, f"PDF processing failed: {str(e)}", -1)
            return None
    
    def _create_pdf_output(self, original_path: str, file_id: str, filename: str,
                          profile: str, adapted_content: Dict[str, Any],
                          translated_content: Optional[Dict[str, Any]] = None,
                          target_language: Optional[str] = None,
                          output_path_callback: Optional[callable] = None) -> Optional[str]:
        """Create PDF output with optional translation"""
        # Generate output filename
        base_name = os.path.splitext(filename)[0]
        if base_name.startswith('adapted_'):
            output_filename = f"{base_name}.pdf"
        else:
            output_filename = f"adapted_{base_name}.pdf"
        
        # Get output path using callback or default
        if output_path_callback:
            output_path = output_path_callback(file_id, output_filename)
        else:
            output_dir = os.path.join(os.path.dirname(original_path), '..', 'outputs')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{file_id}_{output_filename}")
        
        # Validate adapted content before processing
        if not adapted_content or not adapted_content.get('pages'):
            self.logger.error("No adapted content available for PDF creation")
            return None
        
        # Check if adapted content has actual text (not just placeholders)
        has_real_content = False
        for page in adapted_content.get('pages', []):
            text = page.get('text', '').strip()
            # Check for placeholder markers that indicate adaptation failure
            placeholder_markers = ['[DYSLEXIA]', '[Adapted: DYSLEXIA]', '[ADHD]', '[ESL]', 
                                 'Adapted for dyslexia', 'Adapted for adhd', 'Adapted for esl']
            if text and text not in placeholder_markers and len(text) > 10:
                has_real_content = True
                break
        
        if not has_real_content:
            self.logger.warning("Adapted content contains only placeholder markers, falling back to standard method")
            # Force use of standard method if content is just markers
            success = self.create_adapted_pdf(adapted_content, output_path, profile)
            if success:
                return output_path
            else:
                return None
        
        # Try visual preservation methods first
        success = False
        try:
            # Diagnose PDF content
            diagnosis = self.diagnose_pdf_content(original_path)
            self.logger.info(f"PDF diagnosis: {diagnosis['total_text_length']} chars, {len(diagnosis['pages'])} pages")
            
            # Try visual-preserving method
            self.logger.info("Using visual-preserving PDF adaptation method")
            success = self.create_visual_preserved_pdf(original_path, adapted_content, output_path, profile)
            
            if success and os.path.exists(output_path):
                # Validate the output file has reasonable content
                output_size = os.path.getsize(output_path)
                if output_size > 500 * 1024 * 1024:  # 500MB threshold
                    self.logger.warning(f"Visual preservation created very large file ({output_size/1024/1024:.1f}MB), trying fallback")
                    success = False
                    try:
                        os.remove(output_path)
                    except:
                        pass
            
            if not success:
                self.logger.info("Falling back to standard method")
                success = self.create_adapted_pdf(adapted_content, output_path, profile)
                
        except Exception as e:
            self.logger.error(f"Error in visual preservation: {e}")
            # Fall back to standard method
            success = self.create_adapted_pdf(adapted_content, output_path, profile)
        
        if not success:
            return None
        
        # Validate final output
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            self.logger.info(f"PDF created successfully: {output_path} ({file_size} bytes)")
        else:
            self.logger.error("PDF creation reported success but file does not exist")
            return None
        
        # Create translated version if available
        if translated_content and target_language:
            self._create_translated_pdf(
                original_path, file_id, filename, profile,
                translated_content, target_language, output_path_callback
            )
        
        return output_path
    
    def _create_translated_pdf(self, original_path: str, file_id: str, filename: str,
                              profile: str, translated_content: Dict[str, Any],
                              target_language: str, output_path_callback: Optional[callable] = None) -> Optional[str]:
        """Create translated PDF"""
        # Clean the base filename
        base_name = os.path.splitext(filename)[0]
        if base_name.startswith('adapted_'):
            base_name = base_name[8:]  # Remove 'adapted_' prefix
        
        translated_filename = f"translated_{target_language}_{base_name}.pdf"
        
        # Get output path using callback or default
        if output_path_callback:
            translated_path = output_path_callback(file_id, translated_filename)
        else:
            output_dir = os.path.join(os.path.dirname(original_path), '..', 'outputs')
            translated_path = os.path.join(output_dir, f"{file_id}_{translated_filename}")
        
        success = False
        try:
            success = self.create_visual_preserved_pdf(
                original_path, translated_content, translated_path, profile
            )
            # Text overlay method not yet implemented
            # if not success:
            #     success = self.create_visual_preserved_with_text_overlay(
            #         original_path, translated_content, translated_path, profile
            #     )
            if not success:
                success = self.create_adapted_pdf(translated_content, translated_path, profile)
        except Exception as e:
            self.logger.error(f"Error creating translated PDF: {e}")
        
        return translated_path if success else None
    
    def _create_pptx_output(self, file_id: str, filename: str, profile: str,
                           adapted_content: Dict[str, Any]) -> Optional[str]:
        """Create PowerPoint output from PDF content"""
        # This would need to be implemented or use a conversion service
        # For now, returning None as this requires additional implementation
        self.logger.warning("PowerPoint output from PDF not yet implemented in PDFService")
        return None
    
    def create_advanced_pdf(self, original_path: str, adapted_content: Dict[str, Any], 
                           output_path: str, profile: str = 'default',
                           options: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create PDF with advanced visual preservation features
        
        Args:
            original_path: Path to original PDF
            adapted_content: Adapted content structure
            output_path: Path for output PDF
            profile: Learning profile
            options: Advanced options (use_gradients, optimize_layout, add_reading_guides, etc.)
        
        Returns:
            Success status
        """
        return self.visual_handler.create_visual_preserved_pdf_with_advanced_features(
            original_path, adapted_content, output_path, profile, options
        )
    
    def calculate_quality_metrics(self, original_path: str, adapted_path: str) -> Dict[str, Any]:
        """
        Calculate quality metrics for PDF adaptation
        
        Args:
            original_path: Path to original PDF
            adapted_path: Path to adapted PDF
            
        Returns:
            Quality metrics dictionary
        """
        return self.visual_handler.calculate_adaptation_quality_metrics(original_path, adapted_path)
    
    def batch_process_pdfs(self, pdf_files: List[Dict[str, str]], profile: str,
                          progress_callback: Optional[callable] = None,
                          options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Batch process multiple PDFs with progress tracking
        
        Args:
            pdf_files: List of dicts with 'input' and 'output' paths
            profile: Learning profile to apply
            progress_callback: Optional callback for progress updates
            options: Processing options
            
        Returns:
            Results dictionary with success/failure info
        """
        return self.visual_handler.batch_process_pdfs_with_progress(
            pdf_files, profile, progress_callback, options
        )
    
    def optimize_for_accessibility(self, original_path: str, output_path: str) -> bool:
        """
        Optimize PDF for screen reader accessibility
        
        Args:
            original_path: Input PDF path
            output_path: Output PDF path
            
        Returns:
            Success status
        """
        return self.visual_handler.optimize_for_screen_reader(original_path, output_path)
    
    def process_large_pdf(self, pdf_path: str, output_path: str, profile: str,
                         chunk_size: int = 10, options: Optional[Dict[str, Any]] = None) -> bool:
        """
        Process large PDFs in chunks to manage memory
        
        Args:
            pdf_path: Input PDF path
            output_path: Output PDF path
            profile: Learning profile
            chunk_size: Pages per chunk
            options: Processing options
            
        Returns:
            Success status
        """
        return self.visual_handler.process_large_pdf_in_chunks(
            pdf_path, output_path, profile, chunk_size, options
        )