FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends lynis ca-certificates procps \
    && rm -rf /var/lib/apt/lists/*

# Default workdir and a non-root user are not required for Lynis; it needs root-like privileges.
WORKDIR /

# No entrypoint here; compose will set sleep/infinity so we can override with --entrypoint "" when running.
CMD ["/bin/bash"]
