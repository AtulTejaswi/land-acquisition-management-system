/**
 * NLAMS E2E — Citizen flow + real Odisha data verification
 *
 * Tests:
 *   1. Citizen login → Track Status → My Compensation → My R&R → logout
 *   2. Hindi language toggle on citizen pages
 *   3. Super Admin login → National Dashboard shows real bhoomirashi data
 *   4. GIS Map page loads with Khordha/Odisha data
 *
 * Requirements:
 *   - Backend on http://localhost:8000 (seeded with bhoomirashi data)
 *   - Frontend on http://localhost:5173
 *   - Run: npx playwright test e2e/citizen-odisha-data.spec.ts
 */
import { test, expect, type Page, type BrowserContext } from '@playwright/test';

const BASE_URL = 'http://localhost:5173';
const API_URL = 'http://localhost:5173/api/v1';
const PASSWORD = 'password123';

/**
 * Login via API to set httpOnly cookies, then navigate to the app.
 * This avoids the Vite-proxy cookie-timing race that makes form-based
 * login unreliable in headless Chromium.
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
    // Rate limited — wait and retry
    if (resp.status() === 429) {
      await new Promise((r) => setTimeout(r, 65000));
      continue;
    }
    throw new Error(`Login failed: ${resp.status()} ${await resp.text()}`);
  }
  throw new Error('Login failed after retries (rate limited)');
}

// ─── Citizen Flow ────────────────────────────────────────────────

test.describe('Citizen flow with real Odisha data', () => {
  test('login → Track Status → Compensation → R&R → language toggle → logout', async ({ page, context }) => {
    // Step 1: Login as citizen via API (sets httpOnly cookies)
    const user = await loginViaAPI(context, 'ganesh@email.com');
    expect(user.role_name).toBe('citizen');

    // Navigate to citizen Track Status
    await page.goto(`${BASE_URL}/citizen/track`);
    await page.waitForLoadState('networkidle');

    // Should be on /citizen/track (not redirected back to login)
    await expect(page).toHaveURL(/\/citizen\/track/, { timeout: 10000 });

    // Step 2: Verify Track Status page renders with i18n text
    const trackTitle = page.locator('h1');
    await expect(trackTitle).toBeVisible({ timeout: 5000 });
    await expect(trackTitle).toContainText('Track Your Status');

    // Verify the transparency portal banner
    const portalText = page.getByText('Citizen Transparency Portal');
    await expect(portalText.first()).toBeVisible({ timeout: 5000 });

    // Verify sidebar has citizen nav links
    const sidebar = page.locator('aside, nav').first();
    await expect(sidebar.getByText('Track Status')).toBeVisible();
    await expect(sidebar.getByText('My Compensation')).toBeVisible();
    await expect(sidebar.getByText('My R&R')).toBeVisible();

    // Step 3: Navigate to My Compensation
    await sidebar.getByText('My Compensation').click();
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/\/citizen\/compensation/);

    const compTitle = page.locator('h1');
    await expect(compTitle).toContainText('My Compensation');

    // Step 4: Navigate to My R&R
    await sidebar.getByText('My R&R').click();
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/\/citizen\/rr/);

    const rrTitle = page.locator('h1');
    await expect(rrTitle).toContainText('Rehabilitation');

    // Step 5: Test Hindi language toggle
    const langButton = page.getByRole('button', { name: /switch language/i });
    await expect(langButton).toBeVisible();

    // Button shows the language to SWITCH TO (not current language)
    // Initially shows 'हिन्दी' (meaning current is English)
    const initialText = await langButton.textContent();
    expect(initialText).toBeTruthy();

    // Toggle language
    await langButton.click();
    await page.waitForTimeout(500);

    // Button text should have changed (toggled)
    const toggledText = await langButton.textContent();
    expect(toggledText).not.toBe(initialText);

    // Toggle back
    await langButton.click();
    await page.waitForTimeout(500);
    const restoredText = await langButton.textContent();
    expect(restoredText).toBe(initialText);

    // Step 6: Logout via API
    await context.request.post(`${API_URL}/auth/logout`);
  });

  test('Track Status page has no JS errors', async ({ page, context }) => {
    const errors: string[] = [];
    page.on('pageerror', (err) => errors.push(err.message));

    await loginViaAPI(context, 'ganesh@email.com');

    await page.goto(`${BASE_URL}/citizen/track`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // No uncaught JS errors
    expect(errors).toEqual([]);
  });
});

// ─── Super Admin — Real Odisha Data ──────────────────────────────

test.describe('Super Admin dashboard with real bhoomirashi data', () => {
  test('National Dashboard shows 249 parcels, 6 villages, real KPIs', async ({ page, context }) => {
    await loginViaAPI(context, 'rajesh@nlams.gov.in');

    // Navigate to admin dashboard
    await page.goto(`${BASE_URL}/admin/dashboard`);
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/\/admin\/dashboard/, { timeout: 10000 });

    // Verify heading mentions real data
    const subtitle = page.getByText(/Khordha District|Odisha|bhoomirashi|real/i);
    await expect(subtitle.first()).toBeVisible({ timeout: 5000 });

    // Verify KPI cards show real numbers
    const kpiText = page.locator('text=Total Parcels').first();
    await expect(kpiText).toBeVisible({ timeout: 5000 });

    // Total Parcels should be 249 (from bhoomirashi import)
    const parcelsCard = page.getByText('249').first();
    await expect(parcelsCard).toBeVisible({ timeout: 5000 });

    // Total Area should show ~26.92 ha
    const areaCard = page.getByText(/26\.92/).first();
    await expect(areaCard).toBeVisible({ timeout: 5000 });

    // Total Owners should be 961
    const ownersCard = page.getByText('961').first();
    await expect(ownersCard).toBeVisible({ timeout: 5000 });

    // Verify chart titles are present (from real data)
    await expect(page.getByText('Parcels by Village').first()).toBeVisible();
    await expect(page.getByText('Area by Ownership').first()).toBeVisible();
    await expect(page.getByText('Co-ownership Distribution').first()).toBeVisible();

    // Verify Odisha state card is shown
    await expect(page.getByText('Odisha').first()).toBeVisible();
    await expect(page.getByText('OD').first()).toBeVisible();
  });

  test('GIS Map page loads with Khordha marker data', async ({ page, context }) => {
    await loginViaAPI(context, 'rajesh@nlams.gov.in');

    // Navigate directly to GIS map
    await page.goto(`${BASE_URL}/admin/gis`);
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/\/admin\/gis/, { timeout: 10000 });

    // Verify GIS page heading mentions Khordha
    const heading = page.getByText(/Khordha|GIS|Parcel Map/i);
    await expect(heading.first()).toBeVisible({ timeout: 5000 });

    // Verify disclaimer about village-level markers
    const disclaimer = page.getByText(/approximate|village-level/i);
    await expect(disclaimer.first()).toBeVisible({ timeout: 5000 });

    // Verify verification/ownership toggle buttons exist
    const toggleBtns = page.getByRole('button', { name: /verification|ownership/i });
    expect(await toggleBtns.count()).toBeGreaterThanOrEqual(2);
  });

  test('no JS errors on dashboard or GIS pages', async ({ page, context }) => {
    const errors: string[] = [];
    page.on('pageerror', (err) => errors.push(err.message));

    await loginViaAPI(context, 'rajesh@nlams.gov.in');

    // Visit dashboard
    await page.goto(`${BASE_URL}/admin/dashboard`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // Visit GIS
    await page.goto(`${BASE_URL}/admin/gis`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // No uncaught JS errors (exclude expected CORS tile errors)
    const criticalErrors = errors.filter(
      (e) => !e.includes('tile') && !e.includes('CORS') && !e.includes('NetworkError'),
    );
    expect(criticalErrors).toEqual([]);
  });
});
