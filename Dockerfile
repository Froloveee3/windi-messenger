FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc libpq-dev postgresql-client curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY ./alembic.ini ./alembic.ini
COPY ./alembic ./alembic
COPY ./tests ./tests
COPY ./.env ./.env

RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser


EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD python -c "import sys, urllib.request; \
    urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health/').read() or sys.exit(1)" || exit 1

ENTRYPOINT ["bash", "-c", "\
    alembic upgrade head && \
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000\
    "]
