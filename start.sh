#!/bin/bash

# Make migrations
echo Making migrations.
python manage.py makemigrations

# Migrate
echo Starting migration.
python manage.py migrate

python manage.py runserver
