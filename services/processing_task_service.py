"""
Processing Task Service

Manages processing task state and metadata with Redis persistence.
This service handles the lifecycle of file processing tasks across
different operations (upload, assessment, adaptation, etc.)
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from .base_service import BaseService
from .session_store_service import SessionStoreService


class ProcessingTaskService(BaseService):
    """Service for managing processing task state and metadata"""
    
    def _initialize(self):
        """Initialize processing task service with session store"""
        # Initialize session store for persistence
        session_config = {
            'redis_url': self.config.get('redis_url', 'redis://redis:6379/0'),
            'session_ttl_hours': self.config.get('task_ttl_hours', 24)
        }
        self.session_store = SessionStoreService(session_config)
        
        # In-memory cache for performance
        self.task_cache = {}
    
    def create_task(self, file_id: str, task_data: Dict[str, Any]) -> bool:
        """
        Create a new processing task
        
        Args:
            file_id: Unique file identifier
            task_data: Initial task data
            
        Returns:
            bool: Success status
        """
        # Add timestamp
        task_data['created_at'] = datetime.now().isoformat()
        task_data['file_id'] = file_id
        
        # Store in both cache and persistent storage
        self.task_cache[file_id] = task_data
        success = self.session_store.store_file_metadata(file_id, task_data)
        
        if success:
            self.logger.info(f"Created processing task for {file_id}")
        else:
            self.logger.error(f"Failed to create processing task for {file_id}")
            
        return success
    
    def get_task(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Get processing task data
        
        Args:
            file_id: Unique file identifier
            
        Returns:
            Task data or None if not found
        """
        # Check cache first
        if file_id in self.task_cache:
            return self.task_cache[file_id]
        
        # Try persistent storage
        task_data = self.session_store.get_file_metadata(file_id)
        if task_data:
            # Update cache
            self.task_cache[file_id] = task_data
            return task_data
        
        return None
    
    def update_task(self, file_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update processing task data
        
        Args:
            file_id: Unique file identifier
            updates: Fields to update
            
        Returns:
            bool: Success status
        """
        # Get existing task
        task_data = self.get_task(file_id)
        if not task_data:
            self.logger.warning(f"Task {file_id} not found for update")
            return False
        
        # Update timestamp
        updates['updated_at'] = datetime.now().isoformat()
        
        # Update cache
        if file_id in self.task_cache:
            self.task_cache[file_id].update(updates)
        
        # Update persistent storage
        success = self.session_store.update_file_metadata(file_id, updates)
        
        if success:
            self.logger.info(f"Updated task {file_id}: {list(updates.keys())}")
        
        return success
    
    def task_exists(self, file_id: str) -> bool:
        """
        Check if a processing task exists
        
        Args:
            file_id: Unique file identifier
            
        Returns:
            bool: True if task exists
        """
        return file_id in self.task_cache or self.session_store.file_exists(file_id)
    
    def delete_task(self, file_id: str) -> bool:
        """
        Delete a processing task
        
        Args:
            file_id: Unique file identifier
            
        Returns:
            bool: Success status
        """
        # Remove from cache
        if file_id in self.task_cache:
            del self.task_cache[file_id]
        
        # Remove from persistent storage
        return self.session_store.delete_file_metadata(file_id)
    
    def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get all tasks with a specific status
        
        Args:
            status: Status to filter by
            
        Returns:
            List of task data dictionaries
        """
        return self.session_store.get_files_by_status(status)
    
    def update_progress(self, file_id: str, processed: int, total: int, message: Optional[str] = None) -> bool:
        """
        Update task progress
        
        Args:
            file_id: Unique file identifier
            processed: Number of items processed
            total: Total number of items
            message: Optional progress message
            
        Returns:
            bool: Success status
        """
        updates = {
            'progress': {
                'processed': processed,
                'total': total,
                'percentage': int((processed / total * 100) if total > 0 else 0)
            }
        }
        
        if message:
            updates['message'] = message
        
        return self.update_task(file_id, updates)
    
    def set_status(self, file_id: str, status: str, message: Optional[str] = None) -> bool:
        """
        Set task status
        
        Args:
            file_id: Unique file identifier
            status: New status
            message: Optional status message
            
        Returns:
            bool: Success status
        """
        updates = {'status': status}
        if message:
            updates['message'] = message
        
        return self.update_task(file_id, updates)
    
    def set_result(self, file_id: str, result_key: str, result_data: Any) -> bool:
        """
        Store a result for a task
        
        Args:
            file_id: Unique file identifier
            result_key: Key for the result (e.g., 'assessment', 'scaffolding')
            result_data: Result data to store
            
        Returns:
            bool: Success status
        """
        return self.update_task(file_id, {result_key: result_data})
    
    def get_result(self, file_id: str, result_key: str) -> Optional[Any]:
        """
        Get a specific result from a task
        
        Args:
            file_id: Unique file identifier
            result_key: Key for the result
            
        Returns:
            Result data or None if not found
        """
        task_data = self.get_task(file_id)
        if task_data:
            return task_data.get(result_key)
        return None
    
    def cleanup_completed_tasks(self, hours_old: int = 24) -> int:
        """
        Clean up old completed tasks
        
        Args:
            hours_old: Age threshold in hours
            
        Returns:
            Number of tasks cleaned up
        """
        # This is handled by Redis TTL, but we can clean the cache
        cleaned = 0
        current_time = datetime.now()
        
        for file_id in list(self.task_cache.keys()):
            task_data = self.task_cache[file_id]
            if task_data.get('status') == 'completed':
                created_at = task_data.get('created_at', '')
                if created_at:
                    try:
                        task_time = datetime.fromisoformat(created_at)
                        if (current_time - task_time).total_seconds() > hours_old * 3600:
                            del self.task_cache[file_id]
                            cleaned += 1
                    except:
                        pass
        
        if cleaned > 0:
            self.logger.info(f"Cleaned {cleaned} old tasks from cache")
        
        return cleaned