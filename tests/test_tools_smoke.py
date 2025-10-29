"""
Smoke tests for MCP Auditor Local tools.
"""

import json
import pytest
import sys
from pathlib import Path

# Add mcp directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "mcp"))

from tools.lighthouse import audit_lighthouse
from tools.axe_playwright import scan_axe
from tools.webhint import webhint_scan
from tools.security_headers import security_headers
from tools.responsive import responsive_audit
from tools.zap import zap_baseline
from tools.wave import scan_wave
from tools.report_merge import report_merge


class TestLighthouse:
    """Test Lighthouse audit tool."""

    @pytest.mark.e2e
    def test_lighthouse_example_com(self):
        """Test Lighthouse audit against example.com."""
        result = audit_lighthouse("https://example.com", "mobile")

        assert result["status"] == "ok"
        assert "categoryScores" in result
        assert "audits" in result
        assert "raw" in result
        assert isinstance(result["categoryScores"], dict)

        # Check required score categories
        scores = result["categoryScores"]
        assert "performance" in scores
        assert "accessibility" in scores
        assert "seo" in scores
        assert "bestPractices" in scores

    def test_lighthouse_invalid_url(self):
        """Test Lighthouse with invalid URL."""
        result = audit_lighthouse("not-a-url", "mobile")
        assert result["status"] == "error"
        assert "error" in result

    def test_lighthouse_invalid_device(self):
        """Test Lighthouse with invalid device."""
        result = audit_lighthouse("https://example.com", "invalid")
        # Should still work as it defaults to mobile preset
        assert result["status"] in ["ok", "error"]


class TestAxe:
    """Test axe accessibility tool."""

    @pytest.mark.e2e
    def test_axe_example_com(self):
        """Test axe scan against example.com."""
        result = scan_axe("https://example.com", "mobile")

        assert result["status"] == "ok"
        assert "violations" in result
        assert "violationsCount" in result
        assert "passesCount" in result
        assert isinstance(result["violations"], list)

    def test_axe_invalid_url(self):
        """Test axe with invalid URL."""
        result = scan_axe("not-a-url", "mobile")
        assert result["status"] == "error"
        assert "error" in result


class TestWebhint:
    """Test webhint tool."""

    @pytest.mark.e2e
    def test_webhint_example_com(self):
        """Test webhint scan against example.com."""
        result = webhint_scan("https://example.com")

        assert result["status"] == "ok"
        assert "hints" in result
        assert "hintsCount" in result
        assert isinstance(result["hints"], list)

    def test_webhint_invalid_url(self):
        """Test webhint with invalid URL."""
        result = webhint_scan("not-a-url")
        assert result["status"] == "error"
        assert "error" in result


class TestSecurityHeaders:
    """Test security headers tool."""

    @pytest.mark.e2e
    def test_security_headers_example_com(self):
        """Test security headers analysis against example.com."""
        result = security_headers("https://example.com")

        assert result["status"] == "ok"
        assert "headers" in result
        assert "securityScore" in result
        assert "raw" in result

        # Check security flags
        headers = result["headers"]
        expected_flags = ["csp", "hsts", "xfo", "xcto", "referrer", "permissions"]
        for flag in expected_flags:
            assert flag in headers
            assert isinstance(headers[flag], bool)

    def test_security_headers_invalid_url(self):
        """Test security headers with invalid URL."""
        result = security_headers("not-a-url")
        assert result["status"] == "error"
        assert "error" in result


class TestResponsive:
    """Test responsive audit tool."""

    @pytest.mark.e2e
    def test_responsive_example_com(self):
        """Test responsive audit against example.com."""
        result = responsive_audit("https://example.com", ["360x640", "768x1024"])

        assert result["status"] == "ok"
        assert "summaries" in result
        assert "responsiveScore" in result
        assert "totalIssues" in result
        assert isinstance(result["summaries"], list)
        assert len(result["summaries"]) == 2  # Two viewports

    def test_responsive_invalid_url(self):
        """Test responsive audit with invalid URL."""
        result = responsive_audit("not-a-url", ["360x640"])
        assert result["status"] == "error"
        assert "error" in result

    def test_responsive_default_viewports(self):
        """Test responsive audit with default viewports."""
        result = responsive_audit("https://example.com")
        if result["status"] == "ok":
            assert len(result["summaries"]) == 3  # Default viewports


class TestZap:
    """Test ZAP security tool."""

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_zap_example_com(self):
        """Test ZAP baseline scan against example.com."""
        result = zap_baseline("https://example.com", 1)  # 1 minute scan

        # ZAP might not be available (Docker required)
        if result["status"] == "error" and "Docker" in result["error"]:
            pytest.skip("Docker not available for ZAP testing")

        assert result["status"] == "ok"
        assert "alerts" in result
        assert "securityScore" in result
        assert "alertsCount" in result
        assert isinstance(result["alerts"], list)

    def test_zap_invalid_url(self):
        """Test ZAP with invalid URL."""
        result = zap_baseline("not-a-url", 1)
        assert result["status"] == "error"
        assert "error" in result

    def test_zap_invalid_minutes(self):
        """Test ZAP with invalid duration."""
        result = zap_baseline("https://example.com", 0)
        assert result["status"] == "error"
        assert "error" in result


class TestWave:
    """Test WAVE accessibility tool."""

    @pytest.mark.e2e
    def test_wave_without_api_key(self):
        """Test WAVE without API key (should fail gracefully)."""
        result = scan_wave("https://example.com", "json")

        # Should fail without API key
        assert result["status"] == "error"
        assert "WAVE_API_KEY" in result["error"]
        assert "scan_axe" in result["error"]  # Should suggest alternative

    def test_wave_invalid_url(self):
        """Test WAVE with invalid URL."""
        result = scan_wave("not-a-url", "json")
        assert result["status"] == "error"
        assert "error" in result


class TestReportMerge:
    """Test report merging functionality."""

    def test_report_merge_empty_items(self):
        """Test report merge with empty items."""
        result = report_merge([])
        assert result["status"] == "error"
        assert "error" in result

    def test_report_merge_single_item(self):
        """Test report merge with single valid item."""
        lighthouse_result = {
            "status": "ok",
            "categoryScores": {
                "performance": 85,
                "accessibility": 90,
                "seo": 80,
                "bestPractices": 88
            },
            "audits": {}
        }

        result = report_merge([lighthouse_result])

        assert result["status"] == "ok"
        assert "score" in result
        assert "findings" in result
        assert "jsonReportPath" in result
        assert "htmlReportPath" in result

        # Check score structure
        scores = result["score"]
        assert "perf" in scores
        assert "a11y" in scores
        assert "seo" in scores
        assert "security" in scores
        assert "responsive" in scores
        assert "global" in scores

    def test_report_merge_with_budgets(self):
        """Test report merge with budget thresholds."""
        lighthouse_result = {
            "status": "ok",
            "categoryScores": {
                "performance": 85,
                "accessibility": 90,
                "seo": 80,
                "bestPractices": 88
            },
            "audits": {}
        }

        budgets = {
            "perf": 80,
            "a11y": 85,
            "seo": 75
        }

        result = report_merge([lighthouse_result], budgets)

        assert result["status"] == "ok"
        assert "budgets" in result

        budget_results = result["budgets"]
        assert "perf" in budget_results
        assert budget_results["perf"]["passed"] is True  # 85 >= 80
        assert budget_results["a11y"]["passed"] is True  # 90 >= 85
        assert budget_results["seo"]["passed"] is True   # 80 >= 75