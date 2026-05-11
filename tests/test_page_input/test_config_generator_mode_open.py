from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

# ==================== 浏览器配置 ====================
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()
BASE_URL = "http://192.168.66.123/#/Input/Generator"  # 替换为你实际页面地址
wait = WebDriverWait(driver, 10)
driver.get(BASE_URL)
time.sleep(8)  # 等待页面加载完成


# ==================== 核心函数 ====================

def get_switch_state():
    """
    读取当前开关状态
    返回: "on" 如果包含 'Switch-module_open__' 类名，否则 "off"
    """
    try:
        # 定位开关元素
        switch_el = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div[class*='Switch-module_Switch__']")
        ))

        classes = switch_el.get_attribute("class")
        if "Switch-module_open__" in classes:
            return "on"
        else:
            return "off"
    except Exception as e:
        print(f"   ❌ 获取开关状态失败: {e}")
        return None


def toggle_switch():
    """
    点击开关按钮，并验证状态翻转
    """
    try:
        # 记录初始状态
        initial_state = get_switch_state()
        if initial_state is None:
            print("   ⚠️ 无法获取初始状态，跳过")
            return False

        print(f"   📊 初始状态: '{initial_state}'")

        # 定位并点击开关
        switch_el = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "div[class*='Switch-module_Switch__']")
        ))

        # 滚动到视图中心
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", switch_el)
        time.sleep(0.3)

        # 使用 JS 点击（更可靠）
        driver.execute_script("arguments[0].click();", switch_el)
        print("   ✅ 已点击开关")

        # 等待 UI 更新
        time.sleep(1.5)

        # 读取新状态
        new_state = get_switch_state()
        print(f"   📊 新状态: '{new_state}'")

        # 验证状态是否翻转
        if new_state == initial_state:
            print(f"   ❌ 状态未改变！仍为 '{new_state}'")
            return False
        elif (initial_state == "off" and new_state == "on") or \
                (initial_state == "on" and new_state == "off"):
            print(f"   ✅ 状态成功翻转: '{initial_state}' → '{new_state}'")
            return True
        else:
            print(f"   ⚠️ 未知状态组合: '{initial_state}' → '{new_state}'")
            return False

    except Exception as e:
        print(f"   ❌ 切换开关失败: {str(e)[:80]}")
        return False


# ==================== 主流程 ====================

if __name__ == "__main__":
    print("=" * 70)
    print("Generator 开关自动化测试：开 ↔ 关 状态切换验证")
    print("=" * 70)

    # 执行多次切换测试（例如 3 次循环）
    for i in range(1, 4):
        print(f"\n>>> 【第 {i} 轮】开关切换测试")
        success = toggle_switch()
        if not success:
            print(f"   ⚠️ 第 {i} 轮失败")
        time.sleep(1.0)  # 每轮之间稍作停顿

    print("\n" + "=" * 70)
    print("✅ 开关切换测试完成")
    print("=" * 70)

    input("\n按回车退出...")
    driver.quit()
