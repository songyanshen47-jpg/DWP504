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

# 目标 URL
BASE_URL = "http://192.168.66.123/#/Output/Output1/Equalizer"
wait = WebDriverWait(driver, 15)


# ==================== 核心逻辑函数 ====================

def click_edit_button():
    """点击Edit按钮，触发弹窗"""
    try:
        edit_btn_loc = (By.XPATH, "//div[contains(@class,'Equalizer-module_btn') and normalize-space()='Edit']")
        edit_btn = wait.until(EC.element_to_be_clickable(edit_btn_loc))
        edit_btn.click()
        print("✅ 已点击Edit按钮，等待弹窗加载")
        time.sleep(1.5)  # 等待弹窗动画完成
        return True
    except Exception as e:
        print(f"❌ 点击Edit按钮失败：{str(e)[:40]}")
        return False


def adjust_parameters_sequence(param_list, steps=50):
    """
    按顺序对参数进行下调再上调的操作
    param_list: 形如 ["Gain", "Frequency", "Q"]
    """
    for param_name in param_list:
        print(f"\n🔎 正在定位参数行: 【{param_name}】")
        try:
            # 定位包含该参数名称的整行容器 (Selector)
            container_xpath = f"//div[contains(@class,'Edit-module_Selector') and .//*[contains(text(),'{param_name}')]]"
            container = wait.until(EC.visibility_of_element_located((By.XPATH, container_xpath)))

            # 获取初始数值文本
            display_loc = ".//div[contains(@class,'ScaleSteper-module_display-message')]"
            initial_val = container.find_element(By.XPATH, display_loc).text
            print(f"  [初始位置] -> {initial_val}")

            # 定位行内的加减按钮
            minus_btn = container.find_element(By.XPATH, ".//div[contains(@class,'Edit-module_pre')]")
            plus_btn = container.find_element(By.XPATH, ".//div[contains(@class,'Edit-module_plus')]")

            # --- 下调操作 ---
            print(f"  [-] 开始连续下调 {steps} 次...")
            for i in range(steps):
                minus_btn.click()
                # time.sleep(0.02) # 若通信卡顿请开启此行

            time.sleep(0.5)

            # --- 上调操作 ---
            print(f"  [+] 开始连续上调 {steps} 次...")
            for i in range(steps):
                plus_btn.click()
                # time.sleep(0.02) # 若通信卡顿请开启此行

            # 获取调整后的数值
            final_val = container.find_element(By.XPATH, display_loc).text
            print(f"  [调控完成] -> 当前值: {final_val}")

        except Exception as e:
            print(f"  ❌ 调控 {param_name} 时发生错误: {str(e)[:50]}")


def click_ok_button_in_popup():
    """点击弹窗内的OK按钮"""
    try:
        ok_btn_loc = (By.XPATH, "//div[contains(@class,'Edit-module') and normalize-space()='OK']")
        ok_btn = wait.until(EC.element_to_be_clickable(ok_btn_loc))
        ok_btn.click()
        print("\n✅ 已点击OK按钮，保存并关闭弹窗")
        return True
    except:
        print("\n❌ 点击OK按钮失败")
        return False


# ==================== 主流程 ====================
if __name__ == "__main__":
    try:
        print("🌐 正在初始化浏览器并访问页面...")
        driver.get(BASE_URL)

        # 1. 打开 Edit 弹窗
        if click_edit_button():
            # 2. 执行三个参数的有序调控 (Gain -> Frequency -> Q)
            target_params = ["Gain", "Frequency", "Q"]
            adjust_parameters_sequence(target_params, steps=50)

            # 3. 点击 OK 关闭
            time.sleep(1)
            click_ok_button_in_popup()

            print("\n" + "=" * 40)
            print("🎉 所有参数自动化调控测试流程已完成")
            print("=" * 40)

    except Exception as e:
        print(f"程序运行中断: {e}")
    finally:
        input("\n测试已结束，按回车键退出并关闭浏览器...")
        driver.quit()