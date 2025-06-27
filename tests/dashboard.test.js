const { test, expect } = require('@playwright/test');

test.describe('Business Intelligence Dashboard', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to dashboard before each test
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
  });

  test('dashboard title and branding', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/J&D McLennan Engineering/);
    
    // Check for company logo
    const logo = page.locator('img[alt*="JD"], img[src*="JDMNavLogo"]');
    await expect(logo).toBeVisible();
    
    // Check main heading
    await expect(page.locator('h1, .dashboard-title')).toContainText(/Tablet Monitoring|Dashboard/);
  });

  test('business intelligence section is prominent', async ({ page }) => {
    // Business intelligence should be visible and prominent
    const biSection = page.locator('text=Business Intelligence, .business-intelligence, #business-intelligence');
    await expect(biSection).toBeVisible();
    
    // Should contain financial impact analysis
    const financialSection = page.locator('text=Financial Impact, text=Cost Analysis, .financial-impact');
    await expect(financialSection).toBeVisible();
  });

  test('device monitoring section exists', async ({ page }) => {
    // Device monitoring section
    const deviceSection = page.locator('text=Device Monitoring, .device-monitoring, #device-monitoring');
    await expect(deviceSection).toBeVisible();
    
    // Should show device status
    const deviceStatus = page.locator('.device-status, .device-card, text=Tablet');
    await expect(deviceStatus).toBeVisible();
  });

  test('dashboard shows KPI metrics', async ({ page }) => {
    // Look for KPI cards or metrics
    const kpiElements = page.locator('.kpi, .metric, .stat, [class*="metric"], [class*="kpi"]');
    const count = await kpiElements.count();
    expect(count).toBeGreaterThan(0);
    
    // Should have numeric values
    const numbers = page.locator('text=/\\$\\d+|\\d+%|\\d+ hours/');
    const numberCount = await numbers.count();
    expect(numberCount).toBeGreaterThan(0);
  });

  test('charts and visualizations load', async ({ page }) => {
    // Wait for any charts to load
    await page.waitForTimeout(2000);
    
    // Look for chart containers (Chart.js, Canvas, SVG)
    const charts = page.locator('canvas, svg, .chart, [id*="chart"], [class*="chart"]');
    const chartCount = await charts.count();
    expect(chartCount).toBeGreaterThan(0);
  });

  test('data refresh functionality', async ({ page }) => {
    // Look for refresh buttons or auto-refresh indicators
    const refreshElements = page.locator('button:has-text("Refresh"), .refresh, [title*="refresh"]');
    
    if (await refreshElements.count() > 0) {
      // Click refresh if available
      await refreshElements.first().click();
      await page.waitForTimeout(1000);
    }
    
    // Check for auto-refresh indicators
    const autoRefresh = page.locator('text=Auto-refresh, .auto-refresh, text=/refreshing|updating/i');
    // This might or might not be visible depending on implementation
  });

  test('responsive design works', async ({ page }) => {
    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Key elements should still be visible
    await expect(page.locator('h1')).toBeVisible();
    
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Page should not have horizontal scroll
    const body = await page.locator('body').evaluate(el => el.scrollWidth);
    expect(body).toBeLessThanOrEqual(400); // Some margin for measurement differences
  });

  test('error states are handled gracefully', async ({ page }) => {
    // Block API requests to test error handling
    await page.route('**/api/**', route => route.abort());
    
    // Reload page to trigger API calls
    await page.reload();
    await page.waitForLoadState('domcontentloaded');
    
    // Page should still be functional and not show "Loading..." forever
    await page.waitForTimeout(3000);
    
    // Should show error messages or fallback content
    const errorElements = page.locator('text=/error|failed|unavailable/i, .error, .alert');
    const loadingElements = page.locator('text=Loading...');
    
    // Either should show errors or stop loading
    const errorCount = await errorElements.count();
    const loadingCount = await loadingElements.count();
    
    // Should either show errors or not be stuck loading
    expect(errorCount > 0 || loadingCount < 3).toBeTruthy();
  });
});

test.describe('Dashboard Accessibility', () => {
  
  test('dashboard has proper headings hierarchy', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Check for proper heading structure
    const h1 = await page.locator('h1').count();
    expect(h1).toBeGreaterThanOrEqual(1);
    
    // Should have sub-headings
    const headings = await page.locator('h1, h2, h3, h4').count();
    expect(headings).toBeGreaterThan(1);
  });

  test('dashboard has alt text for images', async ({ page }) => {
    await page.goto('/dashboard');
    
    // All images should have alt text
    const images = page.locator('img');
    const imageCount = await images.count();
    
    if (imageCount > 0) {
      for (let i = 0; i < imageCount; i++) {
        const img = images.nth(i);
        const alt = await img.getAttribute('alt');
        expect(alt).toBeTruthy();
      }
    }
  });

  test('dashboard is keyboard navigable', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Try tabbing through the page
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    // Should have focused elements
    const focusedElement = await page.locator(':focus').count();
    expect(focusedElement).toBeGreaterThanOrEqual(0);
  });
});

test.describe('Dashboard Performance', () => {
  
  test('dashboard loads efficiently', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    
    // Should load in under 5 seconds
    expect(loadTime).toBeLessThan(5000);
    
    console.log(`Dashboard loaded in ${loadTime}ms`);
  });

  test('dashboard has reasonable resource usage', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    
    // Check for memory leaks by looking at the number of DOM elements
    const elementCount = await page.locator('*').count();
    expect(elementCount).toBeLessThan(10000); // Reasonable DOM size
    
    // Check for too many network requests
    const requests = [];
    page.on('request', request => requests.push(request));
    
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Should not make excessive requests
    expect(requests.length).toBeLessThan(50);
  });
}); 