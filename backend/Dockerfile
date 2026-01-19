FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Download MiDaS ONNX model for wall detection
RUN mkdir -p /app/apps/mockup/ml/models && \
    curl -L -o /app/apps/mockup/ml/models/dpt_swin2_tiny_256.onnx \
    "https://huggingface.co/julienkay/sentis-MiDaS/resolve/main/onnx/dpt_swin2_tiny_256.onnx"

# Collect static files
RUN python manage.py collectstatic --noinput --settings=config.settings.production || true

# Railway uses $PORT, default to 8000 for local
CMD python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}
