import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class GainTester:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.label = "Gain"

    def _get_section(self):
        """精准定位 Gain 控制区域容器"""
        xpath = f"//div[contains(@class, 'Sliders-module_Selector-box')][descendant::span[contains(text(), '{self.label}')]]"
        return self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

    def get_current_value(self):
        """读取当前显示的 Gain 数值"""
        try:
            section = self._get_section()
            display_el = section.find_element(By.CSS_SELECTOR, "div[class*='display-message']")
            text = display_el.text.strip()
            # 提取数字（支持负号和小数点）
            match = re.search(r"(-?\d+\.?\d*)", text)
            if not match: return None
            return round(float(match.group(1)), 1)
        except Exception as e:
            print(f"❌ 读取 Gain 数值失败: {e}")
            return None

    def run_test(self, target_db):
        """执行 Gain 测试流程"""
        # 限制目标值不超出物理范围
        target_db = max(-15.0, min(15.0, target_db))

        print(f"\n🚀 开始 Gain 测试 | 目标值: {target_db} dB")
        print("-" * 60)

        section = self._get_section()
        plus_btn = section.find_element(By.CSS_SELECTOR, "div[class*='plus']")
        minus_btn = section.find_element(By.CSS_SELECTOR, "div[class*='pre']")

        while True:
            curr = self.get_current_value()
            if curr is None: break

            # 判断是否到达目标（允许 0.05 的极小浮点误差）
            if abs(curr - target_db) < 0.05:
                print(f"✅ 测试完成：已到达目标值 {curr} dB")
                break

            # 确定方向与预期步进
            direction = "up" if curr < target_db else "down"
            expected_step = 0.1

            # 计算理论预期值
            theory_val = round(curr + expected_step if direction == "up" else curr - expected_step, 1)

            # 执行点击
            (plus_btn if direction == "up" else minus_btn).click()
            time.sleep(0.2)  # 等待页面数据刷新

            # 读取实际结果
            new_val = self.get_current_value()
            actual_step = round(abs(new_val - curr), 1)

            # 状态判定：正常步进 0.1 OR 到达边界时步进为 0
            is_at_boundary = (curr <= -15.0 and direction == "down") or (curr >= 15.0 and direction == "up")

            if is_at_boundary:
                if actual_step == 0:
                    print(
                        f"[✅ PASS] 边界校验 | 目标: {target_db} | 预期值: {curr} (边界) | 实际值: {new_val} | 步进: 0 (符合预期)")
                    break
                else:
                    print(
                        f"[❌ FAIL] 边界越界 | 目标: {target_db} | 预期值: {curr} | 实际值: {new_val} | 步进: {actual_step}")
                    break
            else:
                if actual_step == expected_step:
                    print(
                        f"[✅ PASS] 步进正常 | 目标: {target_db} | 预期值: {theory_val} | 实际值: {new_val} | 步进: {actual_step}")
                else:
                    print(
                        f"[❌ FAIL] 步进异常 | 目标: {target_db} | 预期值: {theory_val} | 实际值: {new_val} | 步进: {actual_step}")
                    break


# ==================== 运行示例 ====================
if __name__ == "__main__":
    # 初始化浏览器
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        # 进入页面
        driver.get("http://192.168.66.123/#/Input/Input1")  # 请替换为实际地址
        time.sleep(2)

        tester = GainTester(driver)

        # 场景 1：从当前值上调到 1.5 dB
        tester.run_test(1.5)

        # 场景 2：下调至最小值边界并压测（-15.0 dB）
        # 如果设置目标为 -15.1，脚本会自动识别并测试到达 -15.0 后继续下调的情况
        tester.run_test(-15.1)

        # 场景 3：从最小值回调
        tester.run_test(-14.8)

    finally:
        input("\n测试演示结束，按回车键关闭浏览器...")
        driver.quit()