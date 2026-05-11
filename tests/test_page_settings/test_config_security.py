import re
import time
from playwright.sync_api import Page, expect, sync_playwright


def test_security():
    with sync_playwright() as p:
        # headless=False 确保弹出浏览器窗口
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("http://192.168.66.123/#/Home")
        time.sleep(2)
        page.locator("div").filter(has_text=re.compile(r"^Settings$")).click()
        time.sleep(2)
        page.locator("div").filter(has_text=re.compile(r"^Security$")).nth(1).click()
        time.sleep(2)
        page.get_by_text("ENABLED").click()
        time.sleep(2)
        page.get_by_text("DISABLED").click()
        time.sleep(2)
        browser.close()
if __name__ == "__main__":
    test_security()