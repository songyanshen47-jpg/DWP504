import json
import time
import re
from playwright.sync_api import sync_playwright

# ==================== 配置 ====================
BASE_URL = "http://192.168.66.123/#/Home"


# ==============================================

def run_scanner():
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=False)  # 建议设为 False，你可以看到他在自动输入
        context = browser.new_context()
        page = context.new_page()

        print(f"🌐 正在连接 {BASE_URL}...")
        page.goto(BASE_URL)

        # 等待关键元素出现 (OUTPUT 1)
        card_xpath = "//div[contains(@class, 'Card-module_Card')][descendant::span[text()='OUTPUT 1']]"
        page.wait_for_selector(card_xpath, timeout=15000)

        # 定义 UI 元素
        # 1. 点击这个显示区域唤起输入框
        display_selector = f"{card_xpath}//div[contains(@class, 'ScaleSteper-module_display-message')]"
        # 2. 这是我们要抓取的百分比来源
        handle_selector = f"{card_xpath}//div[contains(@class, 'ant-slider-handle')]"
        # 3. 弹出的输入框
        input_selector = "input.ant-input-number-input"

        results = []
        # 从 -80.0 到 0.0，步长 0.1
        current_db = -80.0

        print("🧪 开始自动化扫描，这可能需要几分钟...")

        while current_db <= 0.05:  # 稍微多一点点防止浮点数精度漏掉 0.0
            db_str = f"{current_db:.1f}"

            try:
                # A. 唤起输入框
                page.click(display_selector)

                # B. 输入数值并回车
                page.wait_for_selector(input_selector, timeout=2000)
                page.fill(input_selector, db_str)
                page.keyboard.press("Enter")

                # C. ！！！关键：给 UI 渲染一点时间，确保滑块已经移动到位
                time.sleep(0.3)

                # D. 抓取句柄的 style 属性
                style = page.get_attribute(handle_selector, "style")
                # 提取 left: 12.3456% 中的数字部分
                match = re.search(r"left:\s*([\d\.]+)%", style)

                if match:
                    percent_val = match.group(1)
                    results.append({"db": db_str, "percent": percent_val})
                    print(f"  [Progress] {db_str} dB -> {percent_val}%")

                # E. 按 ESC 键关闭可能残留的弹窗/焦点
                page.keyboard.press("Escape")

            except Exception as e:
                print(f"  ⚠️ 处理 {db_str} dB 时发生错误: {e}")
                page.keyboard.press("Escape")

            current_db += 0.1

        # 保存为新的 JSON 文件
        with open("db_to_percent_mapping_v2.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)

        print("-" * 50)
        print(f"✅ 扫描完成！共记录 {len(results)} 个坐标点")
        print(f"📂 文件已保存为: db_to_percent_mapping_v2.json")
        print("-" * 50)

        browser.close()


if __name__ == "__main__":
    run_scanner()