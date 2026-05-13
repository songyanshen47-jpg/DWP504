import re
from playwright.sync_api import sync_playwright, expect


def run():
    # sync_playwright 允许手动控制浏览器
    with sync_playwright() as p:
        # headless=False 即开启“有头模式”
        # slow_mo=500 让每个操作停顿 0.5 秒，方便肉眼观察
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()

        # --- 以下是你的业务逻辑 ---
        page.goto("http://192.168.66.123/#/Home")

        # 增加一个等待确保页面加载
        page.wait_for_load_state("networkidle")

        page.locator("div").filter(has_text=re.compile(r"^Settings$")).click()
        page.get_by_text("GPIO").click()

        # GPIO 设置
        page.get_by_text("Standby (NO)").click()
        page.get_by_text("Standby (NC)").click()
        page.get_by_text("Mute (NO)").click()
        page.get_by_text("Mute (NC)").click()
        page.get_by_text("CH1 Volume Control").click()
        page.get_by_text("CH2 Volume Control").click()
        page.get_by_text("CH3 Volume Control").click()
        page.get_by_text("12V Trigger In").click()
        page.get_by_text("CH4 Volume Control").click()
        page.get_by_text("12V Trigger Out").click()
        page.get_by_text("CH4 Volume Control").click()

        # 处理 Off 按钮
        page.get_by_text("Off").nth(4).click()
        page.get_by_text("CH3 Volume Control").click()
        page.get_by_text("Off").nth(3).click()
        page.get_by_text("Off").nth(3).click()
        page.get_by_text("Off").nth(2).click()
        page.get_by_text("Off").nth(1).click()

        # 恢复/切换
        page.get_by_text("Mute (NO)").click()
        page.get_by_text("Standby (NC)").click()
        page.get_by_text("Standby (NO)").click()
        page.get_by_text("Off").first.click()

        print("测试执行完毕，浏览器将在 5 秒后关闭...")
        page.wait_for_timeout(5000)
        browser.close()


if __name__ == "__main__":
    run()