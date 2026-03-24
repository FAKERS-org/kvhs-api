# STAGE 1: The Build Environment
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

# Enable Bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1
# Use 'copy' mode so we don't rely on hardlinks (which fail in some Docker drivers)
ENV UV_LINK_MODE=copy

WORKDIR /app

# Cache the uv cache specifically. 
# We bind 'uv.lock' and 'pyproject.toml' so uv can resolve the environment 
# WITHOUT actually copying the files into the layer yet.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# STAGE 2: The Runtime Environment (The "Production" Image)
FROM python:3.13-slim-bookworm

# Copy ONLY the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv

# Place the venv at the front of the PATH so 'python' and 'uvicorn' work globally
ENV PATH="/app/.venv/bin:$PATH"

# Crucial for FastAPI logs to show up in Docker logs immediately
ENV PYTHONUNBUFFERED=1

# Set the package root (where 'app' is located) to PYTHONPATH
ENV PYTHONPATH="/app/src"

WORKDIR /app

# Copy your source code (the 'src' directory)
COPY ./src /app/src

# Execute using the module path. 
# Since 'src' is in PYTHONPATH, and we have 'app/main.py', the module is 'app.main'
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
