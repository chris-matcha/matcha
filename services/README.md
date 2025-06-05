# Matcha Services Architecture

This directory contains the modular services that make up the Matcha adaptive learning system. Each service is designed to handle a specific domain and can be used and tested independently.

## Services Overview

### 1. **FileStoreService** (`filestore_service.py`)
- Manages all file storage operations
- Handles uploads, outputs, and temporary files
- Provides file cleanup and organization

### 2. **UploadService** (`upload_service.py`)
- Handles file upload validation and processing
- Checks file types and sizes
- Integrates with FileStoreService for storage

### 3. **LearningProfilesService** (`profiles_service.py`)
- Manages learning profiles (Dyslexia, ADHD, ESL)
- Stores configuration for each profile
- Provides thresholds, formatting preferences, and adaptation settings

### 4. **FormatsService** (`formats_service.py`)
- Handles different file formats (PDF, PowerPoint)
- Extracts content from files
- Creates new files with adapted content

### 5. **AdaptationsService** (`adaptations_service.py`)
- Core service for content adaptation
- Uses AI (Anthropic Claude) or rule-based methods
- Calculates readability metrics
- Adapts text based on learning profiles

### 6. **TranslationsService** (`translations_service.py`)
- Handles content translation
- Supports 13 languages
- Uses AI for high-quality translations

### 7. **AssessmentsService** (`assessments_service.py`)
- Analyzes content readability
- Provides recommendations
- Assesses suitability for each learning profile

### 8. **DownloadsService** (`downloads_service.py`)
- Manages download operations
- Creates download links
- Tracks adapted and translated versions

## Benefits of Service Architecture

1. **Isolation**: Each service can be developed, tested, and debugged independently
2. **Reusability**: Services can be used in different contexts (web app, CLI, API)
3. **Testability**: Easy to write unit tests for each service
4. **Maintainability**: Changes to one service don't affect others
5. **Scalability**: Services can be deployed separately if needed

## Usage Example

```python
from services import (
    LearningProfilesService,
    AdaptationsService,
    FormatsService
)

# Initialize services
profiles_service = LearningProfilesService({})
adaptations_service = AdaptationsService({'anthropic_api_key': 'your-key'})
formats_service = FormatsService({})

# Extract content from a PDF
content = formats_service.extract_content('document.pdf', 'pdf')

# Adapt content for dyslexia
adapted_content = adaptations_service.adapt_content(content, 'dyslexia')

# Create adapted PDF
formats_service.create_file(adapted_content, 'adapted_document.pdf', 'pdf', 'dyslexia')
```

## Testing

Each service can be tested independently:

```bash
# Run tests for a specific service
python tests/test_profiles_service.py
python tests/test_adaptations_service.py
```

## Configuration

Services accept configuration through their constructors:

```python
config = {
    'anthropic_api_key': 'your-api-key',
    'upload_folder': 'uploads',
    'output_folder': 'outputs',
    'max_file_size': 10 * 1024 * 1024  # 10MB
}

service = AdaptationsService(config)
```

## Integration with Flask

The `app_integration.py` file shows how to integrate all services with Flask routes:

```python
from app_integration import create_app

app = create_app()
app.run(debug=True)
```

## Next Steps

1. **Testing**: Write comprehensive tests for each service
2. **Documentation**: Add detailed API documentation for each service
3. **Error Handling**: Implement robust error handling and logging
4. **Caching**: Add caching layer for expensive operations
5. **Async Support**: Consider adding async versions of services
6. **API Layer**: Create RESTful API endpoints for each service