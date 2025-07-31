"""
Production Configuration with Environment Variables and Security
"""
import os
from typing import Optional


class ProductionConfig:
    """Production configuration with enhanced security and monitoring"""
    
    # Flask Core Settings
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'prod_secret_key_change_me'
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/shipping_gui')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0,
        'pool_size': 10
    }
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    
    # API Keys and External Services
    VEEQO_API_KEY = os.environ.get('VEEQO_API_KEY')
    VEEQO_API_URL = os.environ.get('VEEQO_API_URL', 'https://api.veeqo.com')
    
    EASYSHIP_API_KEY = os.environ.get('EASYSHIP_API_KEY')
    EASYSHIP_API_URL = os.environ.get('EASYSHIP_API_URL', 'https://api.easyship.com')
    
    HUGGINGFACE_TOKEN = os.environ.get('HF_TOKEN')
    
    # Security Settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_HEADERS_ENABLED = True
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT', 'true').lower() == 'true'
    LOG_FILE = os.environ.get('LOG_FILE', '/app/logs/app.log')
    
    # Monitoring and Health Checks
    HEALTH_CHECK_ENABLED = True
    METRICS_ENABLED = os.environ.get('METRICS_ENABLED', 'true').lower() == 'true'
    
    # Application Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/app/uploads')
    
    # External API Timeouts and Retries
    API_TIMEOUT = int(os.environ.get('API_TIMEOUT', '30'))
    API_MAX_RETRIES = int(os.environ.get('API_MAX_RETRIES', '3'))
    API_BACKOFF_FACTOR = float(os.environ.get('API_BACKOFF_FACTOR', '0.3'))
    
    # Celery Configuration
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'UTC'
    CELERY_ENABLE_UTC = True
    
    @staticmethod
    def validate_required_env_vars():
        """Validate that all required environment variables are set"""
        required_vars = [
            'FLASK_SECRET_KEY',
            'DATABASE_URL',
            'VEEQO_API_KEY',
            'EASYSHIP_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
    
    @classmethod
    def from_env(cls) -> 'ProductionConfig':
        """Create configuration from environment variables with validation"""
        cls.validate_required_env_vars()
        return cls()


class StagingConfig(ProductionConfig):
    """Staging configuration inheriting from production with debug enabled"""
    
    DEBUG = True
    TESTING = False
    FLASK_ENV = 'staging'
    
    # More lenient rate limiting for testing
    RATELIMIT_DEFAULT = "1000 per hour"
    
    # Shorter session timeout for testing
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes


class DevelopmentConfig:
    """Development configuration for local development"""
    
    DEBUG = True
    TESTING = False
    FLASK_ENV = 'development'
    
    # Local database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///shipping_gui_dev.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    
    # Local Redis
    REDIS_URL = 'redis://localhost:6379'
    
    # Development API keys (use test keys)
    VEEQO_API_KEY = os.environ.get('VEEQO_API_KEY', 'dev_key')
    EASYSHIP_API_KEY = os.environ.get('EASYSHIP_API_KEY', 'dev_key')
    
    # Disable security for development
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    
    # Generous rate limiting for development
    RATELIMIT_DEFAULT = "10000 per hour"
    
    LOG_LEVEL = 'DEBUG'
    LOG_TO_STDOUT = True


def get_config(env: Optional[str] = None) -> type:
    """Get configuration class based on environment"""
    env = env or os.environ.get('FLASK_ENV', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'staging': StagingConfig,
        'production': ProductionConfig
    }
    
    return config_map.get(env, DevelopmentConfig)