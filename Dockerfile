# Use slim Python base
FROM python:3.12

# set workdir
WORKDIR /app

# Install Redis server
RUN apt-get update && apt-get install -y redis-server && rm -rf /var/lib/apt/lists/*

# Install build deps then python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy app
COPY . .

# Create startup script
RUN echo '#!/bin/bash\n\
# Start Redis server in background\n\
redis-server --daemonize yes\n\
\n\
# Start Celery worker in background\n\
celery -A app.core.celery_worker.celery worker --pool=solo --loglevel=info &\n\
\n\
# Start FastAPI application\n\
uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers\n\
' > /app/start.sh && chmod +x /app/start.sh

# If you use Uvicorn, expose port 8000
ENV PORT=8000
EXPOSE 8000

# Run the startup script
CMD ["/app/start.sh"]
