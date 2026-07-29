FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5101

CMD gunicorn app:app --bind 0.0.0.0: --workers 2 --timeout 30
