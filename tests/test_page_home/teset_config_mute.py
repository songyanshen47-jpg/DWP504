from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL = "http://192.168.66.123/#/Home"

# =============================================================================
# ✅ 【最简、最稳】获取静音状态
# 直接找你截图里的真实 class：DbSelector-module_sound-icon
# =============================================================================
def get_mute_status(driver):
    try:
        # 等待图标出现
        icon = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "img[class*='DbSelector-module_sound-icon']"))
        )
        src = icon.get_attribute("src")

        # 你真实静音的 src 包含这段
        if "f6XkHZ62HzDG" in src:
            return True   # 静音
        else:
            return False  # 非静音
    except:
        print("❌ 找不到静音按钮！")
        return None

# =============================================================================
# ✅ 点击静音按钮（最稳）
# =============================================================================
def click_mute(driver):
    try:
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "img[class*='DbSelector-module_sound-icon']"))
        )
        driver.execute_script("arguments[0].click();", btn)
    except:
        print("❌ 点击失败！")

# =============================================================================
# 测试用例
# =============================================================================
def test_output1_mute():
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        print("▶ 打开首页...")
        driver.get(BASE_URL)

        # --------------------------
        # 必须等页面完全渲染完
        # --------------------------
        print("▶ 等待页面加载 3 秒...")
        time.sleep(3)

        # --------------------------
        # 读初始状态
        # --------------------------
        print("\n▶ 读取当前状态...")
        before = get_mute_status(driver)
        if before is True:
            print("✅ 当前状态：静音")
        else:
            print("✅ 当前状态：非静音")

        # --------------------------
        # 点击切换
        # --------------------------
        print("\n▶ 等待 3 秒后点击...")
        time.sleep(3)
        click_mute(driver)

        # --------------------------
        # 等界面变化
        # --------------------------
        print("▶ 等待 1 秒界面响应...")
        time.sleep(1)

        # --------------------------
        # 读新状态
        # --------------------------
        print("\n▶ 读取新状态...")
        after = get_mute_status(driver)
        if after is True:
            print("✅ 新状态：静音")
        else:
            print("✅ 新状态：非静音")

        # --------------------------
        # 结果
        # --------------------------
        print("\n" + "="*55)
        if before != after:
            print("✅ 测试成功：状态已切换！")
        else:
            print("❌ 测试失败：状态未切换！")
        print("="*55)

    finally:
        input("\n按回车关闭 → ")
        driver.quit()

if __name__ == "__main__":
    test_output1_mute()