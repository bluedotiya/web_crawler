# Stage 1: Build frontend
FROM node:22-bookworm-slim AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Build Rust binary
FROM rust:1.83-bookworm AS builder

ARG PROFILE=release

RUN apt-get update && apt-get install -y --no-install-recommends pkg-config libssl-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy entire workspace
COPY Cargo.toml Cargo.lock ./
COPY shared/ shared/
COPY feeder/ feeder/
COPY manager/ manager/

RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/app/target \
    TARGET_DIR=$([ "$PROFILE" = "dev" ] && echo "debug" || echo "$PROFILE") && \
    cargo build --profile ${PROFILE} --package manager && \
    cp /app/target/${TARGET_DIR}/manager /usr/local/bin/manager

# Stage 3: Runtime
FROM debian:bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates libssl3 && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user matching Helm securityContext (uid 1000)
RUN useradd -r -u 1000 -m manager
USER manager

COPY --from=builder /usr/local/bin/manager /usr/local/bin/manager
COPY --from=frontend-builder /app/frontend/dist /app/static

ENV STATIC_DIR=/app/static

ENTRYPOINT ["/usr/local/bin/manager"]
