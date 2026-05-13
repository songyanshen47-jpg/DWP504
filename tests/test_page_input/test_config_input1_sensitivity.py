from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ==================== 配置 ====================
BASE_URL = "http://192.168.66.123/#/Input"

# ==================== 通用工具函数 ====================
def get_selected_analog_channel(driver):
    """读取当前选中的 Analog 通道"""
    try:
        elem = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div[class*='RadiosBlock-module_selected']")
            )
        )
        return elem.text.strip()
    except:
        return None

def get_selected_sensitivity(driver):
    """读取当前选中的 Sensitivity 值"""
    try:
        # 按截图的结构，直接找带 selected class 的按钮
        elem = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[contains(@class, 'RadiosBlock-module_selected') and (text()='MIC' or text()='-10dBV' or text()='+4dBu' or text()='+14dBu')]")
            )
        )
        return elem.text.strip()
    except:
        return None

def click_analog_channel(driver, target_channel):
    """点击 Analog 通道按钮"""
    try:
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//div[contains(@class, 'RadiosBlock-module_col') and text()='{target_channel}']")
            )
        )
        btn.click()
        time.sleep(1.5)  # 等待状态切换
    except Exception as e:
        print(f"点击 Analog 通道 {target_channel} 失败: {e}")

def click_sensitivity(driver, target_value):
    """点击 Sensitivity 按钮"""
    try:
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//div[contains(@class, 'RadiosBlock-module_col') and text()='{target_value}']")
            )
        )
        btn.click()
        time.sleep(1.5)  # 等待状态切换
    except Exception as e:
        print(f"点击 Sensitivity {target_value} 失败: {e}")

# ==================== 主测试流程 ====================
def test_channel_sensitivity_binding():
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        driver.get(BASE_URL)
        time.sleep(6)

        print("=" * 65)
        print("🎯 Analog 通道与 Sensitivity 绑定关系测试")
        print("=" * 65)

        # 1. 记录初始状态
        print("\n【步骤1】记录初始状态")
        initial_channel = get_selected_analog_channel(driver)
        initial_sensitivity = get_selected_sensitivity(driver)
        print(f"初始通道: {initial_channel}, 初始灵敏度: {initial_sensitivity}")

        # 2. 为每个通道设置不同的灵敏度值
        print("\n【步骤2】为每个通道设置独立的灵敏度值")
        channel_sensitivity_map = {
            "CH1": "+14dBu",
            "CH2": "-10dBV",
            "CH3": "MIC",
            "CH4": "+4dBu"
        }

        for channel, sensitivity in channel_sensitivity_map.items():
            print(f"设置 {channel} 的灵敏度为 {sensitivity}")
            click_analog_channel(driver, channel)
            click_sensitivity(driver, sensitivity)

            # 验证设置成功
            actual = get_selected_sensitivity(driver)
            if actual == sensitivity:
                print(f"✅ {channel} 设置成功: {actual}")
            else:
                print(f"❌ {channel} 设置失败: 预期 {sensitivity}, 实际 {actual}")

        # 3. 验证通道切换时，灵敏度会自动切换
        print("\n【步骤3】验证通道切换时灵敏度的绑定关系")
        all_pass = True
        for channel, expected_sensitivity in channel_sensitivity_map.items():
            print(f"切换到 {channel}, 预期灵敏度: {expected_sensitivity}")
            click_analog_channel(driver, channel)
            actual_sensitivity = get_selected_sensitivity(driver)
            print(f"实际灵敏度: {actual_sensitivity}")

            if actual_sensitivity == expected_sensitivity:
                print(f"✅ 绑定关系正常")
            else:
                print(f"❌ 绑定关系异常: 预期 {expected_sensitivity}, 实际 {actual_sensitivity}")
                all_pass = False

        # 4. 最终结论
        print("\n" + "=" * 65)
        if all_pass:
            print("✅ 所有通道与灵敏度的绑定关系测试通过！")
        else:
            print("❌ 部分通道绑定关系异常，请检查")
        print("=" * 65)

    except Exception as e:
        print(f"程序异常: {str(e)}")

    finally:
        input("\n按回车关闭浏览器...")
        driver.quit()

if __name__ == "__main__":
    test_channel_sensitivity_binding()