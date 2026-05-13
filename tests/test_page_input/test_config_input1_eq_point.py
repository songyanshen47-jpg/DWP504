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
BASE_URL = "http://192.168.66.123/#/Input"
wait = WebDriverWait(driver, 10)
driver.get(BASE_URL)
time.sleep(6)


# ==================== 核心函数 ====================

def get_active_channel():
    """
    读取当前激活的通道编号
    增加详细调试日志，定位失败原因
    """
    try:
        # 1. 尝试查找所有可能的导航按钮，看看它们的 class 是什么
        all_navs = driver.find_elements(By.CSS_SELECTOR, "div[class*='Eq-module_nav']")
        print(f"   [Debug] 找到 {len(all_navs)} 个导航按钮")

        active_num = None

        for nav in all_navs:
            classes = nav.get_attribute("class")
            span_text = nav.find_element(By.TAG_NAME, "span").text.strip()

            # 打印每个按钮的详细信息
            print(f"   [Debug] 通道{span_text} Class: {classes}")

            # 检查是否包含 'activated' 关键字
            if "activated" in classes.lower() or "active" in classes.lower():
                active_num = int(span_text)
                print(f"   ✅ 发现激活状态标识: 通道 {active_num}")
                break

        if active_num:
            return active_num
        else:
            print("   ⚠️ 未找到任何带有 'activated' 或 'active' 类名的元素")
            return None

    except Exception as e:
        print(f"   ❌ 获取激活通道异常: {e}")
        return None


def click_channel(num):
    """
    点击指定通道按钮（1~5）
    使用 JS 强制点击 + 滚动居中，确保稳定触发
    """
    try:
        # 定位到包含该数字的 nav div 的父元素（因为点击事件绑定在 div 上）
        locator = (By.XPATH, f"//div[contains(@class, 'Eq-module_nav')]//span[text()='{num}']/..")
        btn = wait.until(EC.element_to_be_clickable(locator))

        # 滚动到视图中心，防止被遮挡
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(0.3)

        # 使用 JS 点击，绕过 Selenium 的可点击性检查
        driver.execute_script("arguments[0].click();", btn)
        print(f"✅ 已点击通道 {num}")
        return True
    except Exception as e:
        print(f" 点击通道 {num} 失败: {str(e)[:80]}")
        return False


# ==================== 主流程 ====================

if __name__ == "__main__":
    print("=" * 70)
    print("EQ 通道切换自动化测试：仅基于导航栏激活状态")
    print("=" * 70)

    # 1. 读取初始激活通道
    initial_ch = get_active_channel()
    if initial_ch is None:
        print("❌ 初始状态读取失败，退出")
        driver.quit()
        exit(1)

    print(f"\n📌 初始激活通道: {initial_ch}")

    # 2. 定义要测试的切换序列（例如：从当前通道开始，依次切换到 1→2→3→4→5）
    test_sequence = [1, 2, 3, 4, 5]  # 你可以改成任意顺序，如 [3,1,5,2,4]

    all_passed = True

    for target_ch in test_sequence:
        print(f"\n>>> 尝试切换到通道: {target_ch}")

        # 如果已经是目标通道，跳过
        current_ch = get_active_channel()
        if current_ch == target_ch:
            print(f"   ℹ️ 当前已在通道 {target_ch}，跳过")
            continue

        # 执行切换
        if not click_channel(target_ch):
            all_passed = False
            continue

        # 等待 UI 更新
        time.sleep(0.8)

        # 验证是否成功激活
        new_active_ch = get_active_channel()
        if new_active_ch == target_ch:
            print(f"   ✅ 验证通过：当前激活通道为 {target_ch}")
        else:
            print(f"   ❌ 验证失败：预期 {target_ch}，实际 {new_active_ch}")
            all_passed = False

    # 3. 总结
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 所有通道切换测试通过！")
    else:
        print("💥 部分测试失败，请检查日志")
    print("=" * 70)

    input("\n按回车退出...")
    driver.quit()
