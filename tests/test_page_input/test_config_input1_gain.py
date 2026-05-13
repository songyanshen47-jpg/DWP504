from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ==================== 配置 ====================
BASE_URL = "http://192.168.66.123/#/Input"

def get_display_value(driver):
    """读取显示的 dB 值"""
    try:
        elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[class*='ScaleSteper-module_display-message']")
            )
        )
        text = elem.text.strip().replace("dB", "").strip()
        return float(text)
    except:
        return None

def set_slider_value(driver, target_value):
    """
    直接设置 Ant Slider 的值
    不依赖 aria-valuenow，直接通过组件实例设置
    """
    try:
        wait = WebDriverWait(driver, 10)
        slider_handle = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[class*='ant-slider-handle']")
            )
        )

        # 直接通过JS调用组件内部方法设置值（这才是Ant Slider正确的更新方式）
        driver.execute_script("""
            const handle = arguments[0];
            const value = arguments[1];

            // 1. 设置 aria-valuenow
            handle.setAttribute('aria-valuenow', value);

            // 2. 直接修改滑块位置样式（left/transform），强制移动
            const min = parseFloat(handle.getAttribute('aria-valuemin'));
            const max = parseFloat(handle.getAttribute('aria-valuemax'));
            const percent = ((value - min) / (max - min)) * 100;

            // 更新 track 宽度
            const track = handle.parentElement.querySelector('.ant-slider-track');
            if (track) {
                track.style.left = '0%';
                track.style.width = `${percent}%`;
            }

            // 更新 handle 位置
            handle.style.left = `${percent}%`;
            handle.style.transform = 'translateX(-50%)';

            // 3. 触发所有必要事件
            handle.dispatchEvent(new Event('mousedown', { bubbles: true }));
            handle.dispatchEvent(new Event('input', { bubbles: true }));
            handle.dispatchEvent(new Event('change', { bubbles: true }));
            handle.dispatchEvent(new Event('mouseup', { bubbles: true }));
        """, slider_handle, target_value)

        time.sleep(2)  # 等待UI完全更新
        return True
    except Exception as e:
        print(f"设置失败: {e}")
        return False

# ==================== 主测试 ====================
def test_slider():
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        driver.get(BASE_URL)
        time.sleep(6)

        print("=" * 65)
        print("🎯 Ant Slider 直接设置值测试")
        print("=" * 65)

        # 读取初始值
        print("\n【步骤1】读取初始值")
        initial = get_display_value(driver)
        print(f"初始值: {initial} dB")

        # 设置目标值（你要的 -15）
        target = -1.4
        print(f"\n【步骤2】设置值为 {target}")
        set_slider_value(driver, target)

        # 读取设置后的值
        print("\n【步骤3】读取设置后的值")
        final = get_display_value(driver)
        print(f"设置后的值: {final} dB")

        # 验证
        print("\n" + "=" * 65)
        if final == target:
            print(f"✅ 测试成功！值已更新为 {target} dB")
        else:
            print(f"❌ 测试失败！目标 {target} dB，实际 {final} dB")
        print("=" * 65)

    except Exception as e:
        print(f"程序异常: {str(e)}")

    finally:
        input("\n按回车关闭浏览器...")
        driver.quit()

if __name__ == "__main__":
    test_slider()