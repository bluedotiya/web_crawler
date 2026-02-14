# Stage 1: Build Rust binary
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

# Stage 2: Runtime
FROM debian:bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates libssl3 && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user matching Helm securityContext (uid 1000)
RUN useradd -r -u 1000 -m manager
USER manager

COPY --from=builder /usr/local/bin/manager /usr/local/bin/manager

ENTRYPOINT ["/usr/local/bin/manager"]
