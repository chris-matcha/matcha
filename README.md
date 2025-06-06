# Matcha - Adaptive Learning Platform 🍃

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Flask-2.2.2-green.svg" alt="Flask Version">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/AI-Claude_API-purple.svg" alt="AI Powered">
</div>

## Overview

Matcha is an AI-powered adaptive learning platform that transforms educational content to meet diverse learning needs. Using Claude AI, it automatically adapts PowerPoint presentations and PDF documents for learners with different requirements including dyslexia, ADHD, ESL learners, and visual or cognitive impairments.

### 🌟 Key Features

- **AI-Powered Adaptation**: Leverages Claude API to intelligently adapt content based on learning profiles
- **Multiple Learning Profiles**: Supports dyslexia, ADHD, ESL, visual, and cognitive adaptations
- **Document Processing**: Handles both PowerPoint (PPTX) and PDF files
- **Content Translation**: Translates educational materials into multiple languages
- **Learning Scaffolding Analysis**: Analyzes and enhances educational structure
- **Visual Preservation**: Maintains document formatting and visual elements during adaptation
- **Secure Authentication**: Built-in user management with secure authentication
- **Batch Processing**: Process multiple documents efficiently
- **Real-time Progress Tracking**: Monitor adaptation progress in real-time

### 🎯 Use Cases

- **Educational Institutions**: Adapt course materials for diverse student needs
- **Corporate Training**: Make training materials accessible to all employees
- **Content Creators**: Ensure educational content is inclusive and accessible
- **Special Education**: Create specialized materials for learners with specific needs

## System Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│                 │     │                  │     │                 │
│   Web Client    │────▶│   Flask Backend  │────▶│   Claude API    │
│                 │     │                  │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │                  │
                        │  SQLite Database │
                        │                  │
                        └──────────────────┘
```

### Components

- **Flask Backend**: RESTful API handling document processing, user authentication, and AI integration
- **SQLite Database**: Stores user data, processing history, and adaptation results
- **Claude AI Integration**: Provides intelligent content adaptation and translation
- **Document Processing Services**: Modular services for PDF and PowerPoint manipulation
- **Security Layer**: Authentication, rate limiting, and input validation

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git
- Anthropic API key (for Claude AI)
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/matcha.git
cd matcha
```

### 2. Set Up Python Virtual Environment

```bash
# Create virtual environment
python -m venv matcha_env

# Activate virtual environment
# On Windows:
matcha_env\Scripts\activate
# On macOS/Linux:
source matcha_env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

Required environment variables:
```env
# Security
SECRET_KEY=your-generated-secret-key-here
FLASK_ENV=development  # or 'production'

# API Keys
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Database
DATABASE_URL=sqlite:///matcha.db

# File Settings
MAX_UPLOAD_SIZE=52428800  # 50MB
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=outputs
```

### 5. Initialize the Database

```bash
# Create database and tables
python -c "from app import app; from auth import User; app.app_context().push(); User.init_db()"
```

### 6. Create Admin User (Optional)

```bash
python -c "
from app import app
from auth import User
app.app_context().push()
User.create_user('admin', 'admin@example.com', 'your-secure-password')
"
```

## Running the Application

### Development Mode

```bash
# Basic Flask development server
python app.py

# Or with Flask CLI
export FLASK_APP=app.py
flask run --debug
```

The application will be available at `http://localhost:5000`

### Production Mode

For production deployment, use Gunicorn:

```bash
gunicorn -c gunicorn_config.py app:app
```

Or use Docker:

```bash
docker-compose up -d
```

## Usage Guide

### 1. Access the Application

Navigate to `http://localhost:5000` in your web browser.

### 2. Upload a Document

1. Select a learning profile (Dyslexia, ADHD, ESL, etc.)
2. Choose action: "Assess" or "Adapt"
3. Optionally select a target language for translation
4. Upload your PowerPoint or PDF file
5. Click "Upload and Process"

### 3. Processing Options

- **Assessment**: Analyzes the document's educational structure and provides recommendations
- **Adaptation**: Transforms the content based on the selected learning profile
- **Translation**: Converts content to the selected language (maintains or replaces original)

### 4. Download Results

After processing, you can download:
- Adapted documents in original format
- Translated versions (if requested)
- Assessment reports

## Learning Profiles

### Dyslexia
- Increases font size and spacing
- Uses dyslexia-friendly fonts (OpenDyslexic)
- Simplifies complex sentences
- Adds visual breaks between paragraphs
- Uses high-contrast colors

### ADHD
- Breaks content into smaller chunks
- Adds bullet points and numbered lists
- Highlights key information
- Reduces text density
- Improves visual organization

### ESL (English as Second Language)
- Simplifies vocabulary
- Reduces sentence complexity
- Adds context for idioms
- Provides clearer explanations
- Maintains cultural sensitivity

### Visual Impairments
- Increases contrast ratios
- Enlarges text and UI elements
- Optimizes color combinations
- Ensures screen reader compatibility

### Cognitive Impairments
- Simplifies language structure
- Reduces cognitive load
- Adds visual aids and cues
- Breaks down complex concepts
- Provides clear navigation

## API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - User logout

### Document Processing
- `POST /upload` - Upload and process document
- `GET /status/<file_id>` - Check processing status
- `GET /download/<file_id>/<filename>` - Download processed file

### Analysis
- `GET /analyze/scaffolding/<file_id>` - Analyze learning scaffolding
- `GET /assess_content/<file_id>` - Assess content quality
- `POST /assess_readability` - Check text readability

### Health Check
- `GET /health` - Application health status
- `GET /api/status` - API connection status

## Configuration

### File Size Limits
Edit in `.env`:
```env
MAX_UPLOAD_SIZE=52428800  # 50MB default
```

### Supported File Types
- PowerPoint: `.pptx`, `.ppt`
- PDF: `.pdf`

### Rate Limiting
Configure in `security_config.py`:
- Default: 100 requests per hour
- Upload: 10 per minute
- Login: 5 per minute

## Development

### Project Structure
```
matcha/
├── app.py                 # Main Flask application
├── auth.py               # Authentication module
├── services/             # Core services
│   ├── pdf_service.py
│   ├── pptx_service.py
│   ├── adaptations_service.py
│   └── translations_service.py
├── templates/            # HTML templates
├── static/              # Static assets
├── uploads/             # Uploaded files
├── outputs/             # Processed files
└── instance/            # SQLite database
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_adaptations_service.py

# Run with coverage
pytest --cov=services tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions including:
- Docker deployment
- VPS setup
- Platform-as-a-Service options
- Security hardening
- SSL configuration

## Troubleshooting

### Common Issues

1. **"ANTHROPIC_API_KEY not found"**
   - Ensure `.env` file exists and contains your API key
   - Restart the application after setting environment variables

2. **"File upload failed"**
   - Check file size is under limit (50MB default)
   - Ensure uploads directory exists and is writable
   - Verify file type is supported

3. **"Database locked"**
   - Ensure only one instance is running
   - Check file permissions on SQLite database

4. **Processing takes too long**
   - Large files may take several minutes
   - Check API rate limits
   - Monitor server resources

### Debug Mode

Enable detailed logging:
```python
# In app.py
app.config['DEBUG'] = True
app.logger.setLevel(logging.DEBUG)
```

## Security Considerations

- Always use HTTPS in production
- Change default passwords immediately
- Keep API keys secure and rotate regularly
- Enable rate limiting to prevent abuse
- Regular security updates for dependencies
- Implement proper backup strategies

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- AI powered by [Claude (Anthropic)](https://www.anthropic.com/)
- PDF processing with [PyMuPDF](https://pymupdf.readthedocs.io/) and [ReportLab](https://www.reportlab.com/)
- PowerPoint handling via [python-pptx](https://python-pptx.readthedocs.io/)

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review closed issues for solutions

---

<div align="center">
Made with ❤️ for inclusive education
</div>