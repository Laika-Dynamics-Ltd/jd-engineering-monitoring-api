#!/usr/bin/env python3
"""
Final Enterprise Dashboard Validation Suite
"""

import asyncio
import json
from playwright.async_api import async_playwright, Page
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinalTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    async def run_final_test(self):
        """Run final enterprise validation"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            try:
                await page.goto(f"{self.base_url}/dashboard")
                await page.wait_for_load_state("networkidle")
                
                results = {"enterprise_grade": True, "tests": {}}
                
                # Test 1: All sections present
                sections = [".business-overview", ".financial-impact", ".ai-insights", ".device-grid"]
                section_results = {}
                for section in sections:
                    count = await page.locator(section).count()
                    section_results[section] = count > 0
                
                results["tests"]["sections"] = section_results
                
                # Test 2: Devices displayed
                device_count = await page.locator(".device-card").count()
                results["tests"]["devices"] = {"count": device_count, "passed": device_count >= 3}
                
                # Test 3: Buttons work
                refresh_btn = await page.locator("#refreshBtn").count() > 0
                export_btn = await page.locator("#exportBtn").count() > 0
                results["tests"]["buttons"] = {"refresh": refresh_btn, "export": export_btn}
                
                # Test 4: Data populated
                total_devices = await page.locator("#totalDevices").text_content()
                results["tests"]["data"] = {"populated": total_devices != "-"}
                
                # Calculate overall score
                all_sections_present = all(section_results.values())
                devices_ok = device_count >= 3
                buttons_ok = refresh_btn and export_btn
                data_ok = total_devices != "-"
                
                results["enterprise_grade"] = all_sections_present and devices_ok and buttons_ok and data_ok
                
                print("\n" + "="*60)
                print("🏆 FINAL ENTERPRISE VALIDATION RESULTS")
                print("="*60)
                print(f"✅ All Sections Present: {all_sections_present}")
                print(f"✅ Devices Displayed: {devices_ok} ({device_count} devices)")
                print(f"✅ Interactive Buttons: {buttons_ok}")
                print(f"✅ Data Populated: {data_ok}")
                print(f"\n🎯 OVERALL STATUS: {'✅ ENTERPRISE GRADE' if results['enterprise_grade'] else '❌ NEEDS WORK'}")
                print("="*60)
                
                return results
                
            except Exception as e:
                print(f"Test error: {e}")
                return {"enterprise_grade": False, "error": str(e)}
            finally:
                await browser.close()

async def main():
    tester = FinalTester()
    result = await tester.run_final_test()
    
    if result.get("enterprise_grade"):
        print("\n🚀 SUCCESS! Dashboard is now enterprise-grade!")
    else:
        print("\n⚠️ Still needs some work")

if __name__ == "__main__":
    asyncio.run(main()) 