# OWASP Security Vulnerability Scan

## Objective

Identify common web vulnerabilities (SQL Injection, XSS, CSRF, etc.) using OWASP ZAP baseline scanner.

## Execution

```javascript
const targetUrl = "https://example.com";
const zapScan = await zap_baseline(targetUrl, 10); // 10-minute scan
```

## Report Template

# Security Vulnerability Report

**Target:** [URL]
**Scan Type:** OWASP ZAP Baseline
**Duration:** 10 minutes

## Risk Summary

| Risk Level | Count | Action Required |
|------------|-------|-----------------|
| High | X | Immediate fix |
| Medium | X | Fix within 30 days |
| Low | X | Review and address |
| Informational | X | For awareness |

## High-Risk Vulnerabilities

### 1. SQL Injection (CWE-89)

**Affected Endpoint:** `/api/search?query=`
**CVSS Score:** 9.8 (Critical)
**Proof of Concept:**

```
GET /api/search?query=' OR '1'='1
Response: Database error exposed
```

**Fix (Parameterized Queries):**

```javascript
// ❌ Vulnerable
const query = `SELECT * FROM users WHERE id = '${userId}'`;

// ✅ Secure
const query = 'SELECT * FROM users WHERE id = ?';
db.execute(query, [userId]);
```

### 2. Cross-Site Scripting (XSS) - Reflected

**Location:** Comment form
**CVSS Score:** 6.1 (Medium)

**Fix:**

```javascript
// Sanitize all user input
import DOMPurify from 'dompurify';
const clean = DOMPurify.sanitize(userInput);
```

### 3. Missing CSRF Protection

**Forms Affected:** Login, registration
**Fix:** Implement CSRF tokens

```javascript
// Express.js
const csrf = require('csurf');
app.use(csrf({ cookie: true }));
```

## Medium-Risk Issues

### 4. Information Disclosure

**Issue:** Server headers expose technology stack
**Fix:** Remove or obfuscate `X-Powered-By` header

### 5. Unvalidated Redirects

**Endpoint:** `/redirect?url=`
**Fix:** Whitelist allowed redirect domains

## Remediation Priority

1. **Critical (24h):** Fix SQL injection, implement input validation
2. **High (7 days):** Add CSRF tokens, sanitize XSS vectors
3. **Medium (30 days):** Remove information disclosure, fix redirects

## Compliance Impact

- **OWASP Top 10 2021:** A03 (Injection) ❌
- **PCI DSS:** Requirement 6.5 ❌
- **SOC 2:** CC6.1 (Logical Access) ⚠️

## Verification

- [ ] Re-scan after fixes
- [ ] Penetration test by security team
- [ ] WAF rules updated

**Next Scan:** [Scheduled date]
