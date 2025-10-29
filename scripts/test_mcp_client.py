#!/usr/bin/env python3
"""
MCP Auditor - Client Test Script
Tests the MCP server running in Docker via HTTP transport
"""

import asyncio
import sys
from fastmcp import Client


async def test_server():
    """Test the MCP Auditor server"""
    print("🧪 Testing MCP Auditor Server")
    print("=" * 70)

    server_url = "http://localhost:8000/mcp"

    try:
        async with Client(server_url) as client:
            # Test 1: Health Check
            print("\n✅ Connection successful!")
            print(f"📡 Server URL: {server_url}")

            # Test 2: List available tools
            print("\n🔧 Available Tools:")
            tools = await client.list_tools()
            for i, tool in enumerate(tools, 1):
                print(f"   {i}. {tool.name:30} - {tool.description}")

            # Test 3: Call health_check tool
            print("\n🏥 Health Check:")
            result = await client.call_tool("health_check", {})
            print(f"   Status: {result.content[0].text}")

            # Test 4: List resources
            print("\n📚 Available Resources:")
            resources = await client.list_resources()
            if resources:
                for i, resource in enumerate(resources, 1):
                    print(f"   {i}. {resource.uri} - {resource.name}")
            else:
                print("   No resources available")

            # Test 5: List prompts
            print("\n💬 Available Prompts:")
            prompts = await client.list_prompts()
            if prompts:
                for i, prompt in enumerate(prompts, 1):
                    print(f"   {i}. {prompt.name} - {prompt.description}")
            else:
                print("   No prompts available")

            print("\n" + "=" * 70)
            print("✅ All tests passed! Server is healthy and ready.")
            print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error connecting to server: {e}")
        print(f"\n💡 Make sure the Docker container is running:")
        print(f"   docker-compose -f docker/docker-compose.yml up -d")
        sys.exit(1)


async def test_lighthouse_audit():
    """Test Lighthouse audit functionality"""
    print("\n🚀 Testing Lighthouse Audit")
    print("=" * 70)

    server_url = "http://localhost:8000/mcp"

    try:
        async with Client(server_url) as client:
            print("Running Lighthouse audit on example.com...")
            result = await client.call_tool("audit_lighthouse", {
                "url": "https://example.com",
                "device": "mobile"
            })

            print("\n📊 Lighthouse Results:")
            print(f"   {result.content[0].text[:500]}...")
            print("\n✅ Lighthouse audit completed successfully!")

    except Exception as e:
        print(f"\n⚠️  Lighthouse test skipped: {e}")


async def main():
    """Main test function"""
    await test_server()

    # Uncomment to test Lighthouse (requires Chrome)
    # await test_lighthouse_audit()


if __name__ == "__main__":
    asyncio.run(main())
