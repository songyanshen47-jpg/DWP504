import json
import time
import re
from playwright.sync_api import sync_playwright

# ==================== 配置 ====================
BASE_URL = "http://192.168.66.123/#/Input/Input1"


def get_next_frequency(curr):
    """根据频率范围决定步进逻辑"""
    if curr < 200:
        return curr + 1
    elif curr < 2000:
        return curr + 10
    else:
        return curr + 100


def run_frequency_scanner_and_smooth_drag():
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(device_scale_factor=1)
        page = context.new_page()

        print(f"🌐 正在连接 {BASE_URL}...")
        page.goto(BASE_URL)

        # 1. 核心修复：精准定位 Frequency 所在的行容器
        # 使用 has_text 过滤，确保我们只操作 Frequency 这一行的组件
        # .first 确保如果页面结构复杂，也只取匹配到的第一个
        container = page.locator("div[class*='Sliders-module_Selector']", has_text="Frequency").first

        try:
            container.wait_for(state="visible", timeout=15000)
        except:
            print("❌ 未能找到包含 'Frequency' 的滑块容器，请检查页面是否加载正确。")
            browser.close()
            return

        # 在容器内定义局部定位器，解决 Strict Mode 冲突
        display_selector = container.locator("div[class*='ScaleSteper-module_display-message']")
        handle_locator = container.locator(".ant-slider-handle")
        track_locator = container.locator(".ant-slider-step")
        input_selector = "input.ant-input-number-input"

        results = []
        current_hz = 20
        target_max = 20000

        print("🧪 第一阶段：开始频率与 aria-valuenow 映射扫描...")

        while current_hz <= target_max:
            hz_str = str(current_hz)
            try:
                # 唤起输入框并填值
                display_selector.click()
                page.wait_for_selector(input_selector, timeout=2000)
                page.locator(input_selector).fill(hz_str)
                page.keyboard.press("Enter")

                # 等待 UI 响应和内部计算完成
                time.sleep(0.3)

                # 获取属性（此处 handle_locator 在容器内是唯一的，会自动绕过全局冲突）
                # 如果依然提示冲突，可改用 handle_locator.first
                aria_now = handle_locator.get_attribute("aria-valuenow")
                style = handle_locator.get_attribute("style")

                # 正则解析百分比坐标
                match = re.search(r"left:\s*([\d\.]+)%", style)

                if aria_now and match:
                    percent_val = float(match.group(1))
                    results.append({
                        "hz": current_hz,
                        "aria_valuenow": float(aria_now),
                        "percent": percent_val
                    })
                    # 每隔一段频率打印一次日志，避免刷屏
                    if current_hz % 1000 == 0 or current_hz == 20:
                        print(f"  [Mapping] {hz_str:>5} Hz -> aria-now: {aria_now[:7]} | {percent_val}%")

                # 退出输入状态
                page.keyboard.press("Escape")

            except Exception as e:
                print(f"  ⚠️ 处理 {hz_str} Hz 时跳过: {e}")
                page.keyboard.press("Escape")

            current_hz = get_next_frequency(current_hz)

        # 保存结果
        with open("frequency_mapping.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        print(f"✅ 映射完成，共记录 {len(results)} 个点。")

        # --- 第二阶段：平滑滑动演示 ---
        print("\n🚀 第二阶段：利用映射数据执行平滑滑动...")

        track_box = track_locator.bounding_box()
        if track_box and results:
            # 1. 移动到 20Hz 起始点
            start_x = track_box['x'] + (track_box['width'] * (results[0]['percent'] / 100))
            y_center = track_box['y'] + (track_box['height'] / 2)

            page.mouse.move(start_x, y_center)
            page.mouse.down()
            time.sleep(0.5)

            # 2. 抽样滑动（每 15 个数据点取一个，保证速度适中且轨迹精准）
            for entry in results[::15]:
                current_x = track_box['x'] + (track_box['width'] * (entry['percent'] / 100))
                # steps=2 增加视觉平滑度
                page.mouse.move(current_x, y_center, steps=2)
                time.sleep(0.01)

            # 3. 移动到 20kHz 终点
            end_x = track_box['x'] + (track_box['width'] * (results[-1]['percent'] / 100))
            page.mouse.move(end_x, y_center, steps=5)
            page.mouse.up()

            print("🏁 平滑滑动演练结束！")

        time.sleep(3)
        browser.close()


if __name__ == "__main__":
    run_frequency_scanner_and_smooth_drag()