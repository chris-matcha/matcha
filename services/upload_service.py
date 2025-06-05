"""
Upload Service

Handles file uploads, validation, and initial processing.
"""
import os
from typing import Dict, Any, Tuple, Optional
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from .base_service import BaseService
from .filestore_service import FileStoreService


class UploadService(BaseService):
    """Service for handling file uploads"""
    
    ALLOWED_EXTENSIONS = {'.pdf', '.pptx'}
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    
    def _initialize(self):
        """Initialize upload service"""
        self.filestore = FileStoreService(self.config)
        self.allowed_extensions = self.config.get('allowed_extensions', self.ALLOWED_EXTENSIONS)
        self.max_file_size = self.config.get('max_file_size', self.MAX_FILE_SIZE)
    
    def validate_file(self, file: FileStorage) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file
        
        Args:
            file: Werkzeug FileStorage object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if file exists
        if not file or not file.filename:
            return False, "No file provided"
        
        # Check file extension
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in self.allowed_extensions:
            return False, f"Invalid file type '{file_ext}'. Allowed types: {', '.join(self.allowed_extensions)}"
        
        # Check file size (read first few bytes to check)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > self.max_file_size:
            return False, f"File too large. Maximum size: {self.max_file_size / 1024 / 1024:.0f}MB"
        
        return True, None
    
    def process_upload(self, file: FileStorage, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process file upload
        
        Args:
            file: Werkzeug FileStorage object
            metadata: Additional metadata (profile, action, etc.)
            
        Returns:
            Dict containing upload results
        """
        # Validate file
        is_valid, error_message = self.validate_file(file)
        if not is_valid:
            return {
                'success': False,
                'error': error_message
            }
        
        # Secure filename
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        
        # Read file content
        file_content = file.read()
        
        # Generate file ID and save
        file_id = self.filestore.generate_file_id()
        _, file_path = self.filestore.save_upload(file_content, filename, file_id)
        
        # Prepare result
        result = {
            'success': True,
            'file_id': file_id,
            'filename': filename,
            'file_path': file_path,
            'file_type': file_ext[1:],  # Remove dot
            'file_size': len(file_content),
            'metadata': metadata
        }
        
        self.logger.info(f"Upload processed: {file_id} - {filename}")
        return result
    
    def get_upload_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about an uploaded file
        
        Args:
            file_id: File ID
            
        Returns:
            Dict with file information or None if not found
        """
        # List all files with this ID
        files = self.filestore.list_files(file_id, 'upload')
        
        if not files:
            return None
        
        # Get the first file (should only be one upload per ID)
        filename = files[0]
        file_path = self.filestore.get_file_path(file_id, filename, 'upload')
        
        if not file_path:
            return None
        
        file_info = self.filestore.get_file_info(file_path)
        file_info['file_id'] = file_id
        
        return file_info
    
    def delete_upload(self, file_id: str) -> bool:
        """
        Delete an uploaded file and all associated outputs
        
        Args:
            file_id: File ID
            
        Returns:
            bool: True if deleted successfully
        """
        success = True
        
        # Delete upload files
        for filename in self.filestore.list_files(file_id, 'upload'):
            if not self.filestore.delete_file(file_id, filename, 'upload'):
                success = False
        
        # Delete output files
        for filename in self.filestore.list_files(file_id, 'output'):
            if not self.filestore.delete_file(file_id, filename, 'output'):
                success = False
        
        return success