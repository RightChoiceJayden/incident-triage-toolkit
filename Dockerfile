# Use slim Python base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Set Python path so it recognizes aegisir as a module
ENV PYTHONPATH=/app

# Install dependencies required for shell scripts and system monitoring
RUN apt-get update && apt-get install -y \
    procps \
    sysstat \
    net-tools \
    iputils-ping \
    curl \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full application source code into the container
COPY . .

# Make sure the triage script is executable
RUN chmod +x aegisir/triage.sh

# Expose port Flask is running on
EXPOSE 5001

# Default command to run the Flask API
CMD ["python3", "aegisir/api/webhook.py"]

