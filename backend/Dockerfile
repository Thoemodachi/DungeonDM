# Use Python 3.10 slim
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port for ECS/ALB
EXPOSE 8000

# Run FastAPI with Gunicorn + Uvicorn in production
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000", "--workers", "4", "--log-level", "info"]
