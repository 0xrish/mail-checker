# --- Build Stage ---
FROM rust:1.75-slim-bookworm AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/reacher

# Copy the entire project
COPY . .

# Build the CLI binary
RUN cargo build --release --bin check_if_email_exists

# --- Final Stage ---
FROM apify/actor-python:3.11

# Install Chromium and other dependencies for headless checks
USER root
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    libssl3 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy the compiled binary from the builder stage
COPY --from=builder /usr/src/reacher/target/release/check_if_email_exists /usr/local/bin/reacher-cli
RUN chmod +x /usr/local/bin/reacher-cli

# Set up the app directory
WORKDIR /app

# Copy Python actor code
COPY apify-actor/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY apify-actor/ .
RUN chmod +x start.sh

# Set environment variables
ENV RUST_LOG=info
ENV PATH="/usr/local/bin:${PATH}"

# Run the actor via start script
CMD ["./start.sh"]
