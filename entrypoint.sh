#!/bin/bash
set -e

if [ ! -f /data_loaded ]; then
  python manage.py loaddata fixtures.json
  touch /data_loaded
fi

exec "$@"
