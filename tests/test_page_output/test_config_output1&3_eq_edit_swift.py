from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

# ==================== 基础配置 ====================
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()
wait = WebDriverWait(driver, 15)

# ==================== 功能函数 ====================
def open_eq_edit_popup():
    edit_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//div[contains(@class,'Equalizer-module_btn') and text()='Edit']")
    ))
    edit_btn.click()
    time.sleep(3)

def check_point_display(point_num):
    panels = driver.find_elements(By.XPATH, "//div[contains(@class,'Edit-module_operate-container')]")
    target_index = point_num - 1

    for i in range(len(panels)):
        display = panels[i].value_of_css_property("display")
        if i == target_index:
            if display != "flex":
                return False
        else:
            if display != "none":
                return False
    return True

def test_point(point_num):
    print(f"\n====================================")
    print(f"🎯 测试频点 → {point_num}")
    print(f"====================================")

    tabs = driver.find_elements(By.XPATH, "//div[contains(@class,'Edit-module_waveType-tab')]")

    if point_num != 1:
        target_tab = tabs[point_num]
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", target_tab)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", target_tab)
        time.sleep(2.5)

    success = check_point_display(point_num)
    if success:
        print(f"✅ 频点 {point_num} 切换成功")
    else:
        print(f"❌ 频点 {point_num} 切换失败")
    return success

# ==================== 主流程 ====================
if __name__ == "__main__":
    print("=" * 60)
    print("      EQ 编辑弹窗 1~10 频点切换测试")
    print("=" * 60)

    driver.get("http://192.168.66.123/#/Output/Output1/Equalizer")
    time.sleep(6)

    # 打开弹窗
    open_eq_edit_popup()

    # 执行 1~10 频点测试
    for i in range(1, 11):
        test_point(i)

    print("\n🎉 全部 1~10 频点测试完成！")
    input("\n按回车关闭浏览器...")
    driver.quit()