from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ==================== 配置 ====================
URL = "http://192.168.66.123/#/Input"

# ==================== 工具函数：每次都用文本定位，永不失效 ====================
def get_current_mode(driver):
    """通过文本内容定位，读取 MONO / STEREO"""
    try:
        wait = WebDriverWait(driver, 10)
        # 直接找包含 MONO 或 STEREO 的 span
        elem = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//span[text()='MONO' or text()='STEREO']")
            )
        )
        return elem.text.strip()
    except:
        return "READ_FAILED"

def click_mode_button(driver):
    """每次都用文本定位按钮，绝不缓存"""
    try:
        wait = WebDriverWait(driver, 10)
        # 找到包含 MONO/STEREO 的 span 的父 div（就是按钮）
        btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[text()='MONO' or text()='STEREO']/parent::div")
            )
        )
        btn.click()
        # 点击后强制等待 DOM 重建
        time.sleep(3)
    except:
        pass

# ==================== 主测试流程：严格按顺序执行 ====================
def test_input_mode():
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        driver.get(URL)
        time.sleep(6)
        print("=" * 65)
        print("🎯 Input 页面模式按钮测试（纯DOM文本定位版）")
        print("=" * 65)

        # 1. 读取初始状态
        print("\n【步骤1】读取初始状态")
        initial_state = get_current_mode(driver)
        print(f"初始状态：{initial_state}")
        time.sleep(2)
        # 2. 点击按钮
        print("\n【步骤2】点击模式按钮")
        click_mode_button(driver)
        print("点击完成，等待DOM重建...")
        time.sleep(2)
        # 3. 点击后读取状态
        print("\n【步骤3】读取点击后的状态")
        new_state = get_current_mode(driver)
        print(f"点击后状态：{new_state}")
        time.sleep(2)
        # 4. 验证结果
        print("\n" + "=" * 65)
        if new_state != initial_state and new_state in ["MONO", "STEREO"]:
            print(f"✅ 测试成功！状态已切换：{initial_state} → {new_state}")
        else:
            print(f"❌ 测试失败：状态未切换或读取失败")
        print("=" * 65)

    except Exception as e:
        print(f"错误：{str(e)}")

    finally:
        input("\n按回车关闭 → ")
        driver.quit()

if __name__ == "__main__":
    test_input_mode()