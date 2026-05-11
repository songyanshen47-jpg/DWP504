from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
import re
from datetime import datetime

# ==================== 配置 ====================
CONFIG_DIR = r"d:\tonwel\21087\Desktop\工作\.net\dwp"
BASE_URL = "http://192.168.66.123/#/Output/Output1/SpeakerPreset/Preset"
DOWNLOAD_WAIT = 30

os.makedirs(CONFIG_DIR, exist_ok=True)


# ==================== Chrome 配置 ====================
def get_chrome_options():
    opt = Options()
    opt.add_argument("--start-maximized")
    opt.add_argument("--disable-web-security")
    opt.add_argument("--allow-running-insecure-content")
    opt.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    opt.add_experimental_option("useAutomationExtension", False)

    prefs = {
        "download.default_directory": CONFIG_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,
        "safebrowsing.disable_download_protection": True,
        "profile.default_content_setting_values.automatic_downloads": 1,
    }
    opt.add_experimental_option("prefs", prefs)
    return opt


# ==================== 文件管理 ====================
def get_next_filename():
    """生成下一个文件名（从1开始递增）"""
    existing_numbers = []

    for filename in os.listdir(CONFIG_DIR):
        match = re.match(r'^(\d+)\.peg(?:all)?$', filename)
        if match:
            existing_numbers.append(int(match.group(1)))

    if existing_numbers:
        next_num = max(existing_numbers) + 1
    else:
        next_num = 1

    next_file = os.path.join(CONFIG_DIR, f"{next_num}.peg")
    print(f"📁 导出文件名: {next_num}.peg")
    return next_file, next_num


def wait_for_download(timeout=DOWNLOAD_WAIT):
    """等待下载完成"""
    print("  ⏳ 等待下载完成...")
    start_time = time.time()

    before_files = set(os.listdir(CONFIG_DIR))

    while time.time() - start_time < timeout:
        current_files = set(os.listdir(CONFIG_DIR))
        new_files = current_files - before_files

        for f in new_files:
            if f.endswith('.peg') and not f.endswith('.crdownload'):
                filepath = os.path.join(CONFIG_DIR, f)
                print(f"\n  ✅ 下载完成: {f}")
                return filepath

        downloading = [f for f in current_files if f.endswith('.crdownload')]
        if downloading:
            print(f"\r    下载中: {downloading[0]}", end="")

        time.sleep(1)

    print(f"\n  ❌ 下载超时")
    return None


# ==================== 导航函数 ====================
def click_menu_item(driver, target_name, wait_time=10):
    """点击菜单项"""
    try:
        wait = WebDriverWait(driver, wait_time)
        locator = (By.XPATH, f"//span[normalize-space()='{target_name}']")
        btn = wait.until(EC.element_to_be_clickable(locator))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", btn)
        print(f"  ✅ 点击 '{target_name}' 成功")
        return True
    except Exception as e:
        print(f"  ❌ 点击 '{target_name}' 失败: {e}")
        return False


def navigate_to_preset(driver):
    """导航到 Speaker Preset → Preset"""
    print("\n▶ 导航到 Speaker Preset → Preset")

    if not click_menu_item(driver, "Speaker Preset"):
        return False
    time.sleep(1)

    if not click_menu_item(driver, "Preset"):
        return False
    time.sleep(2)

    print("  ✅ 已进入 Preset 页面")
    return True


# ==================== 导出操作 ====================
def click_export_button(driver):
    """点击 EXPORT PRESET TO FILE 按钮"""
    print("\n▶ 点击导出按钮...")

    export_xpaths = [
        "//span[contains(text(),'EXPORT PRESET TO FILE')]",
        "//button[contains(text(),'EXPORT PRESET TO FILE')]",
        "//div[contains(@class,'Preset-module_btn')]//span[contains(text(),'EXPORT')]",
        "//*[contains(text(),'EXPORT PRESET')]",
    ]

    for xpath in export_xpaths:
        try:
            btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            driver.execute_script("arguments[0].click();", btn)
            print("  ✅ 已点击 EXPORT PRESET TO FILE 按钮")
            return True
        except:
            continue

    print("  ❌ 未找到导出按钮")
    return False


def select_export_options(driver):
    """
    勾选所有导出选项
    根据实际HTML结构：点击未勾选的 radio 区域
    """
    print("\n▶ 勾选导出选项...")

    # 等待弹窗出现
    time.sleep(2)

    # 选项列表（注意拼写：Crossower 是页面中的实际文本）
    options_list = [
        "Speaker Eq",
        "Crossower",  # 注意页面中是 Crossower 不是 Crossover
        "Speaker Delay",
        "FIR",
        "Limiter",
        "Polarity"
    ]

    selected_items = []

    for item in options_list:
        try:
            # 根据HTML结构定位 item 容器
            item_container_xpath = f"//div[contains(@class, 'ExportSpeakerPreset-module_item__')]//span[contains(@class, 'ExportSpeakerPreset-module_label__') and text()='{item}']/ancestor::div[contains(@class, 'ExportSpeakerPreset-module_item__')]"

            item_container = driver.find_element(By.XPATH, item_container_xpath)

            # 检查是否已勾选（查找是否有 activated 类）
            classes = item_container.get_attribute("class")

            # 查找 radio 元素
            radio = item_container.find_element(By.XPATH,
                                                ".//div[contains(@class, 'ExportSpeakerPreset-module_radio__')]")
            radio_classes = radio.get_attribute("class")

            is_checked = "activated" in radio_classes or "checked" in radio_classes or "active" in radio_classes

            if not is_checked:
                # 点击 radio 区域来勾选
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio)
                time.sleep(0.3)
                driver.execute_script("arguments[0].click();", radio)
                print(f"  ✅ 已勾选: {item}")
                selected_items.append(item)
            else:
                print(f"  ℹ️ 已勾选: {item}")
                selected_items.append(item)

            time.sleep(0.5)  # 延迟让UI响应

        except Exception as e:
            print(f"  ⚠️ 处理 '{item}' 时出错: {e}")

    return selected_items


def click_cancel_or_export(driver, action="Export"):
    """点击弹窗中的 Cancel 或 Export 按钮"""
    print(f"\n▶ 点击 {action} 按钮...")

    button_xpaths = [
        f"//div[contains(@class, 'ExportSpeakerPreset-module_footer-btn__') and text()='{action}']",
        f"//div[contains(@class, 'footer-btn') and text()='{action}']",
        f"//button[contains(text(), '{action}')]",
    ]

    for xpath in button_xpaths:
        try:
            btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            driver.execute_script("arguments[0].click();", btn)
            print(f"  ✅ 已点击 {action} 按钮")
            return True
        except:
            continue

    print(f"  ⚠️ 未找到 {action} 按钮")
    return False


# ==================== 主流程 ====================
def main():
    print("=" * 70)
    print("PROEL Speaker Preset → Preset 导出测试")
    print("=" * 70)

    opt = get_chrome_options()
    driver = webdriver.Chrome(options=opt)

    try:
        # 1. 打开页面
        print(f"\n▶ 打开页面: {BASE_URL}")
        driver.get(BASE_URL)
        time.sleep(5)

        # 2. 导航到 Preset
        if not navigate_to_preset(driver):
            print("❌ 导航失败")
            return

        # 3. 生成导出文件名
        export_file, file_num = get_next_filename()

        # 4. 点击导出按钮
        if not click_export_button(driver):
            print("❌ 点击导出按钮失败")
            return

        # 5. 勾选所有选项
        selected = select_export_options(driver)

        if selected:
            print(f"\n  📋 已勾选 {len(selected)}/6 个选项: {selected}")
        else:
            print(f"\n  ⚠️ 未能勾选任何选项")

        # 6. 确认导出
        if not click_cancel_or_export(driver, "Export"):
            print("⚠️ 无法确认导出")
            return

        # 7. 等待下载完成
        downloaded_file = wait_for_download(timeout=30)

        if downloaded_file:
            expected_file = os.path.join(CONFIG_DIR, f"{file_num}.peg")
            if downloaded_file != expected_file:
                if os.path.exists(expected_file):
                    os.remove(expected_file)
                os.rename(downloaded_file, expected_file)
                print(f"\n✅ 文件已保存: {expected_file}")
            else:
                print(f"\n✅ 文件已保存: {downloaded_file}")
        else:
            print("\n❌ 导出失败")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("\n" + "=" * 50)
        choice = input("请选择:\n  [1] 关闭浏览器\n  [2] 保持浏览器打开\n请输入数字: ")
        if choice == "1":
            driver.quit()
            print("✅ 浏览器已关闭")
        else:
            print("✅ 浏览器保持打开")


if __name__ == "__main__":
    main()