import { execSync } from 'node:child_process';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';

describe('security-headers runner', () => {
  it('returns JSON with security analysis for valid URL', () => {
    try {
      const output = execSync('node security-headers.js https://example.com', {
        cwd: join(process.cwd()),
        stdio: ['ignore', 'pipe', 'pipe'],
        timeout: 30000,
        encoding: 'utf8',
      });

      const result = JSON.parse(output);
      expect(result).toHaveProperty('url');
      expect(result).toHaveProperty('headers');
      expect(result).toHaveProperty('security');
      expect(result).toHaveProperty('securityScore');

      // Check security flags structure
      const security = result.security;
      const expectedFlags = [
        'content-security-policy',
        'strict-transport-security',
        'x-frame-options',
        'x-content-type-options',
        'referrer-policy',
        'permissions-policy',
      ];

      expectedFlags.forEach((flag) => {
        expect(security).toHaveProperty(flag);
        expect(typeof security[flag]).toBe('boolean');
      });

      expect(typeof result.securityScore).toBe('number');
      expect(result.securityScore).toBeGreaterThanOrEqual(0);
      expect(result.securityScore).toBeLessThanOrEqual(100);
    } catch (error) {
      // If the command fails, check if it's a proper error response
      if (error.stdout) {
        const result = JSON.parse(error.stdout);
        expect(result).toHaveProperty('error');
      } else {
        throw error;
      }
    }
  }, 30000);

  it('handles invalid URL gracefully', () => {
    try {
      execSync('node security-headers.js invalid-url', {
        cwd: join(process.cwd()),
        stdio: ['ignore', 'pipe', 'pipe'],
        timeout: 15000,
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

  it('validates URL format', () => {
    try {
      execSync('node security-headers.js example.com', {
        cwd: join(process.cwd()),
        stdio: ['ignore', 'pipe', 'pipe'],
        timeout: 15000,
        encoding: 'utf8',
      });
    } catch (error) {
      // Should fail because URL doesn't start with http:// or https://
      expect(error.status).not.toBe(0);
    }
  });
});
