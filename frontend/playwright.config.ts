import { defineConfig } from '@playwright/test';

/**
 * NLAMS Playwright E2E configuration.
 *
 * In CI, servers are started by the GitHub Actions workflow steps.
 * Locally, the webServer block below auto-starts both backend and frontend
 * when you run `npx playwright test` from the frontend/ directory.
 */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: false, // Run sequentially against same DB
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: process.env.CI ? [['github'], ['html', { open: 'never' }]] : 'list',
  timeout: 60_000, // 60s per test (rate-limit retries need headroom)
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    viewport: { width: 1280, height: 720 },
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
  ],
  // Only start servers when NOT in CI (CI handles this in workflow steps)
  ...(process.env.CI
    ? {}
    : {
        webServer: [
          {
            command: 'cd ../backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000',
            port: 8000,
            reuseExistingServer: true,
            timeout: 30_000,
          },
          {
            command: 'npx vite --host 0.0.0.0 --port 5173',
            port: 5173,
            reuseExistingServer: true,
            timeout: 30_000,
          },
        ],
      }),
});
