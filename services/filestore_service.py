"""
File Store Service

Handles all file storage operations including uploads, outputs, and temporary files.
"""
import os
import shutil
import uuid
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime, timedelta
from .base_service import BaseService


class FileStoreService(BaseService):
    """Service for managing file storage"""
    
    def _initialize(self):
        """Initialize file storage directories"""
        self.upload_dir = Path(self.config.get('upload_dir', 'uploads'))
        self.output_dir = Path(self.config.get('output_dir', 'outputs'))
        self.temp_dir = Path(self.config.get('temp_dir', 'temp'))
        
        # Create directories if they don't exist
        for directory in [self.upload_dir, self.output_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def generate_file_id(self) -> str:
        """Generate a unique file ID"""
        return str(uuid.uuid4())
    
    def save_upload(self, file_content: bytes, filename: str, file_id: Optional[str] = None) -> Tuple[str, str]:
        """
        Save an uploaded file
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            file_id: Optional file ID (generated if not provided)
            
        Returns:
            Tuple of (file_id, file_path)
        """
        if not file_id:
            file_id = self.generate_file_id()
        
        # Create safe filename
        safe_filename = f"{file_id}_{filename}"
        file_path = self.upload_dir / safe_filename
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        self.logger.info(f"Saved upload: {file_path}")
        return file_id, str(file_path)
    
    def save_output(self, file_content: bytes, filename: str, file_id: str) -> str:
        """
        Save an output file
        
        Args:
            file_content: File content as bytes
            filename: Output filename
            file_id: File ID for tracking
            
        Returns:
            str: Path to saved file
        """
        output_filename = f"{file_id}_{filename}"
        output_path = self.output_dir / output_filename
        
        with open(output_path, 'wb') as f:
            f.write(file_content)
        
        self.logger.info(f"Saved output: {output_path}")
        return str(output_path)
    
    def get_file_path(self, file_id: str, filename: str, file_type: str = 'upload') -> Optional[str]:
        """
        Get the full path for a file
        
        Args:
            file_id: File ID
            filename: Filename
            file_type: Type of file ('upload', 'output', 'temp')
            
        Returns:
            str: Full file path if exists, None otherwise
        """
        if file_type == 'upload':
            base_dir = self.upload_dir
        elif file_type == 'output':
            base_dir = self.output_dir
        else:
            base_dir = self.temp_dir
        
        file_path = base_dir / f"{file_id}_{filename}"
        
        if file_path.exists():
            return str(file_path)
        
        # Try without file_id prefix
        file_path = base_dir / filename
        if file_path.exists():
            return str(file_path)
        
        return None
    
    def list_files(self, file_id: str, file_type: str = 'output') -> List[str]:
        """
        List all files for a given file_id
        
        Args:
            file_id: File ID to search for
            file_type: Type of files to list
            
        Returns:
            List of filenames
        """
        if file_type == 'upload':
            base_dir = self.upload_dir
        elif file_type == 'output':
            base_dir = self.output_dir
        else:
            base_dir = self.temp_dir
        
        files = []
        for file_path in base_dir.glob(f"{file_id}_*"):
            if file_path.is_file():
                # Remove file_id prefix from filename
                filename = file_path.name[len(file_id)+1:]
                files.append(filename)
        
        return files
    
    def delete_file(self, file_id: str, filename: str, file_type: str = 'upload') -> bool:
        """
        Delete a file
        
        Args:
            file_id: File ID
            filename: Filename
            file_type: Type of file
            
        Returns:
            bool: True if deleted successfully
        """
        file_path = self.get_file_path(file_id, filename, file_type)
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            self.logger.info(f"Deleted file: {file_path}")
            return True
        return False
    
    def cleanup_old_files(self, days: int = 7):
        """
        Clean up files older than specified days
        
        Args:
            days: Number of days to keep files
        """
        cutoff_time = datetime.now() - timedelta(days=days)
        
        for directory in [self.upload_dir, self.output_dir, self.temp_dir]:
            for file_path in directory.iterdir():
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_time:
                        file_path.unlink()
                        self.logger.info(f"Cleaned up old file: {file_path}")
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get information about a file"""
        path = Path(file_path)
        if not path.exists():
            return {}
        
        stat = path.stat()
        return {
            'filename': path.name,
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'extension': path.suffix
        }
    
    def find_file(self, file_id: str, filename: str) -> Optional[str]:
        """
        Find a file by file_id and filename
        
        Args:
            file_id: File identifier
            filename: Filename to search for
            
        Returns:
            Full path to file if found, None otherwise
        """
        # Try with file_id prefix
        prefixed_filename = f"{file_id}_{filename}"
        
        # Search in output directory first
        output_path = self.output_dir / prefixed_filename
        if output_path.exists():
            return str(output_path)
        
        # Search in upload directory
        upload_path = self.upload_dir / prefixed_filename
        if upload_path.exists():
            return str(upload_path)
        
        # Search without prefix
        output_path_no_prefix = self.output_dir / filename
        if output_path_no_prefix.exists():
            return str(output_path_no_prefix)
        
        return None
    
    def find_files_by_pattern(self, pattern: str) -> List[str]:
        """
        Find files matching a pattern
        
        Args:
            pattern: File pattern to match (supports * wildcards)
            
        Returns:
            List of matching file paths
        """
        import glob
        
        matching_files = []
        
        # Search in output directory
        output_pattern = str(self.output_dir / pattern)
        matching_files.extend(glob.glob(output_pattern))
        
        # Search in upload directory
        upload_pattern = str(self.upload_dir / pattern)
        matching_files.extend(glob.glob(upload_pattern))
        
        return matching_files
    
    def list_outputs(self) -> List[Dict[str, Any]]:
        """
        List all output files with metadata
        
        Returns:
            List of file information dictionaries
        """
        files = []
        
        try:
            for file_path in self.output_dir.iterdir():
                if file_path.is_file():
                    file_info = self.get_file_info(str(file_path))
                    file_info['path'] = str(file_path)
                    files.append(file_info)
        except Exception as e:
            self.logger.error(f"Error listing output files: {e}")
        
        return files