from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ==================== 配置 ====================
BASE_URL = "http://192.168.66.123/#/Input"
BUTTONS = ["1", "2", "3", "4", "5"]

# ==================== 核心函数（按你截图的真实class写） ====================
def is_button_open(driver, num):
    """
    只通过 class 判断开关状态：
    - 开启：按钮包含 'WaveTypeSelector-module_open' 这个class
    - 关闭：按钮不包含这个class
    """
    try:
        # 定位按钮
        btn = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//div[contains(@class, 'WaveTypeSelector-module_idx') and text()='{num}']")
            )
        )
        # 获取所有class
        classes = btn.get_attribute("class")
        # 开启状态：包含 'WaveTypeSelector-module_open'
        return "WaveTypeSelector-module_open" in classes
    except:
        return False

def click_button(driver, num):
    """点击按钮，固定延时"""
    btn = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable(
            (By.XPATH, f"//div[contains(@class, 'WaveTypeSelector-module_idx') and text()='{num}']")
        )
    )
    btn.click()
    time.sleep(1.2)  # 等待class更新

# ==================== 测试流程 ====================
driver = webdriver.Chrome()
driver.maximize_window()
driver.get(BASE_URL)
time.sleep(5)

print("=" * 60)
print("🎯 5个按钮开关测试（纯class判断，无颜色）")
print("=" * 60)

# 1. 读取初始状态
print("\n【初始状态】")
before = {}
for n in BUTTONS:
    state = is_button_open(driver, n)
    before[n] = state
    print(f"按钮 {n}: {'开启' if state else '关闭'}")

# 2. 依次点击
print("\n【依次点击】")
for n in BUTTONS:
    print(f"点击按钮 {n}")
    click_button(driver, n)

# 3. 读取点击后状态
print("\n【点击后状态】")
after = {}
for n in BUTTONS:
    state = is_button_open(driver, n)
    after[n] = state
    print(f"按钮 {n}: {'开启' if state else '关闭'}")

# 4. 验证状态是否反转
print("\n【验证结果】")
all_pass = True
for n in BUTTONS:
    if before[n] != after[n]:
        print(f"✅ 按钮 {n} 切换成功")
    else:
        print(f"❌ 按钮 {n} 切换失败")
        all_pass = False

print("\n" + "=" * 60)
if all_pass:
    print("✅ 所有按钮测试通过！")
else:
    print("❌ 部分按钮状态异常")
print("=" * 60)

input("\n按回车关闭 → ")
driver.quit()