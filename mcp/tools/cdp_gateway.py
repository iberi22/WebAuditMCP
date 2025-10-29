"""
Chrome DevTools MCP Gateway - Client for chrome-devtools-mcp server.
"""

import json
import logging
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Literal

logger = logging.getLogger(__name__)

class ChromeMCPClient:
    """Client for communicating with chrome-devtools-mcp server."""

    def __init__(self):
        self.process: subprocess.Popen | None = None
        self.request_id = 0
        self.lock = threading.Lock()

    def _get_next_id(self) -> int:
        """Get next request ID."""
        with self.lock:
            self.request_id += 1
            return self.request_id

    def _ensure_process(self) -> bool:
        """Ensure chrome-devtools-mcp process is running."""
        if self.process and self.process.poll() is None:
            return True

        try:
            # Get command from environment
            command = os.getenv("CHROME_MCP_COMMAND", "npx")
            args = json.loads(os.getenv("CHROME_MCP_ARGS", '["-y", "chrome-devtools-mcp"]'))

            # Start the process
            cmd = [command] + args
            logger.info(f"Starting chrome-devtools-mcp: {' '.join(cmd)}")

            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )

            # Wait a moment for startup
            time.sleep(2)

            # Check if process is still running
            if self.process.poll() is not None:
                stderr = self.process.stderr.read() if self.process.stderr else ""
                raise RuntimeError(f"chrome-devtools-mcp failed to start: {stderr}")

            return True

        except FileNotFoundError:
            logger.error("chrome-devtools-mcp not found. Install with: npm i -g chrome-devtools-mcp")
            return False
        except Exception as e:
            logger.error(f"Failed to start chrome-devtools-mcp: {e}")
            return False

    def _send_request(self, method: str, params: dict[str, Any] = None) -> dict[str, Any]:
        """Send JSON-RPC request to chrome-devtools-mcp."""
        if not self._ensure_process():
            raise RuntimeError("chrome-devtools-mcp is not available")

        request_id = self._get_next_id()
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {}
        }

        try:
            # Send request
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json)
            self.process.stdin.flush()

            # Read response
            response_line = self.process.stdout.readline()
            if not response_line:
                raise RuntimeError("No response from chrome-devtools-mcp")

            response = json.loads(response_line.strip())

            if "error" in response:
                raise RuntimeError(f"Chrome MCP error: {response['error']}")

            return response.get("result", {})

        except Exception as e:
            logger.error(f"Chrome MCP communication error: {e}")
            # Try to restart process on communication error
            if self.process:
                self.process.terminate()
                self.process = None
            raise

# Global client instance
_chrome_client = ChromeMCPClient()

def cdp_health() -> dict[str, Any]:
    """Check health of Chrome DevTools MCP gateway."""
    try:
        if not os.getenv("CHROME_MCP_ENABLED", "true").lower() == "true":
            return {
                'status': 'disabled',
                'message': 'Chrome MCP gateway is disabled (CHROME_MCP_ENABLED=false)'
            }

        # Try to get available tools
        result = _chrome_client._send_request("tools/list")

        return {
            'status': 'ok',
            'message': 'Chrome MCP gateway is healthy',
            'availableTools': len(result.get('tools', []))
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'suggestion': 'Install chrome-devtools-mcp with: npm i -g chrome-devtools-mcp'
        }

def cdp_open(url: str) -> dict[str, Any]:
    """Open URL in Chrome via DevTools MCP."""
    try:
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")

        result = _chrome_client._send_request("navigate", {"url": url})

        return {
            'status': 'ok',
            'url': url,
            'result': result
        }

    except Exception as e:
        logger.error(f"CDP open failed: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

def cdp_screenshot(selector: str | None = None) -> dict[str, Any]:
    """Capture screenshot via Chrome DevTools MCP."""
    try:
        params = {}
        if selector:
            params['selector'] = selector

        result = _chrome_client._send_request("screenshot", params)

        # Save screenshot to artifacts if base64 data is returned
        if 'data' in result:
            artifacts_dir = Path(__file__).parent.parent.parent / "artifacts"
            artifacts_dir.mkdir(exist_ok=True)

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot_path = artifacts_dir / f"cdp-screenshot-{timestamp}.png"

            import base64
            with open(screenshot_path, 'wb') as f:
                f.write(base64.b64decode(result['data']))

            result['screenshotPath'] = str(screenshot_path)

        return {
            'status': 'ok',
            'selector': selector,
            'result': result
        }

    except Exception as e:
        logger.error(f"CDP screenshot failed: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

def cdp_trace(action: Literal["start", "stop"]) -> dict[str, Any]:
    """Start or stop performance tracing via Chrome DevTools MCP."""
    try:
        if action not in ["start", "stop"]:
            raise ValueError("Action must be 'start' or 'stop'")

        method = "trace_start" if action == "start" else "trace_stop"
        result = _chrome_client._send_request(method)

        return {
            'status': 'ok',
            'action': action,
            'result': result
        }

    except Exception as e:
        logger.error(f"CDP trace {action} failed: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

def cdp_emulate(profile: Literal["mobile", "desktop", "custom"]) -> dict[str, Any]:
    """Emulate device profile via Chrome DevTools MCP."""
    try:
        if profile not in ["mobile", "desktop", "custom"]:
            raise ValueError("Profile must be 'mobile', 'desktop', or 'custom'")

        # Map profiles to device settings
        device_settings = {
            "mobile": {"width": 375, "height": 667, "deviceScaleFactor": 2, "mobile": True},
            "desktop": {"width": 1280, "height": 800, "deviceScaleFactor": 1, "mobile": False},
            "custom": {}  # Let the MCP handle custom settings
        }

        params = device_settings.get(profile, {})
        result = _chrome_client._send_request("emulate_device", params)

        return {
            'status': 'ok',
            'profile': profile,
            'result': result
        }

    except Exception as e:
        logger.error(f"CDP emulate {profile} failed: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }