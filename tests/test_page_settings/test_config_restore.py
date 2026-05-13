import re
import time
from playwright.sync_api import sync_playwright, expect


def test_example():
    # 使用 with 确保资源正确释放
    with sync_playwright() as p:
        # 1. 初始化浏览器
        browser = p.chromium.launch(headless=False, slow_mo=800)
        context = browser.new_context()
        page = context.new_page()

        print("🚀 GPIO自动化测试准备开始")

        try:
            # 2. 访问页面并执行重置
            page.goto("http://192.168.66.123/#/Home")
            page.locator("div").filter(has_text=re.compile(r"^Settings$")).click()

            # 点击 Backup&Restore
            page.locator("div").filter(has_text=re.compile(r"^Backup&Restore$")).nth(1).click()

            print("⚠️ 正在执行 RESET...")
            page.get_by_text("RESET !").click()
            page.get_by_role("button", name="OK").click()
            time.sleep(8)
            # --- 第一次处理“重新加载”循环 ---
            handle_reload_loop(page)

            # 3. 执行重启设备
            print("🔄 正在执行 RESTART DEVICE...")
            page.get_by_text("Backup&Restore").click()
            page.get_by_text("RESTART DEVICE").click()
            page.get_by_role("button", name="OK").click()

            # 重启后页面通常会断开，等待一段时间让硬件启动
            print("⏳ 等待设备硬件初始化 (15秒)...")
            page.wait_for_timeout(15000)

            # 尝试回到首页，这可能会触发浏览器的错误页面（带“重新加载”按钮）
            try:
                page.goto("http://192.168.66.123/#/Home", timeout=5000)
            except:
                print("📡 页面暂时无法访问，准备通过‘重新加载’尝试连接...")

            # --- 第二次处理“重新加载”循环 ---
            handle_reload_loop(page)

            print("✅ 测试流程全部完成")

        except Exception as e:
            print(f"❌ 运行中出错: {e}")
        finally:
            time.sleep(5)
            browser.close()


def handle_reload_loop(page):
    """专门处理重新加载按钮的逻辑函数"""
    print("🔎 开始扫描‘重新加载’按钮...")

    # 设定一个总超时，防止无限循环（比如设备真的死机了）
    start_time = time.time()
    max_wait = 120  # 最多等2分钟

    while time.time() - start_time < max_wait:
        # 每次循环重新定位，防止元素过期
        reload_button = page.get_by_role("button", name="重新加载")

        if reload_button.is_visible():
            print(f"🖱️ 检测到按钮，点击并等待 3s... (已用时 {int(time.time() - start_time)}s)")
            try:
                reload_button.click()
            except:
                pass  # 忽略点击瞬间页面刷新的报错
            page.wait_for_timeout(3000)
        else:
            # 如果按钮不可见，尝试看页面核心元素是否加载
            # 比如检查是否回到了首页
            if page.locator("text=Settings").is_visible():
                print("🎉 页面已恢复正常访问")
                break

            # 如果既没按钮也没加载成功，可能还在白屏，继续等
            page.wait_for_timeout(2000)

    if time.time() - start_time >= max_wait:
        print("🛑 等待超时，设备可能未正常启动")


if __name__ == "__main__":
    test_example()