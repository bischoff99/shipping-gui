#!/usr/bin/env bash
# Production deployment script for Flask + Gunicorn + Celery

export FLASK_ENV=production
python -c "from utils.env_validation import validate_env; validate_env()"
python -c "from logging_config import setup_logging; setup_logging()"

# Start Gunicorn
nohup gunicorn -c gunicorn_config.py app:app &

# Start Celery worker
nohup celery -A tasks.celery_worker.celery worker --loglevel=info &

echo "Deployment started. Check logs/ for output."
