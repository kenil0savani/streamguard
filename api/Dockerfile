FROM python:3.11-slim

WORKDIR /app

COPY api/requirements.txt /app/api/requirements.txt
RUN pip install --no-cache-dir -r /app/api/requirements.txt

COPY stream_processor /app/stream_processor
COPY api /app/api
ENV MODEL_PATH=/app/api/isolation_forest.joblib

WORKDIR /app/api
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
