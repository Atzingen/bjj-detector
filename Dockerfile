FROM python:3.13-slim

# Install system deps for OpenCV (ultralytics dependency)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY webapp.py .
COPY templates/ templates/
COPY static/ static/
COPY best.pt* .

EXPOSE 5000

CMD ["python", "webapp.py"]
