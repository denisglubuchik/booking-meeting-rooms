#!/bin/sh
set -e
cd /code
uv run alembic upgrade head

cd /code/src
uv run python -m worker.main
