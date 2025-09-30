# Dashboard Backend Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy dashboard backend requirements
COPY dashboard/backend/requirements.txt ./dashboard/backend/
RUN pip install --no-cache-dir -r dashboard/backend/requirements.txt

# Copy the main src directory (needed for imports)
COPY src/ ./src/

# Copy dashboard backend code
COPY dashboard/backend/ ./dashboard/backend/

# Create logs directory
RUN mkdir -p /app/logs

# Expose the port
EXPOSE 5000

# Set working directory to backend
WORKDIR /app/dashboard/backend

# Command to run the dashboard backend
CMD ["python", "app.py"]