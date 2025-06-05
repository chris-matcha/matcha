"""
Enhanced PDF Visual Handler with Performance Optimizations

Provides advanced visual preservation features for PDF adaptation
"""
import fitz
from typing import Dict, Any, List, Optional, Tuple, Callable
from .pdf_visual_handler import PDFVisualHandler
import logging
import os
import functools
import time
import gc
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed


class PDFVisualHandlerEnhanced(PDFVisualHandler):
    """Enhanced PDF handler with performance optimizations"""
    
    def __init__(self, profile_configs: Optional[Dict[str, Dict[str, Any]]] = None):
        super().__init__(profile_configs)
        self._background_cache = {}
        self._font_cache = {}
        self._adaptation_cache = {}
        self.logger = logging.getLogger(__name__)
    
    def _sample_background_color_cached(self, page, text_rect):
        """Cache background color sampling for performance"""
        # Create cache key from rect coordinates
        cache_key = f"{id(page)}_{text_rect.x0:.1f}_{text_rect.y0:.1f}_{text_rect.x1:.1f}_{text_rect.y1:.1f}"
        
        if cache_key in self._background_cache:
            return self._background_cache[cache_key]
        
        # Perform actual sampling
        color = self._sample_background_color(page, text_rect)
        self._background_cache[cache_key] = color
        return color
    
    def _get_text_metrics(self, text: str, font_name: str, font_size: float) -> Dict[str, float]:
        """Calculate text metrics for better positioning"""
        try:
            # Create temporary page for measurement
            temp_doc = fitz.open()
            temp_page = temp_doc.new_page(width=100, height=100)
            
            # Insert text to measure
            text_rect = fitz.Rect(0, 0, 100, 100)
            temp_page.insert_textbox(
                text_rect,
                text,
                fontname=font_name,
                fontsize=font_size
            )
            
            # Get the actual text dimensions
            text_instances = temp_page.search_for(text)
            if text_instances:
                actual_rect = text_instances[0]
                metrics = {
                    'width': actual_rect.width,
                    'height': actual_rect.height,
                    'ascent': font_size * 0.8,  # Approximate
                    'descent': font_size * 0.2   # Approximate
                }
            else:
                # Fallback estimation
                metrics = {
                    'width': len(text) * font_size * 0.6,
                    'height': font_size * 1.2,
                    'ascent': font_size * 0.8,
                    'descent': font_size * 0.2
                }
            
            temp_doc.close()
            return metrics
            
        except Exception as e:
            self.logger.warning(f"Could not calculate text metrics: {e}")
            return {
                'width': len(text) * font_size * 0.6,
                'height': font_size * 1.2,
                'ascent': font_size * 0.8,
                'descent': font_size * 0.2
            }
    
    def _create_gradient_overlay(self, page, rect, profile_config):
        """Create gradient overlay for better visual adaptation"""
        try:
            # Get the tint color
            tint_color = profile_config.get('tint_color')
            if not tint_color:
                return
            
            # Create gradient steps
            steps = 10
            opacity_start = tint_color[3] / 255.0 if len(tint_color) > 3 else 0.1
            opacity_end = 0.0
            
            step_height = rect.height / steps
            base_color = tuple(c/255.0 for c in tint_color[:3])
            
            for i in range(steps):
                step_rect = fitz.Rect(
                    rect.x0,
                    rect.y0 + (i * step_height),
                    rect.x1,
                    rect.y0 + ((i + 1) * step_height)
                )
                
                # Calculate opacity for this step
                opacity = opacity_start - (opacity_start - opacity_end) * (i / steps)
                
                shape = page.new_shape()
                shape.draw_rect(step_rect)
                shape.finish(
                    fill=base_color,
                    fill_opacity=opacity
                )
                shape.commit()
                
        except Exception as e:
            self.logger.warning(f"Could not create gradient overlay: {e}")
    
    def _optimize_text_layout(self, text: str, rect: fitz.Rect, font_size: float) -> List[str]:
        """Optimize text layout for better readability"""
        words = text.split()
        lines = []
        current_line = []
        
        # Approximate character width
        char_width = font_size * 0.6
        max_chars_per_line = int(rect.width / char_width)
        
        for word in words:
            # Check if adding this word exceeds line width
            current_length = sum(len(w) + 1 for w in current_line)
            if current_length + len(word) > max_chars_per_line and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def create_visual_preserved_pdf_with_advanced_features(
        self, 
        original_path: str, 
        adapted_content: Dict[str, Any], 
        output_path: str, 
        profile: str = 'default',
        options: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create PDF with advanced visual preservation features
        
        Options:
            - use_gradients: Apply gradient overlays
            - optimize_layout: Optimize text layout
            - preserve_images: Keep original images
            - add_reading_guides: Add visual reading guides
            - use_original_fonts: Try to match original fonts exactly
        """
        options = options or {}
        
        try:
            # Clear caches for new document
            self._background_cache.clear()
            self._font_cache.clear()
            
            profile_config = self.profile_configs.get(profile, self.profile_configs['default'])
            
            original_doc = fitz.open(original_path)
            output_doc = fitz.open()
            
            for page_idx in range(original_doc.page_count):
                original_page = original_doc[page_idx]
                
                # Extract text blocks with enhanced information
                text_blocks = self._extract_enhanced_text_blocks(original_page)
                
                # Create cleaned page
                cleaned_page = self._create_text_free_page_advanced(original_page, text_blocks)
                
                # Convert to pixmap
                pix = cleaned_page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
                
                # Create output page
                new_page = output_doc.new_page(
                    width=original_page.rect.width,
                    height=original_page.rect.height
                )
                
                # Insert background
                new_page.insert_image(new_page.rect, pixmap=pix)
                
                # Apply gradient overlay if requested
                if options.get('use_gradients') and profile_config.get('tint_color'):
                    self._create_gradient_overlay(new_page, new_page.rect, profile_config)
                
                # Process adapted content
                if page_idx < len(adapted_content.get('pages', [])):
                    adapted_page = adapted_content['pages'][page_idx]
                    
                    # Place adapted text with enhanced positioning
                    for block_idx, block in enumerate(text_blocks):
                        if block_idx < len(adapted_page.get('adapted_blocks', [])):
                            adapted_text = adapted_page['adapted_blocks'][block_idx]
                            
                            if options.get('optimize_layout'):
                                # Optimize text layout
                                lines = self._optimize_text_layout(
                                    adapted_text, 
                                    fitz.Rect(block['bbox']), 
                                    block['avg_font_size']
                                )
                                adapted_text = '\n'.join(lines)
                            
                            # Place text with enhanced alignment
                            self._place_text_enhanced(
                                new_page, block, adapted_text, profile_config, options
                            )
                
                # Add reading guides if requested
                if options.get('add_reading_guides') and profile_config.get('reading_guide'):
                    self._add_reading_guides(new_page, text_blocks, profile_config)
            
            # Add metadata
            output_doc.set_metadata({
                'title': original_doc.metadata.get('title', 'Adapted Document'),
                'subject': f"Adapted for {profile} profile",
                'creator': 'PDF Visual Handler Enhanced',
                'producer': 'PyMuPDF with Visual Preservation'
            })
            
            # Save with optimization
            output_doc.save(output_path, garbage=4, deflate=True, pretty=True)
            output_doc.close()
            original_doc.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in advanced visual preservation: {str(e)}")
            return False
    
    def _extract_enhanced_text_blocks(self, page) -> List[Dict[str, Any]]:
        """Extract text blocks with enhanced information"""
        text_dict = page.get_text("dict")
        enhanced_blocks = []
        
        for block in text_dict.get('blocks', []):
            if block.get('type') == 0:  # Text block
                # Calculate average font size and dominant font
                font_sizes = []
                font_names = {}
                
                for line in block.get('lines', []):
                    for span in line.get('spans', []):
                        if span.get('size'):
                            font_sizes.append(span['size'])
                        if span.get('font'):
                            font_name = span['font']
                            font_names[font_name] = font_names.get(font_name, 0) + 1
                
                # Get dominant font
                dominant_font = max(font_names.items(), key=lambda x: x[1])[0] if font_names else 'helv'
                
                enhanced_block = {
                    'bbox': block['bbox'],
                    'lines': block.get('lines', []),
                    'avg_font_size': sum(font_sizes) / len(font_sizes) if font_sizes else 12,
                    'dominant_font': dominant_font,
                    'text_direction': self._detect_text_direction(block),
                    'is_heading': self._is_heading(block, font_sizes)
                }
                
                enhanced_blocks.append(enhanced_block)
        
        return enhanced_blocks
    
    def _detect_text_direction(self, block) -> str:
        """Detect if text is horizontal or vertical"""
        # Simple detection based on block dimensions
        bbox = block.get('bbox', [0, 0, 0, 0])
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        
        return 'vertical' if height > width * 2 else 'horizontal'
    
    def _is_heading(self, block, font_sizes) -> bool:
        """Detect if block is likely a heading"""
        if not font_sizes:
            return False
        
        avg_size = sum(font_sizes) / len(font_sizes)
        
        # Headings typically have larger font size and fewer lines
        lines = block.get('lines', [])
        return avg_size > 14 and len(lines) <= 2
    
    def _create_text_free_page_advanced(self, original_page, text_blocks) -> fitz.Page:
        """Create text-free page with advanced background preservation"""
        new_doc = fitz.open()
        new_page = new_doc.new_page(
            width=original_page.rect.width,
            height=original_page.rect.height
        )
        
        # Copy page as image
        pix = original_page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
        new_page.insert_image(new_page.rect, pixmap=pix)
        
        # Advanced text masking with intelligent color matching
        for block in text_blocks:
            block_rect = fitz.Rect(block['bbox'])
            
            # Sample multiple points for better color matching
            sample_points = [
                (block_rect.x0 - 5, block_rect.y0 - 5),    # Top-left
                (block_rect.x1 + 5, block_rect.y0 - 5),    # Top-right
                (block_rect.x0 - 5, block_rect.y1 + 5),    # Bottom-left
                (block_rect.x1 + 5, block_rect.y1 + 5),    # Bottom-right
            ]
            
            colors = []
            for point in sample_points:
                color = self._sample_color_at_point(original_page, point)
                if color:
                    colors.append(color)
            
            # Use the most common color or average
            if colors:
                # Simple average for now
                avg_color = tuple(sum(c[i] for c in colors) / len(colors) for i in range(3))
            else:
                avg_color = (1.0, 1.0, 1.0)  # Default to white
            
            # Fill with matched color
            shape = new_page.new_shape()
            shape.draw_rect(block_rect)
            shape.finish(fill=avg_color, fill_opacity=1.0)
            shape.commit()
        
        return new_page
    
    def _sample_color_at_point(self, page, point) -> Optional[Tuple[float, float, float]]:
        """Sample color at specific point"""
        try:
            x, y = point
            
            # Ensure point is within page bounds
            if x < 0 or y < 0 or x > page.rect.width or y > page.rect.height:
                return None
            
            # Create small rect around point
            sample_rect = fitz.Rect(x-1, y-1, x+1, y+1)
            
            # Get pixmap of small area
            pix = page.get_pixmap(clip=sample_rect, alpha=False)
            
            # Get color from center pixel
            if pix.width > 0 and pix.height > 0:
                pixel = pix.pixel(0, 0)
                return tuple(c/255.0 for c in pixel[:3])
            
            return None
            
        except Exception:
            return None
    
    def _place_text_enhanced(self, page, block, adapted_text, profile_config, options):
        """Enhanced text placement with additional features"""
        # Get text metrics for better positioning
        metrics = self._get_text_metrics(
            adapted_text,
            self._map_font_name(block['dominant_font']),
            block['avg_font_size']
        )
        
        # Apply special formatting for headings
        if block['is_heading']:
            # Slightly larger font for headings
            font_size = block['avg_font_size'] * 1.1
            # Bold font variant
            font_name = self._map_font_name_bold(block['dominant_font'])
        else:
            font_size = block['avg_font_size']
            font_name = self._map_font_name(block['dominant_font'])
        
        # Get color
        text_color = tuple(c/255 for c in profile_config['highlight_color']) if profile_config['highlight_color'] else (0, 0, 0)
        
        # Calculate precise position
        bbox = block['bbox']
        
        # Apply slight offset for better visual appearance
        x_offset = 2
        y_offset = 2
        
        try:
            # Use textbox for better text flow
            text_rect = fitz.Rect(
                bbox[0] + x_offset,
                bbox[1] + y_offset,
                bbox[2] - x_offset,
                bbox[3] - y_offset
            )
            
            page.insert_textbox(
                text_rect,
                adapted_text,
                fontname=font_name,
                fontsize=font_size,
                color=text_color,
                align=self._detect_text_alignment(block)
            )
            
        except Exception as e:
            # Fallback to simple text insertion
            self.logger.warning(f"Enhanced text placement failed: {e}")
            page.insert_text(
                (bbox[0] + x_offset, bbox[1] + font_size + y_offset),
                adapted_text,
                fontname=font_name,
                fontsize=font_size,
                color=text_color
            )
    
    def _detect_text_alignment(self, block) -> int:
        """Detect text alignment based on block properties"""
        # For now, return left alignment (0)
        # Could be enhanced to detect center (1) or right (2) alignment
        return 0
    
    def _map_font_name_bold(self, original_font) -> str:
        """Map to bold variant of font"""
        if not original_font:
            return "hebo"  # Helvetica Bold
        
        font_lower = original_font.lower()
        
        if 'times' in font_lower or 'serif' in font_lower:
            return "tibo"  # Times Bold
        elif 'courier' in font_lower or 'mono' in font_lower:
            return "cobo"  # Courier Bold
        else:
            return "hebo"  # Helvetica Bold
    
    def _add_reading_guides(self, page, text_blocks, profile_config):
        """Add visual reading guides to help with text tracking"""
        guide_color = profile_config.get('highlight_color', (0, 0, 255))
        guide_color_normalized = tuple(c/255 for c in guide_color)
        
        for block in text_blocks:
            if block['is_heading']:
                continue  # Skip headings
            
            bbox = block['bbox']
            
            # Add subtle left margin indicator
            shape = page.new_shape()
            shape.draw_line(
                fitz.Point(bbox[0] - 5, bbox[1]),
                fitz.Point(bbox[0] - 5, bbox[3])
            )
            shape.finish(
                color=guide_color_normalized,
                width=2,
                stroke_opacity=0.3
            )
            shape.commit()
            
            # Add subtle underline for each line
            for line in block.get('lines', []):
                line_bbox = line.get('bbox', [])
                if line_bbox:
                    shape = page.new_shape()
                    shape.draw_line(
                        fitz.Point(line_bbox[0], line_bbox[3] + 1),
                        fitz.Point(line_bbox[2], line_bbox[3] + 1)
                    )
                    shape.finish(
                        color=guide_color_normalized,
                        width=1,
                        stroke_opacity=0.2
                    )
                    shape.commit()
    
    def batch_process_pdfs(
        self,
        pdf_paths: List[str],
        adapted_contents: Dict[str, Dict[str, Any]],
        output_dir: str,
        profile: str = 'default',
        options: Optional[Dict[str, Any]] = None,
        max_workers: int = 4
    ) -> Dict[str, bool]:
        """
        Batch process multiple PDFs with parallel processing
        
        Args:
            pdf_paths: List of input PDF paths
            adapted_contents: Dict mapping PDF paths to adapted content
            output_dir: Directory for output files
            profile: Profile to use for adaptation
            options: Processing options
            max_workers: Maximum parallel workers
            
        Returns:
            Dict mapping input paths to success status
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import os
        
        results = {}
        
        def process_single(pdf_path: str) -> Tuple[str, bool]:
            try:
                # Generate output path
                basename = os.path.basename(pdf_path)
                output_path = os.path.join(output_dir, f"adapted_{profile}_{basename}")
                
                # Get adapted content
                adapted_content = adapted_contents.get(pdf_path, {})
                
                # Process PDF
                success = self.create_visual_preserved_pdf_with_advanced_features(
                    pdf_path,
                    adapted_content,
                    output_path,
                    profile,
                    options
                )
                
                return pdf_path, success
                
            except Exception as e:
                self.logger.error(f"Error processing {pdf_path}: {e}")
                return pdf_path, False
        
        # Process PDFs in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(process_single, pdf_path): pdf_path
                for pdf_path in pdf_paths
            }
            
            for future in as_completed(futures):
                pdf_path, success = future.result()
                results[pdf_path] = success
                self.logger.info(f"Processed {pdf_path}: {'Success' if success else 'Failed'}")
        
        return results
    
    def optimize_for_screen_reader(
        self,
        original_path: str,
        output_path: str,
        preserve_structure: bool = True
    ) -> bool:
        """
        Optimize PDF for screen reader accessibility
        
        Args:
            original_path: Input PDF path
            output_path: Output PDF path
            preserve_structure: Maintain document structure
            
        Returns:
            Success status
        """
        try:
            doc = fitz.open(original_path)
            
            # Extract all text with structure
            full_text = []
            
            for page_idx, page in enumerate(doc):
                page_text = f"\n--- Page {page_idx + 1} ---\n"
                
                # Get structured text
                text_dict = page.get_text("dict")
                
                for block in text_dict.get('blocks', []):
                    if block.get('type') == 0:  # Text block
                        block_text = ""
                        
                        for line in block.get('lines', []):
                            line_text = ""
                            for span in line.get('spans', []):
                                line_text += span.get('text', '')
                            
                            if line_text.strip():
                                block_text += line_text + "\n"
                        
                        if block_text.strip():
                            # Add heading markers for accessibility
                            if self._is_heading(block, [span.get('size', 12) for line in block.get('lines', []) for span in line.get('spans', [])]):
                                full_text.append(f"# {block_text.strip()}")
                            else:
                                full_text.append(block_text.strip())
                
                full_text.append("")  # Page break
            
            # Create new accessible PDF
            new_doc = fitz.open()
            
            # Add text as a single accessible layer
            page = new_doc.new_page(width=612, height=792)
            
            # Insert text with proper structure
            text_content = "\n".join(full_text)
            
            # Use textbox for better formatting
            page.insert_textbox(
                fitz.Rect(72, 72, 540, 720),
                text_content,
                fontname="helv",
                fontsize=12,
                align=0
            )
            
            # Add metadata for accessibility
            new_doc.set_metadata({
                'title': doc.metadata.get('title', 'Screen Reader Optimized Document'),
                'subject': 'Optimized for screen reader accessibility',
                'creator': 'PDF Visual Handler Enhanced',
                'keywords': 'accessible, screen reader, optimized'
            })
            
            # Save with text extraction enabled
            new_doc.save(output_path, garbage=4, deflate=True)
            new_doc.close()
            doc.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error optimizing for screen reader: {e}")
            return False
    
    def calculate_adaptation_quality_metrics(self, original_path: str, 
                                           adapted_path: str) -> Dict[str, Any]:
        """Calculate quality metrics for the adaptation"""
        metrics = {
            'visual_preservation': 0.0,
            'text_alignment': 0.0,
            'readability_improvement': 0.0,
            'file_size_ratio': 0.0,
            'processing_complexity': 0.0
        }
        
        try:
            # Compare file sizes
            original_size = os.path.getsize(original_path)
            adapted_size = os.path.getsize(adapted_path)
            metrics['file_size_ratio'] = adapted_size / original_size
            
            # Open both documents
            orig_doc = fitz.open(original_path)
            adapt_doc = fitz.open(adapted_path)
            
            # Check page count preservation
            if orig_doc.page_count == adapt_doc.page_count:
                metrics['visual_preservation'] += 0.3
            
            # Sample visual similarity (using first page)
            if orig_doc.page_count > 0:
                orig_pix = orig_doc[0].get_pixmap(matrix=fitz.Matrix(0.2, 0.2))
                adapt_pix = adapt_doc[0].get_pixmap(matrix=fitz.Matrix(0.2, 0.2))
                
                # Simple pixel comparison (could use more sophisticated methods)
                if orig_pix.size == adapt_pix.size:
                    metrics['visual_preservation'] += 0.7
            
            # Text alignment check
            for i in range(min(3, orig_doc.page_count)):
                orig_blocks = orig_doc[i].get_text("dict")['blocks']
                adapt_blocks = adapt_doc[i].get_text("dict")['blocks']
                
                if len(orig_blocks) > 0:
                    # Check if text blocks are in similar positions
                    alignment_score = self._calculate_alignment_score(orig_blocks, adapt_blocks)
                    metrics['text_alignment'] += alignment_score / min(3, orig_doc.page_count)
            
            # Calculate readability improvement based on font size changes
            orig_avg_font_size = self._get_average_font_size(orig_doc)
            adapt_avg_font_size = self._get_average_font_size(adapt_doc)
            
            if adapt_avg_font_size > orig_avg_font_size:
                metrics['readability_improvement'] = min(1.0, (adapt_avg_font_size - orig_avg_font_size) / orig_avg_font_size)
            
            orig_doc.close()
            adapt_doc.close()
            
            # Overall quality score
            metrics['overall_quality'] = sum(metrics.values()) / len(metrics)
            
        except Exception as e:
            self.logger.error(f"Quality metrics calculation failed: {e}")
        
        return metrics
    
    def _calculate_alignment_score(self, orig_blocks, adapt_blocks) -> float:
        """Calculate how well adapted text aligns with original positions"""
        if not orig_blocks or not adapt_blocks:
            return 0.0
        
        score = 0.0
        matches = 0
        
        for orig in orig_blocks:
            if orig.get('type') != 0:  # Not a text block
                continue
                
            orig_bbox = orig['bbox']
            
            # Find closest adapted block
            min_distance = float('inf')
            for adapt in adapt_blocks:
                if adapt.get('type') != 0:
                    continue
                    
                adapt_bbox = adapt['bbox']
                
                # Calculate distance between block centers
                orig_center = ((orig_bbox[0] + orig_bbox[2])/2, (orig_bbox[1] + orig_bbox[3])/2)
                adapt_center = ((adapt_bbox[0] + adapt_bbox[2])/2, (adapt_bbox[1] + adapt_bbox[3])/2)
                
                distance = ((orig_center[0] - adapt_center[0])**2 + 
                           (orig_center[1] - adapt_center[1])**2)**0.5
                
                min_distance = min(min_distance, distance)
            
            # Score based on distance (closer = better)
            if min_distance < 10:  # Very close
                score += 1.0
            elif min_distance < 50:  # Reasonably close
                score += 0.5
            
            matches += 1
        
        return score / matches if matches > 0 else 0.0
    
    def _get_average_font_size(self, doc) -> float:
        """Calculate average font size across document"""
        total_size = 0
        count = 0
        
        # Sample first few pages
        for page_num in range(min(5, doc.page_count)):
            page = doc[page_num]
            text_dict = page.get_text("dict")
            
            for block in text_dict.get('blocks', []):
                if block.get('type') == 0:  # Text block
                    for line in block.get('lines', []):
                        for span in line.get('spans', []):
                            if span.get('size'):
                                total_size += span['size']
                                count += 1
        
        return total_size / count if count > 0 else 12.0
    
    def batch_process_pdfs_with_progress(self, pdf_files: List[Dict[str, str]], 
                          profile: str,
                          progress_callback: Optional[Callable] = None,
                          options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Batch process multiple PDFs with visual preservation and progress tracking
        
        Args:
            pdf_files: List of dicts with 'input' and 'output' paths
            profile: Learning profile to apply
            progress_callback: Optional callback for progress updates (current, total, message)
            options: Processing options
            
        Returns:
            Results dictionary with success/failure info
        """
        results = {
            'successful': [],
            'failed': [],
            'total_time': 0,
            'quality_metrics': {}
        }
        
        start_time = time.time()
        
        for idx, file_info in enumerate(pdf_files):
            if progress_callback:
                progress_callback(idx, len(pdf_files), f"Processing {os.path.basename(file_info['input'])}")
            
            try:
                # Extract content with formatting
                content = self.extract_content_with_formatting(file_info['input'])
                
                # Create adapted PDF
                success = self.create_visual_preserved_pdf_with_advanced_features(
                    file_info['input'],
                    content,
                    file_info['output'],
                    profile,
                    options
                )
                
                if success:
                    results['successful'].append(file_info['output'])
                    
                    # Calculate quality metrics
                    metrics = self.calculate_adaptation_quality_metrics(
                        file_info['input'],
                        file_info['output']
                    )
                    results['quality_metrics'][file_info['output']] = metrics
                else:
                    results['failed'].append({
                        'file': file_info['input'],
                        'error': 'Processing failed'
                    })
                    
            except Exception as e:
                results['failed'].append({
                    'file': file_info['input'],
                    'error': str(e)
                })
        
        results['total_time'] = time.time() - start_time
        
        if progress_callback:
            progress_callback(len(pdf_files), len(pdf_files), "Batch processing complete")
        
        return results
    
    def parallel_page_processing(self, pdf_path: str, profile: str, 
                               max_workers: int = 4) -> List[Dict[str, Any]]:
        """Process PDF pages in parallel for better performance"""
        doc = fitz.open(pdf_path)
        total_pages = doc.page_count
        
        # Extract pages data for parallel processing
        pages_data = []
        for page_num in range(total_pages):
            page = doc[page_num]
            page_data = {
                'page_num': page_num,
                'text_dict': page.get_text("dict"),
                'rect': page.rect,
                'rotation': page.rotation
            }
            pages_data.append(page_data)
        
        doc.close()
        
        # Process pages in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self._process_single_page, page_data, profile) 
                for page_data in pages_data
            ]
            
            results = []
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Page processing failed: {e}")
                    results.append(None)
        
        # Sort results by page number
        results.sort(key=lambda x: x['page_num'] if x else float('inf'))
        
        return results
    
    def _process_single_page(self, page_data: Dict[str, Any], profile: str) -> Dict[str, Any]:
        """Process a single page (for parallel processing)"""
        try:
            # Extract enhanced text blocks
            enhanced_blocks = []
            text_dict = page_data['text_dict']
            
            for block in text_dict.get('blocks', []):
                if block.get('type') == 0:  # Text block
                    # Process block
                    enhanced_block = self._enhance_text_block(block)
                    enhanced_blocks.append(enhanced_block)
            
            return {
                'page_num': page_data['page_num'],
                'enhanced_blocks': enhanced_blocks,
                'success': True
            }
            
        except Exception as e:
            return {
                'page_num': page_data['page_num'],
                'error': str(e),
                'success': False
            }
    
    def _enhance_text_block(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance a single text block with additional metadata"""
        font_sizes = []
        font_names = {}
        
        for line in block.get('lines', []):
            for span in line.get('spans', []):
                if span.get('size'):
                    font_sizes.append(span['size'])
                if span.get('font'):
                    font_name = span['font']
                    font_names[font_name] = font_names.get(font_name, 0) + 1
        
        # Get dominant font
        dominant_font = max(font_names.items(), key=lambda x: x[1])[0] if font_names else 'helv'
        
        return {
            'bbox': block['bbox'],
            'lines': block.get('lines', []),
            'avg_font_size': sum(font_sizes) / len(font_sizes) if font_sizes else 12,
            'dominant_font': dominant_font,
            'text_direction': self._detect_text_direction(block),
            'is_heading': self._is_heading(block, font_sizes)
        }
    
    def process_large_pdf_in_chunks(self, pdf_path: str, output_path: str,
                                  profile: str, chunk_size: int = 10,
                                  options: Optional[Dict[str, Any]] = None) -> bool:
        """Process large PDFs in chunks to manage memory"""
        try:
            doc = fitz.open(pdf_path)
            total_pages = doc.page_count
            
            # Create output document
            output_doc = fitz.open()
            
            for start in range(0, total_pages, chunk_size):
                end = min(start + chunk_size, total_pages)
                
                self.logger.info(f"Processing pages {start} to {end} of {total_pages}")
                
                # Process chunk
                chunk_results = self._process_page_range(doc, start, end, profile, options)
                
                # Add processed pages to output
                for result in chunk_results:
                    if result and result.get('page'):
                        output_doc.insert_pdf(
                            result['page'].parent,
                            from_page=result['page'].number,
                            to_page=result['page'].number
                        )
                
                # Force garbage collection after each chunk
                gc.collect()
            
            # Save output document
            output_doc.save(output_path, garbage=4, deflate=True)
            output_doc.close()
            doc.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing large PDF: {e}")
            return False
    
    def _process_page_range(self, doc, start: int, end: int, profile: str,
                          options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Process a range of pages"""
        results = []
        profile_config = self.profile_configs.get(profile, self.profile_configs['default'])
        
        for page_num in range(start, end):
            try:
                page = doc[page_num]
                
                # Extract enhanced text blocks
                text_blocks = self._extract_enhanced_text_blocks(page)
                
                # Create processed page data
                result = {
                    'page_num': page_num,
                    'text_blocks': text_blocks,
                    'page': page,
                    'success': True
                }
                
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Error processing page {page_num}: {e}")
                results.append({
                    'page_num': page_num,
                    'error': str(e),
                    'success': False
                })
        
        return results
    
    @functools.lru_cache(maxsize=128)
    def _map_font_name_cached(self, original_font: str) -> str:
        """Cached version of font mapping for performance"""
        return self._map_font_name(original_font)