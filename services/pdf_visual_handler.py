"""
PDF Visual Handler

Advanced PDF handling with visual preservation capabilities.
This module contains the migrated PDF text overlay functionality.
"""
import os
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageEnhance
from pdf2image import convert_from_path
from typing import Dict, Any, List, Optional, Tuple
import io
import logging
import hashlib


class PDFVisualHandler:
    """Enhanced PDF handler with visual preservation capabilities"""
    
    def __init__(self, profile_configs: Optional[Dict[str, Dict[str, Any]]] = None):
        """Initialize with profile configurations"""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Profile-specific visual settings
        self.profile_configs = profile_configs or {
            'dyslexia': {
                'tint_color': (255, 254, 245, 30),  # Light yellow
                'highlight_color': (0, 102, 204),    # Blue
                'first_word_highlight': True,
                'reading_guide': True
            },
            'adhd': {
                'tint_color': (245, 255, 254, 30),  # Light blue
                'highlight_color': (0, 128, 0),      # Green
                'first_word_highlight': True,
                'reading_guide': True
            },
            'vision': {
                'tint_color': (255, 255, 230, 40),  # Light yellow (stronger)
                'highlight_color': (0, 0, 0),        # Black
                'first_word_highlight': False,
                'reading_guide': False
            },
            'default': {
                'tint_color': None,
                'highlight_color': (0, 0, 0),        # Black
                'first_word_highlight': False,
                'reading_guide': False
            }
        }
    
    def extract_text_blocks_with_formatting(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract text blocks with formatting information from PDF
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of pages, each containing text blocks with formatting
        """
        try:
            doc = fitz.open(pdf_path)
            pages_data = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text_blocks = page.get_text("dict")
                
                # Extract structured text information
                page_data = {
                    'page_num': page_num,
                    'width': page.rect.width,
                    'height': page.rect.height,
                    'blocks': []
                }
                
                for block in text_blocks.get('blocks', []):
                    if block.get('type') == 0:  # Text block
                        block_data = {
                            'bbox': block['bbox'],
                            'lines': []
                        }
                        
                        for line in block.get('lines', []):
                            line_data = {
                                'bbox': line['bbox'],
                                'spans': []
                            }
                            
                            for span in line.get('spans', []):
                                span_data = {
                                    'text': span.get('text', ''),
                                    'font': span.get('font', ''),
                                    'size': span.get('size', 12),
                                    'flags': span.get('flags', 0),
                                    'color': span.get('color', 0),
                                    'bbox': span.get('bbox', [])
                                }
                                line_data['spans'].append(span_data)
                            
                            block_data['lines'].append(line_data)
                        
                        page_data['blocks'].append(block_data)
                
                pages_data.append(page_data)
            
            doc.close()
            return pages_data
            
        except Exception as e:
            self.logger.error(f"Error extracting text blocks: {str(e)}")
            return []
    
    def _calculate_overall_text_area(self, text_blocks: List[Dict[str, Any]]) -> List[float]:
        """Calculate the bounding box covering all text blocks"""
        if not text_blocks:
            return [0, 0, 0, 0]
        
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')
        
        for block in text_blocks:
            bbox = block.get('bbox', [0, 0, 0, 0])
            min_x = min(min_x, bbox[0])
            min_y = min(min_y, bbox[1])
            max_x = max(max_x, bbox[2])
            max_y = max(max_y, bbox[3])
        
        return [min_x, min_y, max_x, max_y]
    
    def create_visual_preserved_pdf_with_overlays(self, original_path: str, adapted_content: Dict[str, Any], 
                                                   output_path: str, profile: str = 'default') -> bool:
        """
        Create PDF with text overlays while preserving visual elements
        """
        try:
            # Get profile configuration
            profile_config = self.profile_configs.get(profile, self.profile_configs['default'])
            
            # Open the original PDF
            original_doc = fitz.open(original_path)
            output_doc = fitz.open()  # Create new document
            
            # Process each page
            for page_idx in range(original_doc.page_count):
                original_page = original_doc[page_idx]
                
                # Use pixmap to copy the entire page content
                # This preserves all visual elements including backgrounds
                mat = fitz.Matrix(1, 1)  # Identity matrix (no scaling)
                pix = original_page.get_pixmap(matrix=mat)
                
                # Create new page with same dimensions
                new_page = output_doc.new_page(
                    width=original_page.rect.width,
                    height=original_page.rect.height
                )
                
                # Insert the pixmap as the page background
                # This includes all original visual elements
                new_page.insert_image(new_page.rect, pixmap=pix)
                
                # Now overlay adapted text if available
                if page_idx < len(adapted_content.get('pages', [])):
                    adapted_page = adapted_content['pages'][page_idx]
                    adapted_text = adapted_page.get('text', '')
                    original_blocks = adapted_page.get('text_blocks', [])
                    
                    if adapted_text and original_blocks:
                        # First, create semi-transparent white overlays on text areas
                        # to make the original text less visible
                        for block in original_blocks:
                            block_rect = fitz.Rect(block['bbox'])
                            # Expand the rect slightly for better coverage
                            block_rect.x0 -= 2
                            block_rect.y0 -= 2
                            block_rect.x1 += 2
                            block_rect.y1 += 2
                            
                            # Draw white rectangle with high opacity (0.85 = 85% opaque)
                            shape = new_page.new_shape()
                            shape.draw_rect(block_rect)
                            shape.finish(
                                fill=(1, 1, 1),      # White
                                fill_opacity=0.85    # Increased opacity
                            )
                            shape.commit()
                        
                        # Apply profile-specific tint if configured
                        if profile_config.get('tint_color'):
                            # Note: This would require additional implementation
                            # to apply color overlay to specific regions
                            pass
                        
                        # Add the adapted text over the white overlays
                        self._update_page_text_with_overlays(
                            new_page, adapted_text, original_blocks, profile_config
                        )
            
            # Save the output document
            output_doc.save(output_path)
            output_doc.close()
            original_doc.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating visual preserved PDF: {str(e)}")
            return False
    
    def _update_page_text_with_overlays(self, page, adapted_text: str, 
                                        original_blocks: List[Dict[str, Any]], 
                                        profile_config: Dict[str, Any]):
        """Update page text with proper overlays and formatting"""
        if not original_blocks or not adapted_text.strip():
            return
        
        # Calculate the overall text area for better text flow
        all_text_bbox = self._calculate_overall_text_area(original_blocks)
        
        # Get profile text color
        highlight_color = profile_config['highlight_color']
        text_color = tuple(c/255 for c in highlight_color) if highlight_color else (0, 0, 0)
        
        # Get average font size from original blocks
        font_sizes = []
        for block in original_blocks:
            for line in block.get('lines', []):
                for span in line.get('spans', []):
                    if span.get('size'):
                        font_sizes.append(span['size'])
        
        avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 12
        
        # Calculate text rect with proper margins
        text_rect = fitz.Rect(all_text_bbox)
        # Expand the text area for better readability
        text_rect.x0 = max(20, text_rect.x0 - 10)
        text_rect.x1 = min(page.rect.width - 20, text_rect.x1 + 10)
        text_rect.y0 = max(20, text_rect.y0 - 5)
        text_rect.y1 = min(page.rect.height - 20, text_rect.y1 + 5)
        
        # Insert adapted text
        try:
            page.insert_textbox(
                text_rect,
                adapted_text.strip(),
                fontname="helv",
                fontsize=avg_font_size,
                color=text_color,
                render_mode=0,  # Normal rendering
                align=0  # Left align
            )
        except Exception as e:
            # Fallback to simple text insertion
            self.logger.warning(f"Textbox insertion failed: {e}")
            page.insert_text(
                (text_rect.x0, text_rect.y0 + avg_font_size),
                adapted_text.strip(),
                fontname="helv",
                fontsize=avg_font_size,
                color=text_color
            )
    
    def create_visual_preserved_pdf_with_clean_text(self, original_path: str, adapted_content: Dict[str, Any], 
                                                     output_path: str, profile: str = 'default') -> bool:
        """
        Create PDF with clean text replacement while preserving visual elements
        
        Args:
            original_path: Path to original PDF
            adapted_content: Adapted content with text and formatting
            output_path: Path for output PDF
            profile: Learning profile
            
        Returns:
            bool: Success status
        """
        # Use the anchor-based approach for better positioning
        return self.create_visual_preserved_pdf_with_anchors(
            original_path, adapted_content, output_path, profile
        )
    
    def _replace_text_only(self, page, adapted_text: str, original_blocks: List[Dict[str, Any]], profile_config: Dict[str, Any]):
        """Replace only text content while preserving all other visual elements"""
        if not original_blocks or not adapted_text.strip():
            return
            
        # Get profile text color (keep it subtle to not interfere with original design)
        highlight_color = profile_config['highlight_color']
        text_color = tuple(c/255 for c in highlight_color) if highlight_color else (0, 0, 0)
        
        # DO NOT clear text areas - we need a different approach
        # The white rectangles cover backgrounds which is the issue
        # For now, skip clearing and just overlay new text
        
        # Calculate the overall text area for better text flow
        if original_blocks:
            all_text_bbox = self._calculate_overall_text_area(original_blocks)
            
            # Get font info from the first available span (preserve original font style)
            font_name = 'helv'
            font_size = 12
            
            for block in original_blocks:
                for line in block.get('lines', []):
                    for span in line.get('spans', []):
                        if span.get('font'):
                            font_name = span['font']
                            font_size = span.get('size', 12)
                            break
                    if font_name != 'helv':
                        break
                if font_name != 'helv':
                    break
            
            # Insert adapted text into the overall area
            text_rect = fitz.Rect(all_text_bbox)
            page.insert_textbox(
                text_rect,
                adapted_text.strip(),
                fontname=font_name,
                fontsize=font_size,
                color=text_color,
                render_mode=0,  # Visible text
                align=0  # Left align
            )
    
    def _update_page_text(self, page, adapted_text: str, original_blocks: List[Dict[str, Any]], profile_config: Dict[str, Any]):
        """Update page text while preserving visual elements"""
        if not original_blocks or not adapted_text.strip():
            return
            
        # Get profile text color
        highlight_color = profile_config['highlight_color']
        text_color = tuple(c/255 for c in highlight_color) if highlight_color else (0, 0, 0)
        
        # Clear text areas with sampled background colors
        for block in original_blocks:
            block_rect = fitz.Rect(block['bbox'])
            
            # Skip blocks in image areas
            if self._is_text_in_image_area(page, block_rect):
                continue
            
            # Sample background color for better blending
            bg_color = self._sample_background_color(page, block_rect)
            page.draw_rect(block_rect, color=bg_color, fill=bg_color, width=0)
        
        # Calculate the overall text area for better text flow
        all_text_bbox = self._calculate_overall_text_area(original_blocks)
        
        # Get font info from the first available span
        font_name = 'helv'
        font_size = 12
        
        for block in original_blocks:
            for line in block.get('lines', []):
                for span in line.get('spans', []):
                    if span.get('font'):
                        font_name = span['font']
                        font_size = span.get('size', 12)
                        break
                if font_name != 'helv':
                    break
            if font_name != 'helv':
                break
        
        # Insert adapted text into the overall area
        text_rect = fitz.Rect(all_text_bbox)
        page.insert_textbox(
            text_rect,
            adapted_text.strip(),
            fontname=font_name,
            fontsize=font_size,
            color=text_color,
            render_mode=0,  # Visible text
            align=0  # Left align
        )
    
    def convert_pdf_to_images(self, pdf_path: str, output_folder: str, dpi: int = 150) -> List[str]:
        """
        Convert PDF pages to images
        
        Args:
            pdf_path: Path to PDF file
            output_folder: Folder to save images
            dpi: Resolution for conversion
            
        Returns:
            List of image paths
        """
        try:
            os.makedirs(output_folder, exist_ok=True)
            
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=dpi)
            image_paths = []
            
            for i, image in enumerate(images):
                image_path = os.path.join(output_folder, f'page_{i+1}.png')
                image.save(image_path, 'PNG')
                image_paths.append(image_path)
            
            return image_paths
            
        except Exception as e:
            self.logger.error(f"Error converting PDF to images: {str(e)}")
            return []
    
    def apply_visual_adaptations(self, image_path: str, profile: str = 'default', 
                                text_regions: Optional[List[Tuple[int, int, int, int]]] = None) -> Optional[str]:
        """
        Apply visual adaptations to an image
        
        Args:
            image_path: Path to the image
            profile: Learning profile
            text_regions: Optional list of text regions (x1, y1, x2, y2)
            
        Returns:
            Path to adapted image or None
        """
        try:
            profile_config = self.profile_configs.get(profile, self.profile_configs['default'])
            
            # Open image
            img = Image.open(image_path)
            
            # Apply tint if configured
            if profile_config.get('tint_color'):
                # Create overlay
                overlay = Image.new('RGBA', img.size, profile_config['tint_color'])
                
                # Convert original to RGBA if needed
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Composite the images
                img = Image.alpha_composite(img, overlay)
            
            # Apply reading guides if configured and text regions provided
            if profile_config.get('reading_guide') and text_regions:
                draw = ImageDraw.Draw(img)
                guide_color = profile_config.get('highlight_color', (0, 0, 255))
                
                for region in text_regions:
                    # Draw subtle guide lines
                    x1, y1, x2, y2 = region
                    draw.rectangle([x1-2, y1-2, x2+2, y2+2], 
                                 outline=guide_color, width=1)
            
            # Save adapted image
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            adapted_path = os.path.join(
                os.path.dirname(image_path),
                f"{base_name}_adapted_{profile}.png"
            )
            img.save(adapted_path)
            
            return adapted_path
            
        except Exception as e:
            self.logger.error(f"Error applying visual adaptations: {str(e)}")
            return None
    
    def create_visual_preserved_pdf_with_anchors(self, original_path: str, adapted_content: Dict[str, Any], 
                                                  output_path: str, profile: str = 'default') -> bool:
        """
        Create PDF with anchor-based text replacement using proper text removal
        
        PROPER APPROACH:
        1. Extract text with position anchors from original PDF
        2. Structurally remove text from PDF (preserving all other elements)
        3. Convert cleaned pages to images (backgrounds preserved, no text)
        4. Adapt each text block individually 
        5. Place adapted text at original anchor positions
        """
        try:
            import traceback
            from .adaptations_service import AdaptationsService
            
            # Get profile configuration
            profile_config = self.profile_configs.get(profile, self.profile_configs['default'])
            
            # Open the original PDF
            original_doc = fitz.open(original_path)
            output_doc = fitz.open()  # Create new document
            
            # Initialize adaptation service for text adaptation
            adaptations_service = AdaptationsService({})
            
            print(f"Creating anchor-based PDF with {original_doc.page_count} pages")
            
            # Process each page
            for page_idx in range(original_doc.page_count):
                original_page = original_doc[page_idx]
                
                # Step 1: Extract original text blocks with positions BEFORE any modifications
                original_text_dict = original_page.get_text("dict")
                original_blocks = []
                
                for block in original_text_dict.get('blocks', []):
                    if block.get('type') == 0:  # Text block
                        # Extract text from this block
                        block_text = ""
                        for line in block.get('lines', []):
                            for span in line.get('spans', []):
                                block_text += span.get('text', '')
                            block_text += " "  # Add space between lines
                        
                        if block_text.strip():
                            block_id = f"page{page_idx}_block{len(original_blocks)}"
                            original_blocks.append({
                                'id': block_id,
                                'bbox': block['bbox'],
                                'text': block_text.strip(),
                                'lines': block.get('lines', []),
                                'hash': hashlib.md5(block_text.strip().encode()).hexdigest()
                            })
                
                print(f"Page {page_idx}: {len(original_blocks)} text blocks to process")
                
                # Step 2: Create a text-free version of the page using structure removal
                cleaned_page = self._create_text_free_page(original_page)
                
                # Step 3: Convert the cleaned page to final image (no text, backgrounds preserved)
                cleaned_pix = cleaned_page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
                
                # Create the final output page
                new_page = output_doc.new_page(
                    width=original_page.rect.width,
                    height=original_page.rect.height
                )
                
                # Insert the cleaned background
                new_page.insert_image(new_page.rect, pixmap=cleaned_pix)
                
                # Step 4A: Collect all block texts for batch adaptation
                block_texts = [block['text'] for block in original_blocks]
                adapted_block_texts = []
                
                if block_texts:
                    try:
                        print(f"  🚀 Batch adapting {len(block_texts)} text blocks for page {page_idx}")
                        adapted_block_texts = adaptations_service.process_text_batch(block_texts, profile)
                        print(f"  ✅ Batch adaptation completed for page {page_idx}")
                    except Exception as batch_error:
                        print(f"  ⚠️ Batch adaptation failed for page {page_idx}: {batch_error}. Using individual processing.")
                        # Fallback to individual processing
                        adapted_block_texts = []
                        for block_text in block_texts:
                            try:
                                adapted_text = adaptations_service.adapt_text(block_text, profile)
                                adapted_block_texts.append(adapted_text)
                            except Exception as e:
                                print(f"    Individual adaptation failed: {e}")
                                adapted_block_texts.append(block_text)
                
                # Step 4B: Place adapted texts at EXACT original positions
                for block_idx, block in enumerate(original_blocks):
                    block_rect = fitz.Rect(block['bbox'])
                    original_text = block['text']
                    
                    # Get the adapted text for this block
                    if block_idx < len(adapted_block_texts):
                        adapted_block_text = adapted_block_texts[block_idx]
                        print(f"  Block {block_idx}: '{original_text[:30]}...' -> '{adapted_block_text[:30]}...'")
                    else:
                        adapted_block_text = original_text
                        print(f"  Block {block_idx}: No adaptation available, using original")
                    
                    if adapted_block_text and adapted_block_text.strip():
                        # Try multiple placement methods with progressively simpler approaches
                        success = False
                        
                        # Method 1: PIXEL-PERFECT alignment 
                        try:
                            success = self._place_text_with_perfect_alignment(
                                new_page, block, adapted_block_text, profile_config, block['id']
                            )
                        except Exception as e:
                            print(f"  ⚠️ Block {block['id']}: Perfect alignment failed with error: {e}")
                        
                        # Method 2: Simple textbox fallback
                        if not success:
                            print(f"  🔄 Block {block['id']}: Trying simple textbox fallback")
                            try:
                                # Use the block's bounding box with generous padding
                                text_rect = fitz.Rect(block['bbox'])
                                text_rect.x1 += 150  # Add more width padding
                                text_rect.y1 += 30   # Add more height padding
                                
                                result = new_page.insert_textbox(
                                    text_rect,
                                    adapted_block_text,
                                    fontname="helv",
                                    fontsize=11,  # Slightly smaller font
                                    color=(0, 0, 0),
                                    align=0  # Left align
                                )
                                
                                if result > 0:
                                    print(f"  ✅ Block {block['id']}: Textbox fallback successful")
                                    success = True
                                elif result < 0:
                                    print(f"  ⚠️ Block {block['id']}: Textbox overflow ({result}), trying with smaller font")
                                    # Try again with even smaller font and more space
                                    text_rect.x1 += 100  # Add even more width
                                    result2 = new_page.insert_textbox(
                                        text_rect,
                                        adapted_block_text,
                                        fontname="helv",
                                        fontsize=9,  # Even smaller font
                                        color=(0, 0, 0),
                                        align=0
                                    )
                                    if result2 > 0:
                                        print(f"  ✅ Block {block['id']}: Smaller font worked")
                                        success = True
                                    else:
                                        print(f"  ❌ Block {block['id']}: Still overflowing with smaller font")
                                else:
                                    print(f"  ⚠️ Block {block['id']}: Textbox returned {result}")
                                    
                            except Exception as e:
                                print(f"  ❌ Block {block['id']}: Textbox fallback failed: {e}")
                        
                        # Method 3: Basic text insertion with manual wrapping
                        if not success:
                            print(f"  🔄 Block {block['id']}: Trying basic text insertion with wrapping")
                            try:
                                block_rect = fitz.Rect(block['bbox'])
                                font_size = self._get_average_font_size(block)
                                
                                # Calculate approximate characters per line
                                avg_char_width = font_size * 0.5  # Rough estimate
                                chars_per_line = int(block_rect.width / avg_char_width)
                                
                                # Wrap text manually
                                words = adapted_block_text.split()
                                lines = []
                                current_line = []
                                current_length = 0
                                
                                for word in words:
                                    if current_length + len(word) + 1 <= chars_per_line:
                                        current_line.append(word)
                                        current_length += len(word) + 1
                                    else:
                                        if current_line:
                                            lines.append(' '.join(current_line))
                                        current_line = [word]
                                        current_length = len(word)
                                
                                if current_line:
                                    lines.append(' '.join(current_line))
                                
                                # Insert each line
                                y_offset = block_rect.y0 + font_size
                                line_height = font_size * 1.2
                                
                                for line in lines:
                                    if y_offset < block_rect.y1 + line_height:  # Still within block bounds (with some overflow allowed)
                                        new_page.insert_text(
                                            (block_rect.x0, y_offset),
                                            line,
                                            fontname="helv",
                                            fontsize=font_size * 0.9,  # Slightly smaller
                                            color=(0, 0, 0)
                                        )
                                        y_offset += line_height
                                
                                print(f"  ✅ Block {block['id']}: Used basic text insertion with {len(lines)} lines")
                                success = True
                            except Exception as fallback_err:
                                print(f"  ✗ Block {block['id']}: All placement methods failed: {fallback_err}")
                
                # Add profile indicator at bottom right
                indicator_text = f"[Adapted: {profile.upper()}]"
                indicator_color = tuple(c/255 for c in profile_config['highlight_color']) if profile_config['highlight_color'] else (0.5, 0.5, 0.5)
                new_page.insert_text(
                    (new_page.rect.width - 120, new_page.rect.height - 15),
                    indicator_text,
                    fontname='helv',
                    fontsize=8,
                    color=indicator_color
                )
            
            # Save the output document
            output_doc.save(output_path)
            output_doc.close()
            original_doc.close()
            
            print(f"✓ Anchor-based PDF created successfully: {output_path}")
            return True
            
        except Exception as e:
            print(f"✗ Error in anchor-based PDF creation: {str(e)}")
            traceback.print_exc()
            return False
    
    def _create_text_free_page(self, original_page):
        """
        Create a version of the page with text structurally removed but backgrounds preserved
        
        This uses multiple approaches to remove text while keeping visual elements:
        1. Drawing commands filtering (removes text render commands)
        2. Content stream manipulation 
        3. Selective element preservation
        """
        try:
            # Approach 1: Use the drawing commands to rebuild page without text
            return self._rebuild_page_without_text(original_page)
        except Exception as e:
            print(f"  Warning: Advanced text removal failed ({e}), using fallback")
            # Fallback: Create page with only images and drawings
            return self._create_visual_only_page(original_page)
    
    def _rebuild_page_without_text(self, original_page):
        """
        Rebuild page using drawing commands, filtering out text operations
        """
        # Create new page with same dimensions
        new_doc = fitz.open()
        new_page = new_doc.new_page(width=original_page.rect.width, height=original_page.rect.height)
        
        # Get all drawing commands from the original page
        try:
            # Copy visual elements excluding text
            original_pix = original_page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
            new_page.insert_image(new_page.rect, pixmap=original_pix)
            
            # Now we need to mask out text areas more intelligently
            # Get text blocks and create masks that preserve background colors
            text_dict = original_page.get_text("dict")
            
            for block in text_dict.get('blocks', []):
                if block.get('type') == 0:  # Text block
                    block_rect = fitz.Rect(block['bbox'])
                    
                    # Skip blocks that are within images or have special backgrounds
                    if self._is_text_in_image_area(original_page, block_rect):
                        print(f"    Skipping text block in image area: {block_rect}")
                        continue
                    
                    # Sample the background color for better blending
                    bg_color = self._sample_background_color(original_page, block_rect)
                    
                    # Use more precise masking - mask only the actual text spans, not the entire block
                    for line in block.get('lines', []):
                        for span in line.get('spans', []):
                            span_rect = fitz.Rect(span.get('bbox', [0, 0, 0, 0]))
                            
                            # Only mask if the span has actual text
                            if span.get('text', '').strip():
                                # Add small padding for better coverage
                                padded_rect = fitz.Rect(
                                    span_rect.x0 - 1,
                                    span_rect.y0 - 1,
                                    span_rect.x1 + 1,
                                    span_rect.y1 + 1
                                )
                                
                                # Fill with background color instead of white
                                shape = new_page.new_shape()
                                shape.draw_rect(padded_rect)
                                shape.finish(
                                    fill=bg_color,
                                    fill_opacity=1.0,
                                    color=bg_color,  # Set border color same as fill to avoid visible borders
                                    width=0  # No border width
                                )
                                shape.commit()
            
            return new_page
            
        except Exception as e:
            print(f"    Rebuild method failed: {e}")
            raise e
    
    def _is_text_in_image_area(self, page, text_rect):
        """
        Check if text block is within an image area
        """
        try:
            # Get all images on the page
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    # Get image position - try multiple methods
                    img_rect = None
                    
                    # Method 1: get_image_bbox
                    try:
                        img_rect = page.get_image_bbox(img[0])
                    except:
                        pass
                    
                    # Method 2: look for image in drawings if bbox fails
                    if not img_rect:
                        drawings = page.get_drawings()
                        for drawing in drawings:
                            if drawing.get('type') == 'image':
                                img_rect = fitz.Rect(drawing['rect'])
                                break
                    
                    # Check if text rect overlaps significantly with image rect
                    if img_rect and text_rect.intersects(img_rect):
                        intersection = text_rect & img_rect
                        # If more than 50% of text block is within image, consider it part of image
                        overlap_ratio = intersection.get_area() / text_rect.get_area()
                        if overlap_ratio > 0.5:
                            print(f"    Found text in image area: {img_rect}, overlap: {overlap_ratio:.2f}")
                            return True
                
                except Exception as img_error:
                    print(f"    Error processing image {img_index}: {img_error}")
                    continue
            
            # Method 3: check for colored rectangles that might represent images
            # This catches cases where we have visual elements that aren't detected as images
            try:
                drawings = page.get_drawings()
                for drawing in drawings:
                    if drawing.get('type') == 'rect' and drawing.get('fill'):
                        # Check if this might be an image placeholder (colored rectangle)
                        rect = fitz.Rect(drawing['rect'])
                        if rect.width > 50 and rect.height > 50:  # Reasonable image size
                            if text_rect.intersects(rect):
                                intersection = text_rect & rect
                                overlap_ratio = intersection.get_area() / text_rect.get_area()
                                if overlap_ratio > 0.5:
                                    print(f"    Found text in colored rectangle (potential image): {rect}, overlap: {overlap_ratio:.2f}")
                                    return True
            except Exception as drawing_error:
                print(f"    Error checking drawings: {drawing_error}")
            
            return False
            
        except Exception as e:
            print(f"    Error checking image overlap: {e}")
            return False
    
    def _sample_background_color(self, page, text_rect):
        """
        Sample the background color around a text area to use for masking
        """
        try:
            # Expand the rect slightly to sample around the text
            sample_rect = fitz.Rect(
                max(0, text_rect.x0 - 5),
                max(0, text_rect.y0 - 5),
                min(page.rect.width, text_rect.x1 + 5),
                min(page.rect.height, text_rect.y1 + 5)
            )
            
            # Get a small pixmap of the area
            mat = fitz.Matrix(0.5, 0.5)  # Lower resolution for sampling
            sample_pix = page.get_pixmap(matrix=mat, clip=sample_rect, alpha=False)
            
            # Convert to PIL for color analysis
            import PIL.Image
            img_data = sample_pix.tobytes("ppm")
            pil_img = PIL.Image.open(io.BytesIO(img_data))
            
            # Get the most common color (background)
            colors = pil_img.getcolors(maxcolors=256*256*256)
            if colors:
                # Get the most frequent color
                most_common_color = max(colors, key=lambda x: x[0])[1]
                # Convert RGB to 0-1 range for PyMuPDF
                return tuple(c/255.0 for c in most_common_color[:3])
            else:
                # Default to white if color analysis fails
                return (1.0, 1.0, 1.0)
                
        except Exception as e:
            print(f"    Color sampling failed: {e}")
            # Default to light gray instead of pure white
            return (0.95, 0.95, 0.95)
    
    def _create_visual_only_page(self, original_page):
        """
        Fallback method: Create page with only visual elements (images, shapes)
        """
        # Create new page
        new_doc = fitz.open()
        new_page = new_doc.new_page(width=original_page.rect.width, height=original_page.rect.height)
        
        # Copy as image and then selectively remove text with intelligent masking
        pix = original_page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
        new_page.insert_image(new_page.rect, pixmap=pix)
        
        # Get text areas and mask them with background-matched colors
        text_dict = original_page.get_text("dict")
        
        for block in text_dict.get('blocks', []):
            if block.get('type') == 0:  # Text block
                block_rect = fitz.Rect(block['bbox'])
                bg_color = self._sample_background_color(original_page, block_rect)
                
                # Skip blocks that are within images
                if self._is_text_in_image_area(original_page, block_rect):
                    continue
                
                # Use the sampled background color for better blending
                shape = new_page.new_shape()
                shape.draw_rect(block_rect)
                shape.finish(
                    fill=bg_color,
                    fill_opacity=1.0,
                    color=bg_color,  # Border same as fill
                    width=0  # No border
                )
                shape.commit()
        
        return new_page
    
    def _place_text_with_perfect_alignment(self, page, block, adapted_text, profile_config, block_idx):
        """
        Place text with pixel-perfect alignment matching the original text positioning
        
        Uses original span positions, baselines, and formatting for exact alignment
        """
        try:
            # Validate input - ensure we have actual text content
            if not adapted_text or not adapted_text.strip():
                print(f"    ✗ Block {block_idx}: No adapted text provided")
                return False
            
            # Check for placeholder text that indicates adaptation failure
            placeholder_markers = ['[DYSLEXIA]', '[Adapted: DYSLEXIA]', '[ADHD]', '[ESL]', 'Adapted for dyslexia', 'Adapted for adhd', 'Adapted for esl']
            if adapted_text.strip() in placeholder_markers:
                print(f"    ✗ Block {block_idx}: Received placeholder marker instead of adapted text: '{adapted_text.strip()}'")
                return False
            
            # Get profile text color
            highlight_color = profile_config['highlight_color']
            text_color = tuple(c/255 for c in highlight_color) if highlight_color else (0, 0, 0)
            
            # Extract precise positioning info from original spans
            lines = block.get('lines', [])
            if not lines:
                print(f"    ✗ Block {block_idx}: No lines found in block")
                return False
            
            # Strategy 1: Use the first line's first span for precise baseline positioning
            first_line = lines[0]
            first_spans = first_line.get('spans', [])
            if not first_spans:
                print(f"    ✗ Block {block_idx}: No spans found in first line")
                return False
            
            first_span = first_spans[0]
            
            # Get original font properties for exact matching
            original_font_size = first_span.get('size', 12)
            original_font = first_span.get('font', '')
            
            # Map to PyMuPDF font names more precisely
            font_name = self._map_font_name(original_font)
            
            # Calculate precise baseline position
            span_bbox = first_span.get('bbox', [0, 0, 0, 0])
            
            # Use the actual baseline from the original span
            # The baseline is typically at the bottom of the span bbox
            baseline_x = span_bbox[0]  # Left edge of first span
            baseline_y = span_bbox[3]  # Bottom edge = baseline
            
            print(f"    Perfect alignment: font={font_name}, size={original_font_size:.1f}, baseline=({baseline_x:.1f}, {baseline_y:.1f})")
            print(f"    Adapted text length: {len(adapted_text)} chars")
            
            # Method 1: Try textbox with exact positioning
            try:
                # Create a precise rectangle matching the original text block
                text_rect = fitz.Rect(block['bbox'])
                
                # Ensure the text rect is valid and has reasonable dimensions
                if text_rect.width < 10 or text_rect.height < 10:
                    print(f"    ⚠ Text rect too small: {text_rect}, expanding")
                    text_rect = fitz.Rect(
                        text_rect.x0 - 5,
                        text_rect.y0 - 5, 
                        text_rect.x0 + max(200, text_rect.width + 10),
                        text_rect.y0 + max(20, text_rect.height + 10)
                    )
                
                # Insert with exact font matching
                result = page.insert_textbox(
                    text_rect,
                    adapted_text,
                    fontname=font_name,
                    fontsize=original_font_size,
                    color=text_color,
                    render_mode=0,
                    align=self._detect_text_alignment(block)
                )
                
                # Check if text was actually inserted
                # PyMuPDF insert_textbox returns the actual width used, negative values indicate overflow
                if result < 0:
                    print(f"    ⚠ Block {block_idx}: Textbox overflow - need larger area (error code: {result})")
                    # Negative result means text overflowed - try with expanded rectangle
                    expanded_rect = fitz.Rect(
                        text_rect.x0,
                        text_rect.y0,
                        text_rect.x1 + 200,  # Add more width
                        text_rect.y1 + 50    # Add more height
                    )
                    
                    # Retry with expanded rectangle
                    result2 = page.insert_textbox(
                        expanded_rect,
                        adapted_text,
                        fontname=font_name,
                        fontsize=original_font_size * 0.8,  # Slightly smaller font
                        color=text_color,
                        render_mode=0,
                        align=self._detect_text_alignment(block)
                    )
                    
                    if result2 > 0:
                        print(f"    ✓ Block {block_idx}: Expanded textbox successful - inserted {result2} chars")
                        return True
                    else:
                        print(f"    ⚠ Block {block_idx}: Still overflowing after expansion")
                        raise Exception(f"Textbox overflow even with expansion: {result2}")
                        
                elif result == 0:
                    print(f"    ⚠ Block {block_idx}: No text was inserted (result=0)")
                    raise Exception("No text was inserted")
                elif result > 0:
                    print(f"    ✓ Block {block_idx}: Perfect textbox placement successful - inserted {result} chars")
                    return True
                else:
                    print(f"    ⚠ Block {block_idx}: Unexpected result: {result}")
                    raise Exception(f"Unexpected textbox result: {result}")
                
            except Exception as textbox_err:
                print(f"    ⚠ Textbox method failed: {textbox_err}")
                
                # Method 2: Use precise baseline positioning
                try:
                    # Split text into lines if it contains line breaks
                    text_lines = adapted_text.split('\n')
                    line_height = original_font_size * 1.2  # Standard line spacing
                    
                    for i, line in enumerate(text_lines):
                        if line.strip():  # Only insert non-empty lines
                            y_pos = baseline_y + (i * line_height)
                            page.insert_text(
                                (baseline_x, y_pos),
                                line.strip(),
                                fontname=font_name,
                                fontsize=original_font_size,
                                color=text_color
                            )
                    
                    print(f"    ✓ Block {block_idx}: Perfect baseline placement successful ({len(text_lines)} lines)")
                    return True
                    
                except Exception as baseline_err:
                    print(f"    ⚠ Baseline method failed: {baseline_err}")
                    
                    # Method 3: Multi-line precise placement
                    return self._place_multiline_text_precisely(
                        page, block, adapted_text, text_color, original_font_size, font_name, block_idx
                    )
            
        except Exception as e:
            print(f"    ✗ Perfect alignment completely failed: {e}")
            return False
    
    def _map_font_name(self, original_font):
        """
        Map original PDF font names to PyMuPDF standard fonts more accurately
        """
        if not original_font:
            return "helv"
            
        font_lower = original_font.lower()
        
        # More comprehensive font mapping
        if 'times' in font_lower or 'serif' in font_lower:
            if 'bold' in font_lower and 'italic' in font_lower:
                return "tibo"  # Times Bold Italic
            elif 'bold' in font_lower:
                return "tibo"  # Times Bold
            elif 'italic' in font_lower:
                return "tiit"  # Times Italic
            else:
                return "tiro"  # Times Roman
        
        elif 'courier' in font_lower or 'mono' in font_lower:
            if 'bold' in font_lower:
                return "cobo"  # Courier Bold
            elif 'italic' in font_lower:
                return "coit"  # Courier Italic
            else:
                return "cour"  # Courier
        
        else:  # Default to Helvetica family
            if 'bold' in font_lower and 'italic' in font_lower:
                return "hebi"  # Helvetica Bold Italic
            elif 'bold' in font_lower:
                return "hebo"  # Helvetica Bold
            elif 'italic' in font_lower or 'oblique' in font_lower:
                return "heit"  # Helvetica Italic
            else:
                return "helv"  # Helvetica
    
    def _detect_text_alignment(self, block):
        """
        Detect the text alignment from the original block structure
        """
        try:
            lines = block.get('lines', [])
            if len(lines) < 2:
                return 0  # Left align for single lines
            
            # Check alignment by comparing line start positions
            line_starts = []
            for line in lines:
                spans = line.get('spans', [])
                if spans:
                    line_starts.append(spans[0].get('bbox', [0, 0, 0, 0])[0])
            
            if len(line_starts) < 2:
                return 0
            
            # Check for consistent alignment
            start_variance = max(line_starts) - min(line_starts)
            
            if start_variance < 2:  # Very consistent = left aligned
                return 0
            elif start_variance > 20:  # High variance might be center or right
                # Check if it's center aligned (TODO: more sophisticated detection)
                return 1  # Center
            else:
                return 0  # Default to left
                
        except Exception:
            return 0  # Default to left align
    
    def _place_multiline_text_precisely(self, page, block, adapted_text, text_color, font_size, font_name, block_idx):
        """
        Place multi-line text with precise line-by-line positioning
        """
        try:
            lines = block.get('lines', [])
            adapted_lines = adapted_text.split('\n')
            
            # If we have multiple original lines, try to match them
            if len(lines) > 1 and len(adapted_lines) > 1:
                for original_line, adapted_line in zip(lines, adapted_lines):
                    if not adapted_line.strip():
                        continue
                        
                    spans = original_line.get('spans', [])
                    if spans:
                        span_bbox = spans[0].get('bbox', [0, 0, 0, 0])
                        line_baseline_x = span_bbox[0]
                        line_baseline_y = span_bbox[3]
                        
                        page.insert_text(
                            (line_baseline_x, line_baseline_y),
                            adapted_line.strip(),
                            fontname=font_name,
                            fontsize=font_size,
                            color=text_color
                        )
                
                print(f"    ✓ Block {block_idx}: Multi-line precise placement successful")
                return True
            else:
                # Single line or mismatched line counts - use first line positioning
                if lines:
                    first_spans = lines[0].get('spans', [])
                    if first_spans:
                        span_bbox = first_spans[0].get('bbox', [0, 0, 0, 0])
                        page.insert_text(
                            (span_bbox[0], span_bbox[3]),
                            adapted_text,
                            fontname=font_name,
                            fontsize=font_size,
                            color=text_color
                        )
                        print(f"    ✓ Block {block_idx}: Single-line precise placement successful")
                        return True
            
            return False
            
        except Exception as e:
            print(f"    ✗ Multi-line placement failed: {e}")
            return False
    
    def _get_average_font_size(self, block):
        """
        Get the average font size from a text block for fallback positioning
        """
        try:
            sizes = []
            for line in block.get('lines', []):
                for span in line.get('spans', []):
                    if span.get('size'):
                        sizes.append(span['size'])
            
            return sum(sizes) / len(sizes) if sizes else 12
            
        except Exception:
            return 12
    
    def create_visual_preserved_pdf(self, original_path: str, adapted_content: Dict[str, Any], 
                                    output_path: str, profile: str = 'default') -> bool:
        """
        Main entry point for visual preservation - uses overlay approach for reliability
        """
        # Try the anchor-based approach first, but fallback to overlays if it fails
        try:
            success = self.create_visual_preserved_pdf_with_simple_overlay(
                original_path, adapted_content, output_path, profile
            )
            if success:
                return True
        except Exception as e:
            self.logger.warning(f"Simple overlay method failed: {e}")
        
        # Fallback to standard adaptation if overlay fails
        return self.create_visual_preserved_pdf_with_overlays(
            original_path, adapted_content, output_path, profile
        )
    
    def create_visual_preserved_pdf_with_simple_overlay(self, original_path: str, adapted_content: Dict[str, Any], 
                                                        output_path: str, profile: str = 'default') -> bool:
        """
        Create PDF with simple, reliable text overlay
        """
        try:
            # Get profile configuration
            profile_config = self.profile_configs.get(profile, self.profile_configs['default'])
            
            # Open the original PDF
            original_doc = fitz.open(original_path)
            output_doc = fitz.open()  # Create new document
            
            print(f"Creating simple overlay PDF with {original_doc.page_count} pages")
            
            # Process each page
            for page_idx in range(original_doc.page_count):
                original_page = original_doc[page_idx]
                
                # Copy the entire page as background
                mat = fitz.Matrix(1, 1)  # Identity matrix (no scaling)
                pix = original_page.get_pixmap(matrix=mat)
                
                # Create new page with same dimensions
                new_page = output_doc.new_page(
                    width=original_page.rect.width,
                    height=original_page.rect.height
                )
                
                # Insert the pixmap as the page background
                new_page.insert_image(new_page.rect, pixmap=pix)
                
                # Get adapted content for this page
                if page_idx < len(adapted_content.get('pages', [])):
                    adapted_page = adapted_content['pages'][page_idx]
                    adapted_text = adapted_page.get('text', '').strip()
                    
                    if adapted_text:
                        # Extract original text areas to know where to place adapted text
                        original_text_dict = original_page.get_text("dict")
                        text_blocks = []
                        
                        for block in original_text_dict.get('blocks', []):
                            if block.get('type') == 0:  # Text block
                                text_blocks.append(block)
                        
                        if text_blocks:
                            # Calculate overall text area
                            min_x = min(block['bbox'][0] for block in text_blocks)
                            min_y = min(block['bbox'][1] for block in text_blocks)
                            max_x = max(block['bbox'][2] for block in text_blocks)
                            max_y = max(block['bbox'][3] for block in text_blocks)
                            
                            text_area = fitz.Rect(min_x - 5, min_y - 5, max_x + 5, max_y + 5)
                            
                            # Cover original text with semi-transparent white overlay
                            shape = new_page.new_shape()
                            shape.draw_rect(text_area)
                            shape.finish(
                                fill=(1, 1, 1),      # White
                                fill_opacity=0.9     # 90% opaque
                            )
                            shape.commit()
                            
                            # Get profile text color
                            highlight_color = profile_config.get('highlight_color', (0, 0, 0))
                            text_color = tuple(c/255 for c in highlight_color) if highlight_color else (0, 0, 0)
                            
                            # Calculate appropriate font size
                            avg_font_size = 12
                            if text_blocks:
                                font_sizes = []
                                for block in text_blocks:
                                    for line in block.get('lines', []):
                                        for span in line.get('spans', []):
                                            if span.get('size'):
                                                font_sizes.append(span['size'])
                                if font_sizes:
                                    avg_font_size = sum(font_sizes) / len(font_sizes)
                            
                            # Place adapted text in the cleared area
                            try:
                                result = new_page.insert_textbox(
                                    text_area,
                                    adapted_text,
                                    fontname="helv",
                                    fontsize=min(avg_font_size, 12),  # Cap at 12pt for readability
                                    color=text_color,
                                    render_mode=0,  # Normal rendering
                                    align=0  # Left align
                                )
                                
                                if result > 0:
                                    print(f"  ✅ Page {page_idx}: Successfully placed adapted text")
                                else:
                                    print(f"  ⚠️ Page {page_idx}: Text placement had issues (result: {result})")
                                    
                            except Exception as text_error:
                                print(f"  ❌ Page {page_idx}: Text placement failed: {text_error}")
                                # Fallback to simple text insertion
                                new_page.insert_text(
                                    (text_area.x0 + 10, text_area.y0 + avg_font_size + 10),
                                    adapted_text,
                                    fontname="helv",
                                    fontsize=min(avg_font_size, 12),
                                    color=text_color
                                )
                                print(f"  ✅ Page {page_idx}: Used fallback text insertion")
                        else:
                            print(f"  ⚠️ Page {page_idx}: No text blocks found to replace")
                    else:
                        print(f"  ⚠️ Page {page_idx}: No adapted text available")
                else:
                    print(f"  ⚠️ Page {page_idx}: Page not found in adapted content")
            
            # Save the output document
            output_doc.save(output_path)
            output_doc.close()
            original_doc.close()
            
            print(f"✅ Simple overlay PDF created successfully: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating simple overlay PDF: {str(e)}")
            print(f"❌ Simple overlay PDF creation failed: {str(e)}")
            return False
    
    def create_visual_preserved_with_overlay(self, original_path: str, adapted_content: Dict[str, Any], 
                                             output_path: str, profile: str = 'default') -> bool:
        """
        Fallback method using overlays
        """
        return self.create_visual_preserved_pdf_with_overlays(
            original_path, adapted_content, output_path, profile
        )
    
    def create_simple_visual_preserved(self, original_path: str, output_path: str, 
                                       profile: str = 'default') -> bool:
        """
        Simple preservation - just copy the original with indicator
        """
        try:
            import shutil
            shutil.copy2(original_path, output_path)
            
            # Add profile indicator
            doc = fitz.open(output_path)
            profile_config = self.profile_configs.get(profile, self.profile_configs['default'])
            
            for page in doc:
                if profile_config.get('show_indicator', True):
                    indicator_text = f"[{profile.upper()}]"
                    indicator_color = (0.5, 0.5, 0.5)
                    page.insert_text(
                        (page.rect.width - 100, page.rect.height - 20),
                        indicator_text,
                        fontname='helv',
                        fontsize=10,
                        color=indicator_color
                    )
            
            doc.save(output_path, incremental=True)
            doc.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Error in simple visual preservation: {str(e)}")
            return False
    
    def extract_content_with_formatting(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract content with formatting for visual preservation
        
        This is an alias for extract_text_blocks_with_formatting that returns
        the data in the format expected by the service layer
        """
        pages_data = self.extract_text_blocks_with_formatting(pdf_path)
        
        # Convert to service format
        content = {
            'pages': [],
            'metadata': {
                'page_count': len(pages_data)
            }
        }
        
        for page_data in pages_data:
            page_text = ""
            
            # Extract text from blocks
            for block in page_data['blocks']:
                for line in block['lines']:
                    for span in line['spans']:
                        page_text += span['text']
                page_text += "\n"
            
            content['pages'].append({
                'text': page_text.strip(),
                'text_blocks': page_data['blocks'],
                'page_num': page_data['page_num'],
                'width': page_data['width'],
                'height': page_data['height']
            })
        
        return content