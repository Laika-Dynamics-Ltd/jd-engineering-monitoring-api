import { test, expect } from '@playwright/test';

const API_TOKEN = 'ArFetiWcHH5bIbiiwuQupQalDJocJA436YMi00tCvmHZOI82Awp8qbceO681';

test.describe('JD Engineering Dashboard - Full Audit', () => {
  
  test('API Health Check', async ({ request }) => {
    const response = await request.get('/health');
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.status).toBe('healthy');
    console.log('✅ API Health Check passed');
  });

  test('API Analytics Endpoint', async ({ request }) => {
    const response = await request.get('/analytics', {
      headers: { 'Authorization': `Bearer ${API_TOKEN}` }
    });
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    
    console.log('📊 Analytics Data:', data);
    
    // Check required fields exist
    expect(data).toHaveProperty('total_devices');
    expect(data).toHaveProperty('online_devices');
    expect(data).toHaveProperty('avg_battery');
    expect(data).toHaveProperty('myob_active');
    expect(data).toHaveProperty('scanner_active');
    expect(data).toHaveProperty('timeout_risks');
    
    // Validate data types and ranges
    expect(typeof data.total_devices).toBe('number');
    expect(typeof data.online_devices).toBe('number');
    expect(typeof data.avg_battery).toBe('number');
    
    // Check for reasonable values
    expect(data.total_devices).toBeGreaterThanOrEqual(0);
    expect(data.online_devices).toBeLessThanOrEqual(data.total_devices);
    expect(data.avg_battery).toBeGreaterThanOrEqual(0);
    expect(data.avg_battery).toBeLessThanOrEqual(100);
    
    console.log('✅ Analytics API validation passed');
  });

  test('API Devices Endpoint', async ({ request }) => {
    const response = await request.get('/devices', {
      headers: { 'Authorization': `Bearer ${API_TOKEN}` }
    });
    expect(response.ok()).toBeTruthy();
    const devices = await response.json();
    
    console.log('📱 Devices Data:', devices);
    
    expect(Array.isArray(devices)).toBeTruthy();
    
    if (devices.length > 0) {
      const device = devices[0];
      expect(device).toHaveProperty('device_id');
      expect(device).toHaveProperty('device_name');
      expect(device).toHaveProperty('status');
      expect(device).toHaveProperty('last_seen');
    }
    
    console.log('✅ Devices API validation passed');
  });

  test('Dashboard Login Page', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Check if login form is visible
    await expect(page.locator('.login-container')).toBeVisible();
    await expect(page.locator('.login-title')).toContainText('Tablet Monitoring System');
    
    // Check logo loading
    const logo = page.locator('.login-logo');
    await expect(logo).toBeVisible();
    
    // Check if logo actually loads (not broken)
    const logoSrc = await logo.getAttribute('src');
    console.log('🖼️ Logo src:', logoSrc);
    
    // Test logo loading by checking if it has dimensions
    const logoBox = await logo.boundingBox();
    if (logoBox) {
      expect(logoBox.width).toBeGreaterThan(0);
      expect(logoBox.height).toBeGreaterThan(0);
      console.log('✅ Logo loads with dimensions:', logoBox);
    } else {
      console.log('❌ Logo not loading properly');
    }
    
    // Check form elements
    await expect(page.locator('#username')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(page.locator('.login-button')).toBeVisible();
    
    console.log('✅ Login page elements validation passed');
  });

  test('Dashboard Authentication Flow', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Fill login form
    await page.fill('#username', 'admin');
    await page.fill('#password', 'Jd3ng!n33r!ng2025#S3cur3');
    await page.click('.login-button');
    
    // Wait for dashboard to load
    await expect(page.locator('.dashboard-container')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('.login-container')).not.toBeVisible();
    
    // Check if dashboard header is visible
    await expect(page.locator('.header')).toBeVisible();
    await expect(page.locator('.header h1')).toContainText('Tablet Monitoring System');
    
    // Check dashboard logo
    const dashboardLogo = page.locator('.company-logo');
    await expect(dashboardLogo).toBeVisible();
    
    const logoBox = await dashboardLogo.boundingBox();
    if (logoBox) {
      expect(logoBox.width).toBeGreaterThan(0);
      expect(logoBox.height).toBeGreaterThan(0);
      console.log('✅ Dashboard logo loads with dimensions:', logoBox);
    } else {
      console.log('❌ Dashboard logo not loading properly');
    }
    
    console.log('✅ Authentication flow validation passed');
  });

  test('Dashboard Metrics Display', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Login
    await page.fill('#username', 'admin');
    await page.fill('#password', 'Jd3ng!n33r!ng2025#S3cur3');
    await page.click('.login-button');
    await expect(page.locator('.dashboard-container')).toBeVisible({ timeout: 10000 });
    
    // Wait for data to load
    await page.waitForTimeout(3000);
    
    // Check stats grid
    await expect(page.locator('.stats-grid')).toBeVisible();
    
    // Check all stat cards
    const statCards = [
      { id: '#totalDevices', label: 'Total Devices' },
      { id: '#onlineDevices', label: 'Online Now' },
      { id: '#avgBattery', label: 'Avg Battery' },
      { id: '#myobActive', label: 'MYOB Active' },
      { id: '#scannerActive', label: 'Scanner Active' },
      { id: '#timeoutRisks', label: 'Timeout Risks' }
    ];
    
    for (const stat of statCards) {
      const element = page.locator(stat.id);
      await expect(element).toBeVisible();
      
      const value = await element.textContent();
      console.log(`📊 ${stat.label}: ${value}`);
      
      // Check if value is not just "-" (loading state)
      expect(value).not.toBe('-');
      expect(value).not.toBe('');
    }
    
    // Check device grid
    await expect(page.locator('.device-grid')).toBeVisible();
    
    // Check if devices are displayed
    const deviceCards = page.locator('.device-card');
    const deviceCount = await deviceCards.count();
    console.log(`📱 Number of device cards: ${deviceCount}`);
    
    if (deviceCount > 0) {
      // Check first device card structure
      const firstDevice = deviceCards.first();
      await expect(firstDevice.locator('.device-name')).toBeVisible();
      await expect(firstDevice.locator('.device-status')).toBeVisible();
      await expect(firstDevice.locator('.device-metrics')).toBeVisible();
      
      // Check metrics within device card
      await expect(firstDevice.locator('.metric-value')).toHaveCount(4); // Battery, WiFi, MYOB, Scanner
    }
    
    // Check alerts section
    await expect(page.locator('.alert-section')).toBeVisible();
    await expect(page.locator('#alertsContainer')).toBeVisible();
    
    console.log('✅ Dashboard metrics display validation passed');
  });

  test('Dashboard Real-time Updates', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Login
    await page.fill('#username', 'admin');
    await page.fill('#password', 'Jd3ng!n33r!ng2025#S3cur3');
    await page.click('.login-button');
    await expect(page.locator('.dashboard-container')).toBeVisible({ timeout: 10000 });
    
    // Wait for initial load
    await page.waitForTimeout(2000);
    
    // Get initial values
    const initialTotalDevices = await page.locator('#totalDevices').textContent();
    const initialOnlineDevices = await page.locator('#onlineDevices').textContent();
    const initialBattery = await page.locator('#avgBattery').textContent();
    
    console.log('📊 Initial values:', {
      total: initialTotalDevices,
      online: initialOnlineDevices,
      battery: initialBattery
    });
    
    // Test manual refresh
    await page.click('#refreshBtn');
    
    // Wait for refresh to complete
    await page.waitForTimeout(3000);
    
    // Check if last updated timestamp changed
    const lastUpdated = await page.locator('#lastUpdated').textContent();
    expect(lastUpdated).not.toContain('Never');
    console.log('🕒 Last updated:', lastUpdated);
    
    // Check refresh button state
    const refreshBtn = page.locator('#refreshBtn');
    await expect(refreshBtn).not.toBeDisabled();
    
    console.log('✅ Real-time updates validation passed');
  });

  test('Dashboard Responsive Design', async ({ page }) => {
    // Test desktop view
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/dashboard');
    
    // Login
    await page.fill('#username', 'admin');
    await page.fill('#password', 'Jd3ng!n33r!ng2025#S3cur3');
    await page.click('.login-button');
    await expect(page.locator('.dashboard-container')).toBeVisible({ timeout: 10000 });
    
    // Check desktop layout
    const statsGrid = page.locator('.stats-grid');
    await expect(statsGrid).toBeVisible();
    
    // Test mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);
    
    // Check mobile layout still works
    await expect(statsGrid).toBeVisible();
    await expect(page.locator('.header')).toBeVisible();
    
    console.log('✅ Responsive design validation passed');
  });

  test('Dashboard Error Handling', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Test invalid login
    await page.fill('#username', 'invalid');
    await page.fill('#password', 'invalid');
    await page.click('.login-button');
    
    // Check error message appears
    await expect(page.locator('.login-error')).toBeVisible();
    
    // Test valid login after error
    await page.fill('#username', 'admin');
    await page.fill('#password', 'Jd3ng!n33r!ng2025#S3cur3');
    await page.click('.login-button');
    
    await expect(page.locator('.dashboard-container')).toBeVisible({ timeout: 10000 });
    
    console.log('✅ Error handling validation passed');
  });

  test('Dashboard Performance', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/dashboard');
    
    // Login
    await page.fill('#username', 'admin');
    await page.fill('#password', 'Jd3ng!n33r!ng2025#S3cur3');
    await page.click('.login-button');
    
    await expect(page.locator('.dashboard-container')).toBeVisible({ timeout: 10000 });
    
    // Wait for all data to load
    await page.waitForTimeout(3000);
    
    const loadTime = Date.now() - startTime;
    console.log(`⚡ Dashboard load time: ${loadTime}ms`);
    
    // Check if load time is reasonable (under 10 seconds)
    expect(loadTime).toBeLessThan(10000);
    
    console.log('✅ Performance validation passed');
  });
});