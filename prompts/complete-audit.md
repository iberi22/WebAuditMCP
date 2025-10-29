# Complete Website Audit - Professional Prompt

## Objective
Perform a comprehensive, production-ready audit of the target website covering performance, security, accessibility, SEO, and visual design. Generate a single Markdown report suitable for stakeholder review and AI-driven iteration.

## Instructions for AI Agent

### 1. Pre-Audit Checklist
- Verify WebAuditMCP server is running (`health_check()`)
- Confirm target URL is accessible
- Check if localhost: ensure development server is running
- Note baseline scores if previous audit exists

### 2. Execute Full Audit Suite

Run the following tools in sequence:

```javascript
const targetUrl = "https://example.com"; // Replace with actual URL

// 1. Performance & Best Practices
const lighthouseMobile = await audit_lighthouse(targetUrl, "mobile");
const lighthouseDesktop = await audit_lighthouse(targetUrl, "desktop");

// 2. Accessibility
const axeResults = await scan_axe(targetUrl, "desktop");
const waveResults = await scan_wave(targetUrl, "json");

// 3. Security
const securityHeaders = await security_headers(targetUrl);
const zapScan = await zap_baseline(targetUrl, 10); // 10-minute scan

// 4. Best Practices
const webhintResults = await webhint_scan(targetUrl);

// 5. Responsive Design
const responsiveResults = await responsive_audit(targetUrl, [
  "375x667",   // iPhone SE
  "390x844",   // iPhone 12/13/14
  "768x1024",  // iPad Portrait
  "1920x1080"  // Desktop FHD
]);

// 6. Consolidate Results
const mergedReport = await report_merge(
  [lighthouseMobile, lighthouseDesktop, axeResults, securityHeaders, responsiveResults],
  {
    accessibility: 95,
    performance: 90,
    security: 85,
    bestPractices: 90,
    seo: 85
  }
);
```

### 3. Report Structure

Generate a **single Markdown file** with the following sections:

---

## Executive Summary

**Audit Date:** [Timestamp]
**Target URL:** [URL]
**Audit Type:** Complete Website Audit
**Overall Score:** [X/100]

### Quick Metrics

| Category | Score | Status | Budget |
|----------|-------|--------|--------|
| Performance | XX/100 | 🟢/🟡/🔴 | 90 |
| Accessibility | XX/100 | 🟢/🟡/🔴 | 95 |
| Security | XX/100 | 🟢/🟡/🔴 | 85 |
| SEO | XX/100 | 🟢/🟡/🔴 | 85 |
| Best Practices | XX/100 | 🟢/🟡/🔴 | 90 |
| Responsive Design | XX/100 | 🟢/🟡/🔴 | 80 |

**Legend:** 🟢 Pass (≥Budget) | 🟡 Warning (<Budget, >70) | 🔴 Fail (≤70)

---

## Critical Issues (Priority 1)

List issues that **must** be fixed before production:

1. **[Category] - [Issue Title]**
   - **Severity:** Critical
   - **Impact:** [User impact description]
   - **Affected Users:** [Percentage or user group]
   - **Fix:** [Specific, actionable steps]
   - **Effort:** [Hours/Days estimate]
   - **References:** [Links to documentation]

---

## High Priority Issues (Priority 2)

Issues that should be fixed soon:

[Same format as Critical Issues]

---

## Performance Analysis

### Core Web Vitals

| Metric | Mobile | Desktop | Target | Status |
|--------|--------|---------|--------|--------|
| LCP (Largest Contentful Paint) | X.Xs | X.Xs | ≤2.5s | 🟢/🔴 |
| FID (First Input Delay) | XXXms | XXXms | ≤100ms | 🟢/🔴 |
| CLS (Cumulative Layout Shift) | 0.XX | 0.XX | ≤0.1 | 🟢/🔴 |
| TBT (Total Blocking Time) | XXXms | XXXms | ≤200ms | 🟢/🔴 |
| Speed Index | X.Xs | X.Xs | ≤3.4s | 🟢/🔴 |

### Performance Recommendations

1. **[Optimization Title]**
   - Current: [Metric]
   - Target: [Metric]
   - Impact: [Expected improvement]
   - Implementation: [Steps]

---

## Accessibility Compliance

### WCAG 2.1 Level AA Status

**Total Violations:** X
**Serious Issues:** X
**Moderate Issues:** X
**Minor Issues:** X

### Top Accessibility Issues

1. **[Issue Type] - [WCAG Criterion]**
   - **Affected Elements:** X occurrences
   - **User Impact:** [Screen reader, keyboard, visual impairment impact]
   - **Fix:**
     ```html
     <!-- Before -->
     <div>Click here</div>

     <!-- After -->
     <button aria-label="Submit form">Click here</button>
     ```
   - **WCAG Reference:** [Link to WCAG documentation]

---

## Security Assessment

### Security Score: XX/100

**Critical Vulnerabilities:** X
**High Risk:** X
**Medium Risk:** X
**Low Risk:** X

### Missing Security Headers

| Header | Status | Recommendation |
|--------|--------|----------------|
| Content-Security-Policy | ❌ Missing | `Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline';` |
| Strict-Transport-Security | ✅ Present | - |
| X-Frame-Options | ❌ Missing | `X-Frame-Options: DENY` |
| X-Content-Type-Options | ✅ Present | - |
| Referrer-Policy | ❌ Missing | `Referrer-Policy: strict-origin-when-cross-origin` |
| Permissions-Policy | ❌ Missing | `Permissions-Policy: geolocation=(), microphone=()` |

### Vulnerabilities Found

[List vulnerabilities from OWASP ZAP scan if any]

---

## SEO & Best Practices

### SEO Score: XX/100

**Issues Found:**

1. **[Issue Title]**
   - **Impact:** [Ranking/crawlability impact]
   - **Fix:** [Specific implementation]

### Best Practices Violations

[List from webhint and Lighthouse]

---

## Responsive Design Analysis

### Viewport Testing Results

| Device | Viewport | Overflow Issues | Tap Target Issues | Score |
|--------|----------|-----------------|-------------------|-------|
| iPhone SE | 375x667 | 0 | 2 | 90/100 |
| iPhone 14 | 390x844 | 0 | 1 | 95/100 |
| iPad | 768x1024 | 0 | 0 | 100/100 |
| Desktop | 1920x1080 | 0 | 0 | 100/100 |

### Responsive Issues

1. **Small Tap Targets on Mobile**
   - **Elements:** [List elements with dimensions]
   - **Minimum Size:** 48x48px (WCAG 2.1 AA)
   - **Current Size:** [Dimensions]
   - **Fix:** Increase padding/button size

---

## Recommendations Summary

### Quick Wins (≤4 hours effort)

1. [Issue] - [Expected impact] - [Effort]
2. [Issue] - [Expected impact] - [Effort]

### Medium Effort (1-2 days)

1. [Issue] - [Expected impact] - [Effort]

### Long-term Improvements (>2 days)

1. [Issue] - [Expected impact] - [Effort]

---

## Comparison with Baseline

*(If previous audit exists)*

| Metric | Previous | Current | Change |
|--------|----------|---------|--------|
| Overall Score | XX | XX | +/- X |
| Performance | XX | XX | +/- X |
| Accessibility | XX | XX | +/- X |
| Security | XX | XX | +/- X |

---

## Action Plan

### Immediate (This Sprint)

- [ ] Fix critical security headers
- [ ] Resolve WCAG violations
- [ ] Optimize LCP (target: <2.5s)

### Short-term (Next Sprint)

- [ ] Implement lazy loading for images
- [ ] Add service worker for offline support
- [ ] Fix responsive tap targets

### Long-term (Next Quarter)

- [ ] Complete CSP implementation
- [ ] Achieve 100/100 Lighthouse scores
- [ ] Implement visual regression testing

---

## Artifacts Generated

- **Lighthouse Mobile Report:** `[path/to/lighthouse-mobile.json]`
- **Lighthouse Desktop Report:** `[path/to/lighthouse-desktop.json]`
- **axe Accessibility Report:** `[path/to/axe-report.json]`
- **Security Headers Analysis:** `[path/to/security-headers.json]`
- **Responsive Screenshots:** `[path/to/screenshots/*.png]`
- **OWASP ZAP Scan:** `[path/to/zap-baseline.json]`

---

## Next Steps for AI Iteration

1. **Prioritize fixes:** Focus on Critical and High Priority issues first
2. **Implement recommendations:** Use code examples provided above
3. **Re-audit:** Run this same audit after fixes to measure improvement
4. **Track progress:** Compare with baseline scores
5. **Automate:** Integrate this audit into CI/CD pipeline

---

**Generated by:** WebAuditMCP
**Report Version:** 1.0
**AI Agent:** [Your agent name]
**Date:** [ISO 8601 timestamp]
