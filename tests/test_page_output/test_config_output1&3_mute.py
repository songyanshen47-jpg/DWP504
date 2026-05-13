import re
import time
from playwright.sync_api import sync_playwright, expect

# ================= 全局配置 =================
CONFIG = {
    "target_url": "http://192.168.66.123/#/Home",
    "headless": False,  # False 表示开启有头模式
    "slow_mo": 1000  # 每次操作停顿 1 秒，方便肉眼观察
}


def run_sound_icon_test():
    with sync_playwright() as p:
        # 1. 启动浏览器
        browser = p.chromium.launch(
            headless=CONFIG["headless"],
            slow_mo=CONFIG["slow_mo"]
        )
        context = browser.new_context()
        page = context.new_page()

        print(f"🚀 测试开始，正在访问: {CONFIG['target_url']}")

        try:
            # 2. 导航并等待页面加载
            page.goto(CONFIG["target_url"])
            page.wait_for_load_state("networkidle")

            # 3. 进入 Output 菜单
            # 使用更稳健的定位方式
            page.locator("div").filter(has_text=re.compile(r"^Output$")).click()

            # 4. 连续点击 Sound Icon (静音/取消静音图标)
            # 这里的类名包含 Hash 值，如果以后报错，建议改用更通用的定位器
            sound_icon = page.locator(".DbSelector-module_sound-icon__BC33GBiAVYMioqla4zYO")

            print("🔔 开始点击 Sound Icon...")
            for i in range(1, 5):
                # 检查元素是否可见再点击
                if sound_icon.is_visible():
                    sound_icon.click()
                    print(f"   第 {i} 次点击完成")
                else:
                    print(f"   ⚠️ 第 {i} 次尝试时图标不可见")

            print("✅ 连续点击测试完成")

        except Exception as e:
            print(f"❌ 测试中断: {e}")

        finally:
            # 5. 结束后停留 5 秒观察结果，然后关闭
            print("🏁 流程结束，5秒后关闭浏览器...")
            time.sleep(5)
            browser.close()


if __name__ == "__main__":
    run_sound_icon_test()