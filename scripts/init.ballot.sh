#!/usr/bin/env sh

poetry run python ballot/manage.py migrate
poetry run python ballot/manage.py runserver "0.0.0.0:80"
