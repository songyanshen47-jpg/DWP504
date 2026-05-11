import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# ==================== 配置与映射表 ====================
BASE_URL = "http://192.168.66.123/#/Home"

# 映射表：(dB值, 对应HTML中的百分比位置)
# 注意：这些百分比来源于你提供的 HTML 属性 left: XX%
VOLUME_MAP = [
    (-80.0, 0.0),  # 假设起点
    (-48.0, 13.6033),
    (-24.0, 39.8568),
    (-12.0, 63.7843),
    (-6.0, 80.0226),
    (-3.0, 89.4942),
    (0.0, 100.0)
]


def db_to_physical_percent(db):
    """使用分段线性插值计算 dB 对应的物理百分比位置"""
    if db <= VOLUME_MAP[0][0]: return VOLUME_MAP[0][1]
    if db >= VOLUME_MAP[-1][0]: return VOLUME_MAP[-1][1]

    for i in range(len(VOLUME_MAP) - 1):
        db_start, p_start = VOLUME_MAP[i]
        db_end, p_end = VOLUME_MAP[i + 1]

        if db_start <= db <= db_end:
            # 区间内插值计算
            ratio = (db - db_start) / (db_end - db_start)
            return p_start + (ratio * (p_end - p_start))
    return 0


# ==================== 工具函数 ====================

def get_current_ui_db(driver, card):
    """从 UI 文本抓取当前的 dB 数值"""
    try:
        # 定位显示数值的容器 (ScaleSteper-module_display-message)
        element = card.find_element(By.CSS_SELECTOR, "div[class*='display-message']")
        text = element.text.strip()
        match = re.search(r"(-?\d+\.?\d*)", text)
        return float(match.group(1)) if match else None
    except:
        return None


def drag_to_db(driver, card, target_db):
    try:
        slider = card.find_element(By.CSS_SELECTOR, ".ant-slider")
        handle = card.find_element(By.CSS_SELECTOR, ".ant-slider-handle")
        rail = card.find_element(By.CSS_SELECTOR, ".ant-slider-rail")

        # 1. 获取轨道精确宽度和起始 X
        # 使用 get_attribute('offsetWidth') 有时比 .size 更准
        slider_width = rail.size['width']

        # 核心改进：先把滑块拖到最左侧（0%），确定物理起始点
        actions = ActionChains(driver)
        actions.click_and_hold(handle).move_to_element_with_offset(rail, 0, 5).release().perform()
        time.sleep(0.5)

        # 记录 0% 时的 Handle 中心坐标
        zero_x = handle.location['x'] + (handle.size['width'] / 2)

        # 2. 计算目标 dB 应该对应的物理百分比
        target_percent = db_to_physical_percent(target_db)

        # 3. 计算相对于零点的总偏移像素
        total_offset_from_zero = slider_width * (target_percent / 100)

        # 4. 执行二次移动：从当前位置（零点）移动到目标位置
        # 注意：ActionChains 在 release 后，下一次 click_and_hold 是从 handle 当前位置开始的
        actions.click_and_hold(handle).move_by_offset(total_offset_from_zero, 0).release().perform()

        print(f"  > 目标 {target_db}dB | 百分比 {target_percent:.2f}% | 相对零点移动 {total_offset_from_zero:.1f}px")

        return True
    except Exception as e:
        print(f"  ❌ 拖拽异常: {e}")
        return False


# ==================== 主测试流程 ====================

def run_precision_test():
    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        driver.get(BASE_URL)
        wait = WebDriverWait(driver, 10)

        # 定位 OUTPUT 1 卡片
        card_xpath = "//div[contains(@class, 'Card-module_Card')][descendant::span[text()='OUTPUT 1']]"
        card = wait.until(EC.presence_of_element_located((By.XPATH, card_xpath)))

        # 确保元素可见
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
        time.sleep(1)

        # 测试用例：涵盖各个刻度区间
        test_points = [-80.0, -60.0, -48.0, -36.0, -24.0, -18.0, -12.0, -9.0, -6.0, -4.5, -3.0, 0.0]

        print(f"{'预期dB':>8} | {'实际UI显示':>10} | {'误差':>8} | {'结论'}")
        print("-" * 50)

        for target in test_points:
            drag_to_db(driver, card, target)
            time.sleep(1.0)  # 等待 UI 刷新

            actual = get_current_ui_db(driver, card)

            if actual is not None:
                error = abs(actual - target)
                status = "✅ PASS" if error <= 0.5 else "❌ FAIL"
                print(f"{target:8.1f} | {actual:10.1f} | {error:8.1f} | {status}")
            else:
                print(f"{target:8.1f} | {'READ ERR':10} | {'-':8} | ❌")

    finally:
        input("\n测试完成，按回车退出...")
        driver.quit()


if __name__ == "__main__":
    run_precision_test()