#!/usr/bin/env python3
"""
Test MCP connection and basic functionality
"""

import json
import subprocess
import sys
from pathlib import Path

def test_mcp_server():
    """Test if MCP server can start and respond"""
    print("🧪 Testing MCP Auditor Local...")

    # Test 1: Import server module
    try:
        sys.path.append(str(Path(__file__).parent.parent / "mcp"))
        from server import mcp
        print("✅ Server module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import server: {e}")
        return False

    # Test 2: Check tools registration
    try:
        tools = mcp.list_tools()
        print(f"✅ Found {len(tools)} registered tools:")
        for tool in tools[:5]:  # Show first 5
            print(f"   - {tool.name}")
        if len(tools) > 5:
            print(f"   ... and {len(tools) - 5} more")
    except Exception as e:
        print(f"❌ Failed to list tools: {e}")
        return False

    # Test 3: Test a simple tool
    try:
        from tools.security_headers import security_headers
        result = security_headers("https://httpbin.org/headers")
        if result.get("status") == "ok":
            print("✅ Security headers tool working")
        else:
            print(f"⚠️ Security headers tool returned: {result.get('status')}")
    except Exception as e:
        print(f"❌ Security headers test failed: {e}")

    print("\n🎉 MCP server basic tests completed!")
    return True

if __name__ == "__main__":
    test_mcp_server()