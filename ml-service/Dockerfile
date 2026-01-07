FROM python:3.11-slim

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY people_detector.py .

# YOLO model will be mounted as volume
# Expected at /app/yolo11n.pt

# Expose Flask port
EXPOSE 5000

# Set environment variables
ENV MODEL_PATH=/app/yolo11n.pt
ENV PORT=5000
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "people_detector.py"]
