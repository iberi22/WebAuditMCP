#!/usr/bin/env python3
"""
MCP Auditor Local - Main Server
FastMCP server that exposes web auditing tools for performance, SEO, accessibility, security, and responsiveness.
"""

import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

# Add tools directory to path
sys.path.append(str(Path(__file__).parent))

from tools.axe_playwright import scan_axe
from tools.cdp_gateway import cdp_emulate, cdp_health, cdp_open, cdp_screenshot, cdp_trace
from tools.lighthouse import audit_lighthouse
from tools.report_merge import report_merge
from tools.responsive import responsive_audit
from tools.security_headers import security_headers
from tools.wave import scan_wave
from tools.webhint import webhint_scan
from tools.zap import zap_baseline
from tools.auth_helper import auto_login, get_available_test_users

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure artifacts directory exists
ARTIFACTS_DIR = Path(__file__).parent.parent / "artifacts"
ARTIFACTS_DIR.mkdir(exist_ok=True)

# Initialize FastMCP server
mcp = FastMCP("MCP Auditor Local")

# Environment configuration
CHROME_MCP_ENABLED = os.getenv("CHROME_MCP_ENABLED", "true").lower() == "true"

def _check_dependency(command: str, version_flag: str = "--version") -> dict[str, Any]:
    """Check if a command is available and get its version."""
    if not shutil.which(command):
        return {"installed": False}

    try:
        result = subprocess.run(
            [command, version_flag],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            return {"installed": True, "version": version}
    except Exception:
        pass

    return {"installed": True, "version": "unknown"}

@mcp.tool()
def health_check() -> dict[str, Any]:
    """
    Health check for the MCP server.
    Returns server status and dependency availability.
    """
    # Check critical dependencies
    node_check = _check_dependency("node", "--version")
    npm_check = _check_dependency("npm", "--version")
    npx_check = _check_dependency("npx", "--version")

    # Check optional tools (will be auto-installed by npx if needed)
    python_check = _check_dependency("python", "--version")

    dependencies = {
        "node": node_check,
        "npm": npm_check,
        "npx": npx_check,
        "python": python_check
    }

    # Add install instructions for missing critical deps
    if not node_check["installed"]:
        dependencies["node"]["install_command"] = "winget install OpenJS.NodeJS (Windows) or visit https://nodejs.org"

    # Check if lighthouse and hint are accessible via npx
    lighthouse_note = "Will be auto-installed by npx on first use" if npx_check["installed"] else "Requires Node.js/npx"
    webhint_note = "Will be auto-installed by npx on first use" if npx_check["installed"] else "Requires Node.js/npx"

    return {
        "status": "ok",
        "server": "mcp-auditor-local",
        "version": "1.1.0",
        "chrome_mcp_enabled": CHROME_MCP_ENABLED,
        "artifacts_dir": str(ARTIFACTS_DIR),
        "dependencies": dependencies,
        "tools_status": {
            "lighthouse": {"status": lighthouse_note, "requires": ["npx"]},
            "webhint": {"status": webhint_note, "requires": ["npx"]},
            "axe": {"status": "Built-in via Playwright", "requires": ["python", "playwright"]},
            "security_headers": {"status": "Built-in", "requires": ["python"]},
            "responsive": {"status": "Built-in via Playwright", "requires": ["python", "playwright"]},
            "zap": {"status": "Requires OWASP ZAP installation", "requires": ["zap"]},
            "wave": {"status": "Requires WAVE_API_KEY env var", "requires": ["python", "WAVE_API_KEY"]},
            "chrome_devtools": {"status": "Enabled" if CHROME_MCP_ENABLED else "Disabled", "requires": ["chrome-devtools-mcp"]}
        }
    }

# Register all audit tools
mcp.tool()(audit_lighthouse)
mcp.tool()(scan_axe)
mcp.tool()(webhint_scan)
mcp.tool()(security_headers)
mcp.tool()(responsive_audit)
mcp.tool()(zap_baseline)
mcp.tool()(scan_wave)
mcp.tool()(report_merge)

# Register authentication and test user tools
mcp.tool()(auto_login)
mcp.tool()(get_available_test_users)

# Register Chrome DevTools gateway tools if enabled
if CHROME_MCP_ENABLED:
    mcp.tool()(cdp_health)
    mcp.tool()(cdp_open)
    mcp.tool()(cdp_screenshot)
    mcp.tool()(cdp_trace)
    mcp.tool()(cdp_emulate)

if __name__ == "__main__":
    logger.info("Starting MCP Auditor Local server...")
    logger.info(f"Chrome MCP Gateway: {'Enabled' if CHROME_MCP_ENABLED else 'Disabled'}")
    logger.info(f"Artifacts directory: {ARTIFACTS_DIR}")

    # Detect environment: Docker or local
    import socket
    in_docker = os.path.exists('/.dockerenv')

    if in_docker:
        # Docker: Use HTTP transport for remote access
        logger.info("Running in Docker container - using HTTP transport")
        mcp.run(
            transport="http",
            host="0.0.0.0",  # Listen on all interfaces
            port=8000,
            path="/mcp"
        )
    else:
        # Local: Use STDIO for desktop clients (Claude Desktop, Cursor, etc.)
        logger.info("Running locally - using STDIO transport")
        mcp.run(transport="stdio")