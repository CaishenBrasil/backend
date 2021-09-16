FROM antonapetrov/uvicorn-gunicorn:python3.9

RUN apt-get update && apt-get install -y netcat

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock* /
RUN poetry install --no-root --no-dev

COPY . .
