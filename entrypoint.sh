#!/bin/sh

# Wait for the PostgreSQL database to be ready
echo "Waiting for postgres..."
/wait-for-it.sh db:5432 --timeout=30 --strict -- echo "Postgres is up"

#Run Make Migrations
echo "Running Django migrations..."
python manage.py makemigrations

# Run migrations
echo "Applying migrations..."
python manage.py migrate

# Collect static files (optional for production)
# python manage.py collectstatic --noinput

# Start the server
echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000
exec "$@"