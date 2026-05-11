from selenium import webdriver
from selenium.common import TimeoutException
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
BASE_URL = "http://192.168.66.123/#/Output/Output1/"
wait = WebDriverWait(driver, 10)
driver.get(BASE_URL)
time.sleep(6)


# ==================== 导航到 EQ ====================
def navigate_to_eq():
    """导航到 Output1 → Equalizer"""
    print("\n>>> 导航到 Equalizer...")

    try:
        # 点击 Output 1
        output1 = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Output 1']")))
        output1.click()
        print("  ✅ 点击 Output 1 成功")
        time.sleep(1)

        # 点击 Equalizer
        eq = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Equalizer']")))
        eq.click()
        print("  ✅ 点击 Equalizer 成功")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"  ❌ 导航失败: {e}")
        return False


# ==================== EQ 弹窗操作函数 ====================

def click_edit_button():
    """点击 Edit 按钮，触发弹窗"""
    try:
        edit_btn_loc = (By.XPATH, "//div[contains(@class,'Equalizer-module_btn') and normalize-space()='Edit']")
        edit_btn = wait.until(EC.element_to_be_clickable(edit_btn_loc))
        edit_btn.click()
        time.sleep(1.5)
        print("✅ 已点击 Edit 按钮")
        return True
    except Exception as e:
        print(f"❌ 点击 Edit 按钮失败: {e}")
        return False


def is_edit_popup_visible():
    """检查 EQ 编辑弹窗是否可见"""
    try:
        popup_loc = (By.XPATH, "//div[contains(@class,'Edit-module_popup-floating')]")
        popup = wait.until(EC.visibility_of_element_located(popup_loc))
        print("✅ EQ 编辑弹窗已打开")
        return True
    except:
        print("❌ EQ 编辑弹窗未打开")
        return False


def get_band_filter_type(band_index=1):
    """
    获取指定 Band 的当前 Filter Type
    band_index: 1, 2, 3, 4, 5
    """
    try:
        # 定位 Band 容器
        band_item = driver.find_element(By.XPATH,
                                        f"(//div[contains(@class, 'Edit-module_operate-item__')])[{band_index}]")

        # 查找显示滤波器类型的元素（带有 arrow-box 类的区域）
        try:
            type_display = band_item.find_element(By.XPATH, ".//div[contains(@class, 'arrow-box')]//span")
            return type_display.text.strip()
        except:
            pass

        # 备选：查找所有 span，过滤出滤波器类型
        spans = band_item.find_elements(By.TAG_NAME, "span")
        filter_keywords = ["Parametric", "Notch", "Lowpass", "Highpass", "Bandpass", "All Pass", "Shelf"]

        for span in spans:
            text = span.text.strip()
            if any(keyword in text for keyword in filter_keywords):
                return text

        return None
    except Exception as e:
        print(f"  ⚠️ 读取 Band {band_index} Filter Type 失败: {e}")
        return None


def switch_band_filter_type(band_index, target_mode_id, target_display_name):
    """
    切换指定 Band 的 Filter Type
    band_index: 1-5
    target_mode_id: data-menu-id 属性值，如 "LOW_SHELF_Q", "HIGH_SHELF_Q", "PARAMETRIC", "NOTCH" 等
    target_display_name: 显示名称，用于打印
    """
    try:
        # 1. 定位 Band 容器
        band_item = wait.until(EC.presence_of_element_located(
            (By.XPATH, f"(//div[contains(@class, 'Edit-module_operate-item__')])[{band_index}]")
        ))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", band_item)
        time.sleep(0.5)

        # 2. 找到并点击当前 Filter Type 显示区域
        click_targets = [
            (By.XPATH, ".//div[contains(@class, 'arrow-box')]"),
            (By.XPATH, ".//div[contains(@class, 'wave-type')]"),
        ]

        clicked = False
        for by, xpath in click_targets:
            try:
                target = band_item.find_element(by, xpath)
                driver.execute_script("arguments[0].click();", target)
                print(f"    🔽 点击 Band {band_index} Filter Type 选择器")
                clicked = True
                break
            except:
                continue

        if not clicked:
            print(f"    ❌ 未找到 Band {band_index} 的选择器")
            return False

        time.sleep(0.8)

        # 3. 在下拉菜单中选择目标类型（使用 data-menu-id）
        option_xpath = f"//li[@data-menu-id='{target_mode_id}']"
        try:
            option = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, option_xpath))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option)
            time.sleep(0.2)
            driver.execute_script("arguments[0].click();", option)
            print(f"    ✅ Band {band_index} -> {target_display_name} 成功")
            return True
        except:
            # 备选：通过文本匹配
            try:
                text_xpath = f"//li//span[contains(text(), '{target_display_name}')]"
                option = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, text_xpath))
                )
                driver.execute_script("arguments[0].click();", option)
                print(f"    ✅ Band {band_index} -> {target_display_name} 成功")
                return True
            except:
                print(f"    ❌ 未找到选项: {target_display_name}")
                return False

    except Exception as e:
        print(f"    ❌ 切换 Band {band_index} 失败: {e}")
        return False


def click_ok_button():
    """点击弹窗内的 OK 按钮"""
    try:
        ok_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(@class, 'ant-btn-primary') and normalize-space()='OK']")))
        ok_btn.click()
        time.sleep(1)
        print("✅ 已点击 OK 按钮")
        return True
    except:
        try:
            ok_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(@class, 'Edit-module') and normalize-space()='OK']")))
            ok_btn.click()
            print("✅ 已点击 OK 按钮")
            return True
        except Exception as e:
            print(f"❌ 点击 OK 按钮失败: {e}")
            return False


# ==================== 主流程 ====================

if __name__ == "__main__":
    print("=" * 70)
    print("EQ Equalizer 自动化测试：Band 1 Filter Type 切换")
    print("=" * 70)

    all_passed = True

    # 1. 导航到 Equalizer
    if not navigate_to_eq():
        print("❌ 导航失败")
        driver.quit()
        exit()

    # 2. 点击 Edit 按钮
    print("\n【步骤 1】点击 Edit 按钮")
    if not click_edit_button():
        all_passed = False
    else:
        # 3. 验证弹窗打开
        print("\n【步骤 2】验证弹窗是否打开")
        if not is_edit_popup_visible():
            all_passed = False
        else:
            # 4. 读取初始 Filter Type
            print("\n【步骤 3】读取 Band 1 初始 Filter Type")
            initial_type = get_band_filter_type(1)
            print(f"   📊 初始类型: {initial_type}")

            # 5. 定义要测试的模式（基于 HTML 中的 data-menu-id）
            test_modes = [
                ("LOW_SHELF_Q", "Low Shelf (with Q)"),
                ("HIGH_SHELF_Q", "High Shelf (with Q)"),
                ("PARAMETRIC", "Parametric"),
                ("LOWPASS_6", "Lowpass (6 dB/octave)"),
                ("HIGHPASS_6", "Highpass (6 dB/octave)"),
                ("LOWPASS_12", "Lowpass (12 dB/octave)"),
                ("HIGHPASS_12", "Highpass (12 dB/octave)"),
                ("ALLPASS_1", "All Pass (1st order)"),
                ("ALLPASS_2", "All Pass (2nd order)"),
                ("BANDPASS", "Bandpass"),
                ("NOTCH", "Notch"),
                ("LOW_SHELF_12", "Low Shelf (12 dB/octave)"),
                ("HIGH_SHELF_12", "High Shelf (12 dB/octave)"),
            ]

            # 6. 依次切换测试
            print("\n【步骤 4】开始切换测试 Band 1 Filter Type")
            print("-" * 50)

            for mode_id, mode_name in test_modes:
                print(f"\n   >>> 切换 Band 1 到: {mode_name}")

                if switch_band_filter_type(1, mode_id, mode_name):
                    time.sleep(1)
                    current = get_band_filter_type(1)
                    print(f"       📍 当前显示: {current}")
                else:
                    all_passed = False
                    print(f"       ❌ 切换失败")

                time.sleep(0.5)

            # 7. 切回初始模式（Parametric）
            print("\n【步骤 5】切回初始模式")
            if switch_band_filter_type(1, "PARAMETRIC", "Parametric"):
                time.sleep(1)
                current = get_band_filter_type(1)
                print(f"   📍 当前显示: {current}")
            else:
                all_passed = False

            # 8. 点击 OK 关闭弹窗
            print("\n【步骤 6】关闭弹窗")
            if not click_ok_button():
                all_passed = False

    # 总结
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 所有 EQ Filter Type 切换测试通过！")
        print(f"   - 共测试 {len(test_modes)} 种滤波器类型")
        print("   - 所有类型切换成功")
    else:
        print("💥 部分测试失败，请检查上方日志")
    print("=" * 70)

    input("\n按回车退出...")
    driver.quit()