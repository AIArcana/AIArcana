# Multi-stage build for AIArcana platform

# -------------------
# Stage 1: Base image with common dependencies
# -------------------
FROM node:20-alpine AS base
WORKDIR /app
ENV NODE_ENV=production
RUN apk add --no-cache libc6-compat python3 make g++

# -------------------
# Stage 2: Build the frontend
# -------------------
FROM base AS frontend-builder
WORKDIR /app/app

# Copy frontend dependencies
COPY app/package*.json ./
RUN npm ci

# Copy frontend source and build
COPY app/ ./
RUN npm run build

# -------------------
# Stage 3: Build the backend
# -------------------
FROM base AS backend-builder
WORKDIR /app/backend

# Copy backend dependencies
COPY backend/package*.json ./
RUN npm ci

# Copy backend source and build
COPY backend/ ./
RUN npm run build

# -------------------
# Stage 4: Install AI model dependencies
# -------------------
FROM python:3.9-slim AS ai-builder
WORKDIR /app/ai

# Install AI dependencies
COPY ai/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy AI source code
COPY ai/ ./

# -------------------
# Stage 5: Production image
# -------------------
FROM node:20-alpine AS production
WORKDIR /app
ENV NODE_ENV=production

# Install runtime dependencies
RUN apk add --no-cache libc6-compat python3

# Copy built artifacts from previous stages
COPY --from=frontend-builder /app/app/.next /app/app/.next
COPY --from=frontend-builder /app/app/public /app/app/public
COPY --from=frontend-builder /app/app/package.json /app/app/package.json
COPY --from=frontend-builder /app/app/next.config.js /app/app/next.config.js

COPY --from=backend-builder /app/backend/dist /app/backend/dist
COPY --from=backend-builder /app/backend/package.json /app/backend/package.json

COPY --from=ai-builder /app/ai /app/ai

# Copy root package.json and install production dependencies
COPY package.json ./
RUN npm ci --only=production

# Copy other necessary files
COPY .env.example .env

# Expose ports
EXPOSE 3000 3001

# Start the application
CMD ["npm", "start"] 