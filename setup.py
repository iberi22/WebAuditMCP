#!/usr/bin/env python3
"""
Setup script for MCP Auditor Local
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and handle errors."""
    try:
        result = subprocess.run(cmd, shell=True, check=True, cwd=cwd,
                              capture_output=True, text=True)
        print(f"✅ {cmd}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {cmd}")
        print(f"Error: {e.stderr}")
        return None

def main():
    """Main setup function."""
    print("🚀 Setting up MCP Auditor Local...")

    # Check Python version
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ is required")
        sys.exit(1)

    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")

    # Install Python dependencies
    print("\n📦 Installing Python dependencies...")
    if not run_command("pip install -r requirements.txt"):
        print("❌ Failed to install Python dependencies")
        sys.exit(1)

    # Setup Node.js dependencies
    print("\n📦 Installing Node.js dependencies...")
    node_tools_dir = Path(__file__).parent / "node-tools"

    if not run_command("npm install", cwd=node_tools_dir):
        print("❌ Failed to install Node.js dependencies")
        sys.exit(1)

    # Install Playwright browsers
    print("\n🌐 Installing Playwright browsers...")
    if not run_command("npx playwright install --with-deps", cwd=node_tools_dir):
        print("❌ Failed to install Playwright browsers")
        sys.exit(1)

    # Create artifacts directory
    artifacts_dir = Path(__file__).parent / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    print(f"✅ Created artifacts directory: {artifacts_dir}")

    # Check optional dependencies
    print("\n🔍 Checking optional dependencies...")

    # Check Docker
    docker_result = run_command("docker --version")
    if docker_result:
        print("✅ Docker available (ZAP security scanning enabled)")
    else:
        print("⚠️  Docker not available (ZAP security scanning disabled)")

    # Check chrome-devtools-mcp
    cdp_result = run_command("npx chrome-devtools-mcp --version")
    if cdp_result:
        print("✅ chrome-devtools-mcp available (Gateway enabled)")
    else:
        print("⚠️  chrome-devtools-mcp not available (Gateway disabled)")
        print("   Install with: npm install -g chrome-devtools-mcp")

    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Set environment variables (optional):")
    print("   export WAVE_API_KEY=your_wave_api_key")
    print("   export CHROME_MCP_ENABLED=true")
    print("2. Run the server:")
    print("   python mcp/server.py")
    print("3. Configure your MCP client to use this server")

if __name__ == "__main__":
    main()