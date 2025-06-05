# App.py Cleanup Summary

## Functions to Remove (Now in Services)

### PDF Service Functions
1. **extract_content_from_pdf** (lines 444-611) → Use `pdf_service.extract_content_from_pdf()`
2. **create_adapted_pdf** (lines 613-900) → Use `pdf_service.create_adapted_pdf()`
3. **cleanup_temp_images** (lines 920-931) → Use `pdf_service.cleanup_temp_images()`
4. **diagnose_pdf_content** (lines 932-1009) → Use `pdf_service.diagnose_pdf_content()`
5. **create_visual_preserved_pdf** (lines 1010-1246) → Use `pdf_service.create_visual_preserved_pdf()`
6. **create_visual_preserved_pdf_simple** (lines 1247-1306) → Use `pdf_service.create_visual_preserved_pdf()`
7. **adapt_pdf_content** (lines 1897-2026) → Use `pdf_service.adapt_pdf_content()`

### PowerPoint Service Functions
1. **extract_content_from_pptx** (lines 2742-2841) → Use `pptx_service.extract_content_from_pptx()`
2. **analyze_pptx** (lines 3612-3659) → Use `pptx_service.analyze_pptx()`
3. **apply_dyslexia_formatting** (lines 3415-3452) → Use `pptx_service.apply_dyslexia_formatting()`

### Conversion Service Functions
1. **convert_pptx_to_pdf_template** (lines 1805-1895) → Use `conversion_service.convert_pptx_to_pdf()`
2. **convert_pptx_to_pdf_windows** (lines 4562-4591) → Use `conversion_service.convert_pptx_to_pdf()`
3. **convert_pptx_to_pdf_libreoffice** (lines 4593-4649) → Use `conversion_service.convert_pptx_to_pdf()`
4. **convert_pptx_to_pdf_fallback** (lines 4651-4732) → Use `conversion_service.convert_pptx_to_pdf()`
5. **convert_pptx_to_pdf** (lines 4734-4784) → Use `conversion_service.convert_pptx_to_pdf()`

### Educational Content Service Functions
1. **generate_lesson_plan** (lines 3728-3832) → Use `educational_service.generate_lesson_plan()`
2. **generate_enriched_lesson_plan** (lines 3833-3965) → Use `educational_service.generate_lesson_plan()`

## Unused Variables and Imports to Remove
- `pdfplumber` import (not used)
- `PyPDF2` import (not used)
- `fitz` import (not used anymore)
- `convert_from_path` import (not used)

## Functions to Keep
- Route handlers (@app.route)
- Helper functions specific to Flask app
- UI template functions
- Processing thread functions