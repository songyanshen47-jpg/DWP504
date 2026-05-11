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

# 初始进入 Output1 页面
BASE_URL = "http://192.168.66.123/#/Output/Output1"
wait = WebDriverWait(driver, 10)
driver.get(BASE_URL)
time.sleep(5)


# ==================== 核心函数 ====================

def get_current_output_channel():
    """
    【终极方案】通过 URL 路径判断当前处于哪个 Output 通道
    例如：
      http://192.168.66.123/#/Output/Output1  → "Output 1"
      http://192.168.66.123/#/Output/Output2  → "Output 2"
    """
    url = driver.current_url.lower()

    if "/output1" in url:
        return "Output 1"
    elif "/output2" in url:
        return "Output 2"
    elif "/output3" in url:
        return "Output 3"
    elif "/output4" in url:
        return "Output 4"
    else:
        # 兜底：尝试从 DOM 中读取激活的顶级菜单项
        try:
            # 查找所有带 active 类的 MenuItem 中的 span，但排除子菜单项（如 Routing, Preset 等）
            active_items = driver.find_elements(By.CSS_SELECTOR, "div[class*='Submenu-module_active__'] span")
            for item in active_items:
                text = item.text.strip()
                if text.startswith("Output ") and len(text) <= 10:  # 如 "Output 1"
                    return text
        except:
            pass
        return None


def click_menu_item(target_name):
    """
    通用点击函数：点击任意可见的菜单项（包括 Output 1~4）
    """
    try:
        locator = (By.XPATH, f"//span[normalize-space()='{target_name}']")
        btn = wait.until(EC.element_to_be_clickable(locator))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", btn)
        return True
    except Exception as e:
        print(f"   ❌ 点击 '{target_name}' 失败: {str(e)[:80]}")
        return False


def verify_switch(expected_name, max_retries=3):
    """
    验证是否成功切换到指定 Output 通道
    """
    for i in range(max_retries):
        time.sleep(0.5)
        current = get_current_output_channel()
        if current == expected_name:
            return True, current
    return False, get_current_output_channel()


# ==================== 主流程 ====================

if __name__ == "__main__":
    print("=" * 70)
    print("PROEL 自动化测试：切换 Output 通道 (Output 1 ~ Output 4)")
    print("=" * 70)

    all_passed = True

    # 定义要切换的输出通道序列
    output_channels = ["Output 1", "Output 2", "Output 3", "Output 4"]

    for target_channel in output_channels:
        print(f"\n>>> 【步骤】切换到: '{target_channel}'")

        # 执行点击
        if not click_menu_item(target_channel):
            print(f"   ⚠️ 点击失败，跳过验证")
            all_passed = False
            continue

        # 等待并验证
        success, actual = verify_switch(target_channel)

        if success:
            print(f"   ✅ 验证通过：当前激活 '{actual}'")
        else:
            print(f"    验证失败：预期 '{target_channel}'，实际 '{actual}'")
            all_passed = False

    # 总结
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 所有 Output 通道切换测试通过！")
    else:
        print("💥 部分测试失败，请检查上方日志")
    print("=" * 70)

    input("\n按回车退出...")
    driver.quit()
