"""
Enhanced Production Logging Configuration
"""
import os
import logging
import logging.handlers
import structlog
from typing import Dict, Any, Optional
from flask import Flask, request, g
from datetime import datetime, timezone


class ProductionLogger:
    """Production-ready logging configuration with structured logging"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.logger: Optional[structlog.BoundLogger] = None
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize logging for Flask application"""
        self.app = app
        self.configure_logging()
        self.setup_request_logging()
        self.setup_error_handlers()
    
    def configure_logging(self):
        """Configure structured logging with multiple handlers"""
        if not self.app or not hasattr(self.app, 'config'):
            raise RuntimeError("Flask app instance with config is required for logging configuration.")
        log_level = getattr(logging, self.app.config.get('LOG_LEVEL', 'INFO'))
        
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # Get structured logger
        self.logger = structlog.get_logger()
        
        # Configure Flask app logger
        app_logger = logging.getLogger('shipping_gui')
        app_logger.setLevel(log_level)
        
        # Remove default handlers
        app_logger.handlers.clear()
        # Con sole handler
        if self.app.config.get('LOG_TO_STDOUT', True):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            app_logger.addHandler(console_handler)
        # File handler with rotation
        log_file = self.app.config.get('LOG_FILE', '/app/logs/app.log')
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(log_level)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            app_logger.addHandler(file_handler)
        # Attach logger to app via extensions dict (Flask convention)
        if self.app is not None:
            if not hasattr(self.app, 'extensions'):
                self.app.extensions = {}
            self.app.extensions['production_logger'] = app_logger
            # Optionally attach as attribute for convenience
            setattr(self.app, '_production_logger', app_logger)
        
        # Configure external library loggers
        self._configure_external_loggers()
    
    def _configure_external_loggers(self):
        """Configure logging for external libraries"""
    def _configure_external_loggers(self):
        """Configure logging for external libraries"""
        # Reduce noise from external libraries
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        
        # API client loggers
        api_logger = logging.getLogger('api_client')
        api_logger.setLevel(logging.INFO)
        if self.app and hasattr(self.app, 'logger') and getattr(self.app.logger, 'handlers', None):
            if self.app.logger.handlers:
                api_logger.addHandler(self.app.logger.handlers[0])
            else:
                api_logger.addHandler(logging.NullHandler())
        else:
            api_logger.addHandler(logging.NullHandler())

    def setup_request_logging(self):
        """Set up request/response logging middleware"""

        @self.app.before_request  # type: ignore
        def before_request():
            g.start_time = datetime.now(timezone.utc)
            g.request_id = self._generate_request_id()

            # Log incoming request
            if self.logger:
                self.logger.info(
                    "request_started",
                    request_id=g.request_id,
                    method=request.method,
                    path=request.path,
                    remote_addr=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', ''),
                    content_length=request.content_length
                )

        @self.app.after_request  # type: ignore
        def after_request(response):
            if hasattr(g, 'start_time'):
                duration = (datetime.now(timezone.utc) - g.start_time).total_seconds()

                # Log response
                if self.logger:
                    self.logger.info(
                        "request_completed",
                        request_id=getattr(g, 'request_id', 'unknown'),
                        method=request.method,
                        duration=duration
                    )

    def setup_error_handlers(self):
        """Set up comprehensive error handlers with reduced cognitive complexity"""

        self.app.register_error_handler(400, self._bad_request)
        self.app.register_error_handler(401, self._unauthorized)
        self.app.register_error_handler(403, self._forbidden)
        self.app.register_error_handler(404, self._not_found)
        self.app.register_error_handler(429, self._rate_limit_exceeded)
        self.app.register_error_handler(500, self._internal_error)
        self.app.register_error_handler(Exception, self._handle_exception)
        self.app.errorhandler(400)(self._bad_request_handler)
        self.app.errorhandler(401)(self._unauthorized_handler)
        self.app.errorhandler(403)(self._forbidden_handler)
        self.app.errorhandler(404)(self._not_found_handler)
        self.app.errorhandler(429)(self._rate_limit_exceeded_handler)
        self.app.errorhandler(500)(self._internal_error_handler)
        self.app.errorhandler(Exception)(self._handle_exception_handler)

    def _bad_request(self, error):
        if self.logger:
            self.logger.error(
                "bad_request",
                request_id=getattr(g, 'request_id', 'unknown'),
                error=str(error),
                path=request.path,
                method=request.method
            )
        return {'error': 'Bad Request', 'message': str(error)}, 400

    def _unauthorized(self, error):
        if self.logger:
            self.logger.warning(
                "unauthorized_access",
                request_id=getattr(g, 'request_id', 'unknown'),
                path=request.path,
                method=request.method,
                remote_addr=request.remote_addr
            )
        return {'error': 'Unauthorized', 'message': 'Authentication required'}, 401

    def _forbidden(self, error):
        if self.logger:
            self.logger.warning(
                "forbidden_access",
                request_id=getattr(g, 'request_id', 'unknown'),
                path=request.path,
                method=request.method,
                remote_addr=request.remote_addr
            )
        return {'error': 'Forbidden', 'message': 'Access denied'}, 403

    def _not_found(self, error):
        if self.logger:
            self.logger.info(
                "not_found",
                request_id=getattr(g, 'request_id', 'unknown'),
                path=request.path,
                method=request.method
            )
        return {'error': 'Not Found', 'message': 'Resource not found'}, 404

    def _rate_limit_exceeded(self, error):
        if self.logger:
            self.logger.warning(
                "rate_limit_exceeded",
                request_id=getattr(g, 'request_id', 'unknown'),
                path=request.path,
                method=request.method,
                remote_addr=request.remote_addr
            )
        return {'error': 'Rate limit exceeded', 'message': 'Too many requests'}, 429

    def _internal_error(self, error):
        if self.logger:
            self.logger.error(
                "internal_server_error",
                request_id=getattr(g, 'request_id', 'unknown'),
                error=str(error),
                path=request.path,
                method=request.method,
                exc_info=True
            )
        return {'error': 'Internal Server Error', 'message': 'An unexpected error occurred'}, 500

    def _handle_exception(self, error):
        """Handle unexpected exceptions"""
        if self.logger:
            self.logger.error(
                "unhandled_exception",
                request_id=getattr(g, 'request_id', 'unknown'),
                error_type=type(error).__name__,
                error_message=str(error),
                path=request.path,
                method=request.method,
                exc_info=True
            )
        # Return generic error in production
        if self.app and hasattr(self.app, 'config') and self.app.config.get('FLASK_ENV') == 'production':
            return {'error': 'Internal Server Error', 'message': 'An unexpected error occurred'}, 500
        else:
            return {'error': str(error), 'type': type(error).__name__}, 500
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def log_api_call(self, api_name: str, endpoint: str, method: str, status_code: int, 
                     duration: float, request_data: Optional[Dict[str, Any]] = None, 
                     response_data: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        """Log API calls with structured data"""
        if not self.logger:
            return
            
        log_data = {
            "event": "api_call",
            "api_name": api_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "duration_seconds": duration,
            "request_id": getattr(g, 'request_id', 'unknown')
        }
        
        if request_data:
            log_data["request_data"] = self._sanitize_data(request_data)
        
        if response_data:
            log_data["response_data"] = self._sanitize_data(response_data)
        
        if error:
            log_data["error"] = error
            self.logger.error("api_call_failed", **log_data)
        else:
            self.logger.info("api_call_success", **log_data)
    
    def log_business_event(self, event_type: str, **kwargs):
        """Log business events (orders, shipments, etc.)"""
        if self.logger:
            self.logger.info(
                "business_event",
                event_type=event_type,
                request_id=getattr(g, 'request_id', 'unknown'),
                **kwargs
            )
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from logs"""
        sensitive_keys = ['password', 'token', 'api_key', 'secret', 'authorization']
        
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = '***REDACTED***'
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value)
            else:
                sanitized[key] = value
        
        return sanitized


def setup_logging(app: Flask) -> ProductionLogger:
    """Initialize production logging for Flask application"""
    return ProductionLogger(app)