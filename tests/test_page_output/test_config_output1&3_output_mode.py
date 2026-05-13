import re
import time
from playwright.sync_api import sync_playwright, expect

# ================= 全局配置 =================
CONFIG = {
    "target_url": "http://192.168.66.123/#/Home",
    "slow_mo": 800  # 设置操作间隔，有头模式下方便肉眼观察
}


def run_output_test():
    # 使用 sync_playwright 手动控制
    with sync_playwright() as p:
        # headless=False 开启有头模式
        browser = p.chromium.launch(headless=False, slow_mo=CONFIG["slow_mo"])
        context = browser.new_context()
        page = context.new_page()

        print(f"🚀 开始测试 Output Mode，目标: {CONFIG['target_url']}")

        try:
            # 1. 导航
            page.goto(CONFIG["target_url"])
            page.wait_for_load_state("networkidle")

            # 2. 进入 Output 菜单
            page.locator("html").click()
            page.locator("div").filter(has_text=re.compile(r"^Output$")).click()

            # 点击展开按钮 (使用你原始代码中的选择器)
            page.locator("div:nth-child(4) > div > .Submenu-module_arrowBox__x51srRwrcs0t6HtdVXhx > img").first.click()

            # 点击进入 Output Mode 详情
            page.get_by_text("Output Mode").first.click()

            # 3. 逐个点击模式选项
            # 注意：这里建议增加 visible=True 过滤，防止点到背景里隐藏的元素
            print("🔄 正在循环切换输出模式...")

            # 模式列表
            modes = ["Lo-Z", "Lo-Z Bridge", "Hi-Z-70V", "Hi-Z-100V", "OFF"]

            for mode in modes:
                print(f"   点击模式: {mode}")
                # exact=True 确保不会把 Lo-Z 误认为 Lo-Z Bridge
                # .first 解决如果页面同时存在“已选中”和“待选中”两个同名元素时的冲突
                page.get_by_text(mode, exact=True).first.click()

                # 每一步切换后给硬件一点反应时间
                page.wait_for_timeout(1000)

            print("✅ Output 模式循环切换完成")

        except Exception as e:
            print(f"❌ 测试过程中出现错误: {e}")

        finally:
            print("🏁 测试结束，停留 5 秒后关闭浏览器...")
            time.sleep(5)
            browser.close()


if __name__ == "__main__":
    run_output_test()