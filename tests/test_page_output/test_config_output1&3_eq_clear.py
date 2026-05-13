import re
import time
from playwright.sync_api import sync_playwright, expect

# ================= 全局配置 =================
CONFIG = {
    "target_url": "http://192.168.66.123/#/Home",
    "headless": False,  # False 表示开启有头模式
    "slow_mo": 800      # 每个操作停顿 800 毫秒，方便观察
}

def run_equalizer_test():
    with sync_playwright() as p:
        # 1. 启动浏览器：有头模式 + 自定义速度
        browser = p.chromium.launch(
            headless=CONFIG["headless"],
            slow_mo=CONFIG["slow_mo"]
        )
        context = browser.new_context()
        page = context.new_page()

        print(f"🚀 开始 Equalizer 测试，目标: {CONFIG['target_url']}")

        try:
            # 2. 导航并进入 Equalizer 界面
            page.goto(CONFIG["target_url"])
            page.wait_for_load_state("networkidle")

            page.locator("html").click()
            page.locator("div").filter(has_text=re.compile(r"^Output$")).click()
            # 点击第二个 Equalizer (通常一个是菜单，一个是内容)
            page.locator("div").filter(has_text=re.compile(r"^Equalizer$")).nth(1).click()

            # 3. 执行 Copy 操作
            print("📝 正在执行 Copy 逻辑...")
            page.get_by_text("Copy").first.click() # 点击顶部的 Copy 开启弹窗

            # 选择 Copy 的源/目标 (基于你的 nth-child 选择器)
            # 提示：类名带 Hash (xRQovd...) 比较脆弱，若失效建议改用 text 定位
            page.locator(".Copy-module_radio__xRQovdOVj8k_SfGIskF9").first.click()
            page.locator("div:nth-child(2) > .Copy-module_radio__xRQovdOVj8k_SfGIskF9").click()
            page.locator("div:nth-child(3) > .Copy-module_radio__xRQovdOVj8k_SfGIskF9").click()

            # 点击弹窗内的确认 Copy
            # 使用 nth(2) 或是 exact=True 取决于页面具体结构
            page.get_by_text("Copy").nth(2).click()
            page.get_by_text("Copy", exact=True).click()

            # 4. 执行取消与清理
            print("🧹 正在执行取消与清理...")
            page.get_by_text("Cancel").click()
            page.get_by_text("Clear").click()
            page.get_by_text("Ok").click()

            print("✅ Equalizer 测试流程执行完毕")

        except Exception as e:
            print(f"❌ 测试中断: {e}")

        finally:
            # 5. 结束后停留 5 秒供人工检查结果
            print("🏁 流程结束，5秒后自动关闭浏览器...")
            time.sleep(5)
            browser.close()

if __name__ == "__main__":
    run_equalizer_test()