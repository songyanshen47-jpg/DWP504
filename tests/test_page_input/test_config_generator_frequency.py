import re
from playwright.sync_api import Page, expect


def test_example(page: Page) -> None:
    with sync_playwright() as p:
        # 1. 初始化浏览器
        browser = p.chromium.launch(headless=False, slow_mo=800)
        context = browser.new_context()
        page = context.new_page()

        print("\n🚀 开始 DWP504 Security 模块自动化测试")

        try:
            # 2. 导航至目标页面
            page.goto("http://192.168.66.123/#/Input/Input1")
            expect(page).to_have_url("http://192.168.66.123/#/Input/Input1")
            page.locator("div").filter(has_text=re.compile(r"^Generator$")).nth(1).click()
            expect(page).to_have_url(re.compile(r".*/Input/Generator"))
            print("✅ 成功定位至 Generator 配置页")
            # 1. 定位轨道和滑块中心点
            slider_track = page.locator(".ant-slider-step")
            handle = page.locator(".ant-slider-handle").first

            box = slider_track.bounding_box()
            handle_box = handle.bounding_box()

            if box and handle_box:
                # 起点：滑块当前中心位置
                start_x = handle_box['x'] + handle_box['width'] / 2
                start_y = handle_box['y'] + handle_box['height'] / 2
                # 终点：轨道的最右侧
                end_x = box['x'] + box['width']
                end_y = box['y'] + box['height'] / 2
                # 2. 鼠标移动到滑块并按下
                page.mouse.move(start_x, start_y)
                page.mouse.down()
                # 3. 分段滑动实现“不快不慢”
                # steps 参数决定了移动的平滑度（Playwright 会在两个坐标间插入中间点）
                # 我们分多次移动，每次移动一小段，中间加微小延迟
                segments = 10  # 将全长分为10段
                for i in range(1, segments + 1):
                    current_target_x = start_x + (end_x - start_x) * (i / segments)
                    # steps=5 表示每段路径细分为5个中间帧，增加视觉上的连续感
                    page.mouse.move(current_target_x, end_y, steps=5)
                    # 适当等待（如 50ms），控制整体滑动时间
                    page.wait_for_timeout(50)
                    # 4. 松开鼠标
                    page.mouse.up()
                    page.get_by_role("slider").nth(1).click()


