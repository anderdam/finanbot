FROM python:3.11-slim

WORKDIR /usr/src/app
COPY ./pyproject.toml ./poetry.lock* ./
RUN apt-get update && apt-get install -y build-essential libpq-dev --no-install-recommends && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-root

COPY ./app ./app
COPY ./ui ./ui
COPY ./attachments ./attachments

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
