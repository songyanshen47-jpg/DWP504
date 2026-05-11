from selenium import webdriver
from selenium.webdriver.common.by import By
import time

BASE_URL = "http://192.168.66.123/#/Home"

# =============================================================================
# 工具：直接获取页面上 4 个静音图标
# =============================================================================
def get_all_mute_icons(driver):
    return driver.find_elements(By.CSS_SELECTOR, "img[class*='DbSelector-module_sound-icon']")

# =============================================================================
# 读取状态 + 打印是 静音 / 非静音
# =============================================================================
def get_and_show_status(driver, output_num, step_name):
    icons = get_all_mute_icons(driver)
    icon = icons[output_num - 1]

    # 滚动到元素
    driver.execute_script("arguments[0].scrollIntoView(true);", icon)
    time.sleep(0.5)

    src = icon.get_attribute("src")

    # ======================
    # 判断静音/非静音
    # ======================
    if "Z62HzDG" in src:  # 你静音图标的特征
        status = "静音"
    else:
        status = "非静音"

    print(f"📌 Output{output_num} {step_name}：【{status}】")
    return status, src

# =============================================================================
# 点击静音开关
# =============================================================================
def click_mute(driver, output_num):
    icons = get_all_mute_icons(driver)
    icon = icons[output_num - 1]
    driver.execute_script("arguments[0].scrollIntoView(true);", icon)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", icon)
    print(f"👉 Output{output_num} 已点击\n")

# =============================================================================
# 主测试：4个通道轮流 → 读状态 → 点击 → 读状态 → 判断
# =============================================================================
def test_all_output():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(BASE_URL)
    time.sleep(5)

    success = 0
    fail = 0

    print("=" * 60)
    print("📌 开始测试 Output1 / Output2 / Output3 / Output4")
    print("=" * 60)

    # 轮流测试 1、2、3、4
    for i in [1, 2, 3, 4]:
        print(f"\n=====================================")
        print(f"🎯 测试 Output{i}")
        print(f"=====================================")

        # 1. 读取【点击前】状态
        before_status, before_src = get_and_show_status(driver, i, "点击前状态")

        # 2. 点击
        time.sleep(1)
        click_mute(driver, i)
        time.sleep(2)

        # 3. 读取【点击后】状态
        after_status, after_src = get_and_show_status(driver, i, "点击后状态")

        # 4. 判断是否切换成功
        if before_status != after_status:
            print(f"✅ Output{i} 切换【成功】")
            success += 1
        else:
            print(f"❌ Output{i} 切换【失败】")
            fail += 1

    # 最终结果
    print("\n" + "=" * 60)
    print("📊 测试结果统计")
    print(f"✅ 成功：{success} 个")
    print(f"❌ 失败：{fail} 个")

    if success == 4:
        print("\n🎉 测试结论：全部通道正常！")
    else:
        print("\n⚠️ 测试结论：部分通道异常！")

    input("\n按回车关闭 → ")
    driver.quit()

if __name__ == "__main__":
    test_all_output()