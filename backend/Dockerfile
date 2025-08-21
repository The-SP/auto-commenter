FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project files
COPY . .

# Install the application dependencies
RUN uv sync --frozen --no-cache

EXPOSE 8000

# Run the application
CMD ["uv", "run", "main.py"]