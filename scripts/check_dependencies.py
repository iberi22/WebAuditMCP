#!/usr/bin/env python3
"""
Dependency checker for MCP Auditor Local.
Checks availability of external tools and provides installation guidance.
"""

import subprocess
import sys
import os
from pathlib import Path


def check_command(cmd, description):
    """Check if a command is available."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return True, result.returncode == 0, result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return True, False, ""


def check_npm_package(package, description):
    """Check if an npm package is available globally."""
    try:
        result = subprocess.run(["npm", "list", "-g", package], capture_output=True, text=True, timeout=10)
        return True, result.returncode == 0, ""
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return True, False, ""


def main():
    """Check all dependencies."""
    print("🔍 MCP Auditor Local - Dependency Check")
    print("=" * 50)

    checks = [
        # Core dependencies
        (["python", "--version"], "Python", "Required for MCP server"),
        (["node", "--version"], "Node.js", "Required for runners"),
        (["npm", "--version"], "npm", "Required for package management"),

        # Tool dependencies
        (["npx", "lighthouse", "--version"], "Lighthouse", "Performance auditing"),
        (["npx", "hint", "--version"], "webhint", "Web best practices"),
        (["docker", "--version"], "Docker", "ZAP security scanning"),

        # Browser dependencies
        (["npx", "playwright", "--version"], "Playwright", "Browser automation"),
    ]

    npm_packages = [
        ("chrome-devtools-mcp", "Chrome DevTools Gateway"),
    ]

    available = []
    missing = []

    # Check command-line tools
    for cmd, name, desc in checks:
        found, success, output = check_command(cmd, desc)

        if found and success:
            version = output.split('\n')[0] if output else "Unknown version"
            print(f"✅ {name}: {version}")
            available.append(name)
        else:
            print(f"❌ {name}: Not available - {desc}")
            missing.append((name, desc, cmd[0]))

    # Check npm packages
    for package, desc in npm_packages:
        found, success, _ = check_npm_package(package, desc)

        if found and success:
            print(f"✅ {package}: Available globally")
            available.append(package)
        else:
            print(f"⚠️  {package}: Not available globally - {desc}")
            missing.append((package, desc, "npm"))

    # Environment variables
    print("\n🔧 Environment Variables:")
    env_vars = [
        ("WAVE_API_KEY", "WAVE accessibility API", False),
        ("CHROME_MCP_ENABLED", "Chrome DevTools Gateway", False),
    ]

    for var, desc, required in env_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set")
        else:
            status = "❌" if required else "⚠️ "
            print(f"{status} {var}: Not set - {desc}")

    # Summary and recommendations
    print("\n📋 Summary:")
    print(f"✅ Available: {len(available)} tools")
    print(f"❌ Missing: {len(missing)} tools")

    if missing:
        print("\n🔧 Installation Recommendations:")
        for name, desc, installer in missing:
            if installer == "npx":
                print(f"• {name}: Already available via npx")
            elif installer == "npm":
                print(f"• {name}: npm install -g {name}")
            elif installer == "docker":
                print(f"• {name}: Install Docker Desktop")
            elif installer == "node":
                print(f"• {name}: Install Node.js from nodejs.org")
            elif installer == "python":
                print(f"• {name}: Install Python 3.10+ from python.org")
            else:
                print(f"• {name}: Check installation guide")

    # Specific guidance
    print("\n💡 Quick Setup Guide:")
    print("1. Install missing dependencies above")
    print("2. Run: npx playwright install --with-deps")
    print("3. Optional: docker pull owasp/zap2docker-stable")
    print("4. Optional: export WAVE_API_KEY=your_key")
    print("5. Run: python scripts/run_e2e.py")

    return 0 if len(missing) == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)