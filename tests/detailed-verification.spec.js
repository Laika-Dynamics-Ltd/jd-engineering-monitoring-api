import { test, expect } from '@playwright/test';

const API_TOKEN = 'ArFetiWcHH5bIbiiwuQupQalDJocJA436YMi00tCvmHZOI82Awp8qbceO681';

test('Detailed Dashboard Verification with Screenshots', async ({ page }) => {
  console.log('🔍 Starting detailed dashboard verification...');
  
  // Navigate to dashboard
  await page.goto('/dashboard');
  
  // Take screenshot of login page
  await page.screenshot({ path: 'test-results/01-login-page.png', fullPage: true });
  console.log('📸 Login page screenshot captured');
  
  // Verify logo on login page
  const loginLogo = page.locator('.login-logo');
  await expect(loginLogo).toBeVisible();
  const loginLogoSrc = await loginLogo.getAttribute('src');
  console.log(`🖼️ Login logo src: ${loginLogoSrc}`);
  
  // Login
  await page.fill('#username', 'admin');
  await page.fill('#password', 'Jd3ng!n33r!ng2025#S3cur3');
  await page.click('.login-button');
  
  // Wait for dashboard to load
  await expect(page.locator('.dashboard-container')).toBeVisible({ timeout: 10000 });
  
  // Take screenshot of dashboard
  await page.screenshot({ path: 'test-results/02-dashboard-loaded.png', fullPage: true });
  console.log('📸 Dashboard screenshot captured');
  
  // Verify dashboard logo
  const dashboardLogo = page.locator('.company-logo');
  await expect(dashboardLogo).toBeVisible();
  const dashboardLogoSrc = await dashboardLogo.getAttribute('src');
  console.log(`🖼️ Dashboard logo src: ${dashboardLogoSrc}`);
  
  // Wait for data to load
  await page.waitForTimeout(3000);
  
  // Capture all metrics values
  const metrics = {};
  
  const statElements = [
    { id: '#totalDevices', name: 'Total Devices' },
    { id: '#onlineDevices', name: 'Online Now' },
    { id: '#avgBattery', name: 'Avg Battery' },
    { id: '#myobActive', name: 'MYOB Active' },
    { id: '#scannerActive', name: 'Scanner Active' },
    { id: '#timeoutRisks', name: 'Timeout Risks' }
  ];
  
  console.log('\n📊 CURRENT DASHBOARD METRICS:');
  console.log('================================');
  
  for (const stat of statElements) {
    const element = page.locator(stat.id);
    await expect(element).toBeVisible();
    const value = await element.textContent();
    metrics[stat.name] = value;
    console.log(`${stat.name}: ${value}`);
  }
  
  // Check device cards
  const deviceCards = page.locator('.device-card');
  const deviceCount = await deviceCards.count();
  console.log(`\n📱 Device Cards Found: ${deviceCount}`);
  
  for (let i = 0; i < deviceCount; i++) {
    const card = deviceCards.nth(i);
    const deviceName = await card.locator('.device-name').textContent();
    const deviceStatus = await card.locator('.device-status').textContent();
    console.log(`Device ${i + 1}: ${deviceName} - Status: ${deviceStatus}`);
    
    // Get device metrics
    const deviceMetrics = card.locator('.metric-value');
    const metricCount = await deviceMetrics.count();
    const metricValues = [];
    
    for (let j = 0; j < metricCount; j++) {
      const value = await deviceMetrics.nth(j).textContent();
      metricValues.push(value);
    }
    
    console.log(`  Metrics: Battery: ${metricValues[0]}, WiFi: ${metricValues[1]}, MYOB: ${metricValues[2]}, Scanner: ${metricValues[3]}`);
  }
  
  // Check alerts
  const alertsContainer = page.locator('#alertsContainer');
  const alerts = alertsContainer.locator('.alert');
  const alertCount = await alerts.count();
  console.log(`\n🚨 Active Alerts: ${alertCount}`);
  
  for (let i = 0; i < alertCount; i++) {
    const alertText = await alerts.nth(i).textContent();
    console.log(`Alert ${i + 1}: ${alertText}`);
  }
  
  // Check last updated time
  const lastUpdated = await page.locator('#lastUpdated').textContent();
  console.log(`\n🕒 ${lastUpdated}`);
  
  // Test refresh functionality
  console.log('\n🔄 Testing refresh functionality...');
  await page.click('#refreshBtn');
  await page.waitForTimeout(2000);
  
  const newLastUpdated = await page.locator('#lastUpdated').textContent();
  console.log(`🕒 After refresh: ${newLastUpdated}`);
  
  // Take final screenshot
  await page.screenshot({ path: 'test-results/03-dashboard-final.png', fullPage: true });
  console.log('📸 Final dashboard screenshot captured');
  
  // Verify everything is working
  expect(deviceCount).toBeGreaterThan(0);
  expect(metrics['Total Devices']).not.toBe('-');
  expect(metrics['Online Now']).not.toBe('-');
  expect(metrics['Avg Battery']).not.toBe('-');
  
  console.log('\n✅ VERIFICATION COMPLETE - Dashboard is fully functional!');
}); 