# Migration Guide: Flask Automation GUI Security & Production Enhancements

## 1. Install New Dependencies

```
pip install flask-wtf flask-limiter celery redis requests
```

## 2. Integrate Middleware and Utilities
- Import and register `register_error_handlers` from `middleware/error_handling.py` in your app factory or `app.py`.
- Initialize CSRF protection in your app using `init_csrf` from `middleware/csrf_protection.py`.
- Add rate limiting by calling `init_rate_limiter(app)` from `middleware/rate_limit.py`.
- Use `validate_env()` from `utils/env_validation.py` at startup.
- Protect sensitive endpoints with `@require_api_key` from `middleware/auth.py`.
- Use input validation functions from `utils/input_validation.py` in your API routes.
- Use `safe_api_call` from `utils/api_timeout.py` for all external API requests.

## 3. Set Up Celery for Async Tasks
- Start a Redis server for Celery broker and backend.
- Use `make_celery(app)` from `tasks/celery_worker.py` to integrate Celery with Flask.
- Start Celery worker: `celery -A tasks.celery_worker.celery worker --loglevel=info`

## 4. Configure Gunicorn for Production
- Use `gunicorn_config.py` for Gunicorn deployment: `gunicorn -c gunicorn_config.py app:app`

## 5. Enable Structured Logging
- Call `setup_logging()` from `logging_config.py` at app startup.
- Monitor logs in the `logs/` directory.

## 6. Environment Variables
- Ensure all required environment variables are set (see `utils/env_validation.py`).

## 7. Monitoring & Alerting
- Extend `logging_config.py` to add email or external alerting as needed.

---

For questions or help, see the code comments in each module.
