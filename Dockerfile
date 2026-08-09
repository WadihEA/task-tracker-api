# syntax=docker/dockerfile:1

# ---- Builder stage: install dependencies into an isolated virtualenv ----
FROM python:3.11-slim AS builder

# Create the venv and make it the default python for subsequent RUN steps.
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

# Install only dependencies first for better layer caching.
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---- Runtime stage: copy venv + app source, run as non-root ----
FROM python:3.11-slim AS runtime

# Don't buffer stdout/stderr; don't write .pyc files.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# Non-root user with a fixed UID.
RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid 1000 --create-home --shell /usr/sbin/nologin app

WORKDIR /app

# Copy the prebuilt virtualenv from the builder stage.
COPY --from=builder /opt/venv /opt/venv

# Copy only the application source (no .env, secrets, tests, or tooling).
COPY app ./app

# Ensure the app directory is owned by the non-root user.
RUN chown -R app:app /app

EXPOSE 8000

# Stdlib-only healthcheck (no curl needed): hit /health and exit non-zero on failure.
HEALTHCHECK --interval=30s --timeout=5s \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5).status == 200 else 1)"

USER app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
