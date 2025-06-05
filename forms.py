"""
Flask-WTF forms for authentication and user input validation
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from flask_wtf.file import FileAllowed, FileRequired
from auth import User
from security_config import validate_email


class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=20, message='Username must be between 3 and 20 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=20, message='Username must be between 3 and 20 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

    def validate_username(self, username):
        """Check if username already exists"""
        user = User.get_user_by_username(username.data)
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        """Validate email format and uniqueness"""
        if not validate_email(email.data):
            raise ValidationError('Please enter a valid email address.')


class FileUploadForm(FlaskForm):
    """Secure file upload form"""
    file = FileField('Upload File', validators=[
        FileRequired(message='Please select a file'),
        FileAllowed(['pdf', 'pptx', 'ppt'], message='Only PDF and PowerPoint files are allowed')
    ])
    adaptation_type = SelectField('Adaptation Type', choices=[
        ('dyslexia', 'Dyslexia-Friendly'),
        ('adhd', 'ADHD Support'),
        ('esl', 'ESL (English as Second Language)'),
        ('general', 'General Accessibility')
    ], validators=[DataRequired()])
    submit = SubmitField('Upload and Process')


class ProfileForm(FlaskForm):
    """User profile editing form"""
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=20, message='Username must be between 3 and 20 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    submit = SubmitField('Update Profile')


class PasswordChangeForm(FlaskForm):
    """Password change form"""
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Current password is required')
    ])
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required'),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password'),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')


class FeedbackForm(FlaskForm):
    """User feedback form"""
    subject = StringField('Subject', validators=[
        DataRequired(message='Subject is required'),
        Length(max=100, message='Subject must be less than 100 characters')
    ])
    message = TextAreaField('Message', validators=[
        DataRequired(message='Message is required'),
        Length(max=1000, message='Message must be less than 1000 characters')
    ])
    submit = SubmitField('Send Feedback')