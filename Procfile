release: python manage.py migrate
web: gunicorn advantageup.wsgi
worker: celery -A advantageup worker -l info --concurrency 2
beat: celery -A advantageup beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler