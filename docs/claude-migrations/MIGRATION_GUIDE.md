# PDF Functions Migration Guide

This guide shows how to migrate from the monolithic `app.py` PDF functions to the new service-oriented architecture.

## Migration Overview

The PDF text overlay functionality has been successfully migrated from `app.py` to dedicated services:

- **FormatsService**: Basic PDF/PowerPoint handling
- **PDFVisualHandler**: Advanced visual preservation methods
- **PDFMigrationHelper**: Bridge between old and new APIs

## Key Benefits After Migration

✅ **Isolated Testing**: Each PDF method can be tested independently  
✅ **Better Debugging**: Issues are contained within specific services  
✅ **Cleaner Code**: Single responsibility per service  
✅ **Fixed Text Rendering**: Proper `render_mode=0` implementation  
✅ **Improved Error Handling**: Better fallback chains  

## Migration Mapping

### Old Functions → New Services

| Old Function (app.py) | New Location | Notes |
|----------------------|--------------|-------|
| `process_with_pdf_template_system` | `PDFMigrationHelper.process_with_pdf_template_system` | Full pipeline |
| `create_visual_preserved_pdf` | `PDFVisualHandler.create_visual_preserved_pdf` | Core visual preservation |
| `create_visual_preserved_with_text_overlay` | `PDFVisualHandler.create_visual_preserved_with_overlay` | Image-based overlay |
| `create_visual_preserved_pdf_simple` | `PDFVisualHandler.create_simple_visual_preserved` | Simple tint overlay |
| `create_adapted_pdf` | `PDFHandler.create_file` | Non-visual PDF creation |

## Quick Migration Examples

### 1. Basic PDF Processing

**Old way:**
```python
# In app.py
result = process_with_pdf_template_system(
    pdf_path, 'dyslexia', direct_adapt=True
)
```

**New way:**
```python
from migrate_pdf_functions import PDFMigrationHelper

helper = PDFMigrationHelper({'output_folder': 'outputs'})
result = helper.process_with_pdf_template_system(
    pdf_path, 'dyslexia', direct_adapt=True
)
```

### 2. Direct Service Usage

**Old way:**
```python
# Complex function calls in app.py
success = create_visual_preserved_pdf(original_path, content, output_path, profile)
```

**New way:**
```python
from services import FormatsService

formats_service = FormatsService({})
success = formats_service.pdf_visual_handler.create_visual_preserved_pdf(
    original_path, content, output_path, profile
)
```

### 3. Visual Preservation with Fallbacks

**Old way:**
```python
# Manual fallback chain in app.py
try:
    success = create_visual_preserved_pdf(...)
    if not success:
        success = create_visual_preserved_with_text_overlay(...)
        if not success:
            success = create_visual_preserved_pdf_simple(...)
except:
    success = create_adapted_pdf(...)
```

**New way:**
```python
from services import FormatsService

formats_service = FormatsService({})
success = formats_service.create_file(
    content, output_path, 'pdf',
    profile='dyslexia',
    preserve_visuals=True,
    original_path=original_path
)
# Fallback chain is handled automatically!
```

## Step-by-Step Migration Process

### Phase 1: Test New Services (✅ Complete)
- [x] Migrate PDF functions to services
- [x] Create migration helper
- [x] Write tests for new functionality
- [x] Verify services load correctly

### Phase 2: Update Route Handlers (Next)
Replace PDF processing calls in Flask routes:

1. **Update `/adapt` route:**
```python
# Replace app.py function calls with:
from migrate_pdf_functions import PDFMigrationHelper

helper = PDFMigrationHelper(app.config)
result = helper.process_with_pdf_template_system(
    pdf_path, profile, direct_adapt=True, preserve_visuals=True
)
```

2. **Update download logic:**
```python
# Use new DownloadsService for file tracking
from services import DownloadsService

downloads_service = DownloadsService(app.config)
download_info = downloads_service.prepare_download(
    content, filename, 'pdf', profile
)
```

### Phase 3: Remove Old Functions
Once routes are updated and tested:
1. Comment out old functions in `app.py`
2. Test thoroughly
3. Remove commented functions
4. Update imports

## Testing the Migration

### Run Service Tests
```bash
# Test individual services
python tests/test_pdf_visual_handler.py
python tests/test_migration_helper.py

# Test formats service
python tests/test_formats_service.py
```

### Verify Functionality
```python
# Quick functionality test
from migrate_pdf_functions import PDFMigrationHelper

helper = PDFMigrationHelper({
    'output_folder': 'outputs',
    'anthropic_api_key': 'your-key'  # Optional
})

# This should work identically to the old app.py function
result = helper.process_with_pdf_template_system(
    'test.pdf', 'dyslexia', preserve_visuals=True
)
print(f"Success: {result['success']}")
```

## Key Improvements Made

### 1. Fixed Text Rendering Issue
- **Old**: `render_mode=3` (invisible text)
- **New**: `render_mode=0` (visible text)

### 2. Better Text Clearing
- **Old**: Basic text area clearing
- **New**: Aggressive clearing with expanded areas

### 3. Improved Fallback Chain
- **Old**: Manual try/catch in routes
- **New**: Automatic fallback in FormatsService

### 4. Profile-Specific Formatting
- **Old**: Basic color tints
- **New**: Comprehensive profile configurations with fonts, spacing, colors

## Configuration

Services accept configuration through constructors:

```python
config = {
    'anthropic_api_key': 'your-key',
    'output_folder': 'outputs',
    'upload_folder': 'uploads',
    'max_file_size': 10 * 1024 * 1024  # 10MB
}

helper = PDFMigrationHelper(config)
```

## Rollback Plan

If issues arise during migration:

1. **Keep old functions**: Don't delete until fully tested
2. **Use feature flags**: Toggle between old/new implementations
3. **Gradual rollout**: Migrate one route at a time
4. **Monitor**: Watch for errors and performance issues

## Next Steps

1. **Immediate**: Update Flask routes to use PDFMigrationHelper
2. **Short term**: Add comprehensive error logging
3. **Medium term**: Remove old app.py functions
4. **Long term**: Migrate other functionality (translations, assessments)

## Getting Help

- **Service documentation**: See `services/README.md`
- **Test examples**: Check `tests/` directory
- **Migration helper**: Use `PDFMigrationHelper` for gradual transition
- **Error debugging**: Each service has isolated logging

The PDF text overlay functionality is now properly separated, tested, and ready for production use!