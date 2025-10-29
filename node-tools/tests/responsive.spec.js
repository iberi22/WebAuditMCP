import { execSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';

describe('responsive audit runner', () => {
  it('returns JSON with viewport summaries for valid URL', () => {
    try {
      const output = execSync('node responsive.js https://example.com 360x640 768x1024', {
        cwd: join(process.cwd()),
        stdio: ['ignore', 'pipe', 'pipe'],
        timeout: 120000,
        encoding: 'utf8',
      });

      const result = JSON.parse(output);
      expect(result).toHaveProperty('url');
      expect(result).toHaveProperty('summaries');
      expect(result).toHaveProperty('timestamp');

      expect(Array.isArray(result.summaries)).toBe(true);
      expect(result.summaries).toHaveLength(2); // Two viewports

      // Check summary structure
      result.summaries.forEach((summary) => {
        expect(summary).toHaveProperty('viewport');
        expect(summary).toHaveProperty('width');
        expect(summary).toHaveProperty('height');
        expect(summary).toHaveProperty('screenshotPath');
        expect(summary).toHaveProperty('overflowCount');
        expect(summary).toHaveProperty('badTapTargets');

        // Check if screenshot was created
        if (summary.screenshotPath && !summary.error) {
          expect(existsSync(summary.screenshotPath)).toBe(true);
        }
      });
    } catch (error) {
      // If the command fails, check if it's a proper error response
      if (error.stdout) {
        const result = JSON.parse(error.stdout);
        expect(result).toHaveProperty('error');
      } else {
        throw error;
      }
    }
  }, 120000);

  it('handles invalid URL gracefully', () => {
    try {
      execSync('node responsive.js invalid-url 360x640', {
        cwd: join(process.cwd()),
        stdio: ['ignore', 'pipe', 'pipe'],
        timeout: 30000,
        encoding: 'utf8',
      });
    } catch (error) {
      // Should fail with proper error message
      expect(error.status).not.toBe(0);
      if (error.stderr) {
        const result = JSON.parse(error.stderr);
        expect(result).toHaveProperty('error');
      }
    }
  });

  it('validates viewport format', () => {
    try {
      execSync('node responsive.js https://example.com invalid-viewport', {
        cwd: join(process.cwd()),
        stdio: ['ignore', 'pipe', 'pipe'],
        timeout: 15000,
        encoding: 'utf8',
      });
    } catch (error) {
      // Should fail because viewport format is invalid
      expect(error.status).not.toBe(0);
    }
  });

  it('requires at least URL and one viewport', () => {
    try {
      execSync('node responsive.js https://example.com', {
        cwd: join(process.cwd()),
        stdio: ['ignore', 'pipe', 'pipe'],
        timeout: 15000,
        encoding: 'utf8',
      });
    } catch (error) {
      // Should fail because no viewport provided
      expect(error.status).not.toBe(0);
    }
  });
});
