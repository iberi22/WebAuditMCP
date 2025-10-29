#!/usr/bin/env node
/**
 * Responsive design audit using Playwright
 */

const { chromium } = require('playwright');
const path = require('node:path');
const fs = require('node:fs');

async function runResponsiveAudit(url, viewports) {
  let browser;

  try {
    // Launch browser
    browser = await chromium.launch({ headless: true });

    const results = {
      url: url,
      timestamp: new Date().toISOString(),
      summaries: [],
    };

    // Create artifacts directory
    const artifactsDir = path.join(__dirname, '..', 'artifacts');
    if (!fs.existsSync(artifactsDir)) {
      fs.mkdirSync(artifactsDir, { recursive: true });
    }

    // Test each viewport
    for (const viewport of viewports) {
      const [width, height] = viewport.split('x').map(Number);

      if (!width || !height) {
        console.error(`Invalid viewport format: ${viewport}. Use format: 360x640`);
        continue;
      }

      const context = await browser.newContext({
        viewport: { width, height },
      });

      const page = await context.newPage();

      try {
        // Navigate to URL
        await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });

        // Take screenshot
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const screenshotPath = path.join(
          artifactsDir,
          `screenshot-${width}x${height}-${timestamp}.png`
        );
        await page.screenshot({ path: screenshotPath, fullPage: true });

        // Check for horizontal overflow
        const overflowElements = await page.evaluate(() => {
          /* eslint-env browser */
          const elements = document.querySelectorAll('*');
          const overflowing = [];

          for (const element of elements) {
            const rect = element.getBoundingClientRect();
            if (rect.width > window.innerWidth) {
              overflowing.push({
                tagName: element.tagName,
                className: element.className,
                id: element.id,
              });
            }
          }

          return overflowing;
        });

        // Check tap target sizes
        const smallTapTargets = await page.evaluate(() => {
          /* eslint-env browser */
          const minTapSize = 44; // 44px minimum recommended
          const clickableSelectors =
            'a, button, input[type="button"], input[type="submit"], [onclick], [role="button"]';
          const clickableElements = document.querySelectorAll(clickableSelectors);
          const smallTargets = [];

          for (const element of clickableElements) {
            const rect = element.getBoundingClientRect();
            if (rect.width < minTapSize || rect.height < minTapSize) {
              smallTargets.push({
                tagName: element.tagName,
                className: element.className,
                id: element.id,
                width: rect.width,
                height: rect.height,
              });
            }
          }

          return smallTargets;
        });

        // Add summary for this viewport
        results.summaries.push({
          viewport: viewport,
          width: width,
          height: height,
          screenshotPath: screenshotPath,
          overflowCount: overflowElements.length,
          overflowElements: overflowElements.slice(0, 5), // Limit to first 5
          badTapTargets: smallTapTargets.length,
          smallTapTargets: smallTapTargets.slice(0, 5), // Limit to first 5
        });
      } catch (error) {
        results.summaries.push({
          viewport: viewport,
          width: width,
          height: height,
          error: error.message,
        });
      } finally {
        await context.close();
      }
    }

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
if (args.length < 2) {
  console.error('Usage: node responsive.js <url> <viewport1> [viewport2] [viewport3] ...');
  console.error('Example: node responsive.js https://example.com 360x640 768x1024 1280x800');
  process.exit(1);
}

const url = args[0];
const viewports = args.slice(1);

// Validate URL
if (!url.startsWith('http://') && !url.startsWith('https://')) {
  console.error('URL must start with http:// or https://');
  process.exit(1);
}

// Validate viewports
for (const viewport of viewports) {
  if (!/^\d+x\d+$/.test(viewport)) {
    console.error(`Invalid viewport format: ${viewport}. Use format: 360x640`);
    process.exit(1);
  }
}

// Run the audit
runResponsiveAudit(url, viewports).catch((error) => {
  console.error(
    JSON.stringify({
      error: error.message,
      stack: error.stack,
    })
  );
  process.exit(1);
});
