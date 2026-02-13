# Stage 1: Build
FROM rust:1.83-bookworm AS builder

WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src/ src/

RUN cargo build --release

# Stage 2: Runtime
FROM debian:bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user matching Helm securityContext (uid 1000)
RUN useradd -r -u 1000 -m feeder
USER feeder

COPY --from=builder /app/target/release/feeder /usr/local/bin/feeder

ENTRYPOINT ["/usr/local/bin/feeder"]
