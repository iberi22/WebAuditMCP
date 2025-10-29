#!/usr/bin/env node
/**
 * Axe accessibility scanning using Playwright
 */

const { chromium } = require('playwright');
const { AxeBuilder } = require('@axe-core/playwright');

async function runAxeScan(url, device = 'mobile') {
  let browser;

  try {
    // Launch browser
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
      viewport: device === 'mobile' ? { width: 375, height: 667 } : { width: 1280, height: 800 },
      userAgent:
        device === 'mobile'
          ? 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
          : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    });

    const page = await context.newPage();

    // Navigate to URL
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });

    // Run accessibility scan with AxeBuilder
    const results = await new AxeBuilder({ page }).analyze();

    // Output results as JSON
    console.log(JSON.stringify(results, null, 2));
  } catch (error) {
    console.error(
      JSON.stringify({
        error: error.message,
        stack: error.stack,
      })
    );
    process.exit(1);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

// Parse command line arguments
const args = process.argv.slice(2);
if (args.length < 1) {
  console.error('Usage: node axe-playwright.js <url> [device]');
  process.exit(1);
}

const url = args[0];
const device = args[1] || 'mobile';

// Validate URL
if (!url.startsWith('http://') && !url.startsWith('https://')) {
  console.error('URL must start with http:// or https://');
  process.exit(1);
}

// Run the scan
runAxeScan(url, device).catch((error) => {
  console.error(
    JSON.stringify({
      error: error.message,
      stack: error.stack,
    })
  );
  process.exit(1);
});
