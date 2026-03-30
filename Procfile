release: python manage.py migrate
web: gunicorn ventas_catalogos.wsgi:application --config gunicorn_config.py
