#!/usr/bin/env python3
"""
End-to-end testing script for MCP Auditor Local.
Runs all tools against example.com and generates unified report.
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

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


def check_docker_available():
    """Check if Docker is available."""
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_wave_api_key():
    """Check if WAVE API key is available."""
    return bool(os.getenv("WAVE_API_KEY"))


def save_result(result, filename):
    """Save result to artifacts directory."""
    artifacts_dir = Path(__file__).parent.parent / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)

    filepath = artifacts_dir / filename
    with open(filepath, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"✅ Saved {filename}")
    return str(filepath)


def main():
    """Run end-to-end tests."""
    print("🚀 Starting MCP Auditor Local E2E Tests")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("-" * 50)

    test_url = "https://example.com"
    results = []
    failed_tests = []

    # Test 1: Lighthouse
    print("🔍 Running Lighthouse audit...")
    try:
        lighthouse_result = audit_lighthouse(test_url, "mobile")
        if lighthouse_result["status"] == "ok":
            save_result(lighthouse_result, "lighthouse.json")
            results.append(lighthouse_result)
            print("✅ Lighthouse: PASSED")
        else:
            print(f"❌ Lighthouse: FAILED - {lighthouse_result.get('error', 'Unknown error')}")
            failed_tests.append("lighthouse")
    except Exception as e:
        print(f"❌ Lighthouse: ERROR - {e}")
        failed_tests.append("lighthouse")

    # Test 2: Axe
    print("♿ Running axe accessibility scan...")
    try:
        axe_result = scan_axe(test_url, "mobile")
        if axe_result["status"] == "ok":
            save_result(axe_result, "axe.json")
            results.append(axe_result)
            print("✅ Axe: PASSED")
        else:
            print(f"❌ Axe: FAILED - {axe_result.get('error', 'Unknown error')}")
            failed_tests.append("axe")
    except Exception as e:
        print(f"❌ Axe: ERROR - {e}")
        failed_tests.append("axe")

    # Test 3: Webhint
    print("🌐 Running webhint scan...")
    try:
        webhint_result = webhint_scan(test_url)
        if webhint_result["status"] == "ok":
            save_result(webhint_result, "webhint.json")
            results.append(webhint_result)
            print("✅ Webhint: PASSED")
        else:
            print(f"❌ Webhint: FAILED - {webhint_result.get('error', 'Unknown error')}")
            failed_tests.append("webhint")
    except Exception as e:
        print(f"❌ Webhint: ERROR - {e}")
        failed_tests.append("webhint")

    # Test 4: Security Headers
    print("🔒 Running security headers analysis...")
    try:
        headers_result = security_headers(test_url)
        if headers_result["status"] == "ok":
            save_result(headers_result, "headers.json")
            results.append(headers_result)
            print("✅ Security Headers: PASSED")
        else:
            print(f"❌ Security Headers: FAILED - {headers_result.get('error', 'Unknown error')}")
            failed_tests.append("security_headers")
    except Exception as e:
        print(f"❌ Security Headers: ERROR - {e}")
        failed_tests.append("security_headers")

    # Test 5: Responsive
    print("📱 Running responsive audit...")
    try:
        responsive_result = responsive_audit(test_url, ["360x640", "768x1024"])
        if responsive_result["status"] == "ok":
            save_result(responsive_result, "responsive.json")
            results.append(responsive_result)
            print("✅ Responsive: PASSED")
        else:
            print(f"❌ Responsive: FAILED - {responsive_result.get('error', 'Unknown error')}")
            failed_tests.append("responsive")
    except Exception as e:
        print(f"❌ Responsive: ERROR - {e}")
        failed_tests.append("responsive")

    # Test 6: ZAP (optional - requires Docker)
    if check_docker_available():
        print("🛡️ Running ZAP baseline scan...")
        try:
            zap_result = zap_baseline(test_url, 2)  # 2 minute scan
            if zap_result["status"] == "ok":
                save_result(zap_result, "zap.json")
                results.append(zap_result)
                print("✅ ZAP: PASSED")
            else:
                print(f"❌ ZAP: FAILED - {zap_result.get('error', 'Unknown error')}")
                failed_tests.append("zap")
        except Exception as e:
            print(f"❌ ZAP: ERROR - {e}")
            failed_tests.append("zap")
    else:
        print("⚠️ ZAP: SKIPPED (Docker not available)")

    # Test 7: WAVE (optional - requires API key)
    if check_wave_api_key():
        print("🌊 Running WAVE accessibility scan...")
        try:
            wave_result = scan_wave(test_url, "json", {})
            if wave_result["status"] == "ok":
                save_result(wave_result, "wave.json")
                results.append(wave_result)
                print("✅ WAVE: PASSED")
            else:
                print(f"❌ WAVE: FAILED - {wave_result.get('error', 'Unknown error')}")
                failed_tests.append("wave")
        except Exception as e:
            print(f"❌ WAVE: ERROR - {e}")
            failed_tests.append("wave")
    else:
        print("⚠️ WAVE: SKIPPED (WAVE_API_KEY not set)")

    # Test 8: Report Merge
    if results:
        print("📊 Generating unified report...")
        try:
            # Define budgets for testing
            budgets = {
                "perf": 70,
                "a11y": 80,
                "seo": 75,
                "security": 70,
                "responsive": 80
            }

            report_result = report_merge(results, budgets)
            if report_result["status"] == "ok":
                save_result(report_result, "report.json")
                print("✅ Report Merge: PASSED")
                print(f"📄 HTML Report: {report_result['htmlReportPath']}")
                print(f"📄 JSON Report: {report_result['jsonReportPath']}")

                # Print summary
                scores = report_result["score"]
                print(f"📈 Overall Score: {scores['global']:.1f}/100")
                print(f"   Performance: {scores['perf']:.1f}")
                print(f"   Accessibility: {scores['a11y']:.1f}")
                print(f"   SEO: {scores['seo']:.1f}")
                print(f"   Security: {scores['security']:.1f}")
                print(f"   Responsive: {scores['responsive']:.1f}")
            else:
                print(f"❌ Report Merge: FAILED - {report_result.get('error', 'Unknown error')}")
                failed_tests.append("report_merge")
        except Exception as e:
            print(f"❌ Report Merge: ERROR - {e}")
            failed_tests.append("report_merge")
    else:
        print("❌ Report Merge: SKIPPED (No successful results to merge)")
        failed_tests.append("report_merge")

    # Summary
    print("-" * 50)
    print("📋 E2E Test Summary:")
    print(f"✅ Passed: {len(results)} tools")
    print(f"❌ Failed: {len(failed_tests)} tools")

    if failed_tests:
        print(f"Failed tools: {', '.join(failed_tests)}")
        return 1
    else:
        print("🎉 All available tools passed!")
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)