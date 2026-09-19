FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    HOME=/tmp \
    UV_CACHE_DIR=/tmp/uv-cache

ARG TARGETARCH

RUN apt-get update \
    && apt-get install --no-install-recommends -y ca-certificates curl libavahi-client3 sane-utils sane-airscan \
    && if [ "$TARGETARCH" = "amd64" ]; then \
         curl -fsSL https://download.brother.com/welcome/dlf105200/brscan4-0.4.11-1.amd64.deb -o /tmp/brscan4.deb \
         && apt-get install --no-install-recommends -y /tmp/brscan4.deb \
         && rm -f /tmp/brscan4.deb; \
       fi \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.12.17 /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock* README.md ./
RUN uv sync --frozen --no-dev || uv sync --no-dev
COPY app.py ./
COPY templates ./templates

RUN mkdir -p /tmp/uv-cache && chmod 777 /tmp/uv-cache

EXPOSE 8080
USER 65532:65532
CMD ["/app/.venv/bin/gunicorn", "--bind", "0.0.0.0:8080", "--timeout", "0", "app:app"]
