"""
Matcha Services Package

This package contains all the modular services for the Matcha application.
Each service is responsible for a specific domain and can be tested in isolation.
"""

from .upload_service import UploadService
from .formats_service import FormatsService
from .adaptations_service import AdaptationsService
from .translations_service import TranslationsService
from .profiles_service import LearningProfilesService
from .assessments_service import AssessmentsService
from .filestore_service import FileStoreService
from .downloads_service import DownloadsService
from .pdf_visual_handler import PDFVisualHandler
from .pdf_visual_handler_enhanced import PDFVisualHandlerEnhanced
from .pdf_service import PDFService
from .pptx_service import PowerPointService
from .conversion_service import ConversionService
from .educational_content_service import EducationalContentService
from .session_store_service import SessionStoreService
from .processing_task_service import ProcessingTaskService

__all__ = [
    'UploadService',
    'FormatsService',
    'AdaptationsService',
    'TranslationsService',
    'LearningProfilesService',
    'AssessmentsService',
    'FileStoreService',
    'DownloadsService',
    'PDFVisualHandler',
    'PDFVisualHandlerEnhanced',
    'PDFService',
    'PowerPointService',
    'ConversionService',
    'EducationalContentService',
    'SessionStoreService',
    'ProcessingTaskService'
]