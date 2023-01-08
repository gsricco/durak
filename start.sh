#!/bin/bash

#set -o errexit
#set -o pipefail
#set -o nounset

#
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
#daphne -b 0.0.0.0 -p 8000 configs.asgi:application
#python -m uvicorn configs.asgi:application