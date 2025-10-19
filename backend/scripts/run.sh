#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

python manage.py wait_for_db || exit 1
python manage.py migrate --no-input || exit 1
exec python manage.py runserver 0.0.0.0:8000