FROM python:3.11

COPY ballot /app/ballot
COPY poetry.lock /app/poetry.lock
COPY pyproject.toml /app/pyproject.toml
COPY init.sh /app/init.sh

RUN mkdir /data

RUN chmod +x /app/init.sh

WORKDIR /app
RUN pip install poetry && poetry install
