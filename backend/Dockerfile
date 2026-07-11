FROM python:3.12-slim

WORKDIR /app

# System deps for psycopg2 (only used when DATABASE_URL is Postgres).
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt psycopg2-binary

COPY . .

EXPOSE 8000

# $PORT is provided by most PaaS platforms; default to 8000 locally.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
