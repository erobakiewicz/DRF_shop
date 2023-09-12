#!/bin/bash
set -e
if [ "$1" = "docker-compose" ] && [ "$2" = "up" ]; then
  if [ ! -f /data_loaded.flag ]; then
    python manage.py loaddata fixtures.json
    touch /data_loaded.flag
  fi
fi

exec "$@"
