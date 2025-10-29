import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    testTimeout: 120000,
    hookTimeout: 30000,
    teardownTimeout: 10000,
    globals: true,
    environment: 'node',
  },
});
