#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

python manage.py migrate
daphne -b 0.0.0.0 -p 8000 configs.asgi:application
