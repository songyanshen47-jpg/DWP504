from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()
BASE_URL = "http://192.168.66.123/#/Input/Generator"
wait = WebDriverWait(driver, 10)
driver.get(BASE_URL)
time.sleep(6)

MODE_LIST = ["SINE", "PINK"]

# 这里虽然给的地址是对的但是因为浏览器会有一个自动刷新，会默认切换为原地址input1首页，所以后续应该搭配swift中的导航代码进行实现
def get_current_mode_via_class():
    """通过class读取当前选中的模式"""
    try:
        selected_loc = (By.XPATH, "//div[contains(@class,'RadiosBlock-module_selected')]")
        selected_ele = wait.until(EC.presence_of_element_located(selected_loc))
        mode_name = selected_ele.text.strip()
        print(f"[class读取] 当前模式：{mode_name}")
        return mode_name
    except Exception as e:
        print(f"[class读取] 失败：{str(e)[:40]}")
        return None


def get_current_mode_via_js():
    """通过JS读取实际激活状态（可能是data属性或aria-selected）"""
    try:
        script = """
        // 尝试多种方式找到当前选中的模式
        // 方式1：查找有selected类的
        let selected = document.querySelector('[class*="selected"]');
        if (selected && selected.textContent) {
            return selected.textContent.trim();
        }
        // 方式2：查找aria-selected=true的
        let ariaSelected = document.querySelector('[aria-selected="true"]');
        if (ariaSelected && ariaSelected.textContent) {
            return ariaSelected.textContent.trim();
        }
        return null;
        """
        mode_name = driver.execute_script(script)
        print(f"[JS读取] 当前模式：{mode_name}")
        return mode_name
    except Exception as e:
        print(f"[JS读取] 失败：{str(e)[:40]}")
        return None


def click_mode_via_js(target_mode):
    """真实点击切换模式 - JS触发点击事件"""
    try:
        script = f"""
        let options = document.querySelectorAll('[class*="RadiosBlock-module_col"]');
        for (let opt of options) {{
            if (opt.textContent.trim() === '{target_mode}') {{
                // 触发完整的点击事件序列
                opt.click();
                // 也尝试触发布局事件
                opt.dispatchEvent(new MouseEvent('mousedown', {{bubbles: true}}));
                opt.dispatchEvent(new MouseEvent('mouseup', {{bubbles: true}}));
                opt.dispatchEvent(new Event('change', {{bubbles: true}}));
                return true;
            }}
        }}
        return false;
        """
        result = driver.execute_script(script)
        time.sleep(0.5)
        print(f"[JS点击] 尝试切换至 {target_mode}，结果：{'成功触发' if result else '未找到元素'}")
        return result
    except Exception as e:
        print(f"[JS点击] 异常：{str(e)[:40]}")
        return False


def click_mode_via_selenium(target_mode):
    """使用Selenium原生点击"""
    try:
        options_loc = (By.XPATH, "//div[starts-with(@class,'RadiosBlock-module_col')]")
        options = driver.find_elements(*options_loc)
        for opt in options:
            if opt.text.strip() == target_mode:
                # 滚动到元素位置
                driver.execute_script("arguments[0].scrollIntoView(true);", opt)
                time.sleep(0.5)
                # 原生点击
                opt.click()
                print(f"[Selenium点击] 已点击 {target_mode}")
                return True
    except Exception as e:
        print(f"[Selenium点击] 异常：{str(e)[:40]}")
    return False


def get_mode_state_details():
    """获取详细的模式状态信息，用于调试"""
    try:
        script = """
        let result = {
            selectedText: null,
            allOptions: [],
            selectedClass: null,
            ariaSelected: null
        };

        let options = document.querySelectorAll('[class*="RadiosBlock-module_col"]');
        for (let opt of options) {
            let classes = opt.className;
            let text = opt.textContent.trim();
            let isSelected = classes.includes('selected') || 
                            opt.getAttribute('aria-selected') === 'true';

            result.allOptions.push({
                text: text,
                classes: classes,
                hasSelectedClass: classes.includes('selected'),
                ariaSelected: opt.getAttribute('aria-selected')
            });

            if (isSelected) {
                result.selectedText = text;
                result.selectedClass = classes;
                result.ariaSelected = opt.getAttribute('aria-selected');
            }
        }
        return result;
        """
        return driver.execute_script(script)
    except Exception as e:
        print(f"状态获取失败：{e}")
        return None


# ==================== 主流程 ====================
if __name__ == "__main__":
    print("=" * 70)
    print("模式切换诊断测试")
    print("=" * 70)

    # 先读取界面结构详情
    print("\n【当前界面状态详情】")
    details = get_mode_state_details()
    if details:
        print(f"当前选中文本: {details['selectedText']}")
        print("所有选项:")
        for opt in details['allOptions']:
            print(f"  - {opt['text']}: hasSelectedClass={opt['hasSelectedClass']}, ariaSelected={opt['ariaSelected']}")

    print("\n" + "=" * 70)

    # 测试各种切换方法
    for mode in MODE_LIST:
        print(f"\n【测试切换至 {mode}】")

        # 方法1: 修改class（之前的失败方法）
        print("\n--- 方法1: 修改class ---")
        # 这个方法已知会失败，但留作对比

        # 方法2: JS点击
        print("--- 方法2: JS触发点击 ---")
        click_mode_via_js(mode)
        time.sleep(2)
        after_click_js = get_current_mode_via_js()

        # 方法3: Selenium点击
        print("--- 方法3: Selenium原生点击 ---")
        click_mode_via_selenium(mode)
        time.sleep(2)
        after_click_selenium = get_current_mode_via_js()

        # 最终状态
        print(f"\n最终模式: {after_click_selenium}")

        # 查看class变化
        final_details = get_mode_state_details()
        print(f"最终选中class中的文本: {final_details['selectedText'] if final_details else 'None'}")

        print("-" * 50)

    input("\n按回车关闭浏览器...")
    driver.quit()