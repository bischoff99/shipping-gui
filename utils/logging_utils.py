"""
Optimized Logging and Error Handling Utilities
Centralized logging with performance monitoring
"""

import time
import traceback
from functools import wraps
from flask import request, g
import structlog

# Configure structured logging
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
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class PerformanceMonitor:
    """Performance monitoring and logging"""

    @staticmethod
    def log_performance(func_name, execution_time, **context):
        """Log performance metrics"""
        logger.info(
            "performance_metric",
            function=func_name,
            execution_time=execution_time,
            **context,
        )

        # Log slow operations
        if execution_time > 1.0:
            logger.warning(
                "slow_operation",
                function=func_name,
                execution_time=execution_time,
                **context,
            )


def monitor_performance(func):
    """Decorator for monitoring function performance"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            PerformanceMonitor.log_performance(
                func.__name__, execution_time, success=True
            )

            return result

        except Exception as e:
            execution_time = time.time() - start_time

            logger.error(
                "function_error",
                function=func.__name__,
                execution_time=execution_time,
                error=str(e),
                traceback=traceback.format_exc(),
            )

            raise

    return wrapper


def log_api_call(api_name, endpoint, response_time, status_code, **context):
    """Log API call metrics"""
    logger.info(
        "api_call",
        api=api_name,
        endpoint=endpoint,
        response_time=response_time,
        status_code=status_code,
        **context,
    )

    if response_time > 2.0:
        logger.warning(
            "slow_api_call",
            api=api_name,
            endpoint=endpoint,
            response_time=response_time,
            status_code=status_code,
        )


class ErrorHandler:
    """Centralized error handling"""

    @staticmethod
    def handle_api_error(api_name, error, context=None):
        """Handle API-related errors"""
        logger.error(
            "api_error",
            api=api_name,
            error=str(error),
            context=context or {},
            traceback=traceback.format_exc(),
        )

        return {
            "error": f"{api_name} API error",
            "message": str(error),
            "type": "api_error",
        }

    @staticmethod
    def handle_validation_error(validation_errors, context=None):
        """Handle validation errors"""
        logger.warning(
            "validation_error", errors=validation_errors, context=context or {}
        )

        return {
            "error": "Validation failed",
            "details": validation_errors,
            "type": "validation_error",
        }

    @staticmethod
    def handle_business_logic_error(error, context=None):
        """Handle business logic errors"""
        logger.error(
            "business_logic_error",
            error=str(error),
            context=context or {},
            traceback=traceback.format_exc(),
        )

        return {
            "error": "Business logic error",
            "message": str(error),
            "type": "business_error",
        }


def request_logging_middleware():
    """Middleware for request/response logging"""
    g.start_time = time.time()

    logger.info(
        "request_start",
        method=request.method,
        path=request.path,
        remote_addr=request.remote_addr,
        user_agent=request.headers.get("User-Agent", "Unknown"),
    )


def response_logging_middleware(response):
    """Log response metrics"""
    if hasattr(g, "start_time"):
        response_time = time.time() - g.start_time

        logger.info(
            "request_complete",
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            response_time=response_time,
        )

    return response
