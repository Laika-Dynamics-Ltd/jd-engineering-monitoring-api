#!/usr/bin/env python3
"""
Enterprise Dashboard Testing and Improvement Suite
Uses Playwright to systematically test and improve the dashboard to enterprise standards
"""

import asyncio
import json
import time
from playwright.async_api import async_playwright, Page, Browser
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnterpriseDashboardTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "performance": {},
            "functionality": {},
            "ui_ux": {},
            "accessibility": {},
            "security": {},
            "enterprise_features": {}
        }
        
    async def run_full_analysis(self):
        """Run comprehensive enterprise-level analysis of the dashboard"""
        async with async_playwright() as p:
            # Test in Chromium first for initial analysis
            browser = await p.chromium.launch(headless=False)
            await self._test_browser(browser, "chromium")
            await browser.close()
                
        return self.results
    
    async def _test_browser(self, browser: Browser, browser_name: str):
        """Test dashboard in specific browser"""
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # 1. Performance Analysis
            await self._test_performance(page, browser_name)
            
            # 2. Functionality Testing
            await self._test_functionality(page, browser_name)
            
            # 3. UI/UX Analysis
            await self._test_ui_ux(page, browser_name)
            
            # 4. Accessibility Testing
            await self._test_accessibility(page, browser_name)
            
            # 5. Security Analysis
            await self._test_security(page, browser_name)
            
            # 6. Enterprise Features Assessment
            await self._test_enterprise_features(page, browser_name)
            
        except Exception as e:
            logger.error(f"Error testing {browser_name}: {str(e)}")
        finally:
            await context.close()
    
    async def _test_performance(self, page: Page, browser_name: str):
        """Test performance metrics"""
        logger.info(f"Testing performance in {browser_name}")
        
        # Start performance monitoring
        start_time = time.time()
        await page.goto(f"{self.base_url}/dashboard")
        await page.wait_for_load_state("networkidle")
        load_time = time.time() - start_time
        
        self.results["performance"][browser_name] = {
            "page_load_time": load_time,
            "status": "slow" if load_time > 3 else "acceptable"
        }
        
        logger.info(f"Performance results for {browser_name}: {self.results['performance'][browser_name]}")
    
    async def _test_functionality(self, page: Page, browser_name: str):
        """Test core functionality"""
        logger.info(f"Testing functionality in {browser_name}")
        
        await page.goto(f"{self.base_url}/dashboard")
        await page.wait_for_load_state("networkidle")
        
        functionality_results = {}
        
        # Test 1: Dashboard loads without errors
        try:
            title = await page.title()
            functionality_results["title_loaded"] = "JD Engineering" in title
        except:
            functionality_results["title_loaded"] = False
        
        # Test 2: Key elements are present
        key_elements = [
            ".business-overview",
            ".device-grid", 
            ".financial-impact",
            ".ai-insights"
        ]
        
        for element in key_elements:
            try:
                await page.wait_for_selector(element, timeout=5000)
                functionality_results[f"element_{element.replace('.', '').replace('#', '')}"] = True
            except:
                functionality_results[f"element_{element.replace('.', '').replace('#', '')}"] = False
        
        # Test 3: Interactive elements work
        try:
            refresh_button = page.locator("button:has-text('Refresh Data')")
            if await refresh_button.count() > 0:
                await refresh_button.click()
                functionality_results["refresh_button_works"] = True
            else:
                functionality_results["refresh_button_works"] = False
        except:
            functionality_results["refresh_button_works"] = False
        
        # Test 4: Data displays correctly
        try:
            device_cards = page.locator(".device-card")
            device_count = await device_cards.count()
            functionality_results["devices_displayed"] = device_count > 0
            functionality_results["device_count"] = device_count
        except:
            functionality_results["devices_displayed"] = False
            functionality_results["device_count"] = 0
        
        self.results["functionality"][browser_name] = functionality_results
        logger.info(f"Functionality results for {browser_name}: {functionality_results}")
    
    async def _test_ui_ux(self, page: Page, browser_name: str):
        """Test UI/UX quality"""
        logger.info(f"Testing UI/UX in {browser_name}")
        
        await page.goto(f"{self.base_url}/dashboard")
        await page.wait_for_load_state("networkidle")
        
        ui_ux_results = {}
        
        # Test responsive design
        viewport_sizes = [
            {"width": 320, "height": 568},   # Mobile
            {"width": 768, "height": 1024},  # Tablet  
            {"width": 1920, "height": 1080}  # Desktop
        ]
        
        responsive_results = {}
        for size in viewport_sizes:
            await page.set_viewport_size(size)
            await page.wait_for_timeout(500)
            
            try:
                header = page.locator(".header")
                header_visible = await header.is_visible()
                responsive_results[f"{size['width']}x{size['height']}"] = header_visible
            except:
                responsive_results[f"{size['width']}x{size['height']}"] = False
        
        ui_ux_results["responsive_design"] = responsive_results
        
        self.results["ui_ux"][browser_name] = ui_ux_results
        logger.info(f"UI/UX results for {browser_name}: {ui_ux_results}")
    
    async def _test_accessibility(self, page: Page, browser_name: str):
        """Test accessibility compliance"""
        logger.info(f"Testing accessibility in {browser_name}")
        
        await page.goto(f"{self.base_url}/dashboard")
        await page.wait_for_load_state("networkidle")
        
        accessibility_results = {}
        
        # Test ARIA labels and roles
        try:
            aria_elements = await page.locator("[aria-label], [role]").count()
            accessibility_results["aria_elements_count"] = aria_elements
        except:
            accessibility_results["aria_elements_count"] = 0
        
        # Test keyboard navigation
        try:
            focusable_elements = await page.locator("button, a, input, select, textarea, [tabindex]").count()
            accessibility_results["focusable_elements"] = focusable_elements
        except:
            accessibility_results["focusable_elements"] = 0
        
        self.results["accessibility"][browser_name] = accessibility_results
        logger.info(f"Accessibility results for {browser_name}: {accessibility_results}")
    
    async def _test_security(self, page: Page, browser_name: str):
        """Test security aspects"""
        logger.info(f"Testing security in {browser_name}")
        
        security_results = {}
        
        # Test HTTPS usage
        try:
            url = page.url
            security_results["uses_https"] = url.startswith("https://")
        except:
            security_results["uses_https"] = False
        
        self.results["security"][browser_name] = security_results
        logger.info(f"Security results for {browser_name}: {security_results}")
    
    async def _test_enterprise_features(self, page: Page, browser_name: str):
        """Test enterprise-specific features"""
        logger.info(f"Testing enterprise features in {browser_name}")
        
        await page.goto(f"{self.base_url}/dashboard")
        await page.wait_for_load_state("networkidle")
        
        enterprise_results = {}
        
        # Test real-time data updates
        try:
            refresh_elements = await page.locator("button:has-text('Refresh'), .auto-refresh").count()
            enterprise_results["real_time_updates"] = refresh_elements > 0
        except:
            enterprise_results["real_time_updates"] = False
        
        # Test business intelligence features
        try:
            bi_elements = [".financial-impact", ".ai-insights", ".business-overview"]
            bi_count = 0
            for element in bi_elements:
                count = await page.locator(element).count()
                if count > 0:
                    bi_count += 1
            
            enterprise_results["business_intelligence_coverage"] = bi_count / len(bi_elements)
        except:
            enterprise_results["business_intelligence_coverage"] = 0
        
        # Test data export capabilities
        try:
            export_buttons = await page.locator("button:has-text('Export'), .export-btn").count()
            enterprise_results["data_export"] = export_buttons > 0
        except:
            enterprise_results["data_export"] = False
        
        self.results["enterprise_features"][browser_name] = enterprise_results
        logger.info(f"Enterprise features results for {browser_name}: {enterprise_results}")

async def main():
    """Run the enterprise dashboard analysis"""
    logger.info("Starting Enterprise Dashboard Analysis...")
    
    tester = EnterpriseDashboardTester()
    results = await tester.run_full_analysis()
    
    # Save results to file
    with open("enterprise_analysis_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Generate improvement recommendations
    recommendations = generate_recommendations(results)
    
    # Save recommendations
    with open("improvement_recommendations.json", "w") as f:
        json.dump(recommendations, f, indent=2)
    
    logger.info("Analysis complete. Results saved to enterprise_analysis_results.json")
    logger.info("Recommendations saved to improvement_recommendations.json")
    
    # Print summary
    print_analysis_summary(results, recommendations)

def generate_recommendations(results: Dict) -> Dict:
    """Generate improvement recommendations based on test results"""
    recommendations = {
        "critical": [],
        "high": [],
        "medium": [],
        "low": []
    }
    
    # Analyze performance issues
    for browser, perf_data in results["performance"].items():
        if perf_data.get("page_load_time", 0) > 3:
            recommendations["high"].append({
                "category": "Performance",
                "issue": f"Slow page load time in {browser} ({perf_data['page_load_time']:.2f}s)",
                "solution": "Optimize assets, implement lazy loading, minimize JavaScript"
            })
    
    # Analyze functionality issues
    for browser, func_data in results["functionality"].items():
        if not func_data.get("devices_displayed", False):
            recommendations["critical"].append({
                "category": "Functionality",
                "issue": f"No devices displayed in {browser}",
                "solution": "Fix device data loading, implement fallback data"
            })
        
        if not func_data.get("refresh_button_works", False):
            recommendations["high"].append({
                "category": "Functionality", 
                "issue": f"Refresh button not working in {browser}",
                "solution": "Fix JavaScript event handlers, add proper error handling"
            })
    
    # Analyze enterprise features
    for browser, ent_data in results["enterprise_features"].items():
        if not ent_data.get("real_time_updates", False):
            recommendations["high"].append({
                "category": "Enterprise Features",
                "issue": f"No real-time updates in {browser}",
                "solution": "Implement WebSocket or polling for live data updates"
            })
        
        if not ent_data.get("data_export", False):
            recommendations["medium"].append({
                "category": "Enterprise Features",
                "issue": f"No data export functionality in {browser}",
                "solution": "Add CSV/Excel export, PDF reporting capabilities"
            })
    
    return recommendations

def print_analysis_summary(results: Dict, recommendations: Dict):
    """Print a summary of the analysis and recommendations"""
    print("\n" + "="*60)
    print("ENTERPRISE DASHBOARD ANALYSIS SUMMARY")
    print("="*60)
    
    # Count issues by severity
    critical_count = len(recommendations["critical"])
    high_count = len(recommendations["high"])
    medium_count = len(recommendations["medium"])
    low_count = len(recommendations["low"])
    
    print(f"\n📊 ISSUES IDENTIFIED:")
    print(f"  🔴 Critical: {critical_count}")
    print(f"  🟡 High:     {high_count}")
    print(f"  🟠 Medium:   {medium_count}")
    print(f"  🟢 Low:      {low_count}")
    
    print(f"\n🎯 TOP RECOMMENDATIONS:")
    for priority in ["critical", "high", "medium"]:
        if recommendations[priority]:
            print(f"\n{priority.upper()} PRIORITY:")
            for i, rec in enumerate(recommendations[priority][:3], 1):
                print(f"  {i}. [{rec['category']}] {rec['issue']}")
                print(f"     → {rec['solution']}")

if __name__ == "__main__":
    asyncio.run(main()) 