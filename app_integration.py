"""
Flask Application Integration Layer

This module provides the integration between the service-oriented architecture
and Flask routes, replacing the monolithic app.py functionality.
"""
import os
from flask import Flask, request, jsonify, send_file, render_template_string
from werkzeug.utils import secure_filename
from typing import Dict, Any, Optional

# Import all services
from services import (
    UploadService,
    FormatsService,
    AdaptationsService,
    TranslationsService,
    LearningProfilesService,
    AssessmentsService,
    FileStoreService,
    DownloadsService
)


class MatchaApp:
    """Main application class integrating all services"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the application with configuration"""
        self.config = config
        self.app = Flask(__name__)
        
        # Initialize services
        self.upload_service = UploadService(config)
        self.formats_service = FormatsService(config)
        self.adaptations_service = AdaptationsService(config)
        self.translations_service = TranslationsService(config)
        self.profiles_service = LearningProfilesService(config)
        self.assessments_service = AssessmentsService(config)
        self.filestore_service = FileStoreService(config)
        self.downloads_service = DownloadsService(config)
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup all Flask routes"""
        
        @self.app.route('/')
        def index():
            """Home page"""
            profiles = self.profiles_service.list_profiles()
            languages = self.translations_service.get_supported_languages()
            
            return render_template_string(
                self._get_index_template(),
                profiles=profiles,
                languages=languages
            )
        
        @self.app.route('/upload', methods=['POST'])
        def upload_file():
            """Handle file upload"""
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            try:
                # Save uploaded file
                file_info = self.upload_service.save_upload(file)
                
                # Extract content
                file_type = 'pdf' if file_info['filename'].endswith('.pdf') else 'pptx'
                content = self.formats_service.extract_content(file_info['path'], file_type)
                
                # Store in session (in production, use proper session management)
                session_data = {
                    'file_info': file_info,
                    'content': content,
                    'file_type': file_type
                }
                
                return jsonify({
                    'success': True,
                    'file_id': file_info['file_id'],
                    'filename': file_info['filename'],
                    'file_type': file_type
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/assess/<file_id>', methods=['POST'])
        def assess_content(file_id):
            """Assess content readability"""
            try:
                # Get content from session/storage
                content = self._get_content_by_file_id(file_id)
                if not content:
                    return jsonify({'error': 'File not found'}), 404
                
                # Perform assessment
                profile_id = request.json.get('profile_id')
                assessment = self.assessments_service.assess_content(content, profile_id)
                
                return jsonify(assessment)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/adapt/<file_id>', methods=['POST'])
        def adapt_content(file_id):
            """Adapt content for learning profile"""
            try:
                # Get parameters
                profile_id = request.json.get('profile_id')
                translate = request.json.get('translate', False)
                target_language = request.json.get('language')
                
                if not profile_id:
                    return jsonify({'error': 'Profile ID required'}), 400
                
                # Get content
                content = self._get_content_by_file_id(file_id)
                if not content:
                    return jsonify({'error': 'File not found'}), 404
                
                # Adapt content
                adapted_content = self.adaptations_service.adapt_content(
                    content, profile_id, force_adaptation=True
                )
                
                # Translate if requested
                if translate and target_language:
                    adapted_content = self.translations_service.translate_content(
                        adapted_content, target_language
                    )
                
                # Create output file
                file_info = self._get_file_info_by_id(file_id)
                file_type = 'pdf' if file_info['filename'].endswith('.pdf') else 'pptx'
                
                download_info = self.downloads_service.prepare_download(
                    adapted_content,
                    file_info['filename'],
                    file_type,
                    profile_id,
                    target_language if translate else None
                )
                
                return jsonify({
                    'success': True,
                    'download': download_info
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/download/<filename>')
        def download_file(filename):
            """Download a file"""
            try:
                # Get file path
                file_path = self.filestore_service.get_output_path(filename)
                if not os.path.exists(file_path):
                    # Check for translations
                    downloads = self.downloads_service.list_available_downloads()
                    for download in downloads:
                        if filename in download['filename']:
                            file_path = download['path']
                            break
                
                if os.path.exists(file_path):
                    return send_file(file_path, as_attachment=True)
                else:
                    return "File not found", 404
                    
            except Exception as e:
                return str(e), 500
        
        @self.app.route('/downloads')
        def list_downloads():
            """List all available downloads"""
            try:
                downloads = self.downloads_service.list_available_downloads()
                return jsonify(downloads)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/profiles')
        def list_profiles():
            """List learning profiles"""
            profiles = self.profiles_service.list_profiles()
            return jsonify(profiles)
        
        @self.app.route('/languages')
        def list_languages():
            """List supported languages"""
            languages = self.translations_service.get_supported_languages()
            return jsonify(languages)
    
    def _get_content_by_file_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get content by file ID (implement proper storage in production)"""
        # This is a placeholder - in production, implement proper session/storage
        # For now, re-extract from uploaded file
        uploads = self.filestore_service.list_uploads()
        for upload in uploads:
            if file_id in upload['filename']:
                file_type = 'pdf' if upload['filename'].endswith('.pdf') else 'pptx'
                return self.formats_service.extract_content(upload['path'], file_type)
        return None
    
    def _get_file_info_by_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file info by ID"""
        uploads = self.filestore_service.list_uploads()
        for upload in uploads:
            if file_id in upload['filename']:
                return upload
        return None
    
    def _get_index_template(self) -> str:
        """Get the index page HTML template"""
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Matcha - Adaptive Learning System</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .upload-area { 
                    border: 2px dashed #ccc; 
                    padding: 20px; 
                    text-align: center;
                    margin: 20px 0;
                }
                .profile-cards { 
                    display: flex; 
                    gap: 20px; 
                    margin: 20px 0;
                }
                .profile-card {
                    border: 1px solid #ddd;
                    padding: 15px;
                    flex: 1;
                    border-radius: 5px;
                }
                .btn {
                    background: #4CAF50;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }
                .btn:hover { background: #45a049; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Matcha - Adaptive Learning System</h1>
                
                <div class="upload-area">
                    <h2>Upload Document</h2>
                    <form id="uploadForm" enctype="multipart/form-data">
                        <input type="file" id="fileInput" accept=".pdf,.pptx" required>
                        <button type="submit" class="btn">Upload</button>
                    </form>
                </div>
                
                <h2>Learning Profiles</h2>
                <div class="profile-cards">
                    {% for profile in profiles %}
                    <div class="profile-card">
                        <h3>{{ profile.name }}</h3>
                        <p>{{ profile.description }}</p>
                    </div>
                    {% endfor %}
                </div>
                
                <div id="results"></div>
            </div>
            
            <script>
                document.getElementById('uploadForm').onsubmit = async (e) => {
                    e.preventDefault();
                    const formData = new FormData();
                    formData.append('file', document.getElementById('fileInput').files[0]);
                    
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        document.getElementById('results').innerHTML = 
                            `<h3>File uploaded successfully!</h3>
                             <p>File ID: ${result.file_id}</p>
                             <p>You can now adapt this file for different learning profiles.</p>`;
                    }
                };
            </script>
        </body>
        </html>
        '''
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Flask application"""
        self.app.run(host=host, port=port, debug=debug)


def create_app(config: Optional[Dict[str, Any]] = None) -> MatchaApp:
    """Factory function to create the application"""
    if config is None:
        config = {
            'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY'),
            'upload_folder': 'uploads',
            'output_folder': 'outputs',
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'allowed_extensions': ['.pdf', '.pptx']
        }
    
    return MatchaApp(config)


if __name__ == '__main__':
    # Example usage
    app = create_app()
    app.run(debug=True)