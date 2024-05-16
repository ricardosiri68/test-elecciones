FROM python:3.11

WORKDIR /app
COPY poetry.lock /app/poetry.lock
COPY pyproject.toml /app/pyproject.toml
RUN pip install poetry && poetry install

RUN mkdir /data
COPY ballot /app/ballot
COPY scripts /app/scripts
RUN chmod -R +x /app/scripts
