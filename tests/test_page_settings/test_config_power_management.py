import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# --- 配置参数 ---
TARGET_URL = "http://192.168.66.123/#/Settings/PowerManagement"
MUTE_VALUES = [5, 10]  # 目标分钟数
OBSERVATION_DELAY = 10  # 每次设置后的额外观察延迟（秒）


def run_mute_automation():
    # 1. 初始化浏览器
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()

    try:
        driver.get(TARGET_URL)
        time.sleep(5)  # 等待页面加载完成

        # 2. 导航到 Power Management 标签页
        # 根据 HTML 结构，找到包含 "Power Management" 文字的菜单项
        print("正在导航至 Power Management...")
        power_tab = driver.find_element(By.XPATH, "//span[text()='Power Management']")
        power_tab.click()
        time.sleep(2)

        # 3. 循环设置 Mute Time
        # 注意：Mute Time 滑块在 HTML 中由 .ant-slider-handle 控制
        # 我们通过定位刻度（mark-text）来模拟拖拽或直接点击
        # 3. 循环设置 Mute Time
        for val in MUTE_VALUES:
            print(f"\n--- 开始测试环节: Mute Time = {val} 分钟 ---")

            # 优化点：使用显式等待，确保刻度文字已经出现在屏幕上且可点击
            # 优化 XPATH：精准定位 Mute Time 下方的刻度，防止点到 Standby Time 的数字
            xpath_selector = f"//span[text()='Mute Time (Minutes)']/following::span[text()='{val}']"

            try:
                target_mark = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, xpath_selector))
                )

                # 模拟点击
                ActionChains(driver).move_to_element(target_mark).click().perform()
                print(f"已成功设置 Mute Time 为 {val} 分钟。")
            except Exception as e:
                print(f"设置 {val} 分钟时发生错误: {e}")
            # 等待设定的分钟数（转换为秒）
            wait_time = val * 60
            print(f"正在等待设备进入静音状态 ({wait_time}秒)...")
            time.sleep(wait_time)

            print(f"设备应已静音。现在进入自定义观察期 ({OBSERVATION_DELAY}秒)...")
            time.sleep(OBSERVATION_DELAY)

            print(f"环节 {val} 分钟测试完成。")

        print("\n所有自动化测试环节已执行完毕。")

    except Exception as e:
        print(f"自动化执行中出错: {e}")
    finally:
        print("测试结束，浏览器将在 10 秒后关闭。")
        time.sleep(10)
        driver.quit()


if __name__ == "__main__":
    run_mute_automation()