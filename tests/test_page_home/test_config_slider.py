import json
import re
import logging
import time
from playwright.sync_api import sync_playwright, Page

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class SliderRobustTester:
    def __init__(self, page: Page, mapping_file: str = "db_to_percent_mapping_v2.json"):
        self.page = page
        self.mapping = self._load_mapping(mapping_file)
        # 定位器
        self.card_xpath = "//div[contains(@class, 'Card-module_Card')][descendant::span[text()='OUTPUT 1']]"
        self.rail_loc = self.page.locator(f"{self.card_xpath}//div[contains(@class, 'ant-slider-rail')]")
        self.handle_loc = self.page.locator(f"{self.card_xpath}//div[contains(@class, 'ant-slider-handle')]")
        self.display_loc = self.page.locator(
            f"{self.card_xpath}//div[contains(@class, 'ScaleSteper-module_display-message')]")

    def _load_mapping(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {f"{float(item['db']):.1f}": float(item['percent']) for item in data}
        except Exception as e:
            logger.error(f"❌ 加载映射失败: {e}")
            return {}

    def get_stable_ui_state(self, timeout_ms=2000, tolerance=0.15):
        """
        加强版读取：在规定时间内等待数值稳定。
        如果数值在 300ms 内不再变化，则认为已停止滑动。
        tolerance: dB值容差（0.15dB）
        """
        last_state = (None, None)
        last_stable_state = (None, None)
        start_time = time.time()
        stable_start = None

        while (time.time() - start_time) * 1000 < timeout_ms:
            # 读取当前值
            text = self.display_loc.inner_text()
            db_match = re.search(r"(-?\d+\.?\d*)", text)
            cur_db = f"{float(db_match.group(1)):.1f}" if db_match else "N/A"

            style = self.handle_loc.get_attribute("style")
            pct_match = re.search(r"left:\s*([\d\.]+)%", style)
            cur_pct = float(pct_match.group(1)) if pct_match else 0.0

            current_state = (cur_db, cur_pct)

            # 如果状态相同或db值在容差范围内
            if current_state == last_state:
                if stable_start is None:
                    stable_start = time.time()
                if (time.time() - stable_start) * 1000 >= 300:
                    return cur_db, cur_pct
            else:
                # 检查db值是否在容差范围内（认为稳定）
                if last_state[0] != "N/A" and cur_db != "N/A":
                    try:
                        last_db = float(last_state[0])
                        cur_db_float = float(cur_db)
                        if abs(cur_db_float - last_db) <= tolerance:
                            if stable_start is None:
                                stable_start = time.time()
                            if (time.time() - stable_start) * 1000 >= 300:
                                return cur_db, cur_pct
                    except:
                        pass

                stable_start = None
                last_state = current_state

            self.page.wait_for_timeout(50)  # 缩短检查间隔

        return last_state

    def verify_current_before_move(self):
        """滑动前校验：当前 UI 状态是否符合 JSON 映射"""
        db, pct = self.get_stable_ui_state()
        standard_pct = self.mapping.get(db)

        if standard_pct is None:
            logger.warning(f"🔍 起点校验：当前 UI 显示 {db}dB，但映射表中无此值。")
            return False

        is_ok = abs(pct - standard_pct) < 0.2
        status = "✅ 正常" if is_ok else "❌ 异常(偏移)"
        logger.info(f"📍 滑动前起点检查: UI={db}dB, HTML={pct}%, 标准={standard_pct}%, 状态={status}")
        return is_ok

    def run_db_drag_test(self, target_dbs):
        logger.info(f"{'=' * 110}")
        logger.info(
            f"{'序号':<4} | {'起点检查':<10} | {'目标 dB':<10} | {'UI实际dB':<10} | {'UI实际%':<12} | {'JSON标准%':<12} | {'结果'}")
        logger.info(f"{'-' * 110}")

        rail_box = self.rail_loc.bounding_box()

        for i, target_db in enumerate(target_dbs):
            # 1. 滑动前先校验
            pre_check = self.verify_current_before_move()
            pre_status = "OK" if pre_check else "ERR"

            # 2. 准备目标坐标
            target_str = f"{float(target_db):.1f}"
            expected_pct = self.mapping.get(target_str)

            if expected_pct is None: continue

            # 计算坐标
            target_x = rail_box["x"] + (rail_box["width"] * (expected_pct / 100.0))
            target_y = rail_box["y"] + (rail_box["height"] / 2)

            # 3. 执行平滑滑动
            handle_box = self.handle_loc.bounding_box()
            self.page.mouse.move(handle_box["x"] + handle_box["width"] / 2, handle_box["y"] + handle_box["height"] / 2)
            self.page.mouse.down()

            # 模拟慢速拖拽
            steps = 25
            for s in range(1, steps + 1):
                # 即使是滑动过程中也稍微停顿，模拟真实物理阻力
                self.page.mouse.move(handle_box["x"] + (target_x - handle_box["x"]) * s / steps, target_y)
                if s % 5 == 0: self.page.wait_for_timeout(20)

            self.page.mouse.up()

            # 4. 关键：等待数值完全稳定后再读取结果
            # 这里调用加强版读取函数
            actual_db, actual_pct = self.get_stable_ui_state(timeout_ms=3000)


            # 5. 校验
            # 5. 校验（增加容差匹配）
            actual_db_float = float(actual_db) if actual_db != "N/A" else None
            target_db_float = float(target_str)
            db_match = actual_db_float is not None and abs(actual_db_float - target_db_float) <= 0.3
            pct_match = abs(actual_pct - expected_pct) < 0.2
            is_pass = db_match and pct_match
            result_str = "✅ PASS" if is_pass else "❌ FAIL"

            logger.info(
                f"{i + 1:<4} | {pre_status:<10} | {target_str:>8} dB | {actual_db:>8} dB | {actual_pct:>10.4f}% | {expected_pct:>10.4f}% | {result_str}"
            )


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1280, 'height': 800}, device_scale_factor=1)
        page = context.new_page()

        page.goto("http://192.168.66.123/#/Home")
        page.wait_for_selector("text=OUTPUT 1", timeout=15000)

        tester = SliderRobustTester(page)
        test_points = [-62.5, -31.1, -75.2, -28.9, -15.8, -9.4, -5.7, -1.2]

        tester.run_db_drag_test(test_points)
        browser.close()


if __name__ == "__main__":
    main()