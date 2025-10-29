#!/bin/sh
echo "Running Alembic migrations..."
alembic upgrade head

echo "Main.py is loading..."
exec python -m app.main