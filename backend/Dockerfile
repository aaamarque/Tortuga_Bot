# Tortuga Bot - FastAPI backend with TensorFlow/Keras
FROM python:3.11-slim

WORKDIR /app

# Install system deps for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps (match environment.yml for compatibility)
COPY requirements.txt .
RUN pip install --no-cache-dir "numpy<2.0" "opencv-python-headless" && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Models (oil_spill_model.keras, tortuga.keras) must be in backend/
EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
