# Color Contrast & Accessibility Audit

## Objective

Verify color contrast ratios meet WCAG 2.1 Level AA standards (4.5:1 for normal text, 3:1 for large text).

## Execution

```javascript
const targetUrl = "https://example.com";
const axeResults = await scan_axe(targetUrl, "desktop");
// Filter for color-contrast violations
const contrastIssues = axeResults.violations.filter(v => v.id === 'color-contrast');
```

## Report Template

# Color Contrast Audit Report

**Standard:** WCAG 2.1 Level AA
**URL:** [Target]

## Contrast Violations

| Element | Foreground | Background | Ratio | Required | Status |
|---------|------------|------------|-------|----------|--------|
| Body text | #999 | #FFF | 2.8:1 | 4.5:1 | ❌ Fail |
| Button text | #AAA | #333 | 3.2:1 | 4.5:1 | ❌ Fail |
| Link hover | #0066CC | #E0E0E0 | 3.5:1 | 4.5:1 | ❌ Fail |
| Large heading | #666 | #FFF | 5.7:1 | 3:1 | ✅ Pass |

## Critical Fixes

### 1. Body Text Contrast

**Current:** `color: #999` on white background (2.8:1)
**Required:** 4.5:1 minimum

**Fix:**

```css
body {
  color: #666; /* Ratio: 5.7:1 ✅ */
}
```

### 2. Button Text

**Fix:**

```css
.btn-primary {
  background: #0066CC;
  color: #FFFFFF; /* Ratio: 7.0:1 ✅ */
}
```

## Color Palette Recommendations

### Accessible Color Pairs

| Use Case | Foreground | Background | Ratio |
|----------|------------|------------|-------|
| Body text | #333333 | #FFFFFF | 12.6:1 ✅ |
| Links | #0066CC | #FFFFFF | 7.0:1 ✅ |
| Buttons | #FFFFFF | #0066CC | 7.0:1 ✅ |
| Warnings | #663C00 | #FFF4E5 | 7.4:1 ✅ |
| Errors | #8B0000 | #FFEBEE | 8.1:1 ✅ |

## Testing Tools

- Use WebAIM Contrast Checker: <https://webaim.org/resources/contrastchecker/>
- Browser DevTools: Chrome Lighthouse shows contrast issues
- Manual verification with color picker

## Action Items

- [ ] Update body text color from #999 to #666
- [ ] Fix all button contrast ratios
- [ ] Test with colorblind simulators
- [ ] Document brand-compliant accessible colors

**Status:** ❌ 4 critical violations found
