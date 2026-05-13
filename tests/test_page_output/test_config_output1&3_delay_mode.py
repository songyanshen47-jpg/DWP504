import re
import time
from playwright.sync_api import sync_playwright, expect

# ================= 全局配置 =================
CONFIG = {
    "target_url": "http://192.168.66.123/#/Home",
    "headless": False,  # 开启有头模式
    "slow_mo": 800  # 每次操作停顿 800 毫秒，方便肉眼确认 UI 变化
}


def run_delay_test():
    with sync_playwright() as p:
        # 1. 启动浏览器
        browser = p.chromium.launch(
            headless=CONFIG["headless"],
            slow_mo=CONFIG["slow_mo"]
        )
        context = browser.new_context()
        page = context.new_page()

        print(f"🚀 开始 Delay 测试，目标: {CONFIG['target_url']}")

        try:
            # 2. 导航并进入 Delay 界面
            page.goto(CONFIG["target_url"])
            page.wait_for_load_state("networkidle")

            page.locator("div").filter(has_text=re.compile(r"^Output$")).click()
            # 点击第一个 Delay 进入设置
            page.get_by_text("Delay").first.click()

            # 3. 切换单位 (Feet / Meter / Ms)
            print("📏 正在切换物理单位...")
            page.get_by_text("Feet", exact=True).click()
            page.get_by_text("Meter", exact=True).click()

            # 4. 操作开关 (Switch)
            print("🔘 正在操作延迟开关...")
            # 注意：类名带 Hash (raFYyTh...) 容易随版本变化，若失效请改用 text 定位
            page.locator(".Switch-module_Switch__raFYyThR9KYf_1SSrLZ4").click()
            page.get_by_text("Ms", exact=True).click()
            page.locator(".Switch-module_Switch__raFYyThR9KYf_1SSrLZ4").click()

            # 5. 数值加减操作
            print("➕ 正在增加延迟数值...")
            # 点击“加”图标
            page.locator(".Delay-module_plus__rEO3vmOOiYkZhq5pYCiO").first.click()
            # 连续点击加号图片
            for _ in range(3):
                page.locator(".Delay-module_plus__rEO3vmOOiYkZhq5pYCiO > img").first.click()

            print("➖ 正在减少延迟数值...")
            # 点击“减”图标及其图片
            page.locator(".Delay-module_pre__HetWO806GnwZCThb39Wa > img").first.click()
            # 执行双击
            page.locator(".Delay-module_pre__HetWO806GnwZCThb39Wa > img").first.dblclick()

            print("✅ Delay 测试流程执行完毕")

        except Exception as e:
            print(f"❌ 测试中断: {e}")

        finally:
            # 6. 结束后停留 5 秒供观察
            print("🏁 流程结束,5秒后自动关闭浏览器...")
            time.sleep(5)
            browser.close()


if __name__ == "__main__":
    run_delay_test()