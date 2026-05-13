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

BASE_URL = "http://192.168.66.123/#/Output/Output1"
wait = WebDriverWait(driver, 10)
driver.get(BASE_URL)
time.sleep(5)


# ==================== 核心函数 ====================

def get_active_submenu_item():
    """
    【最终修复版】混合策略验证：
    1. 优先通过 URL 路径精确匹配（解决类名不稳定问题）
    2. 如果 URL 匹配失败或模糊，尝试读取右侧主内容区的大标题（兜底方案）
    """
    url = driver.current_url.lower()

    # --- 策略 1: URL 路径匹配 (注意顺序：从长/具体 到 短/通用) ---

    # 二级菜单项 (Speaker Preset 下的子项)
    # 假设 URL 结构为 .../SpeakerPreset/Preset, .../SpeakerPreset/Crossover 等
    if "/outputmode" in url or "/output-mode" in url:
        return "Output Mode"
    elif "/limiter" in url:
        return "Limiter"
    elif "/polarity" in url:
        return "Polarity"
    elif "/speakerdelay" in url or "/speaker-delay" in url:
        return "Speaker Delay"
    elif "/fir" in url:
        return "FIR"
    elif "/speakereq" in url or "/speaker-eq" in url:
        return "Speaker Eq"
    elif "/crossover" in url:
        return "Crossover"
    elif "/preset" in url and "/speakerpreset" not in url:
        # 只有当 URL 包含 /preset 但 不包含 /speakerpreset 时，才认为是独立的 Preset?
        # 不，通常子项 URL 会包含父级路径。
        # 修正：如果 URL 结尾是 /preset，且前面有 speakerpreset，它仍然是子项 Preset
        # 这里的关键是：不要让它匹配到下面的 "Speaker Preset"
        pass  # 继续往下走，让更具体的逻辑处理，或者直接用下面的兜底

    # 一级菜单项
    if "/routing" in url:
        return "Routing"
    elif "/delay" in url:
        return "Delay"
    elif "/equalizer" in url or "/eq" in url:
        return "Equalizer"

    # 特殊处理：如果 URL 包含 SpeakerPreset，我们需要区分是父级还是子级
    if "/speakerpreset" in url:
        # 如果 URL 以 /speakerpreset 结尾，或者是 .../SpeakerPreset (后面没东西)，则是父级
        # 如果 URL 是 .../SpeakerPreset/Preset，则是子级 Preset
        if url.endswith("/speakerpreset") or url.endswith("/speakerpreset/"):
            return "Speaker Preset"
        else:
            # 否则，它是子项。由于上面已经拦截了 Crossover/FIR 等具体子项，
            # 剩下的最可能的就是 "Preset" (因为它的名字和父级很像，容易混淆)
            # 或者我们可以直接返回 URL 最后一段
            path_parts = url.split('/')
            last_part = path_parts[-1].replace('-', ' ').title()  # 简单转换 outputmode -> Outputmode
            if last_part == "Speakerpreset":
                return "Speaker Preset"
            elif last_part == "Preset":
                return "Preset"
            else:
                return last_part  # 尝试返回最后一段作为名称

    # --- 策略 2: 兜底方案 - 读取右侧内容区标题 ---
    # 如果 URL 匹配不出来，或者你想双保险，可以读取页面右侧大标题
    try:
        # 常见的标题选择器，根据你的实际 HTML 调整
        # 例如: <h1>Routing</h1> 或 <div class="Card-header">Routing</div>
        # 这里尝试几个常见的选择器
        title_selectors = [
            ".Card-header-title",
            ".page-title",
            "h1.page-header",
            "//div[contains(@class, 'Card')]//h1",
            "//div[contains(@class, 'Card')]//span[@class='title']"
        ]

        for selector in title_selectors:
            try:
                if selector.startswith("//"):
                    elem = driver.find_element(By.XPATH, selector)
                else:
                    elem = driver.find_element(By.CSS_SELECTOR, selector)

                text = elem.text.strip()
                if text and len(text) > 0:
                    # 过滤掉一些无关文本
                    if text not in ["Output 1", ""]:
                        return text
            except:
                continue
    except Exception as e:
        pass

    return None


def click_menu_item(target_name):
    """
    通用点击函数
    """
    try:
        locator = (By.XPATH, f"//span[normalize-space()='{target_name}']")
        btn = wait.until(EC.element_to_be_clickable(locator))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", btn)
        return True
    except Exception as e:
        print(f"   ❌ 点击 '{target_name}' 失败: {str(e)[:80]}")
        return False


def verify_switch(expected_name, max_retries=3):
    """
    验证切换是否成功
    """
    for i in range(max_retries):
        time.sleep(0.5)
        current = get_active_submenu_item()
        # 打印调试信息，方便你看看到底读到了什么
        # print(f"      [Debug] Expected: '{expected_name}', Current: '{current}'")

        if current == expected_name:
            return True, current
    return False, get_active_submenu_item()


# ==================== 主流程 ====================

if __name__ == "__main__":
    print("=" * 70)
    print("PROEL Output1 自动化测试：处理嵌套菜单 (Speaker Preset)")
    print("=" * 70)

    all_passed = True

    # ---------------------------------------------------------
    # 第一阶段：测试普通一级菜单
    # ---------------------------------------------------------
    level_1_items = ["Routing", "Delay", "Equalizer"]

    for item in level_1_items:
        print(f"\n>>> 【步骤 1】切换到一级菜单: '{item}'")
        if not click_menu_item(item):
            all_passed = False
            continue
        success, actual = verify_switch(item)
        if success:
            print(f"   ✅ 验证通过：当前激活 '{actual}'")
        else:
            print(f"    验证失败：预期 '{item}'，实际 '{actual}'")
            all_passed = False

    # ---------------------------------------------------------
    # 第二阶段：测试 "Speaker Preset" 及其子项
    # ---------------------------------------------------------
    print("\n" + "-" * 70)
    print(">>> 【步骤 2】处理嵌套菜单: 'Speaker Preset'")
    print("-" * 70)

    parent_menu = "Speaker Preset"
    child_items = ["Preset", "Crossover", "Speaker Eq", "FIR", "Speaker Delay", "Polarity", "Limiter", "Output Mode"]

    print(f"\n    动作：点击父菜单 '{parent_menu}' 以展开子列表...")
    if not click_menu_item(parent_menu):
        print("   ❌ 无法展开父菜单，跳过后续子项测试")
        all_passed = False
    else:
        time.sleep(1.0)

        for child in child_items:
            print(f"\n   >>> 子步骤：切换到子项 '{child}'")

            if not click_menu_item(child):
                print(f"      ⚠️ 点击子项 '{child}' 失败")
                all_passed = False
                continue

            success, actual = verify_switch(child)

            if success:
                print(f"      ✅ 验证通过：成功切换到 '{child}'")
            else:
                print(f"      ❌ 验证失败：预期 '{child}'，实际 '{actual}'")
                # 如果是 Preset 失败，特别提示检查 URL
                if child == "Preset" and actual == "Speaker Preset":
                    print(
                        f"      💡 提示：请检查 URL 是否以 '/SpeakerPreset/Preset' 结尾，并确认 get_active_submenu_item 中的逻辑。")
                all_passed = False

    # ---------------------------------------------------------
    # 总结
    # ---------------------------------------------------------
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 所有导航切换测试通过！")
    else:
        print("💥 部分测试失败，请检查上方日志")
    print("=" * 70)

    input("\n按回车退出...")
    driver.quit()
