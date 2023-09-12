#!/bin/bash
set -e

if [ ! -f /code/data_loaded ]; then
  python manage.py loaddata fixtures.json
  touch /code/data_loaded
fi

exec "$@"
