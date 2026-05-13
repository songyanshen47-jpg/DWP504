from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ==================== 配置 ====================
BASE_URL = "http://192.168.66.123/#/Input"

# ==================== 通用工具函数 ====================
def get_current_mode(driver):
    """读取当前模式：MONO / STEREO"""
    try:
        wait = WebDriverWait(driver, 10)
        elem = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//span[text()='MONO' or text()='STEREO']")
            )
        )
        return elem.text.strip()
    except:
        return "UNKNOWN"

def get_selected_channel(driver):
    """读取当前选中的通道"""
    try:
        wait = WebDriverWait(driver, 10)
        # 找带 selected class 的通道按钮
        elem = wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div[class*='RadiosBlock-module_selected']")
            )
        )
        return elem.text.strip()
    except:
        return "UNKNOWN"

def click_channel_button(driver, target_text):
    """点击指定通道按钮（按文本定位）"""
    try:
        wait = WebDriverWait(driver, 10)
        btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//div[contains(@class, 'RadiosBlock-module_col') and text()='{target_text}']")
            )
        )
        btn.click()
        time.sleep(1.5)
    except Exception as e:
        print(f"点击通道 {target_text} 失败: {e}")

# ==================== 测试主逻辑 ====================
def test_analog_channel_switch():
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        driver.get(BASE_URL)
        time.sleep(6)

        print("=" * 65)
        print("🎯 Analog 通道切换测试（按模式区分逻辑）")
        print("=" * 65)

        # 1. 读取当前模式
        print("\n【步骤1】读取当前模式")
        mode = get_current_mode(driver)
        print(f"当前模式: {mode}")

        # 2. 读取初始通道状态
        print("\n【步骤2】读取初始选中通道")
        initial_channel = get_selected_channel(driver)
        print(f"初始通道: {initial_channel}")

        # 3. 根据模式执行不同的测试逻辑
        print("\n【步骤3】执行切换测试")
        if mode == "STEREO":
            print("当前为 STEREO 模式，验证通道锁定行为")
            test_channels = ["CH1&CH2", "CH3", "CH4"]
            locked_channel = "CH1&CH2"

            for ch in test_channels:
                print(f"尝试切换到: {ch}")
                click_channel_button(driver, ch)
                current = get_selected_channel(driver)
                print(f"切换后实际选中: {current}")

                if current != locked_channel:
                    print(f"❌ 测试失败: STEREO 模式下选中状态发生变化")
                    break
            else:
                print(f"✅ 测试成功: STEREO 模式下通道始终锁定为 {locked_channel}")

        elif mode == "MONO":
            print("当前为 MONO 模式，验证通道可正常切换")
            test_channels = ["CH1", "CH2", "CH3", "CH4"]
            success = True

            for ch in test_channels:
                print(f"尝试切换到: {ch}")
                click_channel_button(driver, ch)
                current = get_selected_channel(driver)
                print(f"切换后实际选中: {current}")

                if current != ch:
                    print(f"❌ 测试失败: 未成功切换到 {ch}")
                    success = False
                    break

            if success:
                print("✅ 测试成功: MONO 模式下所有通道均可正常切换")

        else:
            print("❌ 模式识别失败，无法执行测试")

    except Exception as e:
        print(f"程序异常: {str(e)}")

    finally:
        input("\n按回车关闭浏览器...")
        driver.quit()

if __name__ == "__main__":
    test_analog_channel_switch()