# Use Python 3.9 as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src/ ./src/
COPY .env ./

# Copy static files (HTML files, demo files, etc.)
COPY *.html ./
COPY demo.html ./

# Create logs directory
RUN mkdir -p logs

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["python", "src/main.py"]