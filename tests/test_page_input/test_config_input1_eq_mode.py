from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
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
BASE_URL = "http://192.168.66.123/#/Input"
wait = WebDriverWait(driver, 15)
driver.get(BASE_URL)
time.sleep(6)

# ==================== 波形配置 ====================
WAVE_DATA_ID = {
    "Parametric": "PARAMETRIC",
    "Low Shelf": "LOW_SHELF_Q",
    "High Shelf": "HIGH_SHELF_Q",
    "Lowpass": "LOWPASS_12",
    "Highpass": "HIGHPASS_12"
}

WAVE_DISPLAY_TEXT = {
    "Parametric": "Parametric",
    "Low Shelf": "Low Shelf (with Q)",
    "High Shelf": "High Shelf (with Q)",
    "Lowpass": "Lowpass (12 dB/octave)",
    "Highpass": "Highpass (12 dB/octave)"
}

WAVE_ICON_MATCH = {
    "Parametric": "Uozw09Fv4vQAAAABJRU5ErkJggg==",
    "Low Shelf": "cUyaX4eLmOQAAAABJRU5ErkJggg==",
    "High Shelf": "/HcnnabTzYkAAAAASUVORK5CYII=",
    "Lowpass": "LAyg+G5cg0e5rAAAAAElFTkSuQmCC",
    "Highpass": "U/4b+FNwRkQAAAAASUVORK5CYII="
}


# ==================== 工具函数 ====================

def close_all_dropdowns():
    """关闭所有打开的下拉菜单"""
    try:
        driver.execute_script("document.body.click();")
        time.sleep(0.3)
    except:
        pass


def get_channel_idx_element(channel_num):
    """获取通道的序号元素（用于悬浮）"""
    xpath = f"//div[starts-with(@class,'WaveTypeSelector-module_idx') and normalize-space()='{channel_num}']"
    return driver.find_element(By.XPATH, xpath)


def hover_channel(channel_num):
    """悬浮到指定通道"""
    try:
        idx_element = get_channel_idx_element(channel_num)
        ActionChains(driver).move_to_element(idx_element).pause(0.5).perform()
        print(f"  ✅ 通道{channel_num} 悬浮成功")
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"  ❌ 通道{channel_num} 悬浮失败: {e}")
        return False


def get_selected_display(channel_num):
    """获取当前选中的波形显示区域（可点击的元素）"""
    xpath = f"//div[starts-with(@class,'WaveTypeSelector-module_idx') and normalize-space()='{channel_num}']/parent::div//div[contains(@class, 'WaveTypeSelector-module_selected')]"
    return driver.find_element(By.XPATH, xpath)


def click_wave_selector(channel_num):
    """点击波形选择器打开下拉菜单"""
    try:
        hover_channel(channel_num)
        time.sleep(0.3)

        selected_display = get_selected_display(channel_num)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selected_display)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", selected_display)
        print(f"  ✅ 通道{channel_num} 点击波形选择器")
        time.sleep(0.8)
        return True
    except Exception as e:
        print(f"  ❌ 通道{channel_num} 点击选择器失败: {e}")
        return True  # 即使报错也继续尝试


def get_current_wave(channel_num):
    """通过图标识别当前波形类型"""
    try:
        close_all_dropdowns()
        time.sleep(0.2)

        hover_channel(channel_num)
        time.sleep(0.2)

        icon_xpath = f"//div[starts-with(@class,'WaveTypeSelector-module_idx') and normalize-space()='{channel_num}']/following-sibling::div[1]//img"
        img = driver.find_element(By.XPATH, icon_xpath)
        src = img.get_attribute("src")

        for wave_name, match_str in WAVE_ICON_MATCH.items():
            if match_str in src:
                return wave_name
        return "unknown"
    except Exception as e:
        return "unknown"


def select_wave_type(channel_num, wave_name):
    """为指定通道选择波形类型"""
    if wave_name not in WAVE_DATA_ID:
        print(f"  ❌ 未知波形类型: {wave_name}")
        return False

    data_id = WAVE_DATA_ID[wave_name]
    display_text = WAVE_DISPLAY_TEXT[wave_name]

    try:
        # 1. 点击打开下拉菜单
        if not click_wave_selector(channel_num):
            return False

        # 2. 等待下拉菜单出现
        time.sleep(0.8)

        # 3. 查找有文本的选项（关键修复：选择文本非空的选项）
        option = None

        # 查找所有匹配 data-menu-id 且有文本的选项
        try:
            all_options = driver.find_elements(By.XPATH, f"//li[@data-menu-id='{data_id}']")
            for opt in all_options:
                try:
                    text_span = opt.find_element(By.XPATH, ".//span[@class='ant-dropdown-menu-title-content']")
                    text = text_span.text
                    if text and len(text) > 0:  # 只选择有文本的选项
                        option = opt
                        print(f"    ✅ 找到有文本的选项: {text}")
                        break
                except:
                    continue
        except Exception as e:
            print(f"    ⚠️ 查找选项失败: {e}")

        # 方式2: 如果没找到，通过文本直接查找
        if not option:
            try:
                option_xpath = f"//li//span[contains(text(), '{display_text}')]/.."
                option = driver.find_element(By.XPATH, option_xpath)
                print(f"    ✅ 通过文本找到选项: {display_text}")
            except:
                pass

        if not option:
            print(f"    ❌ 未找到选项: {wave_name}")
            return False

        # 4. 滚动到选项并点击
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", option)
        print(f"  ✅ 通道{channel_num} -> {wave_name} 成功")
        time.sleep(1.0)

        # 5. 关闭下拉菜单
        close_all_dropdowns()

        return True

    except Exception as e:
        print(f"  ❌ 通道{channel_num} -> {wave_name} 异常: {e}")
        return False


# ==================== 主流程 ====================

if __name__ == "__main__":
    print("=" * 70)
    print("Input EQ 波形自动化测试：读取 → 设置 → 校验")
    print("=" * 70)

    # 1. 初始读取
    print("\n【步骤 1】初始读取 5 个通道的波形类型")
    print("-" * 50)
    initial_waves = []
    for ch in range(1, 6):
        wave = get_current_wave(ch)
        initial_waves.append(wave)
        print(f"  通道{ch} → {wave}")
        time.sleep(0.5)

    # 2. 逐个设置每个通道
    print("\n【步骤 2】为每个通道设置不同的波形")
    print("-" * 50)

    channel_targets = {
        1: "Parametric",
        2: "Low Shelf",
        3: "High Shelf",
        4: "Lowpass",
        5: "Highpass"
    }

    all_success = True

    for ch in range(1, 6):
        target = channel_targets[ch]
        print(f"\n  ===== 通道{ch} 设置目标: {target} =====")

        # 先关闭所有下拉菜单，确保干净状态
        close_all_dropdowns()
        time.sleep(0.5)

        if select_wave_type(ch, target):
            time.sleep(0.8)
            actual = get_current_wave(ch)
            if actual == target:
                print(f"    ✅ 验证成功: {actual}")
            else:
                print(f"    ⚠️ 验证失败: 期望 {target}, 实际 {actual}")
                all_success = False
        else:
            print(f"    ❌ 设置失败")
            all_success = False

        time.sleep(0.5)

    # 3. 最终验证
    print("\n【步骤 3】最终验证所有通道")
    print("-" * 50)

    all_ok = True
    for ch in range(1, 6):
        actual = get_current_wave(ch)
        expected = channel_targets[ch]
        status = "✅" if actual == expected else "❌"
        print(f"  通道{ch} | 预期：{expected} | 实际：{actual} {status}")
        if actual != expected:
            all_ok = False

    # 4. 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    print(f"  初始状态: {initial_waves}")
    print(f"  设置状态: {'✅ 全部成功' if all_success else '❌ 部分失败'}")
    print(f"  最终结果: {'✅ 全部通过' if all_ok else '❌ 部分失败'}")

    print("=" * 70)

    input("\n按回车退出...")
    driver.quit()