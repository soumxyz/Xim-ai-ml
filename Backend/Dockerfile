FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (build-essential needed for some C extensions like rapidfuzz, ahocorasick)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data required by preprocessing (stopwords)
RUN python -m nltk.downloader stopwords

# Copy backend source code
COPY . .

# Expose FastAPI default port
EXPOSE 8000

# Run the Uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
