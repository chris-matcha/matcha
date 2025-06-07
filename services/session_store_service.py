"""
Session Store Service

Handles persistent storage of file processing metadata and session information
using Redis for Docker environments. This complements the FileStoreService
which handles actual file storage.
"""
import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from .base_service import BaseService

# Import redis conditionally
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None


class SessionStoreService(BaseService):
    """Service for managing persistent session and file metadata storage"""
    
    def _initialize(self):
        """Initialize Redis connection for session storage"""
        # Get Redis URL from config or environment
        redis_url = self.config.get('redis_url', os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
        self.ttl_hours = self.config.get('session_ttl_hours', 24)
        self.prefix = "matcha:sessions:"
        
        if not REDIS_AVAILABLE:
            self.logger.warning("Redis package not installed. Using in-memory fallback.")
            self.redis_available = False
            self.memory_store = {}
            return
            
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_available = True
            # Test connection
            self.redis_client.ping()
            self.logger.info(f"Successfully connected to Redis at {redis_url}")
        except Exception as e:
            self.logger.warning(f"Redis not available: {e}. Using in-memory fallback.")
            self.redis_available = False
            self.memory_store = {}
    
    def store_file_metadata(self, file_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Store file processing metadata
        
        Args:
            file_id: Unique file identifier
            metadata: Dictionary containing file metadata
            
        Returns:
            bool: Success status
        """
        try:
            # Add timestamp if not present
            if 'timestamp' not in metadata:
                metadata['timestamp'] = datetime.now().isoformat()
            
            if self.redis_available:
                key = f"{self.prefix}{file_id}"
                value = json.dumps(metadata)
                ttl = timedelta(hours=self.ttl_hours)
                self.redis_client.setex(key, ttl, value)
            else:
                # Fallback to in-memory storage
                self.memory_store[file_id] = metadata
            
            self.logger.info(f"Stored metadata for file {file_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing file metadata: {e}")
            return False
    
    def get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve file processing metadata
        
        Args:
            file_id: Unique file identifier
            
        Returns:
            Dictionary containing file metadata or None if not found
        """
        try:
            if self.redis_available:
                key = f"{self.prefix}{file_id}"
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                # Fallback to in-memory storage
                return self.memory_store.get(file_id)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error retrieving file metadata: {e}")
            return None
    
    def update_file_metadata(self, file_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update existing file metadata
        
        Args:
            file_id: Unique file identifier
            updates: Dictionary of fields to update
            
        Returns:
            bool: Success status
        """
        try:
            metadata = self.get_file_metadata(file_id)
            if metadata:
                metadata.update(updates)
                metadata['last_updated'] = datetime.now().isoformat()
                return self.store_file_metadata(file_id, metadata)
            
            self.logger.warning(f"No metadata found for file {file_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error updating file metadata: {e}")
            return False
    
    def file_exists(self, file_id: str) -> bool:
        """
        Check if file metadata exists
        
        Args:
            file_id: Unique file identifier
            
        Returns:
            bool: True if metadata exists
        """
        try:
            if self.redis_available:
                key = f"{self.prefix}{file_id}"
                return self.redis_client.exists(key) > 0
            else:
                return file_id in self.memory_store
                
        except Exception as e:
            self.logger.error(f"Error checking file existence: {e}")
            return False
    
    def delete_file_metadata(self, file_id: str) -> bool:
        """
        Remove file metadata
        
        Args:
            file_id: Unique file identifier
            
        Returns:
            bool: Success status
        """
        try:
            if self.redis_available:
                key = f"{self.prefix}{file_id}"
                result = self.redis_client.delete(key)
                return result > 0
            else:
                if file_id in self.memory_store:
                    del self.memory_store[file_id]
                    return True
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting file metadata: {e}")
            return False
    
    def list_all_files(self) -> List[str]:
        """
        Get all stored file IDs
        
        Returns:
            List of file IDs
        """
        try:
            if self.redis_available:
                pattern = f"{self.prefix}*"
                keys = self.redis_client.keys(pattern)
                # Extract file IDs from keys
                return [key.replace(self.prefix, '') for key in keys]
            else:
                return list(self.memory_store.keys())
                
        except Exception as e:
            self.logger.error(f"Error listing files: {e}")
            return []
    
    def get_files_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get all files with a specific status
        
        Args:
            status: Status to filter by
            
        Returns:
            List of file metadata dictionaries
        """
        files = []
        try:
            for file_id in self.list_all_files():
                metadata = self.get_file_metadata(file_id)
                if metadata and metadata.get('status') == status:
                    metadata['file_id'] = file_id
                    files.append(metadata)
                    
        except Exception as e:
            self.logger.error(f"Error getting files by status: {e}")
            
        return files
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired session data
        
        Returns:
            Number of items cleaned up
        """
        cleaned = 0
        try:
            if self.redis_available:
                # Redis handles expiration automatically
                self.logger.info("Redis handles expiration automatically")
            else:
                # Clean up in-memory store
                current_time = datetime.now()
                expired_keys = []
                
                for file_id, metadata in self.memory_store.items():
                    if 'timestamp' in metadata:
                        timestamp = datetime.fromisoformat(metadata['timestamp'])
                        if current_time - timestamp > timedelta(hours=self.ttl_hours):
                            expired_keys.append(file_id)
                
                for key in expired_keys:
                    del self.memory_store[key]
                    cleaned += 1
                    
                if cleaned > 0:
                    self.logger.info(f"Cleaned up {cleaned} expired sessions")
                    
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            
        return cleaned
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the session store
        
        Returns:
            Health status information
        """
        health = {
            'service': 'SessionStore',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            if self.redis_available:
                self.redis_client.ping()
                health['status'] = 'healthy'
                health['backend'] = 'redis'
                health['session_count'] = len(self.list_all_files())
            else:
                health['status'] = 'degraded'
                health['backend'] = 'memory'
                health['session_count'] = len(self.memory_store)
                health['warning'] = 'Using in-memory storage - data will be lost on restart'
                
        except Exception as e:
            health['status'] = 'unhealthy'
            health['error'] = str(e)
            
        return health