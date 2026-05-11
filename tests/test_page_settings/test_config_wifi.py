import re
import time
# 这里的导入必须包含 sync_playwright
from playwright.sync_api import sync_playwright, Page, expect


def test_wifi():
    # 使用 with 语句确保浏览器最后能正确关闭
    with sync_playwright() as p:
        # headless=False 确保弹出浏览器窗口
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # 1. 访问页面
        page.goto("http://192.168.66.123/#/Home")
        time.sleep(2)

        # 2. 点击底部导航栏/图标
        page.locator(".index-module_tabbar___XLvtaPKlwDxKfpwfeuC > div:nth-child(4) > img").click()
        time.sleep(2)

        # 3. 点击 WIFI 菜单
        page.get_by_text("WIFI").click()
        time.sleep(2)

        # 4. 点击 Disable WIFI 选项
        page.locator("div").filter(has_text=re.compile(r"^Disable WIFI$")).nth(1).click()
        time.sleep(2)

        # 5. 选择 30 分钟
        page.get_by_text("30 min").click()
        time.sleep(2)

        # 6. 选择 Always On (精确匹配)
        page.get_by_text("Always On", exact=True).click()
        time.sleep(2)

        # 7. 点击 Do Nothing
        page.locator("div").filter(has_text=re.compile(r"^Do Nothing$")).nth(1).click()
        time.sleep(2)

        # 任务完成，关闭浏览器
        browser.close()


if __name__ == "__main__":
    test_wifi()