FROM python:3.12-slim

WORKDIR /app
COPY uploader.py requirements.txt .env ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "uploader.py"]
