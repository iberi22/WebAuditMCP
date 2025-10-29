#!/usr/bin/env node
/**
 * Security headers analysis using Playwright
 */

const { chromium } = require('playwright');

async function analyzeSecurityHeaders(url) {
  let browser;

  try {
    // Launch browser
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page = await context.newPage();

    let responseHeaders = {};

    // Capture response headers
    page.on('response', async (response) => {
      if (response.url() === url) {
        responseHeaders = response.headers();
      }
    });

    // Navigate to URL
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });

    // Analyze security headers
    const analysis = {
      url: url,
      timestamp: new Date().toISOString(),
      headers: responseHeaders,
      security: {
        'content-security-policy': !!responseHeaders['content-security-policy'],
        'strict-transport-security': !!responseHeaders['strict-transport-security'],
        'x-frame-options': !!responseHeaders['x-frame-options'],
        'x-content-type-options': !!responseHeaders['x-content-type-options'],
        'referrer-policy': !!responseHeaders['referrer-policy'],
        'permissions-policy': !!(
          responseHeaders['permissions-policy'] || responseHeaders['feature-policy']
        ),
      },
    };

    // Calculate security score
    const securityChecks = Object.values(analysis.security);
    const passedChecks = securityChecks.filter(Boolean).length;
    analysis.securityScore = (passedChecks / securityChecks.length) * 100;

    // Output results as JSON
    console.log(JSON.stringify(analysis, null, 2));
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
  console.error(
    JSON.stringify({
      error: 'Usage: node security-headers.js <url>',
    })
  );
  process.exit(1);
}

const url = args[0];

// Validate URL
if (!url.startsWith('http://') && !url.startsWith('https://')) {
  console.error(
    JSON.stringify({
      error: 'URL must start with http:// or https://',
    })
  );
  process.exit(1);
}

// Run the analysis
analyzeSecurityHeaders(url).catch((error) => {
  console.error(
    JSON.stringify({
      error: error.message,
      stack: error.stack,
    })
  );
  process.exit(1);
});
