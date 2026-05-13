import random
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

# ==================== 配置 ====================
chrome_options = Options()
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()
wait = WebDriverWait(driver, 10)

BASE_URL = "http://192.168.66.123/#/Output/Output1/Equalizer"

PARAM_CONFIG = {
    "Gain": {"min": -15, "max": 15, "precision": 1, "unit": "dB", "default": 0, "tolerance": 0.5},
    "Frequency": {"min": 20, "max": 20000, "precision": 0, "unit": "Hz", "default": 1000, "tolerance": 10},
    "Q": {"min": 0.4, "max": 30, "precision": 1, "unit": "", "default": 1, "tolerance": 0.5}
}


def get_random_test_values(param_name, count=10):
    """生成随机测试值"""
    cfg = PARAM_CONFIG[param_name]
    values = []

    # 添加边界值和默认值
    special_values = [cfg["min"], cfg["max"], cfg["default"]]
    for v in special_values:
        if v not in values:
            values.append(v)

    # 添加随机值
    while len(values) < count:
        val = round(random.uniform(cfg["min"], cfg["max"]), cfg["precision"])
        if val not in values:
            values.append(val)

    return values[:count]


def safe_js_click(element):
    """JS点击"""
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.2)
        driver.execute_script("arguments[0].click();", element)
        return True
    except Exception as e:
        print(f"    JS点击失败: {e}")
        return False


def clear_input_field(input_field):
    """彻底清空输入框"""
    # 方法1: Ctrl+A + Delete
    input_field.send_keys(Keys.CONTROL + "a")
    input_field.send_keys(Keys.DELETE)
    time.sleep(0.1)

    # 方法2: 再手动清空一次value属性
    driver.execute_script("arguments[0].value = '';", input_field)
    time.sleep(0.1)


def get_current_display_value(container):
    """获取当前显示的值"""
    try:
        display_div = container.find_element(By.XPATH, ".//div[contains(@class,'ScaleSteper-module_display-message')]")
        text = display_div.text.strip()
        match = re.search(r"(-?\d+\.?\d*)", text)
        if match:
            return float(match.group(1))
        return None
    except:
        return None


def get_param_container(param_name):
    """获取参数所在的行容器"""
    xpath = f"//div[contains(@class,'Edit-module_Selector') and .//*[contains(text(),'{param_name}')]]"
    return wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))


def close_all_popovers():
    """强制关闭所有弹窗"""
    try:
        driver.execute_script("document.body.click();")
        time.sleep(0.2)
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(0.2)
    except:
        pass


def set_param_value(param_name, target_value):
    """
    设置参数值
    返回: (是否成功, 实际值)
    """
    cfg = PARAM_CONFIG[param_name]
    container = get_param_container(param_name)
    display_div = container.find_element(By.XPATH, ".//div[contains(@class,'ScaleSteper-module_display-message')]")

    try:
        # 1. 关闭可能存在的弹窗
        close_all_popovers()

        # 2. 点击显示区域唤起弹窗
        safe_js_click(display_div)
        time.sleep(0.5)

        # 3. 等待弹窗出现
        popover = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ant-popover:not([style*='display: none'])"))
        )

        # 4. 在弹窗内找输入框
        input_field = popover.find_element(By.CSS_SELECTOR, "input.ant-input-number-input")

        # 5. 彻底清空输入框（关键修复）
        clear_input_field(input_field)

        # 6. 输入新值
        input_field.send_keys(str(target_value))
        time.sleep(0.3)

        # 7. 验证输入框的值是否正确
        current_input_value = input_field.get_attribute("value")
        if current_input_value != str(target_value):
            # 如果没输入正确，再试一次
            clear_input_field(input_field)
            input_field.send_keys(str(target_value))
            time.sleep(0.3)

        # 8. 点击确认按钮
        confirm_btn = popover.find_element(By.CSS_SELECTOR, "span[aria-label='check-circle']")
        safe_js_click(confirm_btn)

        # 9. 等待弹窗消失
        wait.until(EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, "div.ant-popover:not([style*='display: none'])"))
        )
        time.sleep(0.5)

        # 10. 验证是否生效
        new_value = get_current_display_value(container)

        if new_value is not None and abs(new_value - target_value) <= cfg["tolerance"]:
            return True, new_value
        else:
            return False, new_value

    except TimeoutException:
        print(f"    超时: 弹窗未出现")
        close_all_popovers()
        return False, None
    except Exception as e:
        print(f"    异常: {str(e)[:80]}")
        close_all_popovers()
        return False, None


def test_param(param_name):
    """测试单个参数"""
    cfg = PARAM_CONFIG[param_name]
    print(f"\n{'=' * 60}")
    print(f"测试参数: 【{param_name}】 ({cfg['min']} ~ {cfg['max']} {cfg['unit']})")
    print(f"{'=' * 60}")

    test_values = get_random_test_values(param_name, 10)
    success_count = 0

    for i, val in enumerate(test_values):
        print(f"\n  [{i + 1}/{len(test_values)}] 测试值: {val} {cfg['unit']}")

        # 获取当前值
        container = get_param_container(param_name)
        old_value = get_current_display_value(container)
        print(f"    设置前: {old_value}")

        # 设置新值
        success, new_value = set_param_value(param_name, val)

        if success:
            print(f"    ✅ 成功! 新值: {new_value}")
            success_count += 1
        else:
            print(f"    ❌ 失败! 预期: {val}, 实际: {new_value}")

        time.sleep(0.5)

    print(
        f"\n  📊 {param_name} 完成: {success_count}/{len(test_values)} 成功 ({success_count / len(test_values) * 100:.1f}%)")
    return success_count


def reset_to_default():
    """重置所有参数"""
    print("\n🔄 重置参数到默认值...")
    for param_name, cfg in PARAM_CONFIG.items():
        success, _ = set_param_value(param_name, cfg["default"])
        status = "✅" if success else "❌"
        print(f"  {status} {param_name} = {cfg['default']} {cfg['unit']}")
        time.sleep(0.5)


def run_full_test():
    """完整测试"""
    print("=" * 70)
    print("🎯 EQ参数随机输入测试")
    print("=" * 70)

    # 点击Edit按钮
    try:
        edit_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'Equalizer-module_btn') and text()='Edit']"))
        )
        safe_js_click(edit_btn)
        print("✅ 进入编辑模式")
        time.sleep(1)
    except Exception as e:
        print(f"⚠️ 点击Edit失败: {e}")

    # 重置
    reset_to_default()
    time.sleep(1)

    # 测试各参数
    total_success = 0
    total_tests = 0

    for param in ["Gain", "Frequency", "Q"]:
        success = test_param(param)
        total_success += success
        total_tests += 10
        time.sleep(1)

    # 总结
    print("\n" + "=" * 70)
    print("📊 测试总结")
    print("=" * 70)
    print(f"总测试: {total_tests}")
    print(f"成功: {total_success}")
    print(f"成功率: {total_success / total_tests * 100:.1f}%")
    print("=" * 70)


def test_single_value(param_name, target_value):
    """测试单个值"""
    cfg = PARAM_CONFIG[param_name]
    print(f"\n测试 {param_name} = {target_value} {cfg['unit']}")

    container = get_param_container(param_name)
    old_value = get_current_display_value(container)
    print(f"当前值: {old_value}")

    success, new_value = set_param_value(param_name, target_value)

    if success:
        print(f"✅ 设置成功! 新值: {new_value}")
    else:
        print(f"❌ 设置失败! 预期: {target_value}, 实际: {new_value}")

    return success


if __name__ == "__main__":
    try:
        driver.get(BASE_URL)
        print(f"🌐 打开: {BASE_URL}")
        time.sleep(3)

        print("\n请选择模式:")
        print("  1 - 完整随机测试")
        print("  2 - 单值测试(Gain)")
        print("  3 - 单值测试(Frequency)")
        print("  4 - 单值测试(Q)")

        choice = input("请输入 (1/2/3/4): ").strip()

        if choice == "1":
            run_full_test()
        elif choice == "2":
            val = float(input("Gain值 (-15~15): "))
            test_single_value("Gain", val)
        elif choice == "3":
            val = int(input("Frequency值 (20~20000): "))
            test_single_value("Frequency", val)
        elif choice == "4":
            val = float(input("Q值 (0.4~30): "))
            test_single_value("Q", val)
        else:
            run_full_test()

    except Exception as e:
        print(f"异常: {e}")
        import traceback

        traceback.print_exc()

    finally:
        input("\n按回车关闭...")
        driver.quit()


