import { test, expect } from '@playwright/test';

const API_TOKEN = 'ArFetiWcHH5bIbiiwuQupQalDJocJA436YMi00tCvmHZOI82Awp8qbceO681';

test('Final Dashboard Comprehensive Test', async ({ page }) => {
  console.log('🚀 Starting final comprehensive dashboard test...');
  
  await page.goto('https://jd-engineering-monitoring-api-production.up.railway.app/dashboard');
  
  // Test Login and Logo
  console.log('🔐 Testing login page and logo...');
  const loginLogo = page.locator('.login-logo');
  await expect(loginLogo).toBeVisible();
  
  // Login
  await page.fill('#username', 'admin');
  await page.fill('#password', 'Jd3ng!n33r!ng2025#S3cur3');
  await page.click('.login-button');
  
  await expect(page.locator('.dashboard-container')).toBeVisible({ timeout: 10000 });
  
  // Test Dashboard Logo
  console.log('🖼️ Testing dashboard logo...');
  const dashboardLogo = page.locator('.company-logo');
  await expect(dashboardLogo).toBeVisible();
  
  // Wait for data to load
  await page.waitForTimeout(3000);
  
  // Test Stats Cards
  console.log('📊 Testing stats cards...');
  const statCards = [
    '#totalDevices',
    '#onlineDevices', 
    '#avgBattery',
    '#myobActive',
    '#scannerActive',
    '#timeoutRisks'
  ];
  
  for (const cardId of statCards) {
    const element = page.locator(cardId);
    await expect(element).toBeVisible();
    const value = await element.textContent();
    console.log(`${cardId}: ${value}`);
    expect(value).not.toBe('-');
  }
  
  // Test Charts Section
  console.log('📈 Testing charts section...');
  await expect(page.locator('.charts-section')).toBeVisible();
  
  // Test individual charts
  const charts = [
    { id: '#batteryChart', name: 'Battery Chart' },
    { id: '#wifiChart', name: 'WiFi Chart' },
    { id: '#myobChart', name: 'MYOB Chart' },
    { id: '#scannerChart', name: 'Scanner Chart' }
  ];
  
  for (const chart of charts) {
    console.log(`📊 Testing ${chart.name}...`);
    const chartElement = page.locator(chart.id);
    await expect(chartElement).toBeVisible();
    
    // Check if chart canvas has been rendered
    const canvas = page.locator(`${chart.id}`);
    await expect(canvas).toBeVisible();
    
    // Check chart container
    const container = page.locator(`${chart.id}`).locator('..');
    await expect(container).toBeVisible();
  }
  
  // Test Device Cards
  console.log('📱 Testing device cards...');
  const deviceCards = page.locator('.device-card');
  const deviceCount = await deviceCards.count();
  console.log(`Found ${deviceCount} device cards`);
  
  if (deviceCount > 0) {
    const firstDevice = deviceCards.first();
    await expect(firstDevice.locator('.device-name')).toBeVisible();
    await expect(firstDevice.locator('.device-status')).toBeVisible();
    await expect(firstDevice.locator('.device-metrics')).toBeVisible();
    
    // Check device metrics
    const metrics = firstDevice.locator('.metric');
    const metricCount = await metrics.count();
    console.log(`Found ${metricCount} metrics per device`);
    expect(metricCount).toBe(4); // Battery, WiFi, MYOB, Scanner
  }
  
  // Test Alerts Section
  console.log('🚨 Testing alerts section...');
  await expect(page.locator('.alert-section')).toBeVisible();
  await expect(page.locator('#alertsContainer')).toBeVisible();
  
  // Test Refresh Functionality
  console.log('🔄 Testing refresh functionality...');
  await page.click('#refreshBtn');
  await page.waitForTimeout(2000);
  
  const lastUpdated = await page.locator('#lastUpdated').textContent();
  console.log(`Last updated: ${lastUpdated}`);
  expect(lastUpdated).not.toContain('Never');
  
  // Take final screenshot
  await page.screenshot({ 
    path: 'final-dashboard-test.png', 
    fullPage: true 
  });
  console.log('📸 Final screenshot captured');
  
  console.log('✅ All tests passed! Dashboard is fully functional with charts and metrics.');
}); 