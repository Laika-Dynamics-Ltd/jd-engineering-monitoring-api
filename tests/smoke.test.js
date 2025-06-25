const { test, expect } = require('@playwright/test');

test.describe('Smoke Tests - Basic Functionality', () => {
  
  test('server is running and responds', async ({ request }) => {
    const response = await request.get('/health');
    expect(response.ok()).toBeTruthy();
    
    const health = await response.json();
    expect(health.status).toBe('healthy');
    console.log('✅ Server health check passed');
  });

  test('API documentation is accessible', async ({ page }) => {
    await page.goto('/docs');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Check if it's the FastAPI docs page
    const title = await page.title();
    expect(title).toContain('FastAPI');
    
    console.log('✅ API documentation is accessible');
  });

  test('dashboard page loads without crashing', async ({ page }) => {
    // Navigate to dashboard
    const response = await page.goto('/dashboard');
    
    // Should not return an error status
    expect(response.status()).toBe(200);
    
    // Should have a title
    const title = await page.title();
    expect(title.length).toBeGreaterThan(0);
    
    // Page should not be completely empty
    const bodyText = await page.locator('body').textContent();
    expect(bodyText.length).toBeGreaterThan(10);
    
    console.log('✅ Dashboard loads without crashing');
  });

  test('dashboard has basic structure', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('domcontentloaded');
    
    // Should have some content
    const headings = await page.locator('h1, h2, h3').count();
    expect(headings).toBeGreaterThan(0);
    
    // Should have some interactive elements
    const interactiveElements = await page.locator('button, input, select, a').count();
    expect(interactiveElements).toBeGreaterThan(0);
    
    console.log('✅ Dashboard has basic structure');
  });

  test('dashboard responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    const response = await page.goto('/dashboard');
    expect(response.status()).toBe(200);
    
    // Should not have horizontal overflow
    const bodyScrollWidth = await page.evaluate(() => document.body.scrollWidth);
    expect(bodyScrollWidth).toBeLessThanOrEqual(400); // Allow some margin
    
    console.log('✅ Dashboard is mobile responsive');
  });

  test('API endpoints return proper status codes', async ({ request }) => {
    // Test endpoints that should be accessible
    const endpoints = [
      { path: '/health', expectedStatus: 200 },
      { path: '/docs', expectedStatus: 200 },
      { path: '/redoc', expectedStatus: 200 },
      { path: '/', expectedStatus: 200 },
      { path: '/dashboard', expectedStatus: 200 },
      { path: '/nonexistent', expectedStatus: 404 },
    ];
    
    for (const endpoint of endpoints) {
      const response = await request.get(endpoint.path);
      expect(response.status()).toBe(endpoint.expectedStatus);
      console.log(`✅ ${endpoint.path} returns ${endpoint.expectedStatus}`);
    }
  });

  test('protected endpoints require authentication', async ({ request }) => {
    // These endpoints should require authentication
    const protectedEndpoints = ['/devices', '/analytics'];
    
    for (const endpoint of protectedEndpoints) {
      const response = await request.get(endpoint);
      // Should return 401 (Unauthorized) or 403 (Forbidden)
      expect([401, 403]).toContain(response.status());
      console.log(`✅ ${endpoint} properly requires authentication`);
    }
  });

  test('static files are served correctly', async ({ page }) => {
    // Test that the dashboard can load static assets
    await page.goto('/dashboard');
    
    // Listen for failed resource loads
    const failedResources = [];
    page.on('response', response => {
      if (!response.ok() && response.url().includes('/static/')) {
        failedResources.push(response.url());
      }
    });
    
    await page.waitForLoadState('networkidle');
    
    // Should not have failed to load critical static resources
    expect(failedResources.length).toBeLessThan(3); // Allow for some optional assets
    
    console.log('✅ Static files served correctly');
  });
}); 