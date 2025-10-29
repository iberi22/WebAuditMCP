# Security Headers Audit - Professional Prompt

## Objective

Analyze HTTP security headers and provide remediation steps for missing or misconfigured headers. Generate actionable security hardening recommendations.

## Execution

```javascript
const targetUrl = "https://example.com";
const securityAnalysis = await security_headers(targetUrl);
```

## Report Template

# Security Headers Audit Report

**Target:** [URL]
**Date:** [Timestamp]
**Overall Security Score:** [X/100]

## Security Posture Summary

| Header | Status | Risk Level | Priority |
|--------|--------|------------|----------|
| Content-Security-Policy | ❌/✅ | Critical | P0 |
| Strict-Transport-Security | ❌/✅ | Critical | P0 |
| X-Frame-Options | ❌/✅ | High | P1 |
| X-Content-Type-Options | ❌/✅ | Medium | P2 |
| Referrer-Policy | ❌/✅ | Medium | P2 |
| Permissions-Policy | ❌/✅ | Low | P3 |

## Critical Issues

### 1. Missing Content-Security-Policy (CSP)

**Risk:** Allows XSS attacks, inline scripts, and unsafe eval()
**Impact:** High - Can lead to data theft, session hijacking
**CVSS Score:** 7.5 (High)

**Recommended Header:**

```
Content-Security-Policy:
  default-src 'self';
  script-src 'self' https://cdn.trusted.com;
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  font-src 'self' https://fonts.gstatic.com;
  connect-src 'self' https://api.yourapp.com;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
```

**Implementation (Next.js):**

```typescript
// next.config.ts
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: "default-src 'self'; script-src 'self'"
  }
];

export default {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: securityHeaders,
      },
    ];
  },
};
```

### 2. Missing HSTS Header

**Risk:** Vulnerable to man-in-the-middle attacks
**Impact:** High - Users can be downgraded to HTTP

**Recommended Header:**

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

**Implementation:**

```nginx
# Nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

# Apache
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
```

## Medium Priority

### 3. X-Frame-Options

**Recommended:** `X-Frame-Options: DENY`

### 4. Referrer-Policy

**Recommended:** `Referrer-Policy: strict-origin-when-cross-origin`

## Action Items

- [ ] Implement CSP header (start with report-only mode)
- [ ] Add HSTS with 1-year max-age
- [ ] Configure X-Frame-Options
- [ ] Test headers with securityheaders.com
- [ ] Monitor CSP violations

## Compliance

- **OWASP Top 10 2021:** A05:2021 – Security Misconfiguration ✅
- **PCI DSS 3.2:** Requirement 6.5.10 ✅

---

**Next Audit:** Schedule re-scan after implementation
