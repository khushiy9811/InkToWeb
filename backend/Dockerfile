FROM python:3.12-slim

# Tesseract OCR binary, plus the system libs OpenCV needs even in
# "headless" mode.
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

COPY . .

# Hugging Face Spaces run containers as a non-root user and expect the app
# on port 7860. The app writes to ./uploads and ./inktoweb.db at runtime,
# so those (and the whole app dir) need to be writable by that user.
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

ENV PORT=7860
EXPOSE 7860

# seed.py is idempotent (checks for the admin user before creating it) —
# safe to run on every container start, which matters here since free-tier
# storage is ephemeral and the demo login needs to exist after every restart.
CMD python seed.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
