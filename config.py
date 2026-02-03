import os
from urllib.parse import urlparse

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    TYPING_PASSAGES_FOLDER = os.environ.get('TYPING_PASSAGES_FOLDER', 'typing_passages')
    ALLOWED_EXTENSIONS = {'mp3', 'wav', 'txt'}
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    
    # Admin contact configuration
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'suyogsudrik1996@gmail.com')
    ADMIN_PHONE = os.environ.get('ADMIN_PHONE', '+917756094286')
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///dictation_app.db'

class ProductionConfig(Config):
    """Production configuration for Hostinger deployment."""
    DEBUG = False
    TESTING = False
    
    # Database configuration for production
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Handle different database URL formats
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        elif database_url.startswith('mysql://'):
            database_url = database_url.replace('mysql://', 'mysql+pymysql://', 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Fallback to SQLite for simple deployment
        SQLALCHEMY_DATABASE_URI = os.environ.get('SQLITE_URL', 'sqlite:///production.db')
    
    # Enhanced security settings
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # Extended session lifetime to prevent mid-practice logouts (8 hours)
    PERMANENT_SESSION_LIFETIME = 28800  # 8 hours (28800 seconds)
    
    # File upload security
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 52428800))  # 50MB
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')
    
    # Performance settings - SQLite compatible
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300
    }

class TestConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestConfig,
    'default': DevelopmentConfig
}
