FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# 🟢 1. EXACT PLACE: Install system binaries (Tesseract & Poppler) right after WORKDIR
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy requirements file first for Docker layer caching
COPY requirements.txt .

# 3. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy application source code
COPY . .

# Expose API port
EXPOSE 8000

# Default command to run FastAPI web app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]