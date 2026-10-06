FROM python:3.13.15-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN useradd \
    --create-home \
    --user-group \
    --uid 10001 \
    appuser

COPY requirements.txt ./

RUN python -m pip install --upgrade pip \
    && python -m pip install --requirement requirements.txt

COPY --chown=appuser:appuser app/ /app/

USER appuser