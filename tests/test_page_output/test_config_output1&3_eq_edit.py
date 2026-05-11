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
BASE_URL = "http://192.168.66.123/#/Output/Output1/Equalizer"
wait = WebDriverWait(driver, 10)
driver.get(BASE_URL)
time.sleep(6)

# ==================== 工具函数 ====================
def click_edit_button():
    """点击Edit按钮，触发弹窗"""
    try:
        # 定位Edit按钮（通过文本+class双重定位，稳定不失效）
        edit_btn_loc = (By.XPATH, "//div[contains(@class,'Equalizer-module_btn') and normalize-space()='Edit']")
        edit_btn = wait.until(EC.element_to_be_clickable(edit_btn_loc))
        edit_btn.click()
        time.sleep(1)  # 等待弹窗加载
        print("✅ 已点击Edit按钮，等待弹窗加载")
        return True
    except Exception as e:
        print(f"❌ 点击Edit按钮失败：{str(e)[:40]}")
        return False

def is_edit_popup_visible():
    """检查EQ编辑弹窗是否可见"""
    try:
        # 定位弹窗容器（截图中Edit-module_popup-floating）
        popup_loc = (By.XPATH, "//div[contains(@class,'Edit-module_popup-floating')]")
        popup = wait.until(EC.visibility_of_element_located(popup_loc))
        print("✅ EQ编辑弹窗已成功打开")
        return True
    except:
        print("❌ EQ编辑弹窗未打开")
        return False

def click_ok_button_in_popup():
    """点击弹窗内的OK按钮，关闭弹窗"""
    try:
        ok_btn_loc = (By.XPATH, "//div[contains(@class,'Edit-module') and normalize-space()='OK']")
        ok_btn = wait.until(EC.element_to_be_clickable(ok_btn_loc))
        ok_btn.click()
        time.sleep(1)
        print("✅ 已点击OK按钮，关闭弹窗")
        return True
    except Exception as e:
        print(f"❌ 点击OK按钮失败：{str(e)[:40]}")
        return False

def is_edit_popup_closed():
    """检查EQ编辑弹窗是否已关闭"""
    try:
        popup_loc = (By.XPATH, "//div[contains(@class,'Edit-module_popup-floating')]")
        wait.until(EC.invisibility_of_element_located(popup_loc))
        print("✅ EQ编辑弹窗已成功关闭")
        return True
    except:
        print("❌ EQ编辑弹窗未关闭")
        return False

# ==================== 主流程：点击Edit→校验弹窗打开→点击OK→校验弹窗关闭 ====================
if __name__ == "__main__":
    print("=" * 60)
    print("EQ Edit按钮自动化测试：点击→弹窗→关闭 完整流程")
    print("=" * 60)

    # 1. 点击Edit按钮
    print("\n【第一步：点击Edit按钮】")
    click_edit_button()

    # 2. 校验弹窗是否打开
    print("\n【第二步：校验弹窗状态】")
    popup_open = is_edit_popup_visible()

    # 3. 点击OK按钮关闭弹窗
    print("\n【第三步：点击OK按钮】")
    if popup_open:
        click_ok_button_in_popup()

    # 4. 校验弹窗是否关闭
    print("\n【第四步：校验弹窗关闭状态】")
    popup_closed = is_edit_popup_closed()

    # 测试结论
    print("\n" + "=" * 60)
    if popup_open and popup_closed:
        print("测试结论：Edit按钮交互流程 全部通过 ✅")
    else:
        print("测试结论：Edit按钮交互流程 存在失败项 ❌")
    print("=" * 60)

    input("\n按回车关闭浏览器...")
    driver.quit()