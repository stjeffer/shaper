FROM python:3.11-slim-bookworm AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN python -m pip install --no-cache-dir uv==0.8.11

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --frozen --no-dev

FROM python:3.11-slim-bookworm AS runtime

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    SHAPER_DATABASE_PATH=/mnt/state/shaper.db \
    SHAPER_RELEASE_ROOT=/mnt/state/publication \
    SHAPER_UPLOAD_ROOT=/mnt/state/uploads

RUN groupadd --gid 10001 shaper \
    && useradd --uid 10001 --gid shaper --create-home shaper \
    && mkdir -p /app /mnt/state/publication /mnt/state/uploads \
    && chown -R shaper:shaper /app /mnt/state

WORKDIR /app
COPY --from=builder --chown=shaper:shaper /app/.venv ./.venv
COPY --from=builder --chown=shaper:shaper /app/src ./src
COPY --chown=shaper:shaper prototype/copilot-studio-knowledge-compiler ./prototype/copilot-studio-knowledge-compiler

USER 10001:10001
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=3)"]

ENTRYPOINT ["shaper"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
