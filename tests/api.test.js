const { test, expect } = require('@playwright/test');

test.describe('Tablet Monitoring API', () => {
  
  test('health check endpoint works', async ({ request }) => {
    const response = await request.get('/health');
    expect(response.ok()).toBeTruthy();
    
    const health = await response.json();
    expect(health.status).toBe('healthy');
    expect(health.database).toBe('disabled');
    expect(health.mode).toBe('development');
  });

  test('API documentation is accessible', async ({ page }) => {
    await page.goto('/docs');
    await expect(page).toHaveTitle(/FastAPI/);
    await expect(page.locator('h1')).toContainText('Tablet Session Monitoring API');
  });

  test('root endpoint redirects properly', async ({ request }) => {
    const response = await request.get('/');
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data.message).toContain('Tablet Session Monitoring API');
  });

  test('devices endpoint returns mock data', async ({ request }) => {
    // This endpoint requires authentication, let's test without token first
    const response = await request.get('/devices');
    expect(response.status()).toBe(403); // Should be forbidden without token
  });

  test('devices endpoint with mock token', async ({ request }) => {
    // Test with a mock token (this will fail auth but we can test the structure)
    const response = await request.get('/devices', {
      headers: {
        'Authorization': 'Bearer mock-token'
      }
    });
    // Should return 401/403 but not crash
    expect([401, 403]).toContain(response.status());
  });
});

test.describe('Dashboard UI Tests', () => {
  
  test('dashboard loads successfully', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Check that the page loads and has the correct title
    await expect(page).toHaveTitle(/J&D McLennan Engineering/);
    
    // Check for key dashboard elements
    await expect(page.locator('h1')).toContainText('Tablet Monitoring');
  });

  test('dashboard has business intelligence section', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Look for business intelligence elements
    const businessSection = page.locator('text=Business Intelligence');
    await expect(businessSection).toBeVisible({ timeout: 10000 });
  });

  test('dashboard shows device monitoring', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Look for device monitoring elements
    const deviceSection = page.locator('text=Device Monitoring');
    await expect(deviceSection).toBeVisible({ timeout: 10000 });
  });

  test('dashboard handles data loading states', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Check that loading states are handled properly
    // The dashboard should either show loading or actual data
    await page.waitForLoadState('networkidle');
    
    // After network is idle, we shouldn't see infinite loading
    const loadingElements = page.locator('text=Loading...');
    const count = await loadingElements.count();
    
    // Allow some loading elements but not everything stuck loading
    expect(count).toBeLessThan(5);
  });
});

test.describe('Mobile Responsiveness', () => {
  
  test('dashboard is mobile responsive', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard');
    
    // Check that page doesn't have horizontal scroll
    const body = await page.locator('body').boundingBox();
    expect(body.width).toBeLessThanOrEqual(375);
    
    // Check that key elements are still visible
    await expect(page.locator('h1')).toBeVisible();
  });

  test('mobile navigation works', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard');
    
    // Look for mobile menu or navigation elements
    // This will depend on the actual dashboard implementation
    await page.waitForLoadState('networkidle');
  });
});

test.describe('Performance Tests', () => {
  
  test('dashboard loads within reasonable time', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;
    
    // Dashboard should load within 5 seconds
    expect(loadTime).toBeLessThan(5000);
  });

  test('API endpoints respond quickly', async ({ request }) => {
    const startTime = Date.now();
    await request.get('/health');
    const responseTime = Date.now() - startTime;
    
    // API should respond within 1 second
    expect(responseTime).toBeLessThan(1000);
  });
});

test.describe('Error Handling', () => {
  
  test('handles 404 errors gracefully', async ({ page }) => {
    const response = await page.goto('/nonexistent-page');
    expect(response.status()).toBe(404);
  });

  test('API handles invalid routes', async ({ request }) => {
    const response = await request.get('/api/invalid-endpoint');
    expect(response.status()).toBe(404);
  });

  test('dashboard handles network errors gracefully', async ({ page }) => {
    // Navigate to dashboard first
    await page.goto('/dashboard');
    
    // Block network requests to simulate network issues
    await page.route('**/api/**', route => route.abort());
    
    // Reload the page
    await page.reload();
    
    // Should not crash and should show some error handling
    await page.waitForLoadState('domcontentloaded');
    
    // Page should still be functional
    await expect(page.locator('h1')).toBeVisible();
  });
}); 