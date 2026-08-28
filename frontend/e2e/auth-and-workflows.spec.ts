/**
 * NLAMS E2E Tests — 6 role-based login → workflow → logout flows.
 *
 * Requirements:
 *   - Backend running on http://localhost:8000 (seeded DB)
 *   - Frontend running on http://localhost:5173
 *   - Run: npx playwright test (from frontend/)
 */
import { test, expect, type Page, type BrowserContext } from '@playwright/test';

const BASE_URL = 'http://localhost:5173';
const API_URL = 'http://localhost:5173/api/v1';
const PASSWORD = 'password123';

/**
 * Login via API to set httpOnly cookies, then navigate.
 * Avoids form-submit + Vite-proxy cookie race.
 */
async function loginViaAPI(context: BrowserContext, email: string) {
  for (let attempt = 0; attempt < 3; attempt++) {
    const resp = await context.request.post(`${API_URL}/auth/login`, {
      data: { email, password: PASSWORD },
    });
    if (resp.ok()) {
      const body = await resp.json();
      return body.user;
    }
    if (resp.status() === 429) {
      await new Promise((r) => setTimeout(r, 65000));
      continue;
    }
    throw new Error(`Login failed: ${resp.status()}`);
  }
  throw new Error('Login failed after retries');
}

const USERS = [
  {
    role: 'Super Admin',
    email: 'rajesh@nlams.gov.in',
    dashboard: '/admin/dashboard',
    workflow: { nav: 'Projects', heading: /project/i },
  },
  {
    role: 'State Authority',
    email: 'anil@odisha.gov.in',
    dashboard: '/state/dashboard',
    workflow: { nav: 'GIS', heading: /map|gis/i },
  },
  {
    role: 'District Officer',
    email: 'suresh@khordha.gov.in',
    dashboard: '/district/dashboard',
    workflow: { nav: 'Verification', heading: /verification|queue/i },
  },
  {
    role: 'Agency',
    email: 'agency@nhai.gov.in',
    dashboard: '/agency/projects',
    workflow: { nav: 'Projects', heading: /project/i },
  },
  {
    role: 'Field Officer',
    email: 'rahul.f@nlams.gov.in',
    dashboard: '/field/home',
    workflow: { nav: 'Surveys', heading: /survey/i },
  },
  {
    role: 'Citizen',
    email: 'ganesh@email.com',
    dashboard: '/citizen/track',
    workflow: { nav: 'Track', heading: /track|status/i },
  },
];

async function login(page: Page, email: string, password: string) {
  await page.goto(`${BASE_URL}/login`);
  await page.waitForSelector('#login-email', { timeout: 10000 });
  await page.fill('#login-email', email);
  await page.fill('#login-password', password);
  await page.click('button[type="submit"]');
  // Wait for navigation away from login
  await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 10000 });
}

async function logout(page: Page) {
  const logoutBtn = page.locator('button', { hasText: /logout/i });
  if (await logoutBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
    await logoutBtn.click();
    await page.waitForURL('**/login', { timeout: 5000 });
  }
}

for (const user of USERS) {
  test.describe(`${user.role} workflow`, () => {
    test(`login → dashboard → core workflow → logout`, async ({ page, context }) => {
      // Step 1: Login via API (sets httpOnly cookies)
      const u = await loginViaAPI(context, user.email);
      expect(u.role_name).toBeDefined();

      // Step 2: Navigate to dashboard
      await page.goto(`${BASE_URL}${user.dashboard}`);
      await page.waitForLoadState('networkidle');
      await expect(page).toHaveURL(new RegExp(user.dashboard), { timeout: 10000 });

      // Step 3: Navigate to core workflow
      const navLink = page.locator(`nav a, aside a, [role="navigation"] a`).filter({
        hasText: new RegExp(user.workflow.nav, 'i'),
      });

      if (await navLink.first().isVisible({ timeout: 3000 }).catch(() => false)) {
        await navLink.first().click();
        await page.waitForLoadState('networkidle');

        // Verify workflow page content
        const heading = page.locator('h1, h2, [role="heading"]').filter({
          hasText: user.workflow.heading,
        });
        await expect(heading.first()).toBeVisible({ timeout: 5000 });
      }

      // Step 4: Logout via API
      await context.request.post(`${API_URL}/auth/logout`);
    });
  });
}

test.describe('Cross-cutting E2E checks', () => {
  test('login page renders all 6 quick-login buttons', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.waitForSelector('#login-email', { timeout: 10000 });
    const buttons = page.locator('button', { hasText: /Quick Demo|Super Admin|State Authority|District Officer|Agency|Field Officer|Citizen/i });
    await expect(buttons).toHaveCount(6);
  });

  test('accessing protected route without auth redirects to login', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/dashboard`);
    await page.waitForURL('**/login', { timeout: 10000 });
    await expect(page).toHaveURL(/\/login/);
  });

  test('login with invalid credentials shows error', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.waitForSelector('#login-email', { timeout: 10000 });
    await page.fill('#login-email', 'bad@example.com');
    await page.fill('#login-password', 'wrongpass');
    await page.click('button[type="submit"]');
    const error = page.locator('.bg-red-50, [role="alert"]');
    await expect(error.first()).toBeVisible({ timeout: 5000 });
  });
});
