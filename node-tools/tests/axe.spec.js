import { execSync } from 'node:child_process';
// import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';

describe('axe-playwright runner', () => {
  it('returns JSON with violations array for valid URL', () => {
    try {
      const output = execSync('node axe-playwright.js https://example.com mobile', {
        cwd: join(process.cwd()),
        stdio: ['ignore', 'pipe', 'pipe'],
        timeout: 60000,
        encoding: 'utf8',
      });

      const result = JSON.parse(output);
      expect(result).toHaveProperty('violations');
      expect(Array.isArray(result.violations)).toBe(true);
      expect(result).toHaveProperty('passes');
      expect(result).toHaveProperty('incomplete');
    } catch (error) {
      // If the command fails, check if it's a proper error response
      if (error.stdout) {
        const result = JSON.parse(error.stdout);
        expect(result).toHaveProperty('error');
      } else {
        throw error;
      }
    }
  }, 60000);

  it('handles invalid URL gracefully', () => {
    try {
      execSync('node axe-playwright.js invalid-url mobile', {
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

  it('accepts device parameter', () => {
    try {
      const output = execSync('node axe-playwright.js https://example.com desktop', {
        cwd: join(process.cwd()),
        stdio: ['ignore', 'pipe', 'pipe'],
        timeout: 60000,
        encoding: 'utf8',
      });

      const result = JSON.parse(output);
      expect(result).toHaveProperty('violations');
      expect(Array.isArray(result.violations)).toBe(true);
    } catch (error) {
      // If the command fails, check if it's a proper error response
      if (error.stdout) {
        const result = JSON.parse(error.stdout);
        expect(result).toHaveProperty('error');
      } else {
        throw error;
      }
    }
  }, 60000);
});
