#!/bin/bash

set -o errexit
set -o nounset
sleep 5
celery -A configs worker --loglevel=info