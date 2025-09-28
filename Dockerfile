# ---------- Stage 1: Build Frontend (Production Only) ----------
FROM node:20-alpine AS frontend-build
WORKDIR /frontend

# Install dependencies
COPY ./frontend/package.json ./frontend/package-lock.json ./
RUN npm install --legacy-peer-deps

# Build production-ready React app
COPY ./frontend/ ./
RUN npm run build

# ---------- Stage 2: Backend Base ----------
FROM python:3.11-slim AS backend-base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y gcc libpq-dev build-essential --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---------- Stage 3: Development ----------
FROM backend-base AS development

COPY ./backend ./backend
COPY .env .env

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ---------- Stage 4: Production ----------
FROM backend-base AS production

COPY ./backend ./backend
COPY --from=frontend-build /frontend/build ./frontend_build
COPY .env .env

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
