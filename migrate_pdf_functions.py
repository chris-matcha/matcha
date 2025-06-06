"""
Migration Helper for PDF Functions

This module provides wrapper functions to help migrate from the old app.py
PDF functions to the new service-based architecture.
"""
import os
from typing import Dict, Any, Optional
from services import FormatsService, AdaptationsService, LearningProfilesService, TranslationsService


class PDFMigrationHelper:
    """Helper class to bridge old and new PDF functionality"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize with configuration"""
        self.config = config or {}
        self.formats_service = FormatsService(config)
        self.adaptations_service = AdaptationsService(config)
        self.profiles_service = LearningProfilesService(config)
        self.translations_service = TranslationsService(config)
    
    def process_with_pdf_template_system(self, pdf_path: str, profile: str,
                                       direct_adapt: bool = False,
                                       preserve_visuals: bool = True,
                                       translate: bool = False,
                                       target_language: Optional[str] = None) -> Dict[str, Any]:
        """
        Replacement for the old process_with_pdf_template_system function
        
        Args:
            pdf_path: Path to input PDF
            profile: Learning profile ID
            direct_adapt: Force adaptation
            preserve_visuals: Preserve visual layout
            translate: Whether to translate
            target_language: Target language for translation
            
        Returns:
            Dict with output path and status
        """
        try:
            # Extract content with formatting if visual preservation is needed
            try:
                print(f"Extracting content with formatting={preserve_visuals}")
                content = self.formats_service.extract_content(
                    pdf_path, 'pdf', include_formatting=preserve_visuals
                )
                if preserve_visuals and content.get('pages'):
                    # Check if we got text_blocks
                    first_page = content['pages'][0] if content['pages'] else {}
                    has_text_blocks = 'text_blocks' in first_page
                    print(f"Extraction successful. Has text_blocks: {has_text_blocks}")
                    if has_text_blocks:
                        print(f"First page has {len(first_page['text_blocks'])} text blocks")
            except Exception as extract_error:
                # If formatted extraction fails, fall back to basic extraction
                print(f"Warning: Formatted extraction failed ({extract_error}), using basic extraction")
                import traceback
                traceback.print_exc()
                content = self.formats_service.extract_content(
                    pdf_path, 'pdf', include_formatting=False
                )
                # If we fell back to basic extraction, disable visual preservation
                preserve_visuals = False
                print("Visual preservation disabled due to extraction failure")
            
            # Adapt content
            adapted_content = self.adaptations_service.adapt_content(
                content, profile, force_adaptation=direct_adapt
            )
            
            # Generate output filename
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_filename = f"adapted_{profile}_{base_name}.pdf"
            output_path = os.path.join(self.config.get('output_folder', 'outputs'), output_filename)
            
            # Create output directory if needed
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Create PDF with adapted content
            success = self.formats_service.create_file(
                adapted_content,
                output_path,
                'pdf',
                profile=profile,
                preserve_visuals=preserve_visuals,
                original_path=pdf_path if preserve_visuals else None
            )
            
            if not success:
                return {
                    'success': False,
                    'error': 'Failed to create adapted PDF'
                }
            
            # Handle translation if requested
            translated_output_path = None
            if translate and target_language:
                try:
                    # Translate the adapted content (not the original)
                    translated_content = self.translations_service.translate_content(
                        adapted_content, target_language
                    )
                    
                    # Generate translated output filename
                    translated_filename = f"translated_{target_language}_{base_name}.pdf"
                    translated_output_path = os.path.join(
                        self.config.get('output_folder', 'outputs'), 
                        translated_filename
                    )
                    
                    # Create translated PDF with visual preservation
                    translation_success = self.formats_service.create_file(
                        translated_content,
                        translated_output_path,
                        'pdf',
                        profile=profile,
                        preserve_visuals=preserve_visuals,
                        original_path=pdf_path if preserve_visuals else None
                    )
                    
                    if not translation_success:
                        print(f"Warning: Failed to create translated PDF")
                        translated_output_path = None
                        
                except Exception as translation_error:
                    print(f"Warning: Translation failed - {translation_error}")
                    translated_output_path = None
            
            # Return both adapted and translated paths
            result = {
                'success': True,
                'output_path': output_path,
                'adapted_content': adapted_content,
                'profile': profile
            }
            
            if translated_output_path:
                result['translated_output_path'] = translated_output_path
                result['translated_language'] = target_language
            
            return result
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_visual_preserved_pdf(self, pdf_path: str, adapted_content: Dict[str, Any],
                                  output_path: str, profile: str) -> bool:
        """
        Direct replacement for create_visual_preserved_pdf function
        
        Args:
            pdf_path: Original PDF path
            adapted_content: Adapted content
            output_path: Output path
            profile: Learning profile
            
        Returns:
            bool: Success status
        """
        return self.formats_service.pdf_visual_handler.create_visual_preserved_pdf(
            pdf_path, adapted_content, output_path, profile
        )
    
    def create_visual_preserved_with_text_overlay(self, pdf_path: str, adapted_content: Dict[str, Any],
                                                output_path: str, profile: str) -> bool:
        """
        Direct replacement for create_visual_preserved_with_text_overlay function
        
        Args:
            pdf_path: Original PDF path
            adapted_content: Adapted content
            output_path: Output path
            profile: Learning profile
            
        Returns:
            bool: Success status
        """
        return self.formats_service.pdf_visual_handler.create_visual_preserved_with_overlay(
            pdf_path, adapted_content, output_path, profile
        )
    
    def create_visual_preserved_pdf_simple(self, pdf_path: str, output_path: str,
                                         profile: str) -> bool:
        """
        Direct replacement for create_visual_preserved_pdf_simple function
        
        Args:
            pdf_path: Original PDF path
            output_path: Output path
            profile: Learning profile
            
        Returns:
            bool: Success status
        """
        return self.formats_service.pdf_visual_handler.create_simple_visual_preserved(
            pdf_path, output_path, profile
        )
    
    def create_adapted_pdf(self, adapted_content: Dict[str, Any], output_path: str,
                         profile: str) -> bool:
        """
        Direct replacement for create_adapted_pdf function
        
        Args:
            adapted_content: Adapted content
            output_path: Output path
            profile: Learning profile
            
        Returns:
            bool: Success status
        """
        return self.formats_service.create_file(
            adapted_content, output_path, 'pdf', profile, preserve_visuals=False
        )


# Example migration usage
def migrate_pdf_processing():
    """Example of how to migrate PDF processing code"""
    
    # Old way (in app.py):
    # result = process_with_pdf_template_system(pdf_path, profile, direct_adapt=True)
    
    # New way:
    helper = PDFMigrationHelper({'output_folder': 'outputs'})
    result = helper.process_with_pdf_template_system(
        'test.pdf', 'dyslexia', direct_adapt=True
    )
    
    print(f"Migration result: {result}")


if __name__ == '__main__':
    # Run example
    print("PDF Function Migration Helper")
    print("This module provides wrapper functions to ease migration.")
    print("\nExample usage:")
    print("helper = PDFMigrationHelper()")
    print("result = helper.process_with_pdf_template_system('test.pdf', 'dyslexia')")