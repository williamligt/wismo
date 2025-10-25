# Use the official uv image with Python 3.10 on Debian bookworm-slim
FROM python:3.10-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create app directory
WORKDIR /app

# Copy dependency files for better caching
COPY pyproject.toml uv.lock ./

# Sync the project into a new environment, asserting the lockfile is up to date
RUN uv sync --locked

# Copy the rest of the application
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application using uv
CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]