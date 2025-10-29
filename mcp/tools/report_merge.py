"""
Report merging and unified scoring system.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

def report_merge(items: list[dict[str, Any]], budgets: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Merge multiple audit results into a unified report.

    Args:
        items: List of audit results from different tools
        budgets: Optional budget thresholds for pass/fail criteria

    Returns:
        Dict containing unified scores, findings, and report paths
    """
    try:
        if not items:
            raise ValueError("Items list cannot be empty")

        # Initialize scores
        scores = {
            'perf': 0,
            'a11y': 0,
            'seo': 0,
            'security': 0,
            'responsive': 0,
            'global': 0
        }

        findings = []
        artifacts = []

        # Process each audit result
        for item in items:
            if item.get('status') != 'ok':
                continue

            # Extract tool type from item
            tool_type = _identify_tool_type(item)

            if tool_type == 'lighthouse':
                _process_lighthouse_results(item, scores, findings, artifacts)
            elif tool_type == 'axe':
                _process_axe_results(item, scores, findings, artifacts)
            elif tool_type == 'wave':
                _process_wave_results(item, scores, findings, artifacts)
            elif tool_type == 'security_headers':
                _process_security_headers_results(item, scores, findings, artifacts)
            elif tool_type == 'zap':
                _process_zap_results(item, scores, findings, artifacts)
            elif tool_type == 'responsive':
                _process_responsive_results(item, scores, findings, artifacts)
            elif tool_type == 'webhint':
                _process_webhint_results(item, scores, findings, artifacts)

        # Calculate global score (weighted average)
        weights = {
            'perf': 0.30,
            'a11y': 0.30,
            'seo': 0.20,
            'security': 0.15,
            'responsive': 0.05
        }

        global_score = sum(scores[category] * weight for category, weight in weights.items())
        scores['global'] = round(global_score, 1)

        # Apply budgets if provided
        budget_results = {}
        if budgets:
            budget_results = _apply_budgets(scores, findings, budgets)

        # Generate report files
        artifacts_dir = Path(__file__).parent.parent.parent / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # JSON report
        json_report_path = artifacts_dir / f"report-{timestamp}.json"
        html_report_path = artifacts_dir / f"report-{timestamp}.html"

        report_data = {
            'timestamp': datetime.now().isoformat(),
            'score': scores,
            'findings': findings,
            'artifacts': artifacts,
            'budgets': budget_results,
            'summary': _generate_summary(scores, findings)
        }

        # Save JSON report
        with open(json_report_path, 'w') as f:
            json.dump(report_data, f, indent=2)

        # Generate and save HTML report
        html_content = _generate_html_report(report_data)
        with open(html_report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return {
            'status': 'ok',
            'score': scores,
            'findings': findings,
            'artifacts': artifacts,
            'budgets': budget_results,
            'jsonReportPath': str(json_report_path),
            'htmlReportPath': str(html_report_path),
            'summary': report_data['summary']
        }

    except Exception as e:
        logger.error(f"Report merge failed: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

def _identify_tool_type(item: dict[str, Any]) -> str:
    """Identify the tool type from audit result."""
    if 'categoryScores' in item:
        return 'lighthouse'
    elif 'violations' in item:
        return 'axe'
    elif 'issues' in item and 'reportType' in item:
        return 'wave'
    elif 'headers' in item and 'securityScore' in item:
        return 'security_headers'
    elif 'alerts' in item and 'scanDuration' in item:
        return 'zap'
    elif 'summaries' in item and 'responsiveScore' in item:
        return 'responsive'
    elif 'hints' in item:
        return 'webhint'
    else:
        return 'unknown'

def _process_lighthouse_results(item: dict[str, Any], scores: dict[str, float], findings: list[dict], artifacts: list[str]):
    """Process Lighthouse audit results."""
    category_scores = item.get('categoryScores', {})

    scores['perf'] = category_scores.get('performance', 0)
    scores['seo'] = category_scores.get('seo', 0)

    # Add accessibility score if available
    if category_scores.get('accessibility', 0) > 0:
        scores['a11y'] = max(scores['a11y'], category_scores.get('accessibility', 0))

    # Extract key findings from audits
    audits = item.get('audits', {})
    for audit_id, audit in audits.items():
        if audit.get('score', 1) < 0.9:  # Failed or warning audits
            findings.append({
                'category': 'perf' if 'performance' in audit_id else 'seo',
                'severity': 'high' if audit.get('score', 1) < 0.5 else 'medium',
                'summary': audit.get('title', audit_id),
                'evidence': {
                    'score': audit.get('score'),
                    'displayValue': audit.get('displayValue')
                },
                'recommendation': audit.get('description', '')
            })

def _process_axe_results(item: dict[str, Any], scores: dict[str, float], findings: list[dict], artifacts: list[str]):
    """Process axe accessibility results."""
    violations = item.get('violations', [])
    item.get('passesCount', 0)

    # Calculate accessibility score based on violations
    critical_violations = sum(1 for v in violations if v.get('impact') == 'critical')
    serious_violations = sum(1 for v in violations if v.get('impact') == 'serious')
    moderate_violations = sum(1 for v in violations if v.get('impact') == 'moderate')

    # Scoring: start at 100, deduct points for violations
    a11y_score = 100
    a11y_score -= critical_violations * 25
    a11y_score -= serious_violations * 15
    a11y_score -= moderate_violations * 10

    scores['a11y'] = max(0, a11y_score)

    # Add violation findings
    for violation in violations:
        findings.append({
            'category': 'a11y',
            'severity': _map_axe_impact_to_severity(violation.get('impact')),
            'summary': violation.get('description', violation.get('id')),
            'evidence': {
                'nodes': violation.get('nodes', 0),
                'tags': violation.get('tags', [])
            },
            'recommendation': violation.get('help', '')
        })

def _process_wave_results(item: dict[str, Any], scores: dict[str, float], findings: list[dict], artifacts: list[str]):
    """Process WAVE accessibility results."""
    issues = item.get('issues', [])

    # Calculate accessibility score based on WAVE issues
    critical_issues = sum(1 for issue in issues if issue.get('impact') == 'critical')
    moderate_issues = sum(1 for issue in issues if issue.get('impact') == 'moderate')

    wave_score = 100 - (critical_issues * 20) - (moderate_issues * 10)

    # Use the better of axe or WAVE scores
    scores['a11y'] = max(scores['a11y'], max(0, wave_score))

    # Add WAVE findings
    for issue in issues:
        findings.append({
            'category': 'a11y',
            'severity': 'high' if issue.get('impact') == 'critical' else 'medium',
            'summary': issue.get('summary', ''),
            'evidence': {
                'type': issue.get('type'),
                'selector': issue.get('selector')
            },
            'recommendation': f"Review {issue.get('type')} issue"
        })

    # Add artifacts
    if item.get('artifacts'):
        artifacts.extend(item['artifacts'])

def _process_security_headers_results(item: dict[str, Any], scores: dict[str, float], findings: list[dict], artifacts: list[str]):
    """Process security headers results."""
    security_score = item.get('securityScore', 0)
    headers = item.get('headers', {})

    scores['security'] = max(scores['security'], security_score)

    # Add findings for missing headers
    header_names = {
        'csp': 'Content Security Policy',
        'hsts': 'HTTP Strict Transport Security',
        'xfo': 'X-Frame-Options',
        'xcto': 'X-Content-Type-Options',
        'referrer': 'Referrer Policy',
        'permissions': 'Permissions Policy'
    }

    for header_key, present in headers.items():
        if not present:
            findings.append({
                'category': 'security',
                'severity': 'high' if header_key in ['csp', 'hsts'] else 'medium',
                'summary': f'Missing {header_names.get(header_key, header_key)} header',
                'evidence': {'header': header_key},
                'recommendation': f'Implement {header_names.get(header_key, header_key)} header'
            })

def _process_zap_results(item: dict[str, Any], scores: dict[str, float], findings: list[dict], artifacts: list[str]):
    """Process ZAP security scan results."""
    zap_security_score = item.get('securityScore', 0)
    alerts = item.get('alerts', [])

    # Use the lower of header analysis and ZAP scan scores
    scores['security'] = min(scores['security'] or 100, zap_security_score)

    # Add ZAP findings
    for alert in alerts:
        risk_level = alert.get('risk', '').split()[0].lower()
        severity = 'critical' if risk_level == 'high' else 'high' if risk_level == 'medium' else 'medium'

        findings.append({
            'category': 'security',
            'severity': severity,
            'summary': alert.get('name', ''),
            'evidence': {
                'risk': alert.get('risk'),
                'instances': alert.get('instances', 0)
            },
            'recommendation': alert.get('solution', 'Review security alert')
        })

def _process_responsive_results(item: dict[str, Any], scores: dict[str, float], findings: list[dict], artifacts: list[str]):
    """Process responsive design results."""
    responsive_score = item.get('responsiveScore', 0)
    summaries = item.get('summaries', [])

    scores['responsive'] = responsive_score

    # Add responsive findings
    for summary in summaries:
        viewport = summary.get('viewport')
        overflow_count = summary.get('overflowCount', 0)
        bad_tap_targets = summary.get('badTapTargets', 0)

        if overflow_count > 0:
            findings.append({
                'category': 'responsive',
                'severity': 'medium',
                'summary': f'Horizontal overflow detected on {viewport}',
                'evidence': {'viewport': viewport, 'overflowCount': overflow_count},
                'recommendation': 'Fix horizontal scrolling issues'
            })

        if bad_tap_targets > 0:
            findings.append({
                'category': 'responsive',
                'severity': 'medium',
                'summary': f'Small tap targets detected on {viewport}',
                'evidence': {'viewport': viewport, 'badTapTargets': bad_tap_targets},
                'recommendation': 'Increase tap target sizes to at least 44px'
            })

        # Add screenshot artifacts
        if summary.get('screenshotPath'):
            artifacts.append(summary['screenshotPath'])

def _process_webhint_results(item: dict[str, Any], scores: dict[str, Any], findings: list[dict], artifacts: list[str]):
    """Process webhint results."""
    hints = item.get('hints', [])

    # Add webhint findings (affects multiple categories)
    for hint in hints:
        hint_id = hint.get('hintId', '')
        category = 'seo'  # Default category

        # Map hint types to categories
        if 'accessibility' in hint_id or 'axe' in hint_id:
            category = 'a11y'
        elif 'performance' in hint_id or 'speed' in hint_id:
            category = 'perf'
        elif 'security' in hint_id or 'https' in hint_id:
            category = 'security'

        severity_map = {'error': 'high', 'warning': 'medium', 'hint': 'low'}
        severity = severity_map.get(hint.get('severity', 'hint'), 'medium')

        findings.append({
            'category': category,
            'severity': severity,
            'summary': hint.get('message', ''),
            'evidence': {
                'hintId': hint_id,
                'resource': hint.get('resource')
            },
            'recommendation': f'Address {hint_id} issue'
        })

def _map_axe_impact_to_severity(impact: str) -> str:
    """Map axe impact levels to severity levels."""
    mapping = {
        'critical': 'critical',
        'serious': 'high',
        'moderate': 'medium',
        'minor': 'low'
    }
    return mapping.get(impact, 'medium')

def _apply_budgets(scores: dict[str, float], findings: list[dict], budgets: dict[str, Any]) -> dict[str, Any]:
    """Apply budget thresholds and return results."""
    budget_results = {}

    for category, threshold in budgets.items():
        if category in scores:
            passed = scores[category] >= threshold
            budget_results[category] = {
                'threshold': threshold,
                'actual': scores[category],
                'passed': passed
            }

    return budget_results

def _generate_summary(scores: dict[str, float], findings: list[dict]) -> dict[str, Any]:
    """Generate a summary of the audit results."""
    critical_findings = [f for f in findings if f.get('severity') == 'critical']
    high_findings = [f for f in findings if f.get('severity') == 'high']

    return {
        'overallScore': scores.get('global', 0),
        'totalFindings': len(findings),
        'criticalFindings': len(critical_findings),
        'highFindings': len(high_findings),
        'topIssues': [f['summary'] for f in critical_findings + high_findings][:5]
    }

def _generate_html_report(report_data: dict[str, Any]) -> str:
    """Generate HTML report from report data."""
    scores = report_data['score']
    findings = report_data['findings']
    summary = report_data['summary']

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Audit Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f5f5f5; padding: 20px; border-radius: 8px; }}
        .score-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
        .score-card {{ background: white; border: 1px solid #ddd; padding: 15px; border-radius: 8px; text-align: center; }}
        .score {{ font-size: 2em; font-weight: bold; }}
        .score.good {{ color: #4CAF50; }}
        .score.average {{ color: #FF9800; }}
        .score.poor {{ color: #F44336; }}
        .findings {{ margin: 20px 0; }}
        .finding {{ background: white; border-left: 4px solid #ddd; padding: 15px; margin: 10px 0; }}
        .finding.critical {{ border-left-color: #F44336; }}
        .finding.high {{ border-left-color: #FF9800; }}
        .finding.medium {{ border-left-color: #2196F3; }}
        .finding.low {{ border-left-color: #4CAF50; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Web Audit Report</h1>
        <p>Generated: {report_data['timestamp']}</p>
        <p>Overall Score: <strong>{scores.get('global', 0):.1f}/100</strong></p>
    </div>

    <div class="score-grid">
        <div class="score-card">
            <div class="score {_get_score_class(scores.get('perf', 0))}">{scores.get('perf', 0):.0f}</div>
            <div>Performance</div>
        </div>
        <div class="score-card">
            <div class="score {_get_score_class(scores.get('a11y', 0))}">{scores.get('a11y', 0):.0f}</div>
            <div>Accessibility</div>
        </div>
        <div class="score-card">
            <div class="score {_get_score_class(scores.get('seo', 0))}">{scores.get('seo', 0):.0f}</div>
            <div>SEO</div>
        </div>
        <div class="score-card">
            <div class="score {_get_score_class(scores.get('security', 0))}">{scores.get('security', 0):.0f}</div>
            <div>Security</div>
        </div>
        <div class="score-card">
            <div class="score {_get_score_class(scores.get('responsive', 0))}">{scores.get('responsive', 0):.0f}</div>
            <div>Responsive</div>
        </div>
    </div>

    <h2>Summary</h2>
    <ul>
        <li>Total Findings: {summary.get('totalFindings', 0)}</li>
        <li>Critical Issues: {summary.get('criticalFindings', 0)}</li>
        <li>High Priority Issues: {summary.get('highFindings', 0)}</li>
    </ul>

    <h2>Findings</h2>
    <div class="findings">
"""

    for finding in findings:
        severity = finding.get('severity', 'medium')
        html += f"""
        <div class="finding {severity}">
            <h3>{finding.get('summary', 'Unknown Issue')}</h3>
            <p><strong>Category:</strong> {finding.get('category', 'Unknown').upper()}</p>
            <p><strong>Severity:</strong> {severity.upper()}</p>
            <p><strong>Recommendation:</strong> {finding.get('recommendation', 'No recommendation available')}</p>
        </div>
"""

    html += """
    </div>
</body>
</html>
"""

    return html

def _get_score_class(score: float) -> str:
    """Get CSS class for score color."""
    if score >= 80:
        return 'good'
    elif score >= 60:
        return 'average'
    else:
        return 'poor'