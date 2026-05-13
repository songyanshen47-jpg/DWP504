import re
import time
from playwright.sync_api import Page, expect, sync_playwright
def test_example() -> None:
  with sync_playwright() as p:
            # 1.初始化流量器
    browser = p.chromium.launch(headless=False, slow_mo=800)
    context = browser.new_context()
    page = context.new_page()
    print("GPIO自动化测试准备开始")

    try:
        page.goto("http://192.168.66.123/#/Home")
        page.locator("div").filter(has_text=re.compile(r"^Output$")).click()
        page.get_by_text("Input 1").click()
        page.get_by_text("Input 2").click()
        page.get_by_text("Input 3").click()
        page.get_by_text("Input 4").click()
        page.get_by_text("Generator").click()
        page.get_by_text("Delay").first.click()
        page.get_by_text("Feet", exact=True).click()
        page.locator("div:nth-child(4) > .Delay-module_plus__rEO3vmOOiYkZhq5pYCiO").click()
        page.locator("div:nth-child(4) > .Delay-module_plus__rEO3vmOOiYkZhq5pYCiO").click()
        page.get_by_text("Meter", exact=True).click()
        page.locator("div:nth-child(5) > .Delay-module_pre__HetWO806GnwZCThb39Wa").click()
        page.locator("div:nth-child(5) > .Delay-module_pre__HetWO806GnwZCThb39Wa").click()
        page.get_by_text("Equalizer").first.click()
        page.get_by_text("Edit").click()
        # 循环点击数字 1 到 10
        for i in range(2, 11):
            # 定位包含特定数字的 span 标签，类名包含 tab-index
            page.locator(f"span[class*='Edit-module_tab-index']:has-text('{i}')").click()
            # 这种方式会寻找页面上文本内容“刚好”是数字的元素
            # for i in range(2, 11):
            #     page.get_by_text(str(i), exact=True).click()
        page.locator("div:nth-child(12) > .Switch-module_Switch__raFYyThR9KYf_1SSrLZ4").click()
        page.get_by_text("OK").click()
        page.get_by_text("Output 3").click()
        page.get_by_text("Input 1").click()
        page.get_by_text("Input 2").click()
        page.get_by_text("Input 3").click()
        page.get_by_text("Input 4").click()
        page.get_by_text("Generator").click()
        page.get_by_text("Delay").nth(4).click()
        page.locator(".Delay-module_plus__rEO3vmOOiYkZhq5pYCiO").first.click()
        page.locator(".Delay-module_plus__rEO3vmOOiYkZhq5pYCiO").first.click()
        page.get_by_text("Feet", exact=True).click()
        page.get_by_text("Meter", exact=True).click()
        page.locator("div:nth-child(5) > .Delay-module_pre__HetWO806GnwZCThb39Wa").click()
        page.get_by_text("Equalizer").nth(2).click()
        page.locator(".Switch-module_Switch__raFYyThR9KYf_1SSrLZ4").click()
        page.locator("div:nth-child(3) > div:nth-child(2) > div:nth-child(4) > div > .Submenu-module_arrowBox__x51srRwrcs0t6HtdVXhx > img").click()
        page.get_by_text("Crossover").nth(2).click()
        page.locator(".Switch-module_Switch__raFYyThR9KYf_1SSrLZ4").click()
        page.locator(".Crossover-module_arrow-box__PC4jiqytNmEJd7iLlXcg").first.click()
        page.get_by_text("Butterworth 12dB/octave").click()
        page.locator(".Crossover-module_arrow-box__PC4jiqytNmEJd7iLlXcg").first.click()
        page.get_by_text("Bessel 48dB/octave").click()
        page.locator("div:nth-child(3) > .Crossover-module_Selector-box__DCrHyFyEc9Jhpe6On9RQ > .Crossover-module_Selector__oVmY7a2JUQqxVK15tduU > .Crossover-module_plus__gbCMWVJG8jcqWo_pjeMO > img").click()
        page.locator("div:nth-child(3) > .Crossover-module_Selector-box__DCrHyFyEc9Jhpe6On9RQ > .Crossover-module_Selector__oVmY7a2JUQqxVK15tduU > .Crossover-module_plus__gbCMWVJG8jcqWo_pjeMO > img").click()
        page.locator("div:nth-child(3) > .Crossover-module_Selector-box__DCrHyFyEc9Jhpe6On9RQ > .Crossover-module_Selector__oVmY7a2JUQqxVK15tduU > .Crossover-module_plus__gbCMWVJG8jcqWo_pjeMO > img").click()
        page.locator("div:nth-child(3) > .Crossover-module_wave-type__DNS1EAr5J5QyTyn3om3M > .Crossover-module_arrow-box__PC4jiqytNmEJd7iLlXcg").click()
        page.get_by_role("menu").get_by_text("Linkwitz-Riley 24dB/octave").click()
        page.get_by_text("Speaker Eq").nth(2).click()
        page.locator(".Switch-module_Switch__raFYyThR9KYf_1SSrLZ4").click()
        page.get_by_text("FIR").nth(2).click()
        page.locator(".Switch-module_Switch__raFYyThR9KYf_1SSrLZ4").click()
        page.get_by_text("Speaker Delay").nth(2).click()
        page.locator(".SpeakerDelay-module_plus__aIxvNyqdMBgnbHez2Vgp > img").first.dblclick()
        page.locator(".SpeakerDelay-module_plus__aIxvNyqdMBgnbHez2Vgp > img").first.click()
        page.locator(".SpeakerDelay-module_plus__aIxvNyqdMBgnbHez2Vgp > img").first.click()
        page.get_by_text("Feet", exact=True).click()
        page.get_by_text("Meter", exact=True).click()
        page.locator("div:nth-child(5) > .SpeakerDelay-module_pre__ix6EgQkIz2ge_6_SRlmr > img").click()
        page.get_by_text("Polarity").nth(2).click()
        page.get_by_text("180°").click()
        page.get_by_text("Limiter").nth(2).click()
        page.locator("div").filter(has_text=re.compile(r"^Output Mode$")).nth(5).click()
        # 1. 定位显示当前模式的元素（假设它在 Limiter 页面某个位置）
        # 注意：你需要根据实际 HTML 找到显示“当前选定值”的那个标签
        # 1. 直接定位那个带有 "selected" 样式的 active 元素
        # 这个类名 OutputMode-module_selected__... 是唯一的标识
        active_locator = page.locator("[class*='OutputMode-module_selected']")

        # 2. 获取这个 active 元素的文字
        if active_locator.count() > 0:
            current_text = active_locator.first.inner_text().strip()
            print(f"🎯 当前实际选中的模式是: '{current_text}'")
        else:
            current_text = ""
            print("⚠️ 未找到已选中的模式")

        # 3. 进行精准判断
        if current_text == "Lo-Z":
            print("✨ 当前已经是 Lo-Z 模式，跳过切换。")
        else:
            print(f"🚀 当前是 '{current_text}'，正在执行切换至 Lo-Z...")

            # 点击那个文本正好是 "Lo-Z" 的 div 块
            # 注意：这里我们直接点选项，不需要先点开什么，因为选项就在页面上
            page.locator("[class*='OutputMode-module_radio-box']").get_by_text("Lo-Z", exact=True).click()

            print("✅ 切换指令已发送")

    except Exception as e:
            print(f"\n❌ 测试失败: {e}")
              # 报错时自动截图保留证据
            page.screenshot(path="security_error.png")
            raise e

    finally:
            time.sleep(2)  # 留点时间看一眼最后的结果
            browser.close()

if __name__ == "__main__":
    test_example()