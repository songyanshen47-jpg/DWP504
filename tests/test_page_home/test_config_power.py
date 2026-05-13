from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL = "http://192.168.66.123/#/Home"

# =============================================================================
# 1. 定位方式：完全按你截图的真实结构
# =============================================================================
def get_power_status(driver):
    try:
        # 1. 定位 Power 开关图片
        icon = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[contains(@class, 'Home-module_header-part')]/img")
            )
        )
        # 2. 定位状态文字（On/Off）
        status_elem = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[contains(@class, 'Home-module_part-content')]/span[2]")
            )
        )

        # 滚动到元素
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", icon)
        time.sleep(0.5)

        return status_elem.text.strip()
    except Exception as e:
        print(f"❌ 读取状态失败: {str(e)}")
        return None

def click_power(driver):
    try:
        # 点击开关图片（可点击区域）
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(@class, 'Home-module_header-part')]/img")
            )
        )
        driver.execute_script("arguments[0].click();", btn)
        print("✅ 已点击 Power 开关")
    except Exception as e:
        print(f"❌ 点击失败: {str(e)}")

# =============================================================================
# 2. 主流程：和静音开关完全一样
# =============================================================================
def test_power_switch():
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        print("=" * 60)
        print("🎯 测试 Power 电源开关")
        print("=" * 60)

        # 打开页面
        driver.get(BASE_URL)
        print("⏳ 页面加载中...")
        time.sleep(5)

        # 1. 读状态
        print("\n1️⃣ 读取点击前状态")
        before = get_power_status(driver)
        print(f"✅ 当前状态：{before}")

        # 2. 点击
        time.sleep(2)
        click_power(driver)
        time.sleep(3)

        # 3. 再读状态
        print("\n3️⃣ 读取点击后状态")
        after = get_power_status(driver)
        print(f"✅ 当前状态：{after}")

        # 4. 结果
        print("\n📊 测试结果")
        if before != after:
            print("🎉 测试成功：状态已切换！")
        else:
            print("❌ 测试失败：状态未变化！")

    except:
        pass

    finally:
        input("\n按回车关闭 → ")
        driver.quit()


if __name__ == "__main__":
    test_power_switch()