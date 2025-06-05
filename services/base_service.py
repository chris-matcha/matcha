"""
Base Service Class

Provides common functionality for all services.
"""
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class BaseService(ABC):
    """Base class for all services"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the service with optional configuration
        
        Args:
            config: Service-specific configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialize()
    
    @abstractmethod
    def _initialize(self):
        """Initialize service-specific resources"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the service"""
        return {
            'service': self.__class__.__name__,
            'status': 'operational',
            'config': self.config
        }
    
    def validate_input(self, data: Dict[str, Any], required_fields: list) -> bool:
        """
        Validate that required fields are present in input data
        
        Args:
            data: Input data dictionary
            required_fields: List of required field names
            
        Returns:
            bool: True if all required fields are present
        """
        for field in required_fields:
            if field not in data or data[field] is None:
                self.logger.error(f"Missing required field: {field}")
                return False
        return True