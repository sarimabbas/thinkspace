release: python manage.py migrate --settings=thinkspace_api.settings.production
web: gunicorn thinkspace_api.wsgi --log-file -