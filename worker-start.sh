#!/bin/bash

set -o errexit
set -o nounset

celery -A configs worker --loglevel=info