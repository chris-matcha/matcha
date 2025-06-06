

# html_templates.py

"""
Contains all HTML templates used in the Flask application.
This helps separate presentation from business logic.
"""

# Main page template with PPTX upload only
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Matcha PowerPoint Adaptor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        form { margin: 20px 0; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        select, input[type="file"] { width: 100%; padding: 8px; }
        button { background: #4CAF50; color: white; border: none; padding: 10px 15px; cursor: pointer; margin-right: 10px; }
        .secondary-btn { background: #3498db; }
        .color-samples { margin-top: 20px; }
        .color-sample { display: inline-block; width: 20px; height: 20px; margin-right: 5px; border: 1px solid #ccc; }
        .dyslexia-color { background-color: #0066cc; }
        .adhd-color { background-color: #2e8b57; }
        .esl-color { background-color: #9400d3; }
        .profile-info { margin-top: 20px; padding: 15px; background-color: #f5f5f5; border-radius: 5px; }
        .profile-info h3 { margin-top: 0; }
        .toggle-section { cursor: pointer; color: #2c3e50; }
        .toggle-section:hover { text-decoration: underline; }
        .hidden { display: none; }
        .logo { font-size: 28px; color: #4CAF50; margin-bottom: 10px; font-weight: bold; }
        .info-box { background-color: #e8f4f8; padding: 15px; border-left: 5px solid #4CAF50; margin: 20px 0; }
        .buttons { display: flex; margin-top: 20px; }
        #export-options { margin-top: 15px; padding: 10px; background-color: #f9f9f9; border-radius: 5px; }
        .form-group.translation-highlight { 
            background-color: #f0f8ff !important; 
            border: 2px solid #4CAF50 !important; 
            padding: 10px !important; 
            border-radius: 5px !important; 
            margin: 10px 0 !important;
            box-shadow: 0 2px 4px rgba(76, 175, 80, 0.3) !important;
        }
        .form-group.translation-highlight label { 
            font-weight: bold !important; 
            color: #2c3e50 !important; 
        }
        .form-group.translation-highlight select {
            border: 1px solid #4CAF50 !important;
            background-color: #ffffff !important;
        }
        
        /* Translation mode styling consistent with app theme */
        #translation_mode_div {
            background-color: #e8f4f8 !important;
            border: 2px solid #4CAF50 !important;
            padding: 15px !important;
            margin: 10px 0 !important;
            border-radius: 5px !important;
            box-shadow: 0 2px 4px rgba(76, 175, 80, 0.3) !important;
        }
        
        #translation_mode_div label {
            color: #2c3e50 !important;
            font-weight: bold !important;
        }
    </style>
    <script>
        function toggleSection(id) {
            var section = document.getElementById(id);
            if (section.classList.contains('hidden')) {
                section.classList.remove('hidden');
            } else {
                section.classList.add('hidden');
            }
        }
        
        
        // Function to show/hide translation mode options based on language selection
        function updateTranslationMode() {
            var targetLanguageSelect = document.getElementById('target_language');
            var translationModeDiv = document.getElementById('translation_mode_div');
            
            if (!targetLanguageSelect || !translationModeDiv) {
                return;
            }
            
            var selectedValue = targetLanguageSelect.value;
            
            // Show translation mode options when a language is selected
            if (selectedValue && selectedValue !== '' && selectedValue.trim() !== '') {
                translationModeDiv.style.display = 'block';
                translationModeDiv.style.visibility = 'visible';
            } else {
                translationModeDiv.style.display = 'none';
            }
        }
        
        // Function to show/hide language dropdown and translation mode options
        function updateLanguageOptions() {
            var profile = document.getElementById('profile').value;
            var languageDiv = document.getElementById('language_div');
            var targetLanguageSelect = document.getElementById('target_language');
            var translationModeDiv = document.getElementById('translation_mode_div');
            
            
            // Show language dropdown especially for ESL, but available for all profiles
            languageDiv.style.display = 'block';
            targetLanguageSelect.disabled = false;
            
            // Update translation mode visibility based on language selection
            updateTranslationMode();
            
            if (profile === 'esl') {
                // For ESL, make it more prominent using both CSS classes and inline styles
                languageDiv.className = 'form-group translation-highlight';
                
                // Fallback inline styles in case CSS class doesn't work
                languageDiv.style.backgroundColor = '#f0f8ff';
                languageDiv.style.border = '2px solid #4CAF50';
                languageDiv.style.padding = '10px';
                languageDiv.style.borderRadius = '5px';
                languageDiv.style.margin = '10px 0';
                languageDiv.style.boxShadow = '0 2px 4px rgba(76, 175, 80, 0.3)';
                
                // Update label to be more specific for ESL
                var label = languageDiv.querySelector('label');
                label.textContent = 'Translate to native language (recommended for ESL):';
                label.style.fontWeight = 'bold';
                label.style.color = '#2c3e50';
                
            } else {
                // For other profiles, show but less prominently
                languageDiv.className = 'form-group';
                
                // Clear any ESL-specific styling
                languageDiv.style.backgroundColor = '';
                languageDiv.style.border = '';
                languageDiv.style.padding = '';
                languageDiv.style.borderRadius = '';
                languageDiv.style.margin = '';
                languageDiv.style.boxShadow = '';
                
                // Standard label for other profiles
                var label = languageDiv.querySelector('label');
                label.textContent = 'Optional: Translate to language';
                label.style.fontWeight = '';
                label.style.color = '';
                
            }
        }
        
        // Function to update file input label based on selected file
        function updateFileInputLabel() {
            var fileInput = document.getElementById('file-input');
            var label = document.getElementById('file-input-label');
            
            if (fileInput.files.length > 0) {
                var filename = fileInput.files[0].name;
                var ext = filename.split('.').pop().toLowerCase();
                
                if (ext === 'pdf') {
                    label.textContent = 'PDF Selected: ' + filename;
                } else if (ext === 'pptx') {
                    label.textContent = 'PowerPoint Selected: ' + filename;
                } else {
                    label.textContent = 'File Selected: ' + filename;
                }
            } else {
                label.textContent = 'Select PowerPoint (.pptx) or PDF file:';
            }
        }

        // Setup form submission handling
        function debugFormSubmission() {
            // Form validation could be added here if needed
        }
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {
            try {
                updateLanguageOptions();
                debugFormSubmission();
                
                var profileSelect = document.getElementById('profile');
                var targetLanguageSelect = document.getElementById('target_language');
                var fileInput = document.getElementById('file-input');
                
                if (profileSelect) {
                    profileSelect.addEventListener('change', updateLanguageOptions);
                }
                
                if (targetLanguageSelect) {
                    targetLanguageSelect.addEventListener('change', updateTranslationMode);
                    targetLanguageSelect.addEventListener('input', updateTranslationMode);
                }
                
                if (fileInput) {
                    fileInput.addEventListener('change', updateFileInputLabel);
                }
                
                setTimeout(function() {
                    updateTranslationMode();
                }, 100);
                
            } catch (error) {
                console.error('Error in setup:', error);
            }
        });
    </script>
</head>
<body>
    <div class="container">
        <div class="logo">Matcha</div>
        <h1>PowerPoint Adaptor</h1>
        <p>Upload a PowerPoint file to adapt its content for different learning needs.</p>
        
        <div class="info-box">
            <strong>Two Ways to Use Matcha:</strong> 
            <ul>
                <li><strong>Assess First:</strong> Get a detailed analysis of your presentation's readability</li>
                <li><strong>Direct Adaptation:</strong> Skip assessment and directly adapt your presentation</li>
            </ul>
        </div>
        
        <form action="/upload" method="POST" enctype="multipart/form-data">
            <!-- SINGLE FILE INPUT - ACCEPTS BOTH PPTX AND PDF -->
            <div class="form-group">
                <label for="file-input" id="file-input-label">Select PowerPoint (.pptx) or PDF file:</label>
                <input type="file" id="file-input" name="pptx" accept=".pptx,.pdf" required>
            </div>
            
            <div class="form-group">
                <label for="profile">Select learning profile:</label>
                <select id="profile" name="profile" required>
                    <option value="dyslexia">Dyslexia Support</option>
                    <option value="adhd">ADHD Support</option>
                    <option value="esl">English Language Learner</option>
                    <option value="translation">Translation Only</option>
                    <option value="dyslexia_translation">Dyslexia Support + Translation</option>
                    <option value="adhd_translation">ADHD Support + Translation</option>
                    <option value="esl_translation">ESL Support + Translation</option>
                </select>
            </div>
            
            <!-- LANGUAGE OPTIONS (ESPECIALLY FOR ESL) -->
            <div id="language_div" class="form-group" style="display:block;">
                <label for="target_language">Optional: Translate to language</label>
                <select id="target_language" name="target_language">
                    <option value="">English only (no translation)</option>
                    <option value="spanish">Spanish</option>
                    <option value="french">French</option>
                    <option value="german">German</option>
                    <option value="italian">Italian</option>
                    <option value="portuguese">Portuguese</option>
                    <option value="polish">Polish</option>
                    <option value="ukrainian">Ukrainian</option>
                    <option value="chinese">Chinese</option>
                    <option value="japanese">Japanese</option>
                    <option value="arabic">Arabic</option>
                    <option value="hindi">Hindi</option>
                    <option value="russian">Russian</option>
                </select>
            </div>
            
            <!-- TRANSLATION MODE OPTIONS (ONLY SHOWN WHEN TRANSLATION IS SELECTED) -->
            <div id="translation_mode_div" class="form-group" style="display:none;">
                <label for="translation_mode"><strong>Translation Mode:</strong></label>
                <div style="margin-top: 8px;">
                    <input type="radio" id="mode-copy" name="translation_mode" value="copy" checked>
                    <label for="mode-copy" style="display: inline; margin-left: 5px; font-weight: normal;">
                        <strong>Create copies</strong> - Keep original slides and add translated copies
                    </label>
                </div>
                <div style="margin-top: 5px;">
                    <input type="radio" id="mode-replace" name="translation_mode" value="replace">
                    <label for="mode-replace" style="display: inline; margin-left: 5px; font-weight: normal;">
                        <strong>Replace content</strong> - Translate text directly in original slides
                    </label>
                </div>
                <small style="color: #666; display: block; margin-top: 5px;">
                    Copy mode: Original slides followed by translated versions<br>
                    Replace mode: Only translated slides (original content replaced)
                </small>
            </div>
            
            <!-- ACTION BUTTONS -->
            <div class="buttons">
                <button type="submit" name="action" value="assess">Assess Content</button>
                <button type="submit" name="action" value="adapt" class="secondary-btn">Direct Adaptation</button>
            </div>
            
            <!-- EXPORT FORMAT OPTIONS (ALWAYS VISIBLE FOR CONSISTENCY) -->
            <div id="export-options" class="form-group">
                <label><strong>Export Format (for Direct Adaptation):</strong></label>
                <div style="margin-top: 8px;">
                    <input type="radio" id="export-pdf" name="export_format" value="pdf" checked>
                    <label for="export-pdf" style="display: inline; margin-left: 5px;">PDF (Recommended)</label>
                </div>
                <div style="margin-top: 5px;">
                    <input type="radio" id="export-pptx" name="export_format" value="pptx">
                    <label for="export-pptx" style="display: inline; margin-left: 5px;">PowerPoint</label>
                </div>
                <small style="color: #666; display: block; margin-top: 5px;">
                    PDF format handles text length variations better after AI adaptation
                </small>
            </div>
            
            <div style="margin-top: 10px; text-align: right;">
                <a href="/check_api" style="color: #3498db; font-size: 0.9em; text-decoration: underline;">Check API Connection</a>
            </div>
        </form>
        
        <div class="color-samples">
            <p><strong>Color Key:</strong> First word in adapted text is highlighted</p>
            <div class="color-sample dyslexia-color"></div> Dyslexia Support
            <div class="color-sample adhd-color"></div> ADHD Support
            <div class="color-sample esl-color"></div> English Language Learner
        </div>
        
        <h3 class="toggle-section" onclick="toggleSection('features-info')">Learn About Adaptation Features ▼</h3>
        <div id="features-info" class="profile-info hidden">
            <h4>Dyslexia Support Features</h4>
            <ul>
                <li>Simplified vocabulary and shorter sentences</li>
                <li>Left-aligned text with increased spacing</li>
                <li>Sans-serif fonts for better readability</li>
                <li>Key information highlighted</li>
                <li>Research-based text adaptations</li>
            </ul>
            
            <h4>ADHD Support Features</h4>
            <ul>
                <li>Structured content with clear organization</li>
                <li>Bullet points for easier focus</li>
                <li>Broken-down paragraphs into manageable chunks</li>
                <li>Highlighted important information</li>
            </ul>
            
            <h4>ESL Support Features</h4>
            <ul>
                <li>Simplified vocabulary with original terms in parentheses</li>
                <li>Shorter sentences for easier comprehension</li>
                <li>Clear explanations of complex terms</li>
                <li>Consistent terminology throughout</li>
            </ul>
            
            <h4>Translation Support (All Profiles)</h4>
            <p>Optional translation is now available for all learning profiles! You can choose to have your adapted presentation translated into any of the supported languages, making it accessible for multilingual classrooms and bilingual learners across all support types.</p>
        </div>
    </div>
</body>
</html>
"""

SCAFFOLDING_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>Learning Scaffolding Analysis</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
        .container { max-width: 900px; margin: 0 auto; }
        .assessment-header { text-align: center; margin-bottom: 30px; }
        h1, h2, h3 { color: #333; }
        .card { border: 1px solid #ddd; border-radius: 4px; padding: 15px; margin-bottom: 20px; }
        .section { margin-bottom: 30px; }
        .slide-purpose { font-size: 14px; color: #666; }
        .key-concept { margin-bottom: 10px; }
        .term { font-weight: bold; }
        .example { background-color: #f9f9f9; padding: 10px; border-radius: 4px; margin-bottom: 10px; }
        
        /* Score container and circle styles from assessment template */
        .score-container { 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            margin: 20px 0;
        }
        .score-circle {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
            font-weight: bold;
            color: white;
            margin-right: 20px;
        }
        .high-need { background-color: #e74c3c; }      /* Red */
        .medium-need { background-color: #f39c12; }    /* Orange */
        .low-need { background-color: #27ae60; }       /* Green */
        .recommendation {
            flex: 1;
            padding: 15px;
            background-color: #f5f5f5;
            border-radius: 5px;
        }
        
        /* Tab styles from assessment template */
        .tab-container {
            margin: 30px 0;
        }
        .tab {
            overflow: hidden;
            border: 1px solid #ccc;
            background-color: #f1f1f1;
            border-radius: 5px 5px 0 0;
        }
        .tab button {
            background-color: inherit;
            float: left;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 10px 16px;
            transition: 0.3s;
            font-size: 16px;
        }
        .tab button:hover {
            background-color: #ddd;
        }
        .tab button.active {
            background-color: #4CAF50;
            color: white;
        }
        .tabcontent {
            display: none;
            padding: 20px;
            border: 1px solid #ccc;
            border-top: none;
            border-radius: 0 0 5px 5px;
        }
        .tabcontent.show {
            display: block;
        }
        
        /* Profile and metrics styles */
        .color-sample { display: inline-block; width: 20px; height: 20px; margin-right: 5px; vertical-align: middle; border: 1px solid #ccc; }
        .profile-color {
            background-color: {% if profile_assessment.profile == "dyslexia" %}#0066cc{% elif profile_assessment.profile == "adhd" %}#2e8b57{% else %}#9400d3{% endif %};
        }
        .logo { font-size: 24px; color: #4CAF50; margin-bottom: 10px; font-weight: bold; text-align: center; }
        .metrics-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .metrics-table th, .metrics-table td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .metrics-table th {
            background-color: #f5f5f5;
        }
        .bad { color: #e74c3c; }
        .okay { color: #f39c12; }
        .good { color: #27ae60; }
        .btn {
            display: inline-block;
            background: #4CAF50;
            color: white;
            text-decoration: none;
            padding: 10px 15px;
            margin: 10px 5px;
            border: none;
            cursor: pointer;
            border-radius: 4px;
        }
        .btn-blue { background-color: #3498db; }
        .action-container { text-align: center; margin-top: 30px; }
    </style>
    <script>
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }
        
        // Initialize first tab as active when page loads
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementsByClassName('tablinks')[0].click();
        });
    </script>
</head>
<body>
    <div class="container">
        <div class="logo">Matcha</div>
        
        <div class="assessment-header">
            <h1>Learning Scaffolding Analysis</h1>
            {% if profile_assessment %}
            <p>
                Profile: 
                <span>
                    <div class="color-sample profile-color"></div>
                    {% if profile_assessment.profile == "dyslexia" %}Dyslexia Support
                    {% elif profile_assessment.profile == "adhd" %}ADHD Support
                    {% else %}English Language Learner{% endif %}
                </span>
            </p>
            {% endif %}
        </div>
        
        {% if profile_assessment %}
        <div class="score-container">
            <div class="score-circle {% if profile_assessment.suitability_score < 60 %}high-need{% elif profile_assessment.suitability_score < 80 %}medium-need{% else %}low-need{% endif %}">
                {{ "%.0f"|format(profile_assessment.suitability_score) }}
            </div>
            <div class="recommendation">
                <h3>Profile Suitability:</h3>
                <p>{{ profile_assessment.recommendation }}</p>
            </div>
        </div>
        {% endif %}
        
        <div class="tab-container">
            <div class="tab">
                <button class="tablinks" onclick="openTab(event, 'Scaffolding')">Learning Elements</button>
                {% if profile_assessment %}
                <button class="tablinks" onclick="openTab(event, 'Profile')">Profile Assessment</button>
                {% endif %}
                <button class="tablinks" onclick="openTab(event, 'Structure')">Slide Structure</button>
                {% if debug_info %}
                <button class="tablinks" onclick="openTab(event, 'Debug')">Debug Info</button>
                {% endif %}
            </div>
            
            <div id="Scaffolding" class="tabcontent">
                <div class="section">
                    <h3>Learning Objectives</h3>
                    <ul>
                        {% for obj in scaffolding.learning_objectives %}
                        <li>{{ obj }}</li>
                        {% else %}
                        <li>No learning objectives detected</li>
                        {% endfor %}
                    </ul>
                </div>
                
                <div class="section">
                    <h3>Key Concepts</h3>
                    {% if scaffolding.key_concepts %}
                    <table class="metrics-table">
                        <tr>
                            <th>Concept</th>
                            <th>Definition</th>
                        </tr>
                        {% for concept in scaffolding.key_concepts %}
                        <tr>
                            <td>
                                {% if concept.concept %}
                                {{ concept.concept }}
                                {% else %}
                                {{ concept }}
                                {% endif %}
                            </td>
                            <td>
                                {% if concept.definition %}
                                {{ concept.definition }}
                                {% else %}
                                -
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </table>
                    {% else %}
                    <p>No key concepts detected</p>
                    {% endif %}
                </div>
                
                <div class="section">
                    <h3>Examples</h3>
                    {% for example in scaffolding.examples %}
                    <div class="example">
                        {% if example.slide_number %}
                        <strong>Slide {{ example.slide_number }}:</strong> {{ example.content }}
                        {% else %}
                        {{ example }}
                        {% endif %}
                    </div>
                    {% else %}
                    <p>No examples detected</p>
                    {% endfor %}
                </div>
                
                <div class="section">
                    <h3>Practice Activities</h3>
                    <ul>
                        {% for activity in scaffolding.practice_activities %}
                        <li>
                            {% if activity.slide_number %}
                            {{ activity.content }} (Slide {{ activity.slide_number }})
                            {% else %}
                            {{ activity }}
                            {% endif %}
                        </li>
                        {% else %}
                        <li>No practice activities detected</li>
                        {% endfor %}
                    </ul>
                </div>
                
                <div class="section">
                    <h3>Assessment Items</h3>
                    <ul>
                        {% for item in scaffolding.assessment_items %}
                        <li>
                            {% if item.slide_number %}
                            {{ item.content }} (Slide {{ item.slide_number }})
                            {% else %}
                            {{ item }}
                            {% endif %}
                        </li>
                        {% else %}
                        <li>No assessment items detected</li>
                        {% endfor %}
                    </ul>
                </div>
                
                <div class="section">
                    <h3>Review Elements</h3>
                    <ul>
                        {% for item in scaffolding.review_elements %}
                        <li>
                            {% if item.slide_number %}
                            {{ item.content }} (Slide {{ item.slide_number }})
                            {% else %}
                            {{ item }}
                            {% endif %}
                        </li>
                        {% else %}
                        <li>No review elements detected</li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
            
            {% if profile_assessment %}
            <div id="Profile" class="tabcontent">
                <h2>Profile Assessment: {{ profile_assessment.profile|title }}</h2>
                
                {% if profile_assessment.readability_metrics %}
                <h3>Readability Metrics</h3>
                <table class="metrics-table">
                    <tr>
                        <th>Metric</th>
                        <th>Current Value</th>
                        <th>Status</th>
                    </tr>
                    <tr>
                        <td>Flesch Reading Ease</td>
                        <td>{{ "%.1f"|format(profile_assessment.readability_metrics.flesch_ease or 0) }}</td>
                        <td class="{% if profile_assessment.readability_metrics.flesch_ease >= 60 %}good{% elif profile_assessment.readability_metrics.flesch_ease >= 40 %}okay{% else %}bad{% endif %}">
                            {% if profile_assessment.readability_metrics.flesch_ease >= 60 %}Good{% elif profile_assessment.readability_metrics.flesch_ease >= 40 %}Needs Improvement{% else %}Needs Significant Improvement{% endif %}
                        </td>
                    </tr>
                    <tr>
                        <td>Grade Level</td>
                        <td>{{ "%.1f"|format(profile_assessment.readability_metrics.grade_level or 0) }}</td>
                        <td class="{% if profile_assessment.readability_metrics.grade_level <= 8 %}good{% elif profile_assessment.readability_metrics.grade_level <= 12 %}okay{% else %}bad{% endif %}">
                            {% if profile_assessment.readability_metrics.grade_level <= 8 %}Good{% elif profile_assessment.readability_metrics.grade_level <= 12 %}Needs Improvement{% else %}Needs Significant Improvement{% endif %}
                        </td>
                    </tr>
                    <tr>
                        <td>Average Sentence Length</td>
                        <td>{{ "%.1f"|format(profile_assessment.readability_metrics.avg_sentence_length or 0) }} words</td>
                        <td class="{% if profile_assessment.readability_metrics.avg_sentence_length <= 15 %}good{% elif profile_assessment.readability_metrics.avg_sentence_length <= 20 %}okay{% else %}bad{% endif %}">
                            {% if profile_assessment.readability_metrics.avg_sentence_length <= 15 %}Good{% elif profile_assessment.readability_metrics.avg_sentence_length <= 20 %}Needs Improvement{% else %}Needs Significant Improvement{% endif %}
                        </td>
                    </tr>
                </table>
                {% endif %}
                
                {% if profile_assessment.strengths %}
                <h3>Strengths</h3>
                <ul style="color: #27ae60;">
                    {% for strength in profile_assessment.strengths %}
                    <li>{{ strength }}</li>
                    {% endfor %}
                </ul>
                {% endif %}
                
                {% if profile_assessment.issues %}
                <h3>Areas for Improvement</h3>
                <ul style="color: #e74c3c;">
                    {% for issue in profile_assessment.issues %}
                    <li>{{ issue }}</li>
                    {% endfor %}
                </ul>
                {% endif %}
                
                {% if profile_assessment.recommendations %}
                <h3>Recommendations</h3>
                <ul>
                    {% for rec in profile_assessment.recommendations %}
                    <li>{{ rec }}</li>
                    {% endfor %}
                </ul>
                {% endif %}
            </div>
            {% endif %}
            
            <div id="Structure" class="tabcontent">
                <h2>Slide Structure Analysis</h2>
                
                <div class="section">
                    <h3>Slide Purposes</h3>
                    {% for slide in slides %}
                    <div class="card">
                        <h3>Slide {{ slide.slide_number }}</h3>
                        <p class="slide-purpose">Purpose: {{ slide.purpose }}</p>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            {% if debug_info %}
            <div id="Debug" class="tabcontent">
                <h2>Debug Information</h2>
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
                    <h3>Processing Statistics</h3>
                    <table class="metrics-table">
                        <tr>
                            <th>Metric</th>
                            <th>Value</th>
                        </tr>
                        <tr>
                            <td>Slides extracted</td>
                            <td>{{ debug_info.slides_extracted }}</td>
                        </tr>
                        <tr>
                            <td>Slides analyzed</td>
                            <td>{{ debug_info.slides_analyzed }}</td>
                        </tr>
                        <tr>
                            <td>AI response length</td>
                            <td>{{ debug_info.ai_response_length }} characters</td>
                        </tr>
                        {% if debug_info.profile_used %}
                        <tr>
                            <td>Profile used</td>
                            <td>{{ debug_info.profile_used }}</td>
                        </tr>
                        {% endif %}
                    </table>
                    
                    <h3>Elements Found</h3>
                    <table class="metrics-table">
                        <tr>
                            <th>Element Type</th>
                            <th>Count</th>
                        </tr>
                        {% for key, value in debug_info.elements_found.items() %}
                        <tr>
                            <td>{{ key|replace('_', ' ')|title }}</td>
                            <td>{{ value }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                    
                    {% if debug_info.sample_elements %}
                    <h3>Sample Elements Structure</h3>
                    <pre style="background-color: #eee; padding: 10px; overflow-x: auto; border-radius: 4px; font-size: 11px;">{{ debug_info.sample_elements }}</pre>
                    {% endif %}
                </div>
            </div>
            {% endif %}
        </div>
        
        <div class="action-container">
            <a href="/" class="btn btn-blue">Analyze Another Document</a>
            {% if profile_assessment and profile_assessment.profile %}
                {% if file_type == '.pptx' %}
                <a href="/adapt/{{ file_id }}/{{ profile_assessment.profile }}" class="btn">Adapt PowerPoint Now</a>
                {% elif file_type == '.pdf' %}
                <a href="/adapt/{{ file_id }}/{{ profile_assessment.profile }}" class="btn">Adapt PDF Now</a>
                {% else %}
                <a href="/adapt/{{ file_id }}/{{ profile_assessment.profile }}" class="btn">Adapt Content Now</a>
                {% endif %}
            {% endif %}
        </div>
    </div>
</body>
</html>"""

FRAMEWORK_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Instructional Framework Analysis</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
        .container { max-width: 900px; margin: 0 auto; }
        h1, h2, h3 { color: #333; }
        .framework-section { margin-bottom: 30px; background-color: #f8f9fa; padding: 20px; border-radius: 5px; }
        .score-container { display: flex; align-items: center; margin: 20px 0; }
        .score-circle {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
            font-weight: bold;
            color: white;
            margin-right: 20px;
        }
        .high-score { background-color: #27ae60; }
        .medium-score { background-color: #f39c12; }
        .low-score { background-color: #e74c3c; }
        .analysis-list { margin: 15px 0; }
        .analysis-list li { margin-bottom: 8px; }
        .phase-visualization {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 20px 0;
        }
        .phase-block {
            padding: 15px;
            border-radius: 5px;
            min-width: 150px;
            text-align: center;
        }
        .present { background-color: #d4edda; border: 1px solid #c3e6cb; }
        .missing { background-color: #f8d7da; border: 1px solid #f5c6cb; }
        .phase-name { font-weight: bold; margin-bottom: 5px; }
        .slide-container { margin-top: 40px; }
        .slide-row {
            display: flex;
            margin-bottom: 15px;
            padding: 15px;
            border: 1px solid #dee2e6;
            border-radius: 5px;
        }
        .slide-number {
            font-weight: bold;
            width: 80px;
        }
        .slide-phase {
            width: 150px;
        }
        .slide-details {
            flex: 1;
        }
        .strong { color: #27ae60; }
        .adequate { color: #f39c12; }
        .weak { color: #e74c3c; }
        .btn {
            display: inline-block;
            background: #4CAF50;
            color: white;
            text-decoration: none;
            padding: 10px 15px;
            margin: 10px 5px;
            border: none;
            cursor: pointer;
            border-radius: 4px;
        }
        .btn-blue { background-color: #3498db; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Instructional Framework Analysis</h1>
        
        <div class="framework-section">
            <h2>{{ framework.framework.identified_framework }}</h2>
            
            <div class="score-container">
                <div class="score-circle {% if framework.framework.framework_alignment_score >= 80 %}high-score{% elif framework.framework.framework_alignment_score >= 60 %}medium-score{% else %}low-score{% endif %}">
                    {{ framework.framework.framework_alignment_score }}
                </div>
                <div>
                    <h3>Framework Alignment Score</h3>
                    <p>{{ framework.framework.balance_analysis }}</p>
                </div>
            </div>
            
            <h3>Strengths</h3>
            <ul class="analysis-list">
                {% for strength in framework.framework.strengths %}
                <li>{{ strength }}</li>
                {% endfor %}
            </ul>
            
            <h3>Areas for Improvement</h3>
            <ul class="analysis-list">
                {% for weakness in framework.framework.weaknesses %}
                <li>{{ weakness }}</li>
                {% endfor %}
            </ul>
            
            <h3>Recommendation</h3>
            <p>{{ framework.framework.recommendations }}</p>
            
            <h3>Instructional Phases</h3>
            <div class="phase-visualization">
                {% if framework.framework.identified_framework.startswith('Recall') %}
                    {% set phases = ['Recall', 'Teacher Demo', 'Guided Practice', 'Independent Work', 'Review'] %}
                {% elif framework.framework.identified_framework.startswith('5E') %}
                    {% set phases = ['Engage', 'Explore', 'Explain', 'Elaborate', 'Evaluate'] %}
                {% else %}
                    {% set phases = [] %}
                {% endif %}
                
                {% for phase in phases %}
                    {% set phase_display = phase %}
                    {% set phase_match = phase %}
                    
                    {% if phase == 'Teacher Demo' %}
                        {% set phase_match = 'I do' %}
                    {% elif phase == 'Guided Practice' %}
                        {% set phase_match = 'We do' %}
                    {% elif phase == 'Independent Work' %}
                        {% set phase_match = 'You do' %}
                    {% endif %}
                    
                    {% set is_missing = phase_match in framework.framework.missing_phases %}
                    <div class="phase-block {{ 'missing' if is_missing else 'present' }}">
                        <div class="phase-name">{{ phase_display }}</div>
                        {% if is_missing %}
                            <div>Missing Phase</div>
                        {% else %}
                            <div>
                                {% set phase_slides = [] %}
                                {% for slide in framework.slides %}
                                    {% if slide.framework_phase == phase_match %}
                                        {% set __ = phase_slides.append(slide.slide_number) %}
                                    {% endif %}
                                {% endfor %}
                                
                                Slides: {{ phase_slides|join(', ') if phase_slides else 'None' }}
                            </div>
                        {% endif %}
                    </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="slide-container">
            <h2>Slide Analysis</h2>
            
            {% for slide in framework.slides %}
            <div class="slide-row">
                <div class="slide-number">Slide {{ slide.slide_number }}</div>
                <div class="slide-phase">{{ slide.framework_phase }}</div>
                <div class="slide-details">
                    <div class="{{ slide.effectiveness }}">Effectiveness: {{ slide.effectiveness|capitalize }}</div>
                    {% if slide.elements %}
                    <ul>
                        {% for element in slide.elements %}
                        <li>{{ element }}</li>
                        {% endfor %}
                    </ul>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div style="text-align:center; margin-top:30px;">
            <a href="/adapt/{{ file_id }}/dyslexia" class="btn">Adapt for Dyslexia</a>
            <a href="/adapt/{{ file_id }}/adhd" class="btn">Adapt for ADHD</a>
            <a href="/adapt/{{ file_id }}/esl" class="btn">Adapt for ESL</a>
            <a href="/" class="btn btn-blue">Back to Home</a>
        </div>
    </div>
</body>
</html>
"""

ASSESSMENT_TEMPLATE_SIMPLIFIED = """
<!DOCTYPE html>
<html>
<head>
    <title>Content Assessment</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .assessment-header { text-align: center; margin-bottom: 30px; }
        .score-container { 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            margin: 20px 0;
        }
        .score-circle {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
            font-weight: bold;
            color: white;
            margin-right: 20px;
        }
        .high-need { background-color: #e74c3c; }      /* Red */
        .medium-need { background-color: #f39c12; }    /* Orange */
        .low-need { background-color: #27ae60; }       /* Green */
        .recommendation {
            flex: 1;
            padding: 15px;
            background-color: #f5f5f5;
            border-radius: 5px;
        }
        .metrics-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .metrics-table th, .metrics-table td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .metrics-table th {
            background-color: #f5f5f5;
        }
        .bad { color: #e74c3c; }
        .okay { color: #f39c12; }
        .good { color: #27ae60; }
        .btn {
            display: inline-block;
            background: #4CAF50;
            color: white;
            text-decoration: none;
            padding: 10px 15px;
            margin: 10px 5px;
            border: none;
            cursor: pointer;
            border-radius: 4px;
        }
        .btn-blue { background-color: #3498db; }
        .action-container { text-align: center; margin-top: 30px; }
        .chart-container { margin: 30px 0; text-align: center; }
        .color-sample { display: inline-block; width: 20px; height: 20px; margin-right: 5px; vertical-align: middle; border: 1px solid #ccc; }
        .profile-color {
            background-color: {% if profile == "dyslexia" %}#0066cc{% elif profile == "adhd" %}#2e8b57{% else %}#9400d3{% endif %};
        }
        .logo { font-size: 24px; color: #4CAF50; margin-bottom: 10px; font-weight: bold; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">Matcha</div>
        
        <div class="assessment-header">
            <h1>Content Assessment Results</h1>
            <p>
                Profile: 
                <span>
                    <div class="color-sample profile-color"></div>
                    {% if profile == "dyslexia" %}Dyslexia Support
                    {% elif profile == "adhd" %}ADHD Support
                    {% else %}English Language Learner{% endif %}
                </span>
            </p>
        </div>
        
        <div class="score-container">
            <div class="score-circle {% if adaptation_score < 60 %}high-need{% elif adaptation_score < 80 %}medium-need{% else %}low-need{% endif %}">
                {{ adaptation_score }}
            </div>
            <div class="recommendation">
                <h3>Recommendation:</h3>
                <p>{{ recommendation }}</p>
            </div>
        </div>
        
        <h2>Readability Analysis</h2>
        <table class="metrics-table">
            <tr>
                <th>Metric</th>
                <th>Current Value</th>
                <th>Target for {{ profile_name }}</th>
                <th>Status</th>
            </tr>
            <tr>
                <td>Flesch Reading Ease</td>
                <td>{{ metrics.flesch_reading_ease }}</td>
                <td>{{ thresholds.flesch_reading_ease }}+</td>
                <td class="{% if metrics.flesch_reading_ease >= thresholds.flesch_reading_ease %}good{% elif metrics.flesch_reading_ease >= thresholds.flesch_reading_ease - 15 %}okay{% else %}bad{% endif %}">
                    {% if metrics.flesch_reading_ease >= thresholds.flesch_reading_ease %}Good{% elif metrics.flesch_reading_ease >= thresholds.flesch_reading_ease - 15 %}Needs Improvement{% else %}Needs Significant Improvement{% endif %}
                </td>
            </tr>
            <tr>
                <td>Grade Level</td>
                <td>{{ metrics.flesch_kincaid_grade }}</td>
                <td>{{ thresholds.flesch_kincaid_grade }} or lower</td>
                <td class="{% if metrics.flesch_kincaid_grade <= thresholds.flesch_kincaid_grade %}good{% elif metrics.flesch_kincaid_grade <= thresholds.flesch_kincaid_grade + 3 %}okay{% else %}bad{% endif %}">
                    {% if metrics.flesch_kincaid_grade <= thresholds.flesch_kincaid_grade %}Good{% elif metrics.flesch_kincaid_grade <= thresholds.flesch_kincaid_grade + 3 %}Needs Improvement{% else %}Needs Significant Improvement{% endif %}
                </td>
            </tr>
            <tr>
                <td>SMOG Index</td>
                <td>{{ metrics.smog_index }}</td>
                <td>{{ thresholds.smog_index }} or lower</td>
                <td class="{% if metrics.smog_index <= thresholds.smog_index %}good{% elif metrics.smog_index <= thresholds.smog_index + 2 %}okay{% else %}bad{% endif %}">
                    {% if metrics.smog_index <= thresholds.smog_index %}Good{% elif metrics.smog_index <= thresholds.smog_index + 2 %}Needs Improvement{% else %}Needs Significant Improvement{% endif %}
                </td>
            </tr>
            <tr>
                <td>Avg. Sentence Length</td>
                <td>{{ metrics.sentence_length }} words</td>
                <td>{{ thresholds.sentence_length }} words or fewer</td>
                <td class="{% if metrics.sentence_length <= thresholds.sentence_length %}good{% elif metrics.sentence_length <= thresholds.sentence_length + 5 %}okay{% else %}bad{% endif %}">
                    {% if metrics.sentence_length <= thresholds.sentence_length %}Good{% elif metrics.sentence_length <= thresholds.sentence_length + 5 %}Needs Improvement{% else %}Needs Significant Improvement{% endif %}
                </td>
            </tr>
            <tr>
                <td>Complex Word %</td>
                <td>{{ metrics.complex_word_percent }}%</td>
                <td>{{ thresholds.complex_word_percent }}% or lower</td>
                <td class="{% if metrics.complex_word_percent <= thresholds.complex_word_percent %}good{% elif metrics.complex_word_percent <= thresholds.complex_word_percent + 10 %}okay{% else %}bad{% endif %}">
                    {% if metrics.complex_word_percent <= thresholds.complex_word_percent %}Good{% elif metrics.complex_word_percent <= thresholds.complex_word_percent + 10 %}Needs Improvement{% else %}Needs Significant Improvement{% endif %}
                </td>
            </tr>
        </table>
        
        <div class="chart-container">
            <h3>Content Complexity Analysis</h3>
            <img src="{{ complexity_chart }}" alt="Content Complexity Chart" style="max-width:100%;">
        </div>
        
        <div class="chart-container">
            <h3>Most Frequent Complex Words</h3>
            <img src="{{ complex_words_chart }}" alt="Complex Words Chart" style="max-width:100%;">
        </div>
        
<div class="action-container">
    <a href="/adapt/{{ file_id }}/{{ profile }}" class="btn">Adapt PowerPoint Now</a>
    <a href="/analyze/framework/{{ file_id }}" class="btn btn-blue">Analyze Teaching Framework</a>
    <a href="/analyze/scaffolding/{{ file_id }}" class="btn btn-blue">Analyze Learning Scaffolding</a>
    <a href="/" class="btn btn-blue">Start Over</a>
</div>
    </div>
</body>
</html>
"""

ASSESSMENT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Content Assessment</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .assessment-header { text-align: center; margin-bottom: 30px; }
        .score-container { 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            margin: 20px 0;
        }
        .score-circle {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
            font-weight: bold;
            color: white;
            margin-right: 20px;
        }
        .high-need { background-color: #e74c3c; }      /* Red */
        .medium-need { background-color: #f39c12; }    /* Orange */
        .low-need { background-color: #27ae60; }       /* Green */
        .recommendation {
            flex: 1;
            padding: 15px;
            background-color: #f5f5f5;
            border-radius: 5px;
        }
        .metrics-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .metrics-table th, .metrics-table td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .metrics-table th {
            background-color: #f5f5f5;
        }
        .bad { color: #e74c3c; }
        .okay { color: #f39c12;
.okay { color: #f39c12; }
        .good { color: #27ae60; }
        .btn {
            display: inline-block;
            background: #4CAF50;
            color: white;
            text-decoration: none;
            padding: 10px 15px;
            margin: 10px 5px;
            border: none;
            cursor: pointer;
            border-radius: 4px;
        }
        .btn-blue { background-color: #3498db; }
        .action-container { text-align: center; margin-top: 30px; }
        .chart-container { margin: 30px 0; text-align: center; }
        .color-sample { display: inline-block; width: 20px; height: 20px; margin-right: 5px; vertical-align: middle; border: 1px solid #ccc; }
        .profile-color {
            background-color: {% if profile == "dyslexia" %}#0066cc{% elif profile == "adhd" %}#2e8b57{% else %}#9400d3{% endif %};
        }
        .logo { font-size: 24px; color: #4CAF50; margin-bottom: 10px; font-weight: bold; text-align: center; }
        
        /* New styles for scaffolding analysis */
        .scaffolding-container {
            margin: 30px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 5px;
            border-left: 5px solid #4CAF50;
        }
        .framework-analysis {
            margin-bottom: 30px;
        }
        .framework-score {
            display: flex;
            align-items: center;
            margin: 15px 0;
        }
        .score-label {
            margin-left: 15px;
            font-weight: bold;
        }
        .framework-visualization {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 20px 0;
        }
        .phase-block {
            padding: 10px;
            border-radius: 5px;
            min-width: 120px;
            text-align: center;
        }
        .present {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
        }
        .missing {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
        }
        .phase-name {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .phase-slides {
            font-size: 0.9em;
            color: #666;
        }
        .phase-missing {
            font-size: 0.9em;
            color: #721c24;
        }
        .learning-elements {
            margin-top: 20px;
        }
        .objective-list {
            padding-left: 20px;
        }
        .objective-list li {
            margin-bottom: 5px;
        }
        .tab-container {
            margin: 30px 0;
        }
        .tab {
            overflow: hidden;
            border: 1px solid #ccc;
            background-color: #f1f1f1;
            border-radius: 5px 5px 0 0;
        }
        .tab button {
            background-color: inherit;
            float: left;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 10px 16px;
            transition: 0.3s;
            font-size: 16px;
        }
        .tab button:hover {
            background-color: #ddd;
        }
        .tab button.active {
            background-color: #4CAF50;
            color: white;
        }
        .tabcontent {
            display: none;
            padding: 20px;
            border: 1px solid #ccc;
            border-top: none;
            border-radius: 0 0 5px 5px;
        }
        .tabcontent.show {
            display: block;
        }
    </style>
    <script>
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }
        
        // Initialize first tab as active when page loads
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementsByClassName('tablinks')[0].click();
        });
    </script>
</head>
<body>
    <div class="container">
        <div class="logo">Matcha</div>
        
        <div class="assessment-header">
            <h1>Content Assessment Results</h1>
            <p>
                Profile: 
                <span>
                    <div class="color-sample profile-color"></div>
                    {% if profile == "dyslexia" %}Dyslexia Support
                    {% elif profile == "adhd" %}ADHD Support
                    {% else %}English Language Learner{% endif %}
                </span>
            </p>
        </div>
        
        <div class="score-container">
            <div class="score-circle {% if adaptation_score < 60 %}high-need{% elif adaptation_score < 80 %}medium-need{% else %}low-need{% endif %}">
                {{ adaptation_score }}
            </div>
            <div class="recommendation">
                <h3>Recommendation:</h3>
                <p>{{ recommendation }}</p>
            </div>
        </div>
        
        <div class="tab-container">
            <div class="tab">
                <button class="tablinks" onclick="openTab(event, 'Readability')">Readability Analysis</button>
                <button class="tablinks" onclick="openTab(event, 'Structure')">Learning Structure</button>
            </div>
            
            <div id="Readability" class="tabcontent">
                <h2>Readability Analysis</h2>
                <table class="metrics-table">
                    <tr>
                        <th>Metric</th>
                        <th>Current Value</th>
                        <th>Target for {{ profile_name }}</th>
                        <th>Status</th>
                    </tr>
                    <tr>
                        <td>Flesch Reading Ease</td>
                        <td>{{ metrics.flesch_reading_ease }}</td>
                        <td>{{ thresholds.flesch_reading_ease }}+</td>
                        <td class="{% if metrics.flesch_reading_ease >= thresholds.flesch_reading_ease %}good{% elif metrics.flesch_reading_ease >= thresholds.flesch_reading_ease - 15 %}okay{% else %}bad{% endif %}">
                            {% if metrics.flesch_reading_ease >= thresholds.flesch_reading_ease %}Good{% elif metrics.flesch_reading_ease >= thresholds.flesch_reading_ease - 15 %}Needs Improvement{% else %}Needs Significant Improvement{% endif %}
                        </td>
                    </tr>
                    <tr>
                        <td>Grade Level</td>
                        <td>{{ metrics.flesch_kincaid_grade }}</td>
                        <td>{{ thresholds.flesch_kincaid_grade }} or lower</td>
                        <td class="{% if metrics.flesch_kincaid_grade <= thresholds.flesch_kincaid_grade %}good{% elif metrics.flesch_kincaid_grade <= thresholds.flesch_kincaid_grade + 3 %}okay{% else %}bad{% endif %}">
                            {% if metrics.flesch_kincaid_grade <= thresholds.flesch_kincaid_grade %}Good{% elif metrics.flesch_kincaid_grade <= thresholds.flesch_kincaid_grade + 3 %}Needs Improvement{% else %}Needs Significant Improvement{% endif %}
                        </td>
                    </tr>
                    <tr>
                        <td>SMOG Index</td>
                        <td>{{ metrics.smog_index }}</td>
                        <td>{{ thresholds.smog_index }} or lower</td>
                        <td class="{% if metrics.smog_index <= thresholds.smog_index %}good{% elif metrics.smog_index <= thresholds.smog_index + 2 %}okay{% else %}bad{% endif %}">
                            {% if metrics.smog_index <= thresholds.smog_index %}Good{% elif metrics.smog_index <= thresholds.smog_index + 2 %}Needs Improvement{% else %}Needs Significant Improvement{% endif %}
                        </td>
                    </tr>
                    <tr>
                        <td>Avg. Sentence Length</td>
                        <td>{{ metrics.sentence_length }} words</td>
                        <td>{{ thresholds.sentence_length }} words or fewer</td>
                        <td class="{% if metrics.sentence_length <= thresholds.sentence_length %}good{% elif metrics.sentence_length <= thresholds.sentence_length + 5 %}okay{% else %}bad{% endif %}">
                            {% if metrics.sentence_length <= thresholds.sentence_length %}Good{% elif metrics.sentence_length <= thresholds.sentence_length + 5 %}Needs Improvement{% else %}Needs Significant Improvement{% endif %}
                        </td>
                    </tr>
                    <tr>
                        <td>Complex Word %</td>
                        <td>{{ metrics.complex_word_percent }}%</td>
                        <td>{{ thresholds.complex_word_percent }}% or lower</td>
                        <td class="{% if metrics.complex_word_percent <= thresholds.complex_word_percent %}good{% elif metrics.complex_word_percent <= thresholds.complex_word_percent + 10 %}okay{% else %}bad{% endif %}">
                            {% if metrics.complex_word_percent <= thresholds.complex_word_percent %}Good{% elif metrics.complex_word_percent <= thresholds.complex_word_percent + 10 %}Needs Improvement{% else %}Needs Significant Improvement{% endif %}
                        </td>
                    </tr>
                </table>
                
                <div class="chart-container">
                    <h3>Content Complexity Analysis</h3>
                    <img src="{{ complexity_chart }}" alt="Content Complexity Chart" style="max-width:100%;">
                </div>
                
                <div class="chart-container">
                    <h3>Most Frequent Complex Words</h3>
                    <img src="{{ complex_words_chart }}" alt="Complex Words Chart" style="max-width:100%;">
                </div>
            </div>
            
            <div id="Structure" class="tabcontent">
                <div class="scaffolding-container">
                    <h2>Learning Structure Analysis</h2>
                    
                    <!-- Instructional Framework Section -->
                    <div class="framework-analysis">
                        <h3>Instructional Approach: {{ framework.identified_framework }}</h3>
                        
                        <div class="score-container">
                            <div class="score-circle {% if framework.framework_alignment_score >= 80 %}low-need{% elif framework.framework_alignment_score >= 60 %}medium-need{% else %}high-need{% endif %}">
                                {{ framework.framework_alignment_score }}
                            </div>
                            <div class="recommendation">
                                <h3>Framework Alignment:</h3>
                                <p>{{ framework.recommendations }}</p>
                            </div>
                        </div>
                        
                        <h4>Lesson Structure</h4>
                        <div class="framework-visualization">
                            {% set phases = ['Recall', 'Check', 'I do', 'We do', 'You do', 'Recap'] if framework.identified_framework == 'Recall, Check, I do, We do, You do, Recap' else ['Engage', 'Explore', 'Explain', 'Elaborate', 'Evaluate'] if framework.identified_framework == '5E Model' else [] %}
                            
                            {% for phase in phases %}
                                {% set has_phase = phase not in framework.missing_phases %}
                                <div class="phase-block {{ 'present' if has_phase else 'missing' }}">
                                    <div class="phase-name">{{ phase }}</div>
                                    
                                    {% if has_phase %}
                                        {% set phase_slides = [] %}
                                        {% for slide in framework.slides if slide.framework_phase == phase %}
                                            {% do phase_slides.append(slide.slide_number) %}
                                        {% endfor %}
                                        
                                        <div class="phase-slides">Slides: {{ phase_slides|join(', ') }}</div>
                                    {% else %}
                                        <div class="phase-missing">Missing</div>
                                    {% endif %}
                                </div>
                            {% endfor %}
                        </div>
                    </div>
                <script>
    // Only run this if analysis is in progress
    {% if analysis_in_progress %}
    // Check analysis status every 5 seconds
    function checkAnalysisStatus() {
        fetch('/analysis_status/{{ file_id }}')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'complete') {
                    // Refresh the page to show complete analysis
                    window.location.reload();
                }
                else if (data.status === 'error') {
                    // Show error message
                    document.getElementById('analysis-error').style.display = 'block';
                    document.getElementById('analysis-error-message').textContent = 
                        "Error analyzing presentation structure: " + data.error;
                    clearInterval(statusInterval);
                }
            })
            .catch(error => console.error('Error checking status:', error));
    }
    
    // Set interval to check status
    var statusInterval = setInterval(checkAnalysisStatus, 5000);
    
    // Initial check after 2 seconds
    setTimeout(checkAnalysisStatus, 2000);
    {% endif %}
</script>

<!-- Add this in your Structure tab content -->
<div id="analysis-error" style="display: none; margin: 20px 0; padding: 15px; background-color: #f8d7da; border-left: 5px solid #e74c3c;">
    <p id="analysis-error-message">Error analyzing structure</p>
</div>

<!-- Show loading indicator if analysis is in progress -->
{% if analysis_in_progress %}
<div class="loading-container" style="text-align: center; margin: 30px 0;">
    <div class="loader" style="border: 8px solid #f3f3f3; border-top: 8px solid #4CAF50; border-radius: 50%; width: 60px; height: 60px; animation: spin 2s linear infinite; margin: 20px auto;"></div>
    <p>Analyzing presentation structure... This may take a minute.</p>
</div>
{% endif %}    
                    <!-- Learning Elements Section -->
                    <div class="learning-elements">
                        <h3>Learning Objectives</h3>
                        <ul class="objective-list">
                            {% for objective in scaffolding.scaffolding.learning_objectives %}
                            <li>{{ objective }}</li>
                            {% endfor %}
                        </ul>
                        
                        <h3>Key Concepts</h3>
                        <table class="metrics-table">
                            <tr>
                                <th>Term</th>
                                <th>Definition</th>
                            </tr>
                            {% for concept in scaffolding.scaffolding.key_concepts %}
                            <tr>
                                <td>{{ concept.term }}</td>
                                <td>{{ concept.definition }}</td>
                            </tr>
                            {% endfor %}
                        </table>
                        
                        {% if scaffolding.scaffolding.examples %}
                        <h3>Examples</h3>
                        <ul class="objective-list">
                            {% for example in scaffolding.scaffolding.examples %}
                            <li>Slide {{ example.slide_number }}: {{ example.content|truncate(100) }}</li>
                            {% endfor %}
                        </ul>
                        {% endif %}
                        
                        {% if scaffolding.scaffolding.assessment_items %}
                        <h3>Assessment Items</h3>
                        <ul class="objective-list">
                            {% for item in scaffolding.scaffolding.assessment_items %}
                            <li>{{ item.question }}</li>
                            {% endfor %}
                        </ul>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="action-container">
            <a href="/adapt/{{ file_id }}/{{ profile }}" class="btn">Adapt PowerPoint Now</a>
            <a href="/" class="btn btn-blue">Start Over</a>
        </div>
    </div>
</body>
</html>
"""

PROCESSING_TEMPLATE_WITH_PROGRESS = """
<!DOCTYPE html>
<html>
<head>
    <title>Processing Your Presentation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; text-align: center; }
        .container { max-width: 800px; margin: 0 auto; }
        .loader { 
            border: 16px solid #f3f3f3;
            border-top: 16px solid #4CAF50;
            border-radius: 50%;
            width: 120px;
            height: 120px;
            animation: spin 2s linear infinite;
            margin: 40px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .info { margin: 30px 0; line-height: 1.6; }
        .logo { font-size: 24px; color: #4CAF50; margin-bottom: 20px; font-weight: bold; }
        .progress-container {
            width: 100%;
            background-color: #f3f3f3;
            border-radius: 10px;
            margin: 20px 0;
        }
        .progress-bar {
            height: 30px;
            background-color: #4CAF50;
            border-radius: 10px;
            width: 0%;
            text-align: center;
            line-height: 30px;
            color: white;
            font-weight: bold;
            transition: width 0.5s;
        }
        #status-message {
            margin: 10px 0;
            font-style: italic;
        }
        #time-estimate {
            margin-top: 5px;
            font-size: 0.9em;
            color: #666;
        }
        .debug-info {
            margin-top: 20px;
            font-size: 0.8em;
            color: #999;
            display: none; /* Hide by default */
        }
    </style>
    <script>
        // Track time to estimate completion
        var startTime = Date.now();
        var lastPercentage = 0;
        var timeEstimate = null;
        var errorCount = 0;
        var maxErrors = 3;
        
        function checkStatus() {
            fetch('/status/{{ file_id }}')
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Status response:', data);
                    
                    // Reset error count on successful response
                    errorCount = 0;
                    
                    // Update debug info
                    var debugInfo = document.getElementById('debug-info');
                    if (debugInfo) {
                        debugInfo.textContent = 'Response: ' + JSON.stringify(data);
                    }
                    
                    // Update status message
                    var statusMsg = document.getElementById('status-message');
                    if (statusMsg && data.message) {
                        statusMsg.textContent = data.message;
                    }
                    
                    // Update progress bar if progress data exists
                    if (data.progress) {
                        var progressBar = document.getElementById('progress-bar');
                        if (progressBar) {
                            var percentage = parseInt(data.progress.percentage) || 0;
                            progressBar.style.width = percentage + '%';
                            progressBar.textContent = percentage + '%';
                            
                            // Calculate estimated time remaining
                            if (percentage > lastPercentage && percentage < 100 && percentage > 10) {
                                var elapsed = Date.now() - startTime;
                                var estimatedTotal = elapsed / (percentage / 100);
                                var remaining = estimatedTotal - elapsed;
                                
                                // Only update time estimate occasionally to avoid jumping around
                                if (!timeEstimate || Math.abs(percentage - lastPercentage) > 5) {
                                    timeEstimate = Math.round(remaining / 1000);
                                    
                                    var timeMsg = document.getElementById('time-estimate');
                                    if (timeMsg && timeEstimate > 0) {
                                        if (timeEstimate > 60) {
                                            var minutes = Math.floor(timeEstimate / 60);
                                            var seconds = timeEstimate % 60;
                                            timeMsg.textContent = 'Estimated time remaining: ' + 
                                                minutes + ' minute' + (minutes !== 1 ? 's' : '') + 
                                                ' ' + seconds + ' second' + (seconds !== 1 ? 's' : '');
                                        } else {
                                            timeMsg.textContent = 'Estimated time remaining: ' + 
                                                timeEstimate + ' second' + (timeEstimate !== 1 ? 's' : '');
                                        }
                                    }
                                }
                                
                                lastPercentage = percentage;
                            }
                        }
                    }
                    
                    // Check for completion
                    if (data.status === 'complete' || data.status === 'completed' || 
                    (data.progress && data.progress.percentage >= 100)) {
                        console.log('Processing complete - redirecting...');
                        clearInterval(statusInterval);
                        
                        // Short delay before redirect
                        setTimeout(function() {
                            window.location.href = '/download/{{ file_id }}/{{ filename }}';
                        }, 500);
                        return;
                    }
                    else if (data.status === 'error') {
                        console.log('Error detected:', data.message);
                        clearInterval(statusInterval);
                        
                        // Show error message
                        if (statusMsg) {
                            statusMsg.textContent = 'Error: ' + (data.message || 'Processing failed');
                            statusMsg.style.color = '#e74c3c';
                        }
                        
                        // Redirect to error page after delay
                        setTimeout(function() {
                            window.location.href = '/error?message=' + encodeURIComponent(data.message || "Processing failed");
                        }, 2000);
                        return;
                    }
                })
                .catch(error => {
                    console.error('Error checking status:', error);
                    errorCount++;
                    
                    // Show error in status message
                    var statusMsg = document.getElementById('status-message');
                    if (statusMsg) {
                        statusMsg.textContent = 'Connection error... retrying (' + errorCount + '/' + maxErrors + ')';
                        statusMsg.style.color = '#f39c12';
                    }
                    
                    // If too many errors, stop trying
                    if (errorCount >= maxErrors) {
                        clearInterval(statusInterval);
                        if (statusMsg) {
                            statusMsg.textContent = 'Unable to connect to server. Please refresh the page.';
                            statusMsg.style.color = '#e74c3c';
                        }
                    }
                });
        }

        // Toggle debug info display - accessible by pressing 'd' key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'd' || event.key === 'D') {
                var debugInfo = document.getElementById('debug-info');
                if (debugInfo) {
                    debugInfo.style.display = debugInfo.style.display === 'none' ? 'block' : 'none';
                }
            }
        });

        // Start checking status
        var statusInterval = setInterval(checkStatus, 2000);
        
        // Initial check after a short delay
        setTimeout(checkStatus, 500);
    </script>
</head>
<body>
    <div class="container">
        <div class="logo">Matcha</div>
        <h1>Processing Your Presentation</h1>
        
        <div class="loader"></div>
        
        <div class="progress-container">
            <div id="progress-bar" class="progress-bar">0%</div>
        </div>
        <div id="status-message">Initializing...</div>
        <div id="time-estimate"></div>
        
        <div class="info">
            <p>Matcha is adapting your PowerPoint for {{ profile_name }}...</p>
            <p>This process may take a few minutes depending on the size of your presentation.</p>
            <p>The page will automatically refresh when your presentation is ready.</p>
        </div>
        
        <div id="debug-info" class="debug-info">Response: {}</div>
    </div>
</body>
</html>
"""

DOWNLOAD_TEMPLATE_WITH_TRANSLATION = """
<!DOCTYPE html>
<html>
<head>
    <title>Download Adapted File</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; text-align: center; }
        .btn { background: #4CAF50; color: white; text-decoration: none; padding: 10px 15px; display: inline-block; margin-top: 20px; border: none; cursor: pointer; border-radius: 4px; }
        .home-btn { background: #3498db; margin-left: 10px; }
        .generate-btn { background: #9b59b6; margin-left: 10px; }
        .translated-btn { background: #e74c3c; margin-top: 10px; }
        .color-sample { display: inline-block; width: 20px; height: 20px; margin-right: 5px; vertical-align: middle; border: 1px solid #ccc; }
        .profile-color {
            background-color: {% if profile == "dyslexia" %}#0066cc{% elif profile == "adhd" %}#2e8b57{% else %}#9400d3{% endif %};
        }
        .adaptation-info { text-align: left; margin: 20px auto; max-width: 600px; padding: 15px; background-color: #f5f5f5; border-radius: 5px; }
        .success-message { margin: 20px 0; padding: 15px; background-color: #d4edda; border-left: 5px solid #28a745; text-align: left; }
        .logo { font-size: 24px; color: #4CAF50; margin-bottom: 10px; font-weight: bold; }
        .translation-info { margin-top: 20px; padding: 15px; background-color: #fff3cd; border-left: 5px solid #ffc107; text-align: left; display: {% if has_translation %}block{% else %}none{% endif %}; }
        .generation-form { display: none; margin-top: 20px; text-align: left; padding: 20px; background-color: #f0f4f8; border-radius: 5px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; }
        select, input[type="text"], input[type="number"], textarea { width: 100%; padding: 8px; }
        .checkbox-container { display: flex; align-items: center; }
        .checkbox-container input[type="checkbox"] { width: auto; margin-right: 8px; }
    </style>
    <script>
        function toggleGenerationForm() {
            var form = document.getElementById('generation-form');
            if (form.style.display === 'block') {
                form.style.display = 'none';
            } else {
                form.style.display = 'block';
            }
        }
    </script>
</head>
<body>
    <div class="container">
        <div class="logo">Matcha</div>
        <h1>Adaptation Complete!</h1>
        
        <div class="success-message">
            <p>Your PowerPoint has been successfully adapted for
               <span>
                   <div class="color-sample profile-color"></div>
                   {% if profile == "dyslexia" %}Dyslexia Support
                   {% elif profile == "adhd" %}ADHD Support
                   {% else %}English Language Learners{% endif %}
               </span>
            </p>
        </div>
        
        <div class="adaptation-info">
            {% if profile == "dyslexia" %}
            <h3>Dyslexia Support Adaptations</h3>
            <p>Your presentation has been adapted following research-based guidelines for dyslexia support:</p>
            <ul>
                <li>Text has been simplified with shorter sentences and clearer vocabulary</li>
                <li>Formatting has been adjusted for better readability</li>
                <li>The first word of each adapted paragraph is highlighted in blue</li>
                <li>Content is left-aligned with increased spacing where possible</li>
            </ul>
            {% elif profile == "adhd" %}
            <h3>ADHD Support Adaptations</h3>
            <p>Your presentation has been adapted with ADHD-friendly features:</p>
            <ul>
                <li>Content is structured with bullet points and clear organization</li>
                <li>Long paragraphs have been broken into manageable chunks</li>
                <li>The first word of each adapted paragraph is highlighted in green</li>
                <li>Information is presented in a more focused way</li>
            </ul>
            {% else %}
            <h3>English Language Learner Adaptations</h3>
            <p>Your presentation has been adapted for English language learners:</p>
            <ul>
                <li>Complex vocabulary has been simplified with original terms in parentheses</li>
                <li>Long sentences have been divided for easier comprehension</li>
                <li>The first word of each adapted paragraph is highlighted in purple</li>
                <li>Idiomatic expressions are explained or replaced</li>
            </ul>
            {% endif %}
        </div>
        
        {% if has_translation %}
        <div class="translation-info">
            <h3>{{ translated_language }} Version Available</h3>
            <p>A translated version of your presentation is also available in {{ translated_language }}:</p>
            <ul>
                <li>Contains a direct translation of the original presentation content to {{ translated_language }}</li>
                <li>Maintains the same slide structure as the English version for easy reference</li>
                <li>Technical terms are preserved in their original form with translations</li>
                <li>Perfect for bilingual classrooms or students transitioning between languages</li>
            </ul>
            <p><strong>Pro tip:</strong> Use both presentations side by side for bilingual learning support.</p>
        </div>
        {% endif %}
        
        <a href="/download_file/{{ file_id }}/{{ filename }}" class="btn">Download Adapted PowerPoint (English)</a>
        {% if has_translation %}
        <a href="/download_file/{{ file_id }}/{{ translated_filename }}" class="btn translated-btn">Download {{ translated_language }} Version</a>
        {% endif %}
        <a href="/" class="btn home-btn">Back to Home</a>
        <button onclick="toggleGenerationForm()" class="btn generate-btn">Enrich & Generate New</button>
        
        <div id="generation-form" class="generation-form">
            <h3>Create an Enhanced Presentation</h3>
            <p>Generate a brand new presentation based on the content in your adapted file, with additional learning resources and engaging visuals.</p>
            
            <form action="/enrich_and_generate" method="POST">
                <input type="hidden" name="original_file_id" value="{{ file_id }}">
                <input type="hidden" name="profile" value="{{ profile }}">
                
                <div class="form-group">
                    <label for="lesson_topic">Presentation Topic:</label>
                    <input type="text" id="lesson_topic" name="lesson_topic" placeholder="e.g., Photosynthesis, World War II" required>
                </div>
                
                <div class="form-group">
                    <label for="subject_area">Subject Area:</label>
                    <select id="subject_area" name="subject_area" required>
                        <option value="english">English</option>
                        <option value="maths">Mathematics</option>
                        <option value="science">Science (General)</option>
                        <option value="biology">Biology</option>
                        <option value="chemistry">Chemistry</option>
                        <option value="physics">Physics</option>
                        <option value="history">History</option>
                        <option value="geography">Geography</option>
                        <option value="religious_studies">Religious Studies</option>
                        <option value="modern_languages">Modern Foreign Languages</option>
                        <option value="computing">Computing</option>
                        <option value="design_technology">Design & Technology</option>
                        <option value="art_design">Art & Design</option>
                        <option value="music">Music</option>
                        <option value="physical_education">Physical Education</option>
                        <option value="citizenship">Citizenship</option>
                        <option value="pshe">PSHE (Personal, Social, Health & Economic)</option>
                        <option value="business">Business Studies</option>
                        <option value="sociology">Sociology</option>
                        <option value="psychology">Psychology</option>
                        <option value="economics">Economics</option>
                        <option value="media_studies">Media Studies</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="grade_level">Education Level:</label>
                    <select id="grade_level" name="grade_level" required>
                        <option value="ks3-year7-8">Key Stage 3 (Year 7-8)</option>
                        <option value="ks3-year9">Key Stage 3 (Year 9)</option>
                        <option value="ks4-gcse">Key Stage 4 (GCSE, Year 10-11)</option>
                        <option value="ks5-alevel">Key Stage 5 (A-Level, Year 12-13)</option>
                        <option value="btec">BTEC</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="slide_count">Number of Slides:</label>
                    <input type="number" id="slide_count" name="slide_count" min="5" max="20" value="10" required>
                </div>
                
                <div class="form-group checkbox-container">
                    <input type="checkbox" id="include_images" name="include_images" checked>
                    <label for="include_images">Include Generated Images</label>
                </div>
                
                <div class="form-group">
                    <label for="extra_notes">Additional Instructions (optional):</label>
                    <textarea id="extra_notes" name="extra_notes" rows="3" placeholder="Any specific content or structure requests"></textarea>
                </div>
                
                <button type="submit" class="btn">Generate Enhanced Presentation</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

DOWNLOAD_TEMPLATE_WITH_PDF = """
<!DOCTYPE html>
<html>
<head>
    <title>Download Adapted File</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; text-align: center; }
        .btn { background: #4CAF50; color: white; text-decoration: none; padding: 10px 15px; display: inline-block; margin-top: 20px; border: none; cursor: pointer; border-radius: 4px; }
        .home-btn { background: #3498db; margin-left: 10px; }
        .generate-btn { background: #9b59b6; margin-left: 10px; }
        .translated-btn { background: #e74c3c; margin-top: 10px; }
        .pdf-btn { background: #f39c12; margin-top: 10px; }
        .color-sample { display: inline-block; width: 20px; height: 20px; margin-right: 5px; vertical-align: middle; border: 1px solid #ccc; }
        .profile-color {
            background-color: {% if profile == "dyslexia" %}#0066cc{% elif profile == "adhd" %}#2e8b57{% else %}#9400d3{% endif %};
        }
        .adaptation-info { text-align: left; margin: 20px auto; max-width: 600px; padding: 15px; background-color: #f5f5f5; border-radius: 5px; }
        .success-message { margin: 20px 0; padding: 15px; background-color: #d4edda; border-left: 5px solid #28a745; text-align: left; }
        .logo { font-size: 24px; color: #4CAF50; margin-bottom: 10px; font-weight: bold; }
        .translation-info { margin-top: 20px; padding: 15px; background-color: #fff3cd; border-left: 5px solid #ffc107; text-align: left; display: {% if has_translation %}block{% else %}none{% endif %}; }
        .pdf-info { margin-top: 20px; padding: 15px; background-color: #d1ecf1; border-left: 5px solid #17a2b8; text-align: left; display: {% if has_pdf %}block{% else %}none{% endif %}; }
        .generation-form { display: none; margin-top: 20px; text-align: left; padding: 20px; background-color: #f0f4f8; border-radius: 5px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; }
        select, input[type="text"], input[type="number"], textarea { width: 100%; padding: 8px; }
        .checkbox-container { display: flex; align-items: center; }
        .checkbox-container input[type="checkbox"] { width: auto; margin-right: 8px; }
        .download-options { display: flex; flex-direction: column; align-items: center; }
        .download-row { margin-bottom: 10px; }
    </style>
    <script>
        function toggleGenerationForm() {
            var form = document.getElementById('generation-form');
            if (form.style.display === 'block') {
                form.style.display = 'none';
            } else {
                form.style.display = 'block';
            }
        }
    </script>
</head>
<body>
    <div class="container">
        <div class="logo">Matcha</div>
        <h1>Adaptation Complete!</h1>
        
        <div class="success-message">
            <p>Your PowerPoint has been successfully adapted for
               <span>
                   <div class="color-sample profile-color"></div>
                   {% if profile == "dyslexia" %}Dyslexia Support
                   {% elif profile == "adhd" %}ADHD Support
                   {% else %}English Language Learners{% endif %}
               </span>
            </p>
        </div>
        
        <div class="adaptation-info">
            {% if profile == "dyslexia" %}
            <h3>Dyslexia Support Adaptations</h3>
            <p>Your presentation has been adapted following research-based guidelines for dyslexia support:</p>
            <ul>
                <li>Text has been simplified with shorter sentences and clearer vocabulary</li>
                <li>Formatting has been adjusted for better readability</li>
                <li>The first word of each adapted paragraph is highlighted in blue</li>
                <li>Content is left-aligned with increased spacing where possible</li>
            </ul>
            {% elif profile == "adhd" %}
            <h3>ADHD Support Adaptations</h3>
            <p>Your presentation has been adapted with ADHD-friendly features:</p>
            <ul>
                <li>Content is structured with bullet points and clear organization</li>
                <li>Long paragraphs have been broken into manageable chunks</li>
                <li>The first word of each adapted paragraph is highlighted in green</li>
                <li>Information is presented in a more focused way</li>
            </ul>
            {% else %}
            <h3>English Language Learner Adaptations</h3>
            <p>Your presentation has been adapted for English language learners:</p>
            <ul>
                <li>Complex vocabulary has been simplified with original terms in parentheses</li>
                <li>Long sentences have been divided for easier comprehension</li>
                <li>The first word of each adapted paragraph is highlighted in purple</li>
                <li>Idiomatic expressions are explained or replaced</li>
            </ul>
            {% endif %}
        </div>
        
        {% if has_translation %}
        <div class="translation-info">
            <h3>{{ translated_language }} Version Available</h3>
            <p>A translated version of your presentation is also available in {{ translated_language }}:</p>
            <ul>
                <li>Contains a direct translation of the original presentation content to {{ translated_language }}</li>
                <li>Maintains the same slide structure as the English version for easy reference</li>
                <li>Technical terms are preserved in their original form with translations</li>
                <li>Perfect for bilingual classrooms or students transitioning between languages</li>
            </ul>
            <p><strong>Pro tip:</strong> Use both presentations side by side for bilingual learning support.</p>
        </div>
        {% endif %}
        
        {% if has_pdf %}
        <div class="pdf-info">
            <h3>PDF Version Available</h3>
            <p>A PDF version of your adapted presentation is available:</p>
            <ul>
                <li>Ensures consistent formatting and layout across different devices and platforms</li>
                <li>Better handles text reflow for varying text lengths after adaptation</li>
                <li>Enhanced compatibility for screen readers and accessibility tools</li>
                <li>Ideal for printing or distributing to students</li>
            </ul>
            <p><strong>Pro tip:</strong> PDF version works best when you need consistent formatting or want to distribute to students who may not have PowerPoint.</p>
        </div>
        {% endif %}
        
        <div class="download-options">
            <div class="download-row">
                <a href="/download_file/{{ file_id }}/{{ filename }}" class="btn">Download Adapted PowerPoint</a>
                {% if has_pdf %}
                <a href="/download_file/{{ file_id }}/{{ pdf_filename }}" class="btn pdf-btn">Download PDF Version</a>
                {% endif %}
            </div>
            
            {% if has_translation %}
            <div class="download-row">
                <a href="/download_file/{{ file_id }}/{{ translated_filename }}" class="btn translated-btn">Download {{ translated_language }} Version</a>
                <!-- Could add PDF for translated version here too if implemented -->
            </div>
            {% endif %}
            
            <div class="download-row">
                <a href="/" class="btn home-btn">Back to Home</a>
                <button onclick="toggleGenerationForm()" class="btn generate-btn">Enrich & Generate New</button>
            </div>
        </div>
        
        <!-- Generation form remains the same -->
        <div id="generation-form" class="generation-form">
            <!-- Form content (same as before) -->
        </div>
    </div>
</body>
</html>
"""
DOWNLOAD_TEMPLATE_UNIVERSAL = """
<!DOCTYPE html>
<html>
<head>
    <title>Download Adapted File</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; text-align: center; }
        .btn { 
            background: #4CAF50; 
            color: white; 
            text-decoration: none; 
            padding: 12px 20px; 
            display: inline-block; 
            margin: 8px 5px; 
            border: none; 
            cursor: pointer; 
            border-radius: 6px; 
            font-size: 16px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
        .btn-primary { background: #4CAF50; }
        .btn-pdf { background: #e74c3c; }
        .btn-pptx { background: #3498db; }
        .btn-secondary { background: #95a5a6; }
        .btn-home { background: #9b59b6; }
        
        .download-section {
            margin: 30px 0;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .format-icon {
            font-size: 48px;
            margin-bottom: 10px;
        }
        
        .download-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .download-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .download-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .success-message { 
            margin: 20px 0; 
            padding: 20px; 
            background-color: #d4edda; 
            border-left: 5px solid #28a745; 
            text-align: left;
            border-radius: 5px;
        }
        
        .logo { font-size: 32px; color: #4CAF50; margin-bottom: 20px; font-weight: bold; }
        
        .profile-badge {
            display: inline-block;
            padding: 5px 15px;
            background: #f0f0f0;
            border-radius: 20px;
            font-weight: 500;
            margin: 10px 0;
        }
        
        .profile-dyslexia { background: #e3f2fd; color: #0066cc; }
        .profile-adhd { background: #e8f5e9; color: #2e8b57; }
        .profile-esl { background: #f3e5f5; color: #9400d3; }
        
        .file-info {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            text-align: left;
        }
        
        .action-buttons {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #eee;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">Matcha</div>
        <h1>✅ Adaptation Complete!</h1>
        
        <div class="success-message">
            <h3 style="margin-top: 0;">Your content has been successfully adapted!</h3>
            <p>Profile: <span class="profile-badge profile-{{ profile }}">{{ profile_name }}</span></p>
            <p>Original file: <strong>{{ filename }}</strong></p>
        </div>
        
        <div class="download-section">
            <h2>📥 Download Your Adapted Files</h2>
            
            <div class="download-grid">
                {% if pdf_available or export_format == 'pdf' %}
                <div class="download-card">
                    <div class="format-icon">📄</div>
                    <h3>PDF Version</h3>
                    <p>Best for printing and consistent formatting across all devices</p>
                    <a href="/download_file/{{ file_id }}/{{ filename.replace('.pptx', '.pdf') }}" 
                       class="btn btn-pdf">
                        Download PDF
                    </a>
                </div>
                {% endif %}
                
                {% if pptx_available or export_format == 'pptx' %}
                <div class="download-card">
                    <div class="format-icon">📊</div>
                    <h3>PowerPoint Version</h3>
                    <p>Editable presentation format for further customization</p>
                    <a href="/download_file/{{ file_id }}/{{ filename.replace('.pdf', '.pptx') }}" 
                       class="btn btn-pptx">
                        Download PPTX
                    </a>
                </div>
                {% endif %}
            </div>
            
            {% if not pdf_available and not pptx_available %}
            <div class="download-card">
                <p>Looking for your files... If they don't appear, try refreshing the page.</p>
                <a href="/download_file/{{ file_id }}/{{ filename }}" class="btn btn-primary">
                    Download Adapted File
                </a>
            </div>
            {% endif %}
        </div>
        
        <div class="file-info">
            <h3>📋 Adaptation Details</h3>
            <ul style="text-align: left; display: inline-block;">
                <li>Original format: <strong>{{ 'PDF' if original_format == 'pdf' else 'PowerPoint' }}</strong></li>
                <li>Adaptation profile: <strong>{{ profile_name }}</strong></li>
                <li>Export format: <strong>{{ export_format|upper if export_format else 'PDF' }}</strong></li>
                {% if has_translation %}
                <li>Translation: <strong>{{ translated_language }}</strong> version available</li>
                {% endif %}
            </ul>
        </div>
        
        {% if has_translation %}
        <div class="download-section" style="background: #fff3cd;">
            <h3>🌍 {{ translated_language }} Version</h3>
            <p>A translated version is also available:</p>
            <a href="/download_file/{{ file_id }}/{{ translated_filename }}" class="btn btn-primary">
                Download {{ translated_language }} Version
            </a>
        </div>
        {% endif %}
        
        <div class="action-buttons">
            <a href="/" class="btn btn-home">🏠 Start New Adaptation</a>
            <a href="/generate" class="btn btn-secondary">✨ Create New Presentation</a>
        </div>
    </div>
</body>
</html>
"""
ERROR_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Error</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; text-align: center; }
        .error { color: #e74c3c; }
        .error-box { background-color: #f8d7da; padding: 15px; text-align: left; border-left: 5px solid #e74c3c; margin: 20px 0; }
        .btn { background: #3498db; color: white; text-decoration: none; padding: 10px 15px; display: inline-block; margin-top: 20px; }
        .logo { font-size: 24px; color: #4CAF50; margin-bottom: 10px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">Matcha</div>
        <h1 class="error">Error</h1>
        
        <div class="error-box">
            <p>{{ message }}</p>
        </div>
        
        <a href="/" class="btn">Back to Home</a>
    </div>
</body>
</html>
"""