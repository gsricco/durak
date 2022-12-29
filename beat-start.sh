#!/bin/bash

set -o errexit
set -o nounset

rm -f './celerybeat.pid'
celery -A configs beat -l INFO  --scheduler django_celery_beat.schedulers:DatabaseScheduler