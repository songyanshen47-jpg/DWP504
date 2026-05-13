import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class QTester:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.label = "Q"

    def _get_section(self):
        """精准定位 Q值 控制区域容器"""
        xpath = f"//div[contains(@class, 'Sliders-module_Selector-box')][descendant::span[contains(text(), '{self.label}')]]"
        return self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

    def get_current_value(self):
        """读取并解析当前 Q 值"""
        try:
            section = self._get_section()
            display_el = section.find_element(By.CSS_SELECTOR, "div[class*='display-message']")
            text = display_el.text.strip()
            match = re.search(r"(\d+\.?\d*)", text)
            if not match: return None
            return round(float(match.group(1)), 1)
        except Exception as e:
            print(f"❌ 读取 Q 值失败: {e}")
            return None

    def calculate_expected_step(self, curr, direction):
        """核心业务逻辑：计算 Q 值的动态步进"""
        if direction == "up":
            if curr >= 10.0: return 0.5
            if curr >= 3.0: return 0.2
            return 0.1
        else:  # direction == "down"
            # 临界点首跳逻辑：10.0下调首跳是0.5，3.0下调首跳是0.2
            if curr > 10.0: return 0.5
            if curr == 10.0: return 0.5
            if curr > 3.0: return 0.2
            if curr == 3.0: return 0.2
            return 0.1

    def run_test(self, target_q):
        """执行 Q 值测试流程"""
        # 物理范围限制
        target_q = max(0.4, min(30.0, target_q))

        print(f"\n🎡 开始 Q值 测试 | 目标值: {target_q}")
        print("-" * 65)

        section = self._get_section()
        plus_btn = section.find_element(By.CSS_SELECTOR, "div[class*='plus']")
        minus_btn = section.find_element(By.CSS_SELECTOR, "div[class*='pre']")

        while True:
            curr = self.get_current_value()
            if curr is None: break

            # 到达目标判定
            if abs(curr - target_q) < 0.01:
                print(f"✅ 测试完成：已精确到达目标值 {curr}")
                break

            direction = "up" if curr < target_q else "down"
            expected_step = self.calculate_expected_step(curr, direction)

            # 计算理论上的下一步数值
            theory_val = round(curr + expected_step if direction == "up" else curr - expected_step, 1)

            # 点击
            (plus_btn if direction == "up" else minus_btn).click()
            time.sleep(0.2)

            # 获取实际结果
            new_val = self.get_current_value()
            actual_step = round(abs(new_val - curr), 1)

            # 边界判定逻辑
            is_at_limit = (curr <= 0.4 and direction == "down") or (curr >= 30.0 and direction == "up")

            if is_at_limit:
                if actual_step == 0:
                    print(f"[✅ PASS] 极限校验 | 目标: {target_q} | 预期值: {curr} (极限) | 实际值: {new_val} | 步进: 0")
                    break
                else:
                    print(
                        f"[❌ FAIL] 极限越界 | 目标: {target_q} | 预期值: {curr} | 实际值: {new_val} | 步进: {actual_step}")
                    break
            else:
                if actual_step == expected_step:
                    print(
                        f"[✅ PASS] 步进正常 | 目标: {target_q} | 预期值: {theory_val} | 实际值: {new_val} | 步进: {actual_step}")
                else:
                    print(
                        f"[❌ FAIL] 步进异常 | 目标: {target_q} | 预期值: {theory_val} | 实际值: {new_val} | 步进: {actual_step}")
                    break


# ==================== 测试用例运行 ====================
if __name__ == "__main__":
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        driver.get("http://192.168.66.123/#/Input/Input1")  # 替换为实际地址
        time.sleep(2)

        tester = QTester(driver)

        # 1. 测试跨越 3.0 的步进切换 (0.1 -> 0.2)
        tester.run_test(3.4)

        # 2. 测试跨越 10.0 的步进切换 (0.2 -> 0.5)
        tester.run_test(11.0)

        # 3. 测试 10.0 下调的首跳逻辑 (应跳 0.5 到 9.5)
        tester.run_test(9.5)

        # 4. 测试最低边界 0.4 的压测
        tester.run_test(0.3)

        # 5. 测试最高边界 30.0 的压测
        tester.run_test(30.1)

    finally:
        input("\n测试演示结束，按回车键关闭...")
        driver.quit()