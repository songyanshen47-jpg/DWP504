from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time

# ==================== 浏览器配置 ====================
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()

BASE_URL = "http://192.168.66.123/#/Output/Output1"
wait = WebDriverWait(driver, 10)
driver.get(BASE_URL)
time.sleep(5)


# ==================== 导航函数 ====================

def click_menu_item(target_name):
    try:
        locator = (By.XPATH, f"//span[normalize-space()='{target_name}']")
        btn = wait.until(EC.element_to_be_clickable(locator))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", btn)
        print(f"  ✅ 点击 '{target_name}' 成功")
        return True
    except Exception as e:
        print(f"  ❌ 点击 '{target_name}' 失败: {str(e)[:80]}")
        return False


# ==================== Crossover 核心函数 ====================

def select_high_pass_mode(mode_id, mode_name):
    """选择 HIGH PASS 模式"""
    try:
        selector_xpath = "//span[contains(@class, 'Crossover-module_title__') and text()='HIGH PASS']/following-sibling::div[contains(@class, 'Crossover-module_wave-type__')]"
        selector = driver.find_element(By.XPATH, selector_xpath)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selector)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", selector)
        print(f"    ✅ 打开 HIGH PASS 下拉菜单")
        time.sleep(0.5)

        option_xpath = f"//li[@data-menu-id='{mode_id}']"
        option = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, option_xpath))
        )
        driver.execute_script("arguments[0].click();", option)
        print(f"    ✅ HIGH PASS -> {mode_name} 成功")
        return True
    except Exception as e:
        print(f"    ❌ HIGH PASS -> {mode_name} 失败: {e}")
        return False


def select_low_pass_mode(mode_id, mode_name):
    """选择 LOW PASS 模式"""
    try:
        selector_xpath = "//span[contains(@class, 'Crossover-module_title__') and text()='LOW PASS']/following-sibling::div[contains(@class, 'Crossover-module_wave-type__')]"
        selector = driver.find_element(By.XPATH, selector_xpath)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selector)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", selector)
        print(f"    ✅ 打开 LOW PASS 下拉菜单")
        time.sleep(0.5)

        options = driver.find_elements(By.XPATH, f"//li[@data-menu-id='{mode_id}']")
        for option in options:
            try:
                text_span = option.find_element(By.XPATH, ".//span[@class='ant-dropdown-menu-title-content']")
                if text_span.text and len(text_span.text) > 0:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option)
                    time.sleep(0.2)
                    driver.execute_script("arguments[0].click();", option)
                    print(f"    ✅ LOW PASS -> {mode_name} 成功")
                    return True
            except:
                continue

        print(f"    ❌ LOW PASS -> {mode_name} 失败")
        return False
    except Exception as e:
        print(f"    ❌ LOW PASS -> {mode_name} 异常: {e}")
        return False


def get_high_pass_current():
    try:
        selector_xpath = "//span[contains(@class, 'Crossover-module_title__') and text()='HIGH PASS']/following-sibling::div[contains(@class, 'Crossover-module_wave-type__')]//div[contains(@class, 'Crossover-module_name__')]"
        element = driver.find_element(By.XPATH, selector_xpath)
        return element.text.strip()
    except:
        return None


def get_low_pass_current():
    try:
        selector_xpath = "//span[contains(@class, 'Crossover-module_title__') and text()='LOW PASS']/following-sibling::div[contains(@class, 'Crossover-module_wave-type__')]//div[contains(@class, 'Crossover-module_name__')]"
        element = driver.find_element(By.XPATH, selector_xpath)
        return element.text.strip()
    except:
        return None










# ==================== 主流程 ====================

if __name__ == "__main__":
    print("=" * 70)
    print("PROEL 自动化测试：导航到 Crossover 并进行分频器测试")
    print("=" * 70)

    # 1. 导航到 Crossover
    print("\n>>> 导航到 Crossover...")

    click_menu_item("Routing")
    time.sleep(0.5)
    click_menu_item("Delay")
    time.sleep(0.5)
    click_menu_item("Equalizer")
    time.sleep(0.5)

    click_menu_item("Speaker Preset")
    time.sleep(1)
    click_menu_item("Crossover")
    time.sleep(2)

    # 2. 测试模式列表
    test_modes = [
        ("OFF", "OFF"),
        ("BUT12", "Butterworth 12dB"),
        ("BUT24", "Butterworth 24dB"),
        ("BUT48", "Butterworth 48dB"),
        ("BES12", "Bessel 12dB"),
        ("BES24", "Bessel 24dB"),
        ("BES48", "Bessel 48dB"),
        ("LR12", "Linkwitz-Riley 12dB"),
        ("LR24", "Linkwitz-Riley 24dB"),
        ("LR48", "Linkwitz-Riley 48dB"),
    ]

    # 3. 测试 HIGH PASS
    print("\n" + "=" * 60)
    print("测试 HIGH PASS 模式切换")
    print("=" * 60)

    for mode_id, mode_name in test_modes:
        print(f"\n  切换 HIGH PASS: {mode_name}")
        if select_high_pass_mode(mode_id, mode_name):
            time.sleep(0.8)
            current = get_high_pass_current()
            print(f"    📍 当前: {current}")
        time.sleep(0.5)

    # 4. 测试 LOW PASS
    print("\n" + "=" * 60)
    print("测试 LOW PASS 模式切换")
    print("=" * 60)

    for mode_id, mode_name in test_modes:
        print(f"\n  切换 LOW PASS: {mode_name}")
        if select_low_pass_mode(mode_id, mode_name):
            time.sleep(0.8)
            current = get_low_pass_current()
            print(f"    📍 当前: {current}")
        time.sleep(0.5)

    # 5. 调节参数
    print("\n" + "=" * 60)
    print("调节参数测试")
    print("=" * 60)

    select_high_pass_mode("BUT12", "Butterworth 12dB")
    time.sleep(1)




    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)

    input("\n按回车退出...")
    driver.quit()