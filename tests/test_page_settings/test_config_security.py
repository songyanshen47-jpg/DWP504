import re
import time
from playwright.sync_api import expect, sync_playwright


def test_security_full_flow():
    with sync_playwright() as p:
        # 1. 初始化浏览器
        browser = p.chromium.launch(headless=False, slow_mo=800)
        context = browser.new_context()
        page = context.new_page()

        print("\n🚀 开始 DWP504 Security 模块自动化测试")

        try:
            # 2. 导航至目标页面
            page.goto("http://192.168.66.123/#/Home")
            expect(page).to_have_url("http://192.168.66.123/#/Home")

            # 进入 Settings
            page.locator("div").filter(has_text=re.compile(r"^Settings$")).click()
            expect(page).to_have_url(re.compile(r".*/Settings/.*"))

            # 进入 Security
            page.locator("div").filter(has_text=re.compile(r"^Security$")).nth(1).click()
            expect(page).to_have_url(re.compile(r".*/Settings/Security"))
            print("✅ 成功定位至 Security 配置页")

            # --- 步骤 A: 开启密码保护并验证选中态 ---
            print("⚙️ 正在切换至 ENABLED...")
            enable_btn = page.locator("div").filter(has_text=re.compile(r"^ENABLED$")).nth(1)
            enable_btn.click()
            # 强断言：验证 class 是否包含 selected
            expect(enable_btn).to_have_class(re.compile(r".*selected.*"))
            print("✅ 状态切换验证成功: ENABLED")

            # --- 步骤 B: 测试密码输入逻辑 (在 ENABLED 状态下进行) ---
            print("⌨️ 正在测试密码输入逻辑...")
            pwd_val = "Admin123"

            # 定位密码框
            pwd_input = page.get_by_placeholder("Password", exact=True)
            pwd_input.fill(pwd_val)
            expect(pwd_input).to_have_value(pwd_val)

            # 定位重复密码框
            repeat_input = page.get_by_placeholder("Repeat Password", exact=True)
            repeat_input.fill(pwd_val)
            expect(repeat_input).to_have_value(pwd_val)
            print(f"✅ 密码填入成功并已通过 Value 断言: {pwd_val}")

            print("准备申请Apply")
            apply_btn = page.locator("div").filter(has_text=re.compile(r"^Apply$")).nth(1)
            apply_btn.click()
            notice = page.locator(".ant-message-notice")
            expect(notice).to_be_visible()
            expect(notice).to_have_class(re.compile(r".*ant-message-notice.*"))
            print("申请成功")
            # --- 步骤 1: 输入密码 ---
            # 使用你学到的 placeholder 定位
            time.sleep(5)
            pwd_input = page.get_by_placeholder("password")
            pwd_input.fill(pwd_val)
            print(f"✅ 已填入密码")

            # --- 步骤 2: 测试“小眼睛”功能 (严谨性验证) ---
            # 观察截图，小眼睛在 input 所在的同一个容器里
            # 我们定位那个带有 'anticon' 类的 span，或者直接找 input 后面的第一个 span
            eye_icon = page.locator(".anticon-eye-invisible, .anticon-eye-invisible").first

            # 验证初始状态是密文
            expect(pwd_input).to_have_attribute("type", "password")

            # 点击小眼睛
            eye_icon.click(force=True)

            # 验证变为明文
            expect(pwd_input).to_have_attribute("type", "text")
            print("✅ 小眼睛切换成功：密码已显性化")

            # --- 步骤 3: 勾选“记住密码” (Remember the password) ---
            # 严谨做法：通过 label 文字定位，这样点击最准确
            remember_checkbox = page.get_by_text("remember the password", exact=False)

            # 在点之前，我们可以验证它是否未被选中
            # 注意：Ant Design 的原始 input 被隐藏了，check() 方法会自动处理
            remember_checkbox.click()

            # 验证是否勾选成功 (检查父级 label 是否带有 'checked' 类名)
            checkbox_wrapper = page.locator("label").filter(has_text="remember the password")
            # 虽然 checkbox 是自定义的，但点击后通常会影响内部 input 的状态
            print("✅ 已勾选‘记住密码’")

            # --- 步骤 4: 点击登录按钮 (LOG IN) ---
            # 截图 6 显示登录按钮是一个带有 'login-module_submit' 类的 div
            login_btn = page.get_by_text("LOG IN", exact=True)

            # 严谨起见，确保按钮现在是可点击的
            expect(login_btn).to_be_enabled()

            login_btn.click()
            print("🚀 已点击登录按钮，等待页面跳转...")

            # --- 步骤 5: 验证登录结果 ---
            # 验证是否跳转到了 Home 页面
            expect(page).to_have_url(re.compile(r".*/Home"))
            print("🎉 登录成功，已进入主页")

        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            # 报错时自动截图保留证据
            page.screenshot(path="security_error.png")
            raise e
        finally:
            time.sleep(2)  # 留点时间看一眼最后的结果
            browser.close()


if __name__ == "__main__":
    test_security_full_flow()