FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=server.py
ENV FLASK_ENV=production

# Change to port 5000
EXPOSE 5000

# Update gunicorn to use port 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "server:app"]