#!/bin/sh
python3 manage.py makemigrations --settings=config.settings.develop
python3 manage.py migrate --run-syncdb --settings=config.settings.develop
python3 manage.py runserver --settings=config.settings.develop 0.0.0.0:8000
