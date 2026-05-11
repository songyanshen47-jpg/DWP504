import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class FrequencyTester:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.errors = []

    def get_value(self):
        try:
            xpath = "//div[contains(@class, 'Sliders-module_Selector-box')][descendant::span[contains(text(), 'Frequency')]]"
            section = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            display_text = section.find_element(By.CSS_SELECTOR, "div[class*='display-message']").text.strip().lower()
            match = re.search(r"(\d+\.?\d*)", display_text)
            if not match: return None
            val = float(match.group(1))
            return int(val * 1000) if 'k' in display_text else int(val)
        except:
            return None

    def get_logical_step(self, curr, direction):
        if direction == "up":
            if curr >= 2000: return 100
            if curr >= 200: return 10
            return 1
        else:
            if curr > 2000: return 100
            if curr == 2000: return 100
            if curr > 200: return 10
            if curr == 200: return 10
            return 1

    def run_test(self, user_target):
        xpath = "//div[contains(@class, 'Sliders-module_Selector-box')][descendant::span[contains(text(), 'Frequency')]]"
        section = self.driver.find_element(By.XPATH, xpath)
        plus_btn = section.find_element(By.CSS_SELECTOR, "div[class*='plus']")
        minus_btn = section.find_element(By.CSS_SELECTOR, "div[class*='pre']")

        print(f"\n▶️ 正在测试目标频率: {user_target}Hz")

        while True:
            curr = self.get_value()
            if curr is None: break

            # 如果已经刚好在目标点，直接结束
            if curr == user_target:
                print(f"✅ 已精确到达目标: {curr}Hz")
                break

            direction = "up" if curr < user_target else "down"
            step = self.get_logical_step(curr, direction)
            expected_val = curr + step if direction == "up" else curr - step

            # 判断这一步点击是否会跳过或刚好到达目标
            # 例如：200 -> 210 (目标205)，这一步执行完就该结束
            will_reach_or_pass = False
            if direction == "up" and expected_val >= user_target:
                will_reach_or_pass = True
            elif direction == "down" and expected_val <= user_target:
                will_reach_or_pass = True

            # 执行操作
            (plus_btn if direction == "up" else minus_btn).click()
            time.sleep(0.4)  # 稍微增加一点等待，确保 UI 刷新后再读取

            actual_val = self.get_value()

            # 判定：只要 实际 == 预期，就是 PASS
            if actual_val == expected_val:
                status = "✅ PASS"
            elif actual_val == curr:  # 边界
                status = "✅ PASS (LIMIT)"
            else:
                status = "❌ FAIL"
                self.errors.append(f"目标:{user_target} | 预期:{expected_val} | 实际:{actual_val}")

            # 打印当前这一步的结果（现在 210 那一行会正常打印了）
            print(f"[{status}] 设定目标: {user_target:5} | 预期有效值: {expected_val:5} | 实际值: {actual_val:5}")

            # 结束当前数值测试的逻辑：
            # 1. 刚才那一步已经跳过或到达了目标
            # 2. 或者数值不再变化（到头了）
            if will_reach_or_pass or actual_val == curr:
                print(f"🏁 目标 {user_target}Hz 测试结束。")
                break


# ==================== 执行流程 ====================
if __name__ == "__main__":
    driver = webdriver.Chrome()
    tester = FrequencyTester(driver)
    try:
        driver.get("http://192.168.66.123/#/Input/Input1")
        time.sleep(2)

        # 测试数据
        test_points = [205, 500, 505,20,0]

        for pt in test_points:
            tester.run_test(pt)

        if tester.errors:
            print(f"\n⚠️ 汇总：发现 {len(tester.errors)} 处步进错误。")
        else:
            print("\n🎉 汇总：全部测试通过。")

    finally:
        driver.quit()