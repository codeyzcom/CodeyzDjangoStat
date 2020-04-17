#!/bin/sh
set -e

python manage.py makemigrations --check --dry-run --noinput
echo "Migrations are OK"

# Run coverage
coverage erase

pytest cdzstat --cov=cdzstat --cov-branch --cov-fail-under=95 --cov-report xml --cov-report term-missing:skip-covered --flake8
