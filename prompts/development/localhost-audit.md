# Localhost Development Audit

**Optimized for local development servers - fast feedback in under 1 minute**

## Quick Development Audit

Using WebAuditMCP, perform a fast development audit of the localhost URL:

### Phase 1: Instant Checks (< 10 seconds)
1. Run `security_headers` to check HTTP security headers
2. Run `health_check` to verify all tools are working

### Phase 2: Fast Visual/UX Audit (< 30 seconds)
3. Run `lighthouse_fast` for basic performance metrics only
4. Run `responsive_audit` with viewports: ["375x667", "1024x768"]

### Phase 3: Accessibility (< 60 seconds)
5. Run `scan_axe` for WCAG compliance check

### Report Format
Generate a concise development report with:

```markdown
# Development Audit Report
**URL:** [URL]
**Date:** [Current Date]

## 🚀 Performance (Fast Mode)
- Score: [X]/100
- FCP: [X]ms
- LCP: [X]ms
- CLS: [X]

## 🔒 Security Headers
- Found: [X]/[Total] headers
- Missing: [List critical missing headers]

## 📱 Responsive Design
- Tested viewports: Mobile (375x667), Desktop (1024x768)
- Issues found: [X]
- Critical issues: [List any overflow or tap target problems]

## ♿ Accessibility
- Violations: [X]
- Critical: [List critical a11y issues]

## 🎯 Development Recommendations
1. [Most important fix]
2. [Second priority]
3. [Third priority]

## ⚡ Next Steps
- Fix critical issues above
- Run full `audit_lighthouse` when ready for production
- Consider `zap_baseline` for security testing
```

**Note:** This audit is optimized for speed during development. For production-ready audits, use the complete audit prompts.