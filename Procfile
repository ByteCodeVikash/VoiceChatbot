web: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app

web: python app.py
release: python -c "print('Database setup complete')"