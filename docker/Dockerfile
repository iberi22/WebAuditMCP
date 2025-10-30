# ==============================================================================
# MCP Auditor - Professional Web Auditing Server
# ==============================================================================
# Multi-stage build for optimal image size and security
# Based on Playwright image for browser automation capabilities
# ==============================================================================

FROM mcr.microsoft.com/playwright:v1.40.0-jammy as base

# Metadata labels for professional deployment
LABEL maintainer="MCP Auditor Team"
LABEL description="FastMCP server for web auditing with Lighthouse, Axe, WAVE, and security tools"
LABEL version="1.1.0"

# Install Python and essential system dependencies
# Note: Playwright image already includes Python3, so we only add what's missing
USER root

# Install Node.js 22.x (required for Lighthouse)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    python3-pip \
    python3-venv \
    curl \
    docker.io \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Verify Node.js version
RUN node --version && npm --version

# Set working directory
WORKDIR /app

# Install Node.js dependencies first (for better caching)
COPY node-tools/package*.json ./node-tools/
RUN cd node-tools && npm install --omit=dev --no-audit --no-fund

# Install Python dependencies
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Ensure Playwright browsers are installed
RUN npx playwright install --with-deps chromium

# Install global Node.js tools for auditing
RUN npm install -g lighthouse chrome-devtools-mcp @hint/hint || echo "Some npm packages failed, continuing..."

# Copy application code
COPY mcp/ ./mcp/
COPY node-tools/ ./node-tools/
COPY artifacts/ ./artifacts/
COPY scripts/ ./scripts/
COPY README.md ./

# Use existing pwuser from playwright image or create auditor user
RUN if id -u 1000 >/dev/null 2>&1; then \
        chown -R 1000:1000 /app; \
    else \
        useradd -m -u 1000 auditor && chown -R auditor:auditor /app; \
    fi

USER 1000

# Environment variables
ENV CHROME_MCP_ENABLED=true
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production

# Health check - verifies HTTP server is responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/mcp || exit 1

# Expose HTTP port for MCP server
EXPOSE 8000

# Default command - runs FastMCP server with HTTP transport
CMD ["python3", "mcp/server.py"]