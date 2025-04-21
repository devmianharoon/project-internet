# Use the official Python slim image for a smaller footprint
FROM python:3.10-slim

# Install uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.cargo/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy dependency files first to leverage Docker cache
# COPY requirements.txt .
# If using pyproject.toml, uncomment the next line and comment out requirements.txt
COPY pyproject.toml .

# Install dependencies with uv
# If using pyproject.toml, use:
RUN uv sync --system --no-cache-dir

# Copy the entire project
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Expose the port FastAPI will run on
EXPOSE 8000

# Run the FastAPI app with Uvicorn
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]