"""
Enhanced Configuration Management
Addresses security concerns and provides environment-specific settings
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration class"""

    # Flask Core Settings
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is required")

    # API Keys (with validation)
    VEEQO_API_KEY = os.environ.get("VEEQO_API_KEY")
    EASYSHIP_API_KEY = os.environ.get("EASYSHIP_API_KEY")

    if not VEEQO_API_KEY:
        raise ValueError("VEEQO_API_KEY environment variable is required")
    if not EASYSHIP_API_KEY:
        raise ValueError("EASYSHIP_API_KEY environment variable is required")

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///shipping_automation.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # Redis Configuration (for caching and rate limiting)
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # Security Settings
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.environ.get("JWT_ACCESS_TOKEN_HOURS", 1))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.environ.get("JWT_REFRESH_TOKEN_DAYS", 30))
    )

    # CORS Settings
    CORS_ORIGINS = (
        os.environ.get("CORS_ORIGINS", "").split(",")
        if os.environ.get("CORS_ORIGINS")
        else ["*"]
    )

    # Rate Limiting
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = os.environ.get("RATELIMIT_DEFAULT", "1000 per hour")

    # API Settings
    API_TITLE = "Shipping Automation API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"

    # Background Task Settings
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", REDIS_URL)

    # Auto-sync Settings
    AUTO_SYNC_ENABLED = os.environ.get("AUTO_SYNC_ENABLED", "false").lower() == "true"
    AUTO_SYNC_INTERVAL = int(os.environ.get("AUTO_SYNC_INTERVAL", 300))  # 5 minutes

    # Inventory Monitoring
    INVENTORY_MONITORING_ENABLED = (
        os.environ.get("INVENTORY_MONITORING_ENABLED", "true").lower() == "true"
    )
    INVENTORY_CHECK_INTERVAL = int(
        os.environ.get("INVENTORY_CHECK_INTERVAL", 60)
    )  # 1 minute
    LOW_STOCK_THRESHOLD = int(os.environ.get("LOW_STOCK_THRESHOLD", 10))

    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FILE = os.environ.get("LOG_FILE", "logs/app.log")

    # External API Settings
    API_REQUEST_TIMEOUT = int(os.environ.get("API_REQUEST_TIMEOUT", 30))
    API_MAX_RETRIES = int(os.environ.get("API_MAX_RETRIES", 3))
    API_RETRY_DELAY = int(os.environ.get("API_RETRY_DELAY", 2))

    # File Upload Settings
    MAX_CONTENT_LENGTH = int(
        os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024)
    )  # 16MB
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")

    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    TESTING = False

    # More verbose logging in development
    LOG_LEVEL = "DEBUG"

    # Relaxed rate limiting for development
    RATELIMIT_DEFAULT = "10000 per hour"

    # Enable auto-sync in development
    AUTO_SYNC_ENABLED = True
    AUTO_SYNC_INTERVAL = 60  # 1 minute for faster testing

    @staticmethod
    def init_app(app):
        Config.init_app(app)

        # Development-specific initialization
        app.logger.info("Development mode enabled")


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    TESTING = False

    # Strict security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Force HTTPS
    PREFERRED_URL_SCHEME = "https"

    # Production database settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 20,
        "max_overflow": 30,
    }

    @staticmethod
    def init_app(app):
        Config.init_app(app)

        # Production-specific initialization
        import logging
        from logging.handlers import SMTPHandler, SysLogHandler

        # Email error notifications
        if app.config.get("MAIL_SERVER"):
            auth = None
            if app.config.get("MAIL_USERNAME") or app.config.get("MAIL_PASSWORD"):
                auth = (
                    app.config.get("MAIL_USERNAME"),
                    app.config.get("MAIL_PASSWORD"),
                )
            secure = None
            if app.config.get("MAIL_USE_TLS"):
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(
                    app.config["MAIL_SERVER"],
                    app.config.get("MAIL_PORT", 587),
                ),
                fromaddr=app.config.get("MAIL_FROM_EMAIL"),
                toaddrs=app.config.get("ADMINS", []),
                subject="Shipping Automation Error",
                credentials=auth,
                secure=secure,
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        # Syslog for production logging
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    DEBUG = True

    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    # Disable background services during testing
    AUTO_SYNC_ENABLED = False
    INVENTORY_MONITORING_ENABLED = False

    # Use fake Redis for testing
    REDIS_URL = "redis://localhost:6379/15"  # Different DB for testing

    # Disable rate limiting for testing
    RATELIMIT_ENABLED = False

    # Fast JWT expiration for testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)

    @staticmethod
    def init_app(app):
        Config.init_app(app)

        # Testing-specific initialization
        app.logger.info("Testing mode enabled")


# Configuration mapping
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Get configuration based on environment"""
    env = os.environ.get("FLASK_ENV", "development")
    return config.get(env, config["default"])
