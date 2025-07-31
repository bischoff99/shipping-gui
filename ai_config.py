"""
AI Model Configuration for Enhanced Customer Input Parsing

This file contains configuration settings for the AI-powered parsing system,
including model selection, fallback options, and performance tuning parameters.
"""

import os
from typing import Dict, Any

# Primary NER model configuration
PRIMARY_NER_MODEL = "dbmdz/bert-large-cased-finetuned-conll03-english"

# Fallback models in case primary model fails
FALLBACK_NER_MODELS = [
    "dbmdz/bert-base-cased-finetuned-conll03-english",  # Smaller, faster
    "mdarhri00/named-entity-recognition",  # Alternative model
]

# Model loading configuration
MODEL_CONFIG = {
    "device": "auto",  # Will use GPU if available, CPU otherwise
    "max_length": 512,  # Maximum input length for tokenization
    "aggregation_strategy": "simple",  # How to aggregate sub-word tokens
    "use_auth_token": os.getenv("HUGGINGFACE_TOKEN"),  # Optional: for private models
}

# Performance settings
PERFORMANCE_CONFIG = {
    "enable_caching": True,  # Cache model instances
    "batch_size": 1,  # Batch size for inference
    "max_workers": 1,  # Number of worker threads
    "timeout_seconds": 30,  # Model loading timeout
}

# Parsing thresholds
PARSING_THRESHOLDS = {
    "min_confidence": 0.6,  # Minimum confidence to use AI results
    "min_entity_score": 0.3,  # Minimum score for individual entities
    "fallback_to_traditional": True,  # Whether to fallback to traditional parsing
}

# Entity type mappings (model-specific)
ENTITY_MAPPINGS = {
    "PER": "PERSON",
    "LOC": "LOCATION", 
    "MISC": "MISCELLANEOUS",
    "ORG": "ORGANIZATION",
}

# Country-specific configurations
COUNTRY_CONFIGS = {
    "US": {
        "phone_patterns": [
            r'\+?1?[-\s]?\(?([0-9]{3})\)?[-\s]?([0-9]{3})[-\s]?([0-9]{4})',
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        ],
        "postal_pattern": r'\b\d{5}(?:-\d{4})?\b',
        "state_validation": True,
    },
    "CA": {
        "phone_patterns": [
            r'\+?1?[-\s]?\(?([0-9]{3})\)?[-\s]?([0-9]{3})[-\s]?([0-9]{4})',
        ],
        "postal_pattern": r'\b[A-Za-z]\d[A-Za-z]\s?\d[A-Za-z]\d\b',
        "state_validation": False,  # Uses provinces
    },
    "UK": {
        "phone_patterns": [
            r'\+?44[-\s]?\d{2,4}[-\s]?\d{3,4}[-\s]?\d{3,4}',
            r'\b0\d{2,4}[-\s]?\d{3,4}[-\s]?\d{3,4}\b',
        ],
        "postal_pattern": r'\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b',
        "state_validation": False,
    },
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_ai_entities": False,  # Whether to log detected entities (privacy consideration)
}

def get_model_config() -> Dict[str, Any]:
    """Get the current model configuration"""
    return MODEL_CONFIG.copy()

def get_parsing_config() -> Dict[str, Any]:
    """Get the current parsing configuration"""
    return {
        "primary_model": PRIMARY_NER_MODEL,
        "fallback_models": FALLBACK_NER_MODELS,
        "thresholds": PARSING_THRESHOLDS,
        "performance": PERFORMANCE_CONFIG,
    }

def get_country_config(country_code: str) -> Dict[str, Any]:
    """Get country-specific configuration"""
    return COUNTRY_CONFIGS.get(country_code.upper(), COUNTRY_CONFIGS["US"])

# Environment-based overrides
def apply_environment_overrides():
    """Apply configuration overrides from environment variables"""
    global PRIMARY_NER_MODEL, MODEL_CONFIG, PARSING_THRESHOLDS
    
    # Allow model override via environment
    if os.getenv("AI_PARSER_MODEL"):
        PRIMARY_NER_MODEL = os.getenv("AI_PARSER_MODEL")
    
    # Allow confidence threshold override
    if os.getenv("AI_PARSER_MIN_CONFIDENCE"):
        try:
            PARSING_THRESHOLDS["min_confidence"] = float(os.getenv("AI_PARSER_MIN_CONFIDENCE"))
        except ValueError:
            pass
    
    # Force CPU-only mode if specified
    if os.getenv("AI_PARSER_CPU_ONLY") == "1":
        MODEL_CONFIG["device"] = -1  # Force CPU in transformers pipeline

# Apply overrides on import
apply_environment_overrides()