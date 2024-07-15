
FROM python:3.9-slim

WORKDIR /app

COPY app/ /app/

COPY fonts/ /usr/local/share/fonts/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:app"]
