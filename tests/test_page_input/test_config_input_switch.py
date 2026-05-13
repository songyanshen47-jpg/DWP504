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
BASE_URL = "http://192.168.66.123/#/Input"  # 替换为你实际页面地址
wait = WebDriverWait(driver, 10)
driver.get(BASE_URL)
time.sleep(8)  # 初始加载等待


# ==================== 核心函数 ====================

def get_active_submenu_item():
    """
    读取当前激活的子菜单项名称（如 "Input 1"）
    """
    try:
        active_item = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div[class*='Submenu-module_active__']")
        ))
        item_text = active_item.text.strip()
        return item_text
    except Exception as e:
        print(f"    无法获取激活导航项: {e}")
        return None


def click_submenu_item(target_name):
    """
    点击指定名称的导航项
    """
    try:
        locator = (By.XPATH,
                   f"//div[contains(@class, 'Submenu-module_MenuItem__') and normalize-space()='{target_name}']")
        btn = wait.until(EC.element_to_be_clickable(locator))

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(0.3)  # 滚动后小停顿

        driver.execute_script("arguments[0].click();", btn)
        return True
    except Exception as e:
        print(f"   ❌ 点击 '{target_name}' 失败: {str(e)[:80]}")
        return False


# ==================== 主流程 ====================

if __name__ == "__main__":
    print("=" * 70)
    print("PROEL 子菜单导航自动化测试：带延迟与实时验证")
    print("=" * 70)

    # 1. 读取初始状态
    initial_item = get_active_submenu_item()
    if not initial_item:
        print("❌ 初始状态读取失败，退出")
        driver.quit()
        exit(1)

    print(f"\n📌 初始激活导航项: '{initial_item}'")

    # 2. 定义切换序列
    test_sequence = ["Input 2", "Input 3", "Input 4", "Generator"]

    all_passed = True

    for target_item in test_sequence:
        print(f"\n>>> 【步骤】切换到: '{target_item}'")

        # 执行点击
        if not click_submenu_item(target_item):
            print(f"   ⚠️ 点击失败，跳过验证")
            all_passed = False
            continue

        # ✅ 关键：添加延迟，让 UI 完全更新
        print("   ⏳ 等待 UI 更新...")
        time.sleep(1.5)  # 增加至 1.5 秒，确保 React 渲染完成

        # ✅ 关键：立即读取并打印当前激活状态
        current_active = get_active_submenu_item()
        print(f"   📊 当前激活项: '{current_active}'")

        # 验证是否匹配
        if current_active == target_item:
            print(f"   ✅ 验证通过：成功切换到 '{target_item}'")
        else:
            print(f"   ❌ 验证失败：预期 '{target_item}'，实际 '{current_active}'")
            all_passed = False

    # 3. 总结
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 所有导航切换测试通过！")
    else:
        print("💥 部分测试失败，请检查日志")
    print("=" * 70)

    input("\n按回车退出...")
    driver.quit()