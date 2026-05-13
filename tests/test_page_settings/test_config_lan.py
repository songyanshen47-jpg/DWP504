import re
import time
from playwright.sync_api import sync_playwright, expect

# ================= 全局配置参数 =================
# 使用 .strip() 彻底防止不可见字符干扰 URL 访问
CONFIG = {
    "target_url": "http://192.168.66.123/#/Home".strip(),
    "ip_address": "192.168.66.124",
    "net_mask": "255.255.255.0",
    "gateway": "192.168.66.1",
    "dns1": "8.8.8.8",
    "dns2": "114.114.114.114",
    "slow_mo": 800  # 操作间隔时间（毫秒）
}

# 输入框映射关系
FIELDS_MAP = {
    "Ip Address...": "ip_address",
    "Network Mask...": "net_mask",
    "Gateway...": "gateway",
    "Dns1...": "dns1",
    "Dns2...": "dns2"
}


def run_lan_test():
    # 使用 sync_playwright 启动手动控制模式
    with sync_playwright() as p:
        # 启动 Chromium 浏览器，有头模式
        browser = p.chromium.launch(
            headless=False,
            slow_mo=CONFIG["slow_mo"]
        )
        context = browser.new_context()
        page = context.new_page()

        # 打印调试信息，确认 URL 长度是否正确（应为 31）
        actual_url = CONFIG['target_url']
        print(f"🚀 测试开始")
        print(f"🔗 访问目标: {actual_url} (长度: {len(actual_url)})")

        try:
            # 1. 导航：使用 domcontentloaded 提高容错率
            # 针对 LAN 测试，只要页面骨架出来就开始操作，不等全加载
            page.goto(actual_url, wait_until="domcontentloaded", timeout=30000)

            # 确保关键元素出现
            page.wait_for_selector("text=Settings", timeout=10000)

            # 2. 进入 LAN 设置
            page.locator("div").filter(has_text=re.compile(r"^Settings$")).click()
            # 找到第二个 LAN（通常第一个是侧边栏文字，第二个是具体内容）
            page.locator("div").filter(has_text=re.compile(r"^LAN$")).nth(1).click()

            # 3. 遍历输入网络参数
            print("⌨️ 正在填充网络配置...")
            for field_label, config_key in FIELDS_MAP.items():
                input_value = CONFIG[config_key]
                # 定位输入框
                textbox = page.get_by_role("textbox", name=f"请输入{field_label}")

                textbox.click()
                textbox.fill("")  # 先清空
                textbox.type(input_value)  # 使用 type 模拟真实输入更稳定
                textbox.press("Enter")
                print(f"   ✅ {field_label[:-3]}: {input_value}")

            # 4. 模式切换与应用
            print("🔄 正在执行模式切换...")
            # 点击 DHCP 标签
            page.get_by_text("DHCP", exact=True).click()

            # 切换到 Static
            page.locator("div").filter(has_text=re.compile(r"^Static$")).nth(1).click()

            # 点击 Apply (注意：点击后 IP 可能会变，导致浏览器断开)
            print("💾 点击 Apply 提交设置...")
            page.get_by_text("Apply").click()

            # 使用原生 time.sleep 而非 page.wait，防止因断网导致的报错
            time.sleep(2)

            # 再切回 DHCP 测试一次
            page.locator("div").filter(has_text=re.compile(r"^DHCP$")).nth(1).click()
            page.get_by_text("Apply").click()

            print("🎉 LAN 配置测试流程已成功跑完")

        except Exception as e:
            # 捕捉常见的浏览器关闭错误，给出友好提示
            if "TargetClosedError" in str(e) or "Target page, context or browser has been closed" in str(e):
                print("📢 提示: 浏览器已断开或被关闭 (可能是修改 IP 导致网络刷新)")
            else:
                print(f"❌ 测试中断: {e}")
                # 尝试保存错误截图（如果浏览器还在的话）
                try:
                    page.screenshot(path="debug_error.png")
                except:
                    pass

        finally:
            print("🏁 准备退出...")
            # 使用 time.sleep 确保最后阶段不会因为调用 page 对象而崩溃
            time.sleep(5)
            try:
                browser.close()
            except:
                pass


if __name__ == "__main__":
    run_lan_test()