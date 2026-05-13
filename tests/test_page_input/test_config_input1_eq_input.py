import re
import time
import logging
from typing import Optional, Tuple
from playwright.sync_api import sync_playwright, Page

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EQControl:
    """EQ控制器 - 优化版"""

    def __init__(self, page: Page):
        self.page = page

    def _scroll_to_element(self, element):
        """滚动到元素可视区域"""
        self.page.evaluate("""
                           (element) => {
                               element.scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'});
                           }
                           """, element)
        self.page.wait_for_timeout(300)

    def _get_selector_box(self, eq_index: int, label: str):
        """获取指定EQ点和标签的选择器盒子"""
        # 使用更精确的定位：先找到所有Selector-box，再根据标签过滤
        return self.page.locator(
            f"div.Sliders-module_Selector-box__MZx3Tlky224Ayt4l94c9"
        ).filter(has=self.page.locator(f"span.Sliders-module_label__OJfkrGUICM0s28YfHyzO:text-is('{label}')")).nth(
            eq_index)

    def _get_display_area(self, eq_index: int, label: str):
        """获取显示区域"""
        selector_box = self._get_selector_box(eq_index, label)
        return selector_box.locator("div.ScaleSteper-module_display-message__wb6ITyygQfQIxZ9puqtw")

    def _get_active_input_in_popover(self, timeout: int = 3000):
        """
        获取当前激活弹窗内的输入框（解决多个输入框问题）
        """
        # 优先查找可见的ant-popover内的输入框
        selectors = [
            "div.ant-popover:not([style*='display: none']) input.ant-input-number-input",
            "div.ant-popover-arrow:not([style*='display: none']) ~ div input.ant-input-number-input",
            ".ant-popover-content input.ant-input-number-input",
        ]

        for selector in selectors:
            try:
                input_box = self.page.locator(selector).first
                if input_box.is_visible(timeout=500):
                    return input_box
            except:
                continue

        # 降级方案：查找所有可见的输入框，取最近激活的
        try:
            all_inputs = self.page.locator("input.ant-input-number-input:visible").all()
            for inp in all_inputs:
                if inp.is_visible() and inp.is_enabled():
                    return inp
        except:
            pass

        return None

    def _wait_for_stable(self, eq_index: int, label: str, timeout_ms: int = 2000) -> Tuple[str, float]:
        """等待UI稳定并返回当前值和百分比"""
        display_area = self._get_display_area(eq_index, label)
        slider_handle = selector_box = self._get_selector_box(eq_index, label).locator("div.ant-slider-handle")

        last_value = None
        last_percent = None
        start_time = time.time()

        while (time.time() - start_time) * 1000 < timeout_ms:
            # 获取当前显示值
            text = display_area.inner_text()
            value_match = re.search(r"(-?\d+\.?\d*)", text)
            current_value = value_match.group(1) if value_match else None

            # 获取当前百分比
            try:
                style = slider_handle.get_attribute("style")
                percent_match = re.search(r"left:\s*([\d\.]+)%", style)
                current_percent = float(percent_match.group(1)) if percent_match else None
            except:
                current_percent = None

            # 连续两次相同则认为稳定
            if (current_value, current_percent) == (last_value, last_percent) and current_value is not None:
                return current_value, current_percent

            last_value, last_percent = current_value, current_percent
            self.page.wait_for_timeout(100)

        return last_value, last_percent

    def set_frequency(self, eq_index: int, hz_value: int) -> bool:
        """设置频率值"""
        label = "Frequency [Hz]"
        logger.info(f"🎵 设置 EQ[{eq_index + 1}] Frequency = {hz_value} Hz")

        try:
            display_area = self._get_display_area(eq_index, label)

            # 滚动到可视区域
            self._scroll_to_element(display_area)

            # 点击显示区域
            display_area.click()
            self.page.wait_for_timeout(500)

            # 获取输入框
            input_field = self._get_active_input_in_popover()
            if not input_field:
                raise Exception("无法找到激活的输入框")

            # 清空并输入
            input_field.click()
            self.page.keyboard.press("Control+A")
            self.page.keyboard.fill(str(hz_value))
            self.page.wait_for_timeout(200)
            self.page.keyboard.press("Enter")

            # 等待稳定并验证
            actual_value, percent = self._wait_for_stable(eq_index, label)

            if actual_value and abs(float(actual_value) - hz_value) < 1:
                logger.info(f"   ✅ 设置成功: {actual_value} Hz (位置: {percent:.2f}%)")
                return True
            else:
                logger.warning(f"   ⚠️ 设置后显示为: {actual_value} Hz")
                return False

        except Exception as e:
            logger.error(f"   ❌ 设置失败: {e}")
            self.page.keyboard.press("Escape")
            return False

    def set_gain(self, eq_index: int, db_value: float) -> bool:
        """设置增益值"""
        label = "Gain [dB]"
        logger.info(f"📊 设置 EQ[{eq_index + 1}] Gain = {db_value} dB")

        try:
            display_area = self._get_display_area(eq_index, label)

            # 滚动到可视区域
            self._scroll_to_element(display_area)

            # 点击显示区域
            display_area.click()
            self.page.wait_for_timeout(500)

            # 获取输入框
            input_field = self._get_active_input_in_popover()
            if not input_field:
                raise Exception("无法找到激活的输入框")

            # 清空并输入
            input_field.click()
            self.page.keyboard.press("Control+A")
            self.page.keyboard.fill(str(db_value))
            self.page.wait_for_timeout(200)
            self.page.keyboard.press("Enter")

            # 等待稳定并验证
            actual_value, percent = self._wait_for_stable(eq_index, label)

            if actual_value and abs(float(actual_value) - db_value) < 0.2:
                logger.info(f"   ✅ 设置成功: {actual_value} dB (位置: {percent:.2f}%)")
                return True
            else:
                logger.warning(f"   ⚠️ 设置后显示为: {actual_value} dB")
                return False

        except Exception as e:
            logger.error(f"   ❌ 设置失败: {e}")
            self.page.keyboard.press("Escape")
            return False

    def set_q(self, eq_index: int, q_value: float) -> bool:
        """设置Q值"""
        label = "Q "
        logger.info(f"🔧 设置 EQ[{eq_index + 1}] Q = {q_value}")

        try:
            display_area = self._get_display_area(eq_index, label)

            # 滚动到可视区域
            self._scroll_to_element(display_area)

            # 点击显示区域
            display_area.click()
            self.page.wait_for_timeout(500)

            # 获取输入框
            input_field = self._get_active_input_in_popover()
            if not input_field:
                raise Exception("无法找到激活的输入框")

            # 清空并输入
            input_field.click()
            self.page.keyboard.press("Control+A")
            self.page.keyboard.fill(str(q_value))
            self.page.wait_for_timeout(200)
            self.page.keyboard.press("Enter")

            # 等待稳定并验证
            actual_value, percent = self._wait_for_stable(eq_index, label)

            if actual_value and abs(float(actual_value) - q_value) < 0.1:
                logger.info(f"   ✅ 设置成功: {actual_value} (位置: {percent:.2f}%)")
                return True
            else:
                logger.warning(f"   ⚠️ 设置后显示为: {actual_value}")
                return False

        except Exception as e:
            logger.error(f"   ❌ 设置失败: {e}")
            self.page.keyboard.press("Escape")
            return False

    def get_current_frequency(self, eq_index: int) -> Optional[float]:
        """获取当前频率值"""
        try:
            display_area = self._get_display_area(eq_index, "Frequency [Hz]")
            text = display_area.inner_text()
            match = re.search(r"(\d+\.?\d*)", text)
            return float(match.group(1)) if match else None
        except:
            return None

    def get_current_gain(self, eq_index: int) -> Optional[float]:
        """获取当前增益值"""
        try:
            display_area = self._get_display_area(eq_index, "Gain [dB]")
            text = display_area.inner_text()
            match = re.search(r"(-?\d+\.?\d*)", text)
            return float(match.group(1)) if match else None
        except:
            return None

    def get_current_q(self, eq_index: int) -> Optional[float]:
        """获取当前Q值"""
        try:
            display_area = self._get_display_area(eq_index, "Q ")
            text = display_area.inner_text()
            match = re.search(r"(\d+\.?\d*)", text)
            return float(match.group(1)) if match else None
        except:
            return None

    def configure_eq_point(self, eq_index: int, frequency: int = None, gain: float = None, q: float = None) -> dict:
        """配置单个EQ点的完整参数"""
        results = {"eq_index": eq_index, "success": True, "details": {}}

        logger.info(f"\n{'=' * 50}")
        logger.info(f"🎛️ 配置 EQ 点 {eq_index + 1}")
        logger.info(f"{'=' * 50}")

        if frequency is not None:
            results["details"]["frequency"] = self.set_frequency(eq_index, frequency)
            if not results["details"]["frequency"]:
                results["success"] = False
            self.page.wait_for_timeout(300)

        if gain is not None:
            results["details"]["gain"] = self.set_gain(eq_index, gain)
            if not results["details"]["gain"]:
                results["success"] = False
            self.page.wait_for_timeout(300)

        if q is not None:
            results["details"]["q"] = self.set_q(eq_index, q)
            if not results["details"]["q"]:
                results["success"] = False
            self.page.wait_for_timeout(300)

        return results

    def verify_eq_point(self, eq_index: int, expected_freq: int = None, expected_gain: float = None,
                        expected_q: float = None) -> dict:
        """验证EQ点配置是否正确"""
        results = {"eq_index": eq_index, "passed": True, "details": {}}

        if expected_freq is not None:
            actual = self.get_current_frequency(eq_index)
            is_match = actual == expected_freq
            results["details"]["frequency"] = {"expected": expected_freq, "actual": actual, "match": is_match}
            if not is_match:
                results["passed"] = False

        if expected_gain is not None:
            actual = self.get_current_gain(eq_index)
            is_match = abs(actual - expected_gain) < 0.1 if actual else False
            results["details"]["gain"] = {"expected": expected_gain, "actual": actual, "match": is_match}
            if not is_match:
                results["passed"] = False

        if expected_q is not None:
            actual = self.get_current_q(eq_index)
            is_match = abs(actual - expected_q) < 0.05 if actual else False
            results["details"]["q"] = {"expected": expected_q, "actual": actual, "match": is_match}
            if not is_match:
                results["passed"] = False

        return results


def run_eq_automation():
    """运行EQ自动化测试"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        page = browser.new_page()

        url = "http://192.168.66.123/#/Input/Input1"
        logger.info(f"🌐 正在连接: {url}")
        page.goto(url)

        # 等待页面加载
        page.wait_for_selector("text=Frequency [Hz]", timeout=15000)
        page.wait_for_timeout(2000)

        eq = EQControl(page)

        # 测试配置（只测试存在的EQ点）
        configs = [
            {"eq_index": 0, "frequency": 100, "gain": 5.5, "q": 1.5},
            {"eq_index": 2, "frequency": 1000, "gain": -3.0, "q": 0.7},
        ]

        all_results = []

        for config in configs:
            result = eq.configure_eq_point(
                eq_index=config["eq_index"],
                frequency=config.get("frequency"),
                gain=config.get("gain"),
                q=config.get("q")
            )
            all_results.append(result)
            page.wait_for_timeout(500)

        # 验证配置
        logger.info(f"\n{'=' * 50}")
        logger.info("🔍 验证配置结果")
        logger.info(f"{'=' * 50}")

        for config in configs:
            verify_result = eq.verify_eq_point(
                eq_index=config["eq_index"],
                expected_freq=config.get("frequency"),
                expected_gain=config.get("gain"),
                expected_q=config.get("q")
            )

            status = "✅ PASS" if verify_result["passed"] else "❌ FAIL"
            logger.info(f"EQ[{verify_result['eq_index'] + 1}]: {status}")

            for key, detail in verify_result["details"].items():
                match_str = "✓" if detail["match"] else "✗"
                logger.info(f"   {key}: 预期={detail['expected']}, 实际={detail['actual']} {match_str}")

        # 统计结果
        passed_count = sum(1 for r in all_results if r["success"])
        logger.info(f"\n📊 测试总结: {passed_count}/{len(all_results)} EQ点配置成功")

        page.wait_for_timeout(2000)
        browser.close()


if __name__ == "__main__":
    run_eq_automation()