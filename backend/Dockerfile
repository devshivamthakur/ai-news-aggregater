FROM python:3.14-slim

WORKDIR /app

# Configure DNS for Render
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .
COPY . .

EXPOSE 8000

# Render injects $PORT at runtime; fall back to 8000 for local use.
CMD ["sh", "-c", "uvicorn app.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
