# Root-level Dockerfile so Render's Docker build succeeds even without a
# Root Directory set. It simply delegates to the real Dockerfile in backend/.
# The build context is the repo root, so we COPY backend/ and build there.
FROM python:3.14-slim

WORKDIR /app

# Copy ONLY the backend application code (avoids frontend/, .git, etc.)
COPY backend/ /app/

RUN pip install --no-cache-dir -e .

EXPOSE 8000

# Render injects $PORT at runtime; fall back to 8000 for local use.
CMD ["sh", "-c", "uvicorn app.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
