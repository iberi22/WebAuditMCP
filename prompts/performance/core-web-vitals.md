# Core Web Vitals & Performance Audit

## Objective

Measure and optimize Core Web Vitals (LCP, FID, CLS) for optimal user experience and SEO rankings.

## Execution

```javascript
const targetUrl = "https://example.com";
const mobile = await audit_lighthouse(targetUrl, "mobile");
const desktop = await audit_lighthouse(targetUrl, "desktop");
```

## Report Template

# Performance Audit Report

**URL:** [Target]
**Test Date:** [Timestamp]

## Core Web Vitals

| Metric | Mobile | Desktop | Target | Status |
|--------|--------|---------|--------|--------|
| **LCP** (Largest Contentful Paint) | X.Xs | X.Xs | ≤2.5s | 🟢/🔴 |
| **FID** (First Input Delay) | XXms | XXms | ≤100ms | 🟢/🔴 |
| **CLS** (Cumulative Layout Shift) | 0.XX | 0.XX | ≤0.1 | 🟢/🔴 |
| **FCP** (First Contentful Paint) | X.Xs | X.Xs | ≤1.8s | 🟢/🔴 |
| **TTI** (Time to Interactive) | X.Xs | X.Xs | ≤3.8s | 🟢/🔴 |
| **TBT** (Total Blocking Time) | XXms | XXms | ≤200ms | 🟢/🔴 |
| **Speed Index** | X.Xs | X.Xs | ≤3.4s | 🟢/🔴 |

## Performance Score

**Mobile:** XX/100
**Desktop:** XX/100

## Critical Performance Issues

### 1. Slow LCP (X.Xs)

**Root Cause:** Large hero image (2.5MB)
**Impact:** -15 points on Lighthouse score

**Fix:**

```html
<!-- Use responsive images with WebP -->
<picture>
  <source srcset="/hero.webp" type="image/webp" />
  <img src="/hero.jpg" alt="Hero" loading="eager" fetchpriority="high" />
</picture>
```

**Expected Improvement:** LCP: 5.2s → 2.1s

### 2. Layout Shift from Web Fonts

**Current CLS:** 0.25
**Fix:** Use `font-display: optional` and preload fonts

```css
@font-face {
  font-family: 'Inter';
  font-display: optional;
  src: url('/fonts/inter.woff2') format('woff2');
}
```

### 3. Render-Blocking Resources

**Blocking:** 450ms from external CSS
**Fix:** Inline critical CSS, defer non-critical

## Optimization Checklist

- [ ] Compress images (target: <100KB per image)
- [ ] Implement lazy loading for below-fold images
- [ ] Minify JavaScript (-30% bundle size)
- [ ] Enable Brotli compression
- [ ] Add resource hints (preload, prefetch)
- [ ] Optimize font loading strategy

## Bundle Analysis

| Resource | Size | Impact |
|----------|------|--------|
| main.js | 250KB | High |
| vendor.js | 180KB | High |
| styles.css | 45KB | Medium |

**Recommendation:** Code split vendor bundles

## Expected Results After Optimization

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| LCP | 5.2s | 2.1s | ⬇️ 60% |
| CLS | 0.25 | 0.05 | ⬇️ 80% |
| Performance Score | 62 | 90+ | ⬆️ 28 points |

---

**Retest:** After implementing optimizations
