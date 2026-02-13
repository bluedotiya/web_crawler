# Stage 1: Build
FROM rust:1.83-bookworm AS builder

WORKDIR /app

# Copy entire workspace
COPY Cargo.toml Cargo.lock ./
COPY shared/ shared/
COPY feeder/ feeder/
COPY manager/ manager/

RUN cargo build --release --package manager

# Stage 2: Runtime
FROM debian:bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user matching Helm securityContext (uid 1000)
RUN useradd -r -u 1000 -m manager
USER manager

COPY --from=builder /app/target/release/manager /usr/local/bin/manager

ENTRYPOINT ["/usr/local/bin/manager"]
