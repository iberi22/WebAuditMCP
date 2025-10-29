# Responsive Design Audit

## Objective

Test website across multiple viewports to ensure optimal mobile, tablet, and desktop experiences.

## Execution

```javascript
const targetUrl = "https://example.com";
const responsive = await responsive_audit(targetUrl, [
  "375x667",   // iPhone SE
  "390x844",   // iPhone 14
  "768x1024",  // iPad
  "1920x1080"  // Desktop
]);
```

## Report Template

# Responsive Design Report

**URL:** [Target]
**Devices Tested:** 4 viewports

## Test Results

| Device | Viewport | Layout Score | Tap Targets | Overflow | Screenshot |
|--------|----------|--------------|-------------|----------|------------|
| iPhone SE | 375x667 | 85/100 | 2 issues | 0 | [Link] |
| iPhone 14 | 390x844 | 90/100 | 1 issue | 0 | [Link] |
| iPad | 768x1024 | 95/100 | 0 | 0 | [Link] |
| Desktop | 1920x1080 | 100/100 | 0 | 0 | [Link] |

## Issues Found

### 1. Small Tap Targets (Mobile)

**Affected Elements:**
- Close button: 32x32px (needs 48x48px)
- Social icons: 36x36px

**Fix:**

```css
.close-button {
  min-width: 48px;
  min-height: 48px;
  padding: 12px;
}
```

### 2. Text Too Small

**Element:** `.caption` at 12px
**Fix:** Minimum 16px for body text

### 3. Horizontal Scroll on iPhone SE

**Cause:** Fixed-width element (400px)
**Fix:** Use `max-width: 100%`

## Viewport Meta Tag

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

## Action Items

- [ ] Increase tap target sizes to 48x48px minimum
- [ ] Fix horizontal overflow issues
- [ ] Test with real devices
- [ ] Validate font sizes (16px+ for body)

**Status:** 🟡 Needs improvement
