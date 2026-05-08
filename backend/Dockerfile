FROM python:3.14

WORKDIR /code

COPY src ./src
COPY alembic.ini start.sh start-worker.sh pyproject.toml uv.lock ./

RUN pip install --root-user-action ignore uv
RUN uv sync --no-dev --compile-bytecode

RUN chmod +x start.sh start-worker.sh

EXPOSE 8000

CMD [ "/bin/bash", "start.sh" ]
