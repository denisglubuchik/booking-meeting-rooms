#!/bin/sh
set -e
cd /code
uv run alembic upgrade head

cd /code/src
uv run uvicorn api.main:app --host 0.0.0.0 --reload
