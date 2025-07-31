import os
import secrets
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration with optimized settings"""

    SECRET_KEY = (
        os.environ.get("SECRET_KEY")
        or os.environ.get("FLASK_SECRET_KEY")
        or secrets.token_hex(32)
    )
    VEEQO_API_KEY = os.environ.get("VEEQO_API_KEY")
    EASYSHIP_API_KEY = os.environ.get("EASYSHIP_API_KEY")
    
    # Hugging Face Token for MCP AI integration
    HF_TOKEN = os.environ.get("HF_TOKEN")

    # Database Configuration - Optimized
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///instance/shipping_automation.db"
    )

    # MCP (Model Context Protocol) Configuration
    MCP_URL = os.environ.get("MCP_URL", "http://localhost:3000")
    MCP_DEBUG = os.environ.get("MCP_DEBUG", "false").lower() == "true"
    MCP_TIMEOUT = int(os.environ.get("MCP_TIMEOUT", "30"))
    MCP_TOOL_TIMEOUT = int(os.environ.get("MCP_TOOL_TIMEOUT", "60"))
    
    # MCP Server Settings
    MCP_PYTHON_DEBUG_ENABLED = os.environ.get("MCP_PYTHON_DEBUG_ENABLED", "true").lower() == "true"
    MCP_FILESYSTEM_ENABLED = os.environ.get("MCP_FILESYSTEM_ENABLED", "true").lower() == "true"
    MCP_GITHUB_ENABLED = os.environ.get("MCP_GITHUB_ENABLED", "true").lower() == "true"
    MCP_SEQUENTIAL_THINKING_ENABLED = os.environ.get("MCP_SEQUENTIAL_THINKING_ENABLED", "true").lower() == "true"
    MCP_HF_SPACES_ENABLED = os.environ.get("MCP_HF_SPACES_ENABLED", "true").lower() == "true"
    
    # API Configuration
    API_TIMEOUT = int(os.environ.get("API_TIMEOUT", "30"))
    API_MAX_RETRIES = int(os.environ.get("API_MAX_RETRIES", "3"))
    API_BACKOFF_FACTOR = float(os.environ.get("API_BACKOFF_FACTOR", "0.3"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 3600,
        "pool_size": 10,
        "max_overflow": 20,
        "echo": False,
    }

    # Performance Settings
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False

    # Caching
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300

    # Rate Limiting
    RATELIMIT_STORAGE_URL = "memory://"


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        "echo": True,
    }


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

    # Use Redis for production caching
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")

    # Security headers
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Production database optimizations
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        "pool_size": 20,
        "max_overflow": 40,
    }


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
