"""
Downloads Service

Manages file downloads and export operations for adapted/translated content.
"""
import os
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from .base_service import BaseService
from .filestore_service import FileStoreService
from .formats_service import FormatsService


class DownloadsService(BaseService):
    """Service for managing downloads"""
    
    def _initialize(self):
        """Initialize downloads service"""
        self.filestore = FileStoreService(self.config)
        self.formats = FormatsService(self.config)
        
        # Configure download paths
        self.download_base_url = self.config.get('download_base_url', '/download')
        self.temp_download_dir = self.config.get('temp_download_dir', 'downloads')
    
    def prepare_download(self, content: Dict[str, Any], filename: str, 
                        file_type: str, profile: Optional[str] = None,
                        language: Optional[str] = None) -> Dict[str, Any]:
        """
        Prepare a file for download
        
        Args:
            content: Content to prepare for download
            filename: Original filename
            file_type: Type of file ('pdf' or 'pptx')
            profile: Learning profile used for adaptation
            language: Translation language if applicable
            
        Returns:
            Download information including path and metadata
        """
        # Generate output filename
        output_filename = self._generate_filename(filename, profile, language)
        
        # Create temporary file
        temp_path = self.filestore.get_temp_path(output_filename)
        
        # Create the file
        success = self.formats.create_file(content, temp_path, file_type, profile or 'default')
        
        if not success:
            raise Exception(f"Failed to create {file_type} file")
        
        # Move to outputs directory
        final_path = self.filestore.save_output(temp_path, output_filename)
        
        # Generate download info
        download_info = {
            'filename': output_filename,
            'path': final_path,
            'file_type': file_type,
            'profile': profile,
            'language': language,
            'download_url': f"{self.download_base_url}/{os.path.basename(final_path)}",
            'size': os.path.getsize(final_path) if os.path.exists(final_path) else 0
        }
        
        return download_info
    
    def list_available_downloads(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all available downloads
        
        Args:
            session_id: Optional session ID to filter downloads
            
        Returns:
            List of available downloads
        """
        downloads = []
        
        # Get all output files
        output_files = self.filestore.list_outputs()
        
        for file_info in output_files:
            # Parse filename to extract metadata
            metadata = self._parse_filename(file_info['filename'])
            
            # Filter by session if specified
            if session_id and metadata.get('session_id') != session_id:
                continue
            
            download = {
                'filename': file_info['filename'],
                'path': file_info['path'],
                'size': file_info['size'],
                'created': file_info['created'],
                'download_url': f"{self.download_base_url}/{file_info['filename']}",
                **metadata
            }
            
            downloads.append(download)
        
        return downloads
    
    def get_download_by_id(self, download_id: str) -> Optional[Dict[str, Any]]:
        """
        Get download information by ID
        
        Args:
            download_id: Download identifier (filename without extension)
            
        Returns:
            Download information or None
        """
        # Search for the file
        output_files = self.filestore.list_outputs()
        
        for file_info in output_files:
            if download_id in file_info['filename']:
                metadata = self._parse_filename(file_info['filename'])
                return {
                    'filename': file_info['filename'],
                    'path': file_info['path'],
                    'size': file_info['size'],
                    'created': file_info['created'],
                    'download_url': f"{self.download_base_url}/{file_info['filename']}",
                    **metadata
                }
        
        return None
    
    def check_translation_exists(self, original_filename: str, language: str) -> Optional[Dict[str, Any]]:
        """
        Check if a translation exists for a file
        
        Args:
            original_filename: Original filename
            language: Target language
            
        Returns:
            Translation download info if exists
        """
        # Look for translated versions
        output_files = self.filestore.list_outputs()
        
        # Extract base name from original
        base_name = Path(original_filename).stem
        
        for file_info in output_files:
            if f'translated_{language}' in file_info['filename'] and base_name in file_info['filename']:
                metadata = self._parse_filename(file_info['filename'])
                return {
                    'filename': file_info['filename'],
                    'path': file_info['path'],
                    'size': file_info['size'],
                    'created': file_info['created'],
                    'download_url': f"{self.download_base_url}/{file_info['filename']}",
                    **metadata
                }
        
        return None
    
    def check_adapted_versions(self, original_filename: str) -> List[Dict[str, Any]]:
        """
        Check for all adapted versions of a file
        
        Args:
            original_filename: Original filename
            
        Returns:
            List of adapted versions
        """
        adapted_versions = []
        output_files = self.filestore.list_outputs()
        
        # Extract base name
        base_name = Path(original_filename).stem
        
        for file_info in output_files:
            if base_name in file_info['filename'] and 'adapted' in file_info['filename']:
                metadata = self._parse_filename(file_info['filename'])
                adapted_versions.append({
                    'filename': file_info['filename'],
                    'path': file_info['path'],
                    'size': file_info['size'],
                    'created': file_info['created'],
                    'download_url': f"{self.download_base_url}/{file_info['filename']}",
                    **metadata
                })
        
        return adapted_versions
    
    def _generate_filename(self, original_filename: str, profile: Optional[str] = None,
                          language: Optional[str] = None) -> str:
        """Generate output filename based on adaptations"""
        base_name = Path(original_filename).stem
        extension = Path(original_filename).suffix
        
        parts = []
        
        # Add profile adaptation marker
        if profile and profile != 'default':
            parts.append('adapted')
        
        # Add language marker
        if language:
            parts.append(f'translated_{language}')
        
        # Add original base name
        parts.append(base_name)
        
        # Join parts
        if parts[0] != base_name:  # Has modifications
            filename = '_'.join(parts) + extension
        else:
            filename = base_name + extension
        
        return filename
    
    def _parse_filename(self, filename: str) -> Dict[str, Any]:
        """Parse metadata from filename"""
        metadata = {
            'is_adapted': False,
            'is_translated': False,
            'profile': None,
            'language': None
        }
        
        # Check for adaptations
        if 'adapted' in filename:
            metadata['is_adapted'] = True
            # Try to infer profile from filename patterns
            if 'dyslexia' in filename.lower():
                metadata['profile'] = 'dyslexia'
            elif 'adhd' in filename.lower():
                metadata['profile'] = 'adhd'
            elif 'esl' in filename.lower():
                metadata['profile'] = 'esl'
        
        # Check for translations
        if 'translated_' in filename:
            metadata['is_translated'] = True
            # Extract language
            import re
            match = re.search(r'translated_(\w+)', filename)
            if match:
                metadata['language'] = match.group(1)
        
        return metadata
    
    def get_download_page_info(self, file_id: str, filename: str, 
                              processing_tasks: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get all information needed for the download page
        
        Args:
            file_id: File identifier
            filename: Requested filename
            processing_tasks: Global processing tasks dict
            
        Returns:
            Dict with all download page information
        """
        # Get task info
        task_info = processing_tasks.get(file_id, {})
        profile = task_info.get('profile', "dyslexia")
        export_format = task_info.get('export_format', 'pdf')
        
        # Clean filename - remove double prefixes
        clean_filename = self._clean_filename(filename)
        
        # Determine file format from task info (more reliable than filename)
        task_file_type = task_info.get('file_type', '').lower()
        if task_file_type in ['.pdf', '.pptx']:
            original_format = 'pdf' if task_file_type == '.pdf' else 'pptx'
        else:
            # Fallback to filename extension
            original_ext = os.path.splitext(clean_filename)[1].lower()
            original_format = 'pdf' if original_ext == '.pdf' else 'pptx'
        
        # Build expected filenames
        base_name = os.path.splitext(clean_filename)[0]
        if not base_name.startswith('adapted_'):
            base_name = f"adapted_{base_name}"
        
        pdf_filename = f"{base_name}.pdf"
        pptx_filename = f"{base_name}.pptx"
        
        # Check file availability
        pdf_path = self.filestore.find_file(file_id, pdf_filename)
        pptx_path = self.filestore.find_file(file_id, pptx_filename)
        
        pdf_available = pdf_path is not None
        pptx_available = pptx_path is not None
        
        # Check for template
        template_available = ('template_path' in task_info and 
                            os.path.exists(task_info.get('template_path', '')))
        
        # Check for translations
        translation_info = self._check_translations(file_id, task_info)
        
        # Determine download filename
        if export_format == 'pdf' and pdf_available:
            download_filename = pdf_filename
        elif export_format == 'pptx' and pptx_available:
            download_filename = pptx_filename
        else:
            # Fallback
            download_filename = pdf_filename if pdf_available else pptx_filename
        
        # Get original filename from task info
        original_filename = task_info.get('filename', clean_filename)
        # Ensure original filename shows correct extension
        if not original_filename.endswith(f'.{original_format}'):
            base_orig = os.path.splitext(original_filename)[0]
            original_filename = f"{base_orig}.{original_format}"
        
        return {
            'file_id': file_id,
            'filename': download_filename,
            'original_filename': original_filename,
            'profile': profile,
            'original_format': original_format,
            'export_format': export_format,
            'pdf_available': pdf_available,
            'pptx_available': pptx_available,
            'pdf_filename': pdf_filename,
            'pptx_filename': pptx_filename,
            'template_available': template_available,
            **translation_info
        }
    
    def get_file_for_download(self, file_id: str, filename: str, 
                             processing_tasks: Dict[str, Any]) -> Optional[Tuple[str, str]]:
        """
        Get file path and clean filename for download
        
        Args:
            file_id: File identifier
            filename: Requested filename
            processing_tasks: Global processing tasks dict
            
        Returns:
            Tuple of (file_path, clean_filename) or None if not found
        """
        # Clean filename
        clean_filename = self._clean_filename(filename)
        
        # Try task info first (most reliable source)
        task_info = processing_tasks.get(file_id, {})
        
        # Check for output_path in task info (from the new service)
        output_path = task_info.get('output_path')
        if output_path and os.path.exists(output_path):
            download_name = os.path.basename(output_path)
            # Remove file_id prefix if present
            if download_name.startswith(f"{file_id}_"):
                download_name = download_name[len(f"{file_id}_"):]
            return output_path, download_name
        
        # Check for adapted_path (legacy)
        adapted_path = task_info.get('adapted_path')
        if adapted_path and os.path.exists(adapted_path):
            download_name = os.path.basename(adapted_path).replace(f"{file_id}_", "", 1)
            return adapted_path, download_name
        
        # Try to find file using filestore
        file_path = self.filestore.find_file(file_id, clean_filename)
        
        if file_path:
            # Extract clean filename
            download_name = os.path.basename(file_path)
            if download_name.startswith(f"{file_id}_"):
                download_name = download_name[len(f"{file_id}_"):]
            return file_path, download_name
        # Last resort: search for matching files
        return self._find_closest_match(file_id, filename)
    
    def _clean_filename(self, filename: str) -> str:
        """Clean filename by removing double prefixes"""
        if filename.startswith('adapted_adapted_'):
            return filename.replace('adapted_adapted_', 'adapted_', 1)
        return filename
    
    def _check_translations(self, file_id: str, task_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check for translation files and return translation info"""
        has_translation = task_info.get('has_translation', False)
        translated_filename = task_info.get('translated_filename', '')
        translated_language = task_info.get('translated_language', 'Translated')
        
        # If not in task info, check filesystem
        if not has_translation:
            translation_files = self.filestore.find_files_by_pattern(f"{file_id}_translated_*")
            if translation_files:
                has_translation = True
                first_file = translation_files[0]
                translated_filename = os.path.basename(first_file)[len(f"{file_id}_"):]
                
                # Extract language from filename
                parts = translated_filename.split('_')
                if len(parts) >= 2 and parts[0] == 'translated':
                    translated_language = parts[1].title()
        
        return {
            'has_translation': has_translation,
            'translated_filename': translated_filename,
            'translated_language': translated_language,
            'file_count': 1 + (1 if has_translation else 0)
        }
    
    def _find_closest_match(self, file_id: str, filename: str) -> Optional[Tuple[str, str]]:
        """Find closest matching file as last resort"""
        try:
            # Get all files that might match
            pattern_files = self.filestore.find_files_by_pattern(f"{file_id}_*")
            base_name = filename.replace('adapted_', '')
            
            for file_path in pattern_files:
                file_basename = os.path.basename(file_path)
                if file_id in file_basename or base_name in file_basename:
                    download_name = file_basename.replace(f"{file_id}_", "", 1)
                    return file_path, download_name
            
            return None
        except Exception:
            return None
    
    def create_batch_download(self, download_ids: List[str]) -> Dict[str, Any]:
        """
        Create a batch download (e.g., zip file) of multiple files
        
        Args:
            download_ids: List of download IDs to include
            
        Returns:
            Batch download information
        """
        import zipfile
        import tempfile
        
        # Create temporary zip file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_zip:
            zip_path = tmp_zip.name
        
        # Add files to zip
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for download_id in download_ids:
                download_info = self.get_download_by_id(download_id)
                if download_info and os.path.exists(download_info['path']):
                    zipf.write(download_info['path'], download_info['filename'])
        
        # Move to outputs
        batch_filename = f"batch_download_{len(download_ids)}_files.zip"
        final_path = self.filestore.save_output(zip_path, batch_filename)
        
        return {
            'filename': batch_filename,
            'path': final_path,
            'download_url': f"{self.download_base_url}/{batch_filename}",
            'file_count': len(download_ids),
            'size': os.path.getsize(final_path)
        }
    
    def cleanup_old_downloads(self, days: int = 7) -> int:
        """
        Clean up old download files
        
        Args:
            days: Files older than this many days will be deleted
            
        Returns:
            Number of files deleted
        """
        return self.filestore.cleanup_old_files('outputs', days)
    
    def get_download_statistics(self) -> Dict[str, Any]:
        """Get statistics about downloads"""
        output_files = self.filestore.list_outputs()
        
        stats = {
            'total_files': len(output_files),
            'total_size': sum(f['size'] for f in output_files),
            'by_type': {},
            'by_profile': {},
            'by_language': {},
            'adapted_count': 0,
            'translated_count': 0
        }
        
        for file_info in output_files:
            # Count by file type
            ext = Path(file_info['filename']).suffix.lower()
            stats['by_type'][ext] = stats['by_type'].get(ext, 0) + 1
            
            # Parse metadata
            metadata = self._parse_filename(file_info['filename'])
            
            if metadata['is_adapted']:
                stats['adapted_count'] += 1
                if metadata['profile']:
                    stats['by_profile'][metadata['profile']] = \
                        stats['by_profile'].get(metadata['profile'], 0) + 1
            
            if metadata['is_translated']:
                stats['translated_count'] += 1
                if metadata['language']:
                    stats['by_language'][metadata['language']] = \
                        stats['by_language'].get(metadata['language'], 0) + 1
        
        return stats