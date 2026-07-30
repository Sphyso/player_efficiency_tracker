# Base image
FROM python:3.13-slim

# Environment variables to optimize python performance in Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create and set internal working directory
WORKDIR /app

# Copy dependeny file first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire directory into the container
COPY . .

# Define default command
CMD ["python", "src/ingestion/fetch_match_logs.py"]

