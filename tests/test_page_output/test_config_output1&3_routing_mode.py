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
chrome_options.add_argument('--disable-gpu')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()
BASE_URL = "http://192.168.66.123/#/Output/Output1/Routing"
wait = WebDriverWait(driver, 10)
driver.get(BASE_URL)
time.sleep(6)

# ==================== 信号源配置 ====================
SOURCE_LIST = ["Input 1", "Input 2", "Input 3", "Input 4", "Generator"]
SELECTED_CLASS = "Routing-module_selected__XC8umqQC8YGk5274xpN3"

# ==================== 工具函数 ====================
def get_current_source():
    """读取当前选中的信号源"""
    try:
        # 找到带selected类的选项
        selected_loc = (By.XPATH, "//div[contains(@class,'Routing-module_selected')]")
        selected_ele = wait.until(EC.presence_of_element_located(selected_loc))
        source_name = selected_ele.text.strip()
        print(f"当前信号源：{source_name}")
        return source_name
    except Exception as e:
        print(f"❌ 读取信号源失败：{str(e)[:40]}")
        return None

def set_source_by_class(target_source):
    """
    纯JS修改class切换信号源：给目标选项加selected，其他选项移除
    完全按你之前改EQ波形的思路，不模拟点击
    """
    if target_source not in SOURCE_LIST:
        print(f"⚠️ 信号源名称错误，可选：{SOURCE_LIST}")
        return False

    try:
        # 1. 找到所有信号源选项
        options_loc = (By.XPATH, "//div[starts-with(@class,'Routing-module_col')]")
        options = wait.until(EC.presence_of_element_located(options_loc))
        options = driver.find_elements(*options_loc)

        # 2. 遍历选项：目标加selected，其他移除
        for opt in options:
            text = opt.text.strip()
            current_class = opt.get_attribute("class")
            if text == target_source:
                # 目标选项：添加selected类
                if SELECTED_CLASS not in current_class:
                    new_class = f"{current_class} {SELECTED_CLASS}"
                    driver.execute_script("arguments[0].setAttribute('class', arguments[1]);", opt, new_class)
            else:
                # 其他选项：移除selected类
                if SELECTED_CLASS in current_class:
                    new_class = current_class.replace(SELECTED_CLASS, "").strip()
                    driver.execute_script("arguments[0].setAttribute('class', arguments[1]);", opt, new_class)

        time.sleep(0.5)
        print(f"✅ 已设置信号源为：{target_source}")
        return True

    except Exception as e:
        print(f"❌ 设置信号源失败：{str(e)[:40]}")
        return False

# ==================== 主流程：读初始→设置→校验 ====================
if __name__ == "__main__":
    print("=" * 60)
    print("信号源选择自动化测试：读取 → 设置 → 校验")
    print("=" * 60)

    # 1. 读取初始信号源
    print("\n【初始信号源】")
    initial_source = get_current_source()

    # 2. 遍历设置所有信号源
    print("\n【开始切换所有信号源】")
    all_pass = True
    for source in SOURCE_LIST:
        set_source_by_class(source)
        time.sleep(0.5)

        # 3. 校验是否切换成功
        actual_source = get_current_source()
        print(f"预期：{source} | 实际：{actual_source}")
        if actual_source == source:
            print("✅ 切换成功")
        else:
            print("❌ 切换失败")
            all_pass = False

    print("\n" + "=" * 60)
    print("测试结论:", "全部通过 ✅" if all_pass else "部分失败 ❌")
    print("=" * 60)

    input("\n按回车关闭浏览器...")
    driver.quit()