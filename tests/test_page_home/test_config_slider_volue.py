import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# ==================== 配置 ====================
BASE_URL = "http://192.168.66.123/#/Home"


def get_output_card(driver, output_name="OUTPUT 1", timeout=10):
    """定位特定的 Output 卡片容器"""
    xpath = f"//div[contains(@class, 'Card-module_Card')][descendant::span[text()='{output_name}']]"
    try:
        card = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        print(f"  ✅ 找到 {output_name} 卡片")
        return card
    except Exception as e:
        print(f"  ❌ 无法找到 {output_name} 卡片: {e}")
        return None


def get_volume_display(driver, card_element):
    """在指定的卡片容器内查找可点击的音量显示元素"""
    try:
        display = card_element.find_element(
            By.CSS_SELECTOR, "div[class*='DbSelector'] div[class*='display-message']"
        )
        text = display.text.strip()
        print(f"  📊 当前音量: {text}")
        return display
    except Exception as e:
        print(f"  ❌ 未找到音量显示元素: {e}")
        return None


def get_current_volume(driver, output_name="OUTPUT 1"):
    """获取指定 Output 的当前音量值"""
    card = get_output_card(driver, output_name, timeout=5)
    if not card:
        return None

    display = get_volume_display(driver, card)
    if not display:
        return None

    text = display.text.strip()
    match = re.search(r"(-?\d+(?:\.\d+)?)", text)
    if match:
        return float(match.group(1))
    return None


def set_volume_value(driver, output_name, target_db):
    """设置指定 Output 的音量值"""
    try:
        # 1. 按 ESC 关闭可能存在的旧弹窗
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(0.3)

        # 2. 定位卡片容器
        card = get_output_card(driver, output_name)
        if not card:
            return False

        # 3. 定位音量显示元素
        display_element = get_volume_display(driver, card)
        if not display_element:
            return False

        current_text = display_element.text.strip()
        print(f"  🎯 目标值: {target_db} dB")

        # 4. 滚动并点击
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", display_element)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", display_element)
        print(f"  ✅ 已点击，等待弹窗...")
        time.sleep(0.8)

        # 5. 查找输入框
        input_box = None
        selectors = [
            "div.ant-popover:not([style*='display: none']) input.ant-input-number-input",
            "input.ant-input-number-input",
        ]

        for selector in selectors:
            try:
                input_box = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                if input_box and input_box.is_displayed():
                    print(f"  ✅ 找到输入框")
                    break
            except:
                continue

        if not input_box:
            print(f"  ❌ 未找到输入框")
            return False

        # 6. 清空并输入新值
        input_box.send_keys(Keys.CONTROL + "a")
        time.sleep(0.1)
        input_box.send_keys(str(target_db))
        print(f"  ✅ 已输入: {target_db}")
        time.sleep(0.3)

        # 7. 按回车确认
        input_box.send_keys(Keys.ENTER)
        print(f"  ✅ 已确认")
        time.sleep(0.8)

        # 8. 按 ESC 关闭弹窗
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()

        # 9. 验证
        actual_value = get_current_volume(driver, output_name)
        print(f"  📊 验证结果: {actual_value} dB")

        return True

    except Exception as e:
        print(f"  ❌ 设置失败: {e}")
        return False


def test_custom_volumes():
    """
    自定义音量设置测试
    可以随意修改每个 OUTPUT 的目标音量值
    """
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    try:
        driver.get(BASE_URL)
        print("等待页面加载...")
        time.sleep(8)

        print("=" * 70)
        print("🎯 自定义 OUTPUT 音量自动化测试")
        print("=" * 70)

        # ==================== 在这里修改你的目标音量值 ====================
        # 格式: ("OUTPUT 通道", 目标音量值)
        test_plan = [
            ("OUTPUT 1", 0.0),  # OUTPUT 1 调到 0 dB
            ("OUTPUT 2", -9.0),  # OUTPUT 2 调到 -9 dB
            ("OUTPUT 3", -80.0),  # OUTPUT 3 调到 -80 dB（最低音量）
            ("OUTPUT 4", -52.0),  # OUTPUT 4 调到 -52 dB
        ]
        # ================================================================

        # 先获取所有 OUTPUT 的初始值
        print("\n📊 初始状态:")
        for output in ["OUTPUT 1", "OUTPUT 2", "OUTPUT 3", "OUTPUT 4"]:
            initial = get_current_volume(driver, output)
            print(f"  {output}: {initial} dB")

        success_count = 0
        fail_count = 0

        print("\n" + "=" * 70)
        print("【开始设置】")
        print("=" * 70)

        for i, (output_name, target_db) in enumerate(test_plan, 1):
            print(f"\n{'=' * 50}")
            print(f"第 {i} 次设置: {output_name} = {target_db} dB")
            print(f"{'=' * 50}")

            if set_volume_value(driver, output_name, target_db):
                success_count += 1
                print(f"  ✨ {output_name} 设置成功")
            else:
                fail_count += 1
                print(f"  💥 {output_name} 设置失败")

            time.sleep(1)

        # 最终验证所有 OUTPUT 的值
        print("\n" + "=" * 70)
        print("📊 最终状态（验证）")
        print("=" * 70)

        for output in ["OUTPUT 1", "OUTPUT 2", "OUTPUT 3", "OUTPUT 4"]:
            final_value = get_current_volume(driver, output)
            print(f"  {output}: {final_value} dB")

        # 测试总结
        print("\n" + "=" * 70)
        print("测试总结")
        print("=" * 70)
        print(f"  成功: {success_count}")
        print(f"  失败: {fail_count}")
        print(f"  总数: {len(test_plan)}")

        if fail_count == 0:
            print("  ✅ 全部通过！")
        else:
            print("  ❌ 部分失败")
        print("=" * 70)

    except Exception as e:
        print(f"异常：{e}")
        import traceback
        traceback.print_exc()

    finally:
        input("\n按回车关闭浏览器...")
        driver.quit()


def test_batch_volumes():
    """
    批量测试模式：可以一次性测试多组配置
    """
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    try:
        driver.get(BASE_URL)
        print("等待页面加载...")
        time.sleep(8)

        print("=" * 70)
        print("🎯 批量音量配置测试")
        print("=" * 70)

        # ==================== 批量测试配置 ====================
        # 可以定义多组配置，依次执行
        batch_configs = [
            {
                "name": "配置1 - 标准测试",
                "settings": [
                    ("OUTPUT 1", 0.0),
                    ("OUTPUT 2", -9.0),
                    ("OUTPUT 3", -80.0),
                    ("OUTPUT 4", -52.0),
                ]
            },
            {
                "name": "配置2 - 全通道统一",
                "settings": [
                    ("OUTPUT 1", -24.0),
                    ("OUTPUT 2", -24.0),
                    ("OUTPUT 3", -24.0),
                    ("OUTPUT 4", -24.0),
                ]
            },
            {
                "name": "配置3 - 渐进式",
                "settings": [
                    ("OUTPUT 1", -12.0),
                    ("OUTPUT 2", -24.0),
                    ("OUTPUT 3", -36.0),
                    ("OUTPUT 4", -48.0),
                ]
            },
            {
                "name": "配置4 - 极值测试",
                "settings": [
                    ("OUTPUT 1", -80.0),
                    ("OUTPUT 2", 0.0),
                    ("OUTPUT 3", -80.0),
                    ("OUTPUT 4", 0.0),
                ]
            },
        ]
        # ======================================================

        # 先获取初始值
        print("\n📊 初始状态:")
        for output in ["OUTPUT 1", "OUTPUT 2", "OUTPUT 3", "OUTPUT 4"]:
            initial = get_current_volume(driver, output)
            print(f"  {output}: {initial} dB")

        total_success = 0
        total_fail = 0

        for config_idx, config in enumerate(batch_configs, 1):
            print(f"\n{'=' * 70}")
            print(f"【{config_idx}】{config['name']}")
            print(f"{'=' * 70}")

            for output_name, target_db in config["settings"]:
                print(f"\n  设置 {output_name} = {target_db} dB")

                if set_volume_value(driver, output_name, target_db):
                    total_success += 1
                    print(f"    ✅ 成功")
                else:
                    total_fail += 1
                    print(f"    ❌ 失败")

                time.sleep(0.5)

            # 每完成一组配置，显示当前状态
            print(f"\n  📊 当前状态:")
            for output in ["OUTPUT 1", "OUTPUT 2", "OUTPUT 3", "OUTPUT 4"]:
                val = get_current_volume(driver, output)
                print(f"    {output}: {val} dB")

            time.sleep(1)

        print("\n" + "=" * 70)
        print("测试总结")
        print("=" * 70)
        print(f"  总操作次数: {total_success + total_fail}")
        print(f"  成功: {total_success}")
        print(f"  失败: {total_fail}")
        print("=" * 70)

    except Exception as e:
        print(f"异常：{e}")
        import traceback
        traceback.print_exc()

    finally:
        input("\n按回车关闭浏览器...")
        driver.quit()


if __name__ == "__main__":
    print("请选择测试模式:")
    print("  1 - 自定义单组音量设置")
    print("  2 - 批量多组配置测试")

    choice = input("请输入选择 (1/2): ")

    if choice == "2":
        test_batch_volumes()
    else:
        test_custom_volumes()