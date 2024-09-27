#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

cd /
alembic upgrade head
if [[ "${BUILD_ENV}" == "dev" ]] ; then
    echo "Initializing database data in ${BUILD_ENV}"
    python /usr/src/app/db/init_db.py
else
    echo "Skipping database intializiation in ${BUILD_ENV}"
fi
echo "Starting backend"
python /usr/src/app/main.py