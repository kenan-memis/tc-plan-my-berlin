FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install uv (Python package + environment manager)
RUN pip install --no-cache-dir uv

WORKDIR /app

# Install Python dependencies first (better build caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Make sure the venv bin is on PATH
ENV PATH="/app/.venv/bin:${PATH}"

# Copy the rest of the app code + data
COPY . /app

RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]

