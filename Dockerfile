# Multi-stage Dockerfile for ASTRA-Sec Space Communications Node
FROM python:3.11-slim AS builder

WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    clang \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml Makefile ./
COPY astra_sec/ ./astra_sec/
COPY algorithms/ ./algorithms/
COPY tests/ ./tests/

# Compile C verification engines
RUN make bin/test_fips_kats

# Final runtime image
FROM python:3.11-slim

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /build/bin /app/bin
COPY --from=builder /build/astra_sec /app/astra_sec
COPY --from=builder /build/pyproject.toml /app/pyproject.toml
COPY .env.example /app/.env.example

RUN pip install --no-cache-dir pydantic>=2.0.0

# Set environment defaults
ENV PYTHONUNBUFFERED=1 \
    ASTRA_NODE_EID=dtn://node.space.net \
    ASTRA_NODE_ROLE=satellite_relay \
    ASTRA_BIND_HOST=0.0.0.0 \
    ASTRA_BIND_PORT=8080 \
    ASTRA_LOG_LEVEL=INFO \
    ASTRA_SPOOL_DIR=/tmp/astra_sec/spool \
    ASTRA_C_ENGINE_BIN=/app/bin/test_fips_kats

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -m astra_sec.app health || exit 1

ENTRYPOINT ["python", "-m", "astra_sec.app"]
CMD ["health"]
