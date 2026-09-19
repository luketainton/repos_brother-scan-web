FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    HOME=/tmp \
    UV_CACHE_DIR=/tmp/uv-cache

RUN apt-get update \
    && apt-get install --no-install-recommends -y sane-utils \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.8.14 /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock* README.md ./
RUN uv sync --frozen --no-dev || uv sync --no-dev
COPY app.py ./
COPY templates ./templates

RUN mkdir -p /tmp/uv-cache && chmod 777 /tmp/uv-cache

EXPOSE 8080
USER 65532:65532
CMD ["/app/.venv/bin/gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
