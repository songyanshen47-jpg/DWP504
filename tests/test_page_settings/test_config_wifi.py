import re
import time
from playwright.sync_api import sync_playwright, expect


def test_wifi_configuration():
    """
    功能：测试 WIFI 配置页面的独立选项切换
    逻辑：
    1. 验证主页并进入设置
    2. 验证并进入 WIFI 详情页
    3. 切换 [WHEN LAN CONNECTED] 模块选项
    4. 切换 [DISABLE WIFI AFTER] 模块选项
    """

    # 启动浏览器，增加 slow_mo 方便肉眼观察 UI 变化（调试建议 500-1000ms）
    with sync_playwright() as p:
        # 工业标准：launch 增加调试友好性
        browser = p.chromium.launch(headless=False, slow_mo=800)
        context = browser.new_context()
        page = context.new_page()

        try:
            # --- 1. 访问主页 ---
            print("\n[STEP 1] 正在访问设备主页...")
            page.goto("http://192.168.66.123/#/Home")
            expect(page).to_have_url("http://192.168.66.123/#/Home")
            print("✅ 成功进入主页")

            # --- 2. 进入设置菜单 ---
            print("[STEP 2] 正在打开设置菜单...")
            # 定位底部导航栏第四个图标
            settings_tab = page.locator(".index-module_tabbar___XLvtaPKlwDxKfpwfeuC > div:nth-child(4) > img")
            settings_tab.click()

            # 严谨断言：确保 URL 包含 Settings 且页面出现了 Information 字样
            expect(page).to_have_url(re.compile(r".*/Settings/.*", re.IGNORECASE))
            expect(page.get_by_text("Information", exact=True)).to_be_visible()
            print("✅ 成功进入设置页面")

            # --- 3. 进入 WIFI 详情页 ---
            # 使用属性选择器精确定位包含特定范围的输入框
            # 这样可以确保你断言的是“那个具有 20-20000 范围的频率输入框”
            target_input = page.locator("input.ant-input-number-input[aria-valuemin='20'][aria-valuemax='20000']")

            # 改进断言 1：验证输入框本身及其范围属性，并且是可见的
            expect(target_input).to_be_visible()

            # 改进断言 2：如果你一定要通过包裹容器（wrap）来断言，可以使用以下结构定位：
            # 定位 target_input 的父级中包含 '-wrap' 类名的那个 div
            input_wrap = page.locator("div[class*='ant-input-number-input-wrap']").filter(has=target_input)
            expect(input_wrap).to_be_visible()

            # 严谨断言：验证进入了 WIFI 专属路径，且看到了专属配置项
            expect(page).to_have_url(re.compile(r".*/Settings/WIFI", re.IGNORECASE))
            expect(page.get_by_text("WiFi Mode")).to_be_visible()
            print("✅ 成功进入 WIFI 配置详情页")

            # --- 4. 配置 [WHEN LAN CONNECTED] 模块 (独立项) ---
            print("[STEP 4] 正在配置 LAN 连接策略...")
            # 使用更精确的定位过滤干扰
            btn_disable_wifi = page.locator("div").filter(has_text=re.compile(r"^Disable WIFI$")).nth(1)
            btn_disable_wifi.click()

            # 验证点击生效：在标准测试中，通常会检查按钮的 class 是否包含 "selected"
            # 这里我们简单验证它依然可见，确保没有发生意外跳转
            expect(btn_disable_wifi).to_have_class(re.compile(r".*selected.*"))
            print("✅ 验证成功：[Disable WIFI]按钮样式已切换为选中状态")


            btn_do_nothing = page.locator("div").filter(has_text=re.compile(r"^Do Nothing$")).nth(1)
            btn_do_nothing.click()
            expect(btn_do_nothing).to_have_class(re.compile(r".*selected.*"))
            print("✅ 已点击 [Do Nothing]")

            # --- 5. 配置 [DISABLE WIFI AFTER] 模块 (独立项) ---
            print("[STEP 5] 正在配置自动关闭延迟...")

            # 选 30 min
            btn_30min = page.get_by_text("30 min", exact=True)
            btn_30min.click()
            expect(btn_30min).to_have_class(re.compile(r".*selected.*"))
            print("✅ 已选中 [30 min]")

            # 恢复为 Always On
            btn_always_on = page.get_by_text("Always On", exact=True)
            btn_always_on.click()
            expect(btn_always_on).to_have_class(re.compile(r".*selected.*"))
            print("✅ 已恢复选中 [Always On]")

            # --- 6. 完成退出 ---
            print("\n[RESULT] 所有配置项点击及断言验证通过！")

            # 调试建议：在关闭前留出时间查看最终状态
            time.sleep(3)

        except Exception as e:
            print(f"\n❌ 测试过程中发生错误: {e}")
            # 工业标准：出错时截个图，方便排查
            page.screenshot(path="error_debug.png")
            print("📸 已保存错误截图至 error_debug.png")
            raise e

        finally:
            browser.close()


if __name__ == "__main__":
    test_wifi_configuration()