import asyncio
import os
from playwright.async_api import async_playwright

FILE_PATH = r"d:\tonwel\21087\Desktop\工作\.net\dwp\客户版本\Firmware package_MXP5.4DSP_260509\MPX5.4DSP_WebApp_Ver1.2.3_20260509_Alpha.dat"
BASE_URL = "http://192.168.66.123/#/Settings"


async def run_update_process(page):
    try:
        # 1. 访问首页并确保状态稳定
        print("正在进入首页...")
        await page.goto(BASE_URL)
        await page.wait_for_load_state("domcontentloaded")

        # 2. 导航：点击左侧菜单的 Device
        # 使用更稳健的选择器，并等待元素可见
        device_menu = page.locator(".Submenu-module_MenuItem__K97C_n6GtoQFOPPG9GRF", has_text="Device")
        await device_menu.wait_for(state="visible")
        await device_menu.click()
        print("已进入 Device 设置页面")

        # 3. 点击页面主按钮 [Update]
        update_trigger = page.locator(".Device-module_update-btn__ZH5_9dRpigoCkqB61fdt")
        await update_trigger.wait_for(state="visible")
        await update_trigger.click()

        # 4. 选择文件
        async with page.expect_file_chooser() as fc_info:
            await page.click("text=Options Folder")
        file_chooser = await fc_info.value
        await file_chooser.set_files(FILE_PATH)
        print("固件文件已加载")

        # 5. 点击弹窗内的 [Update] 按钮
        await page.locator(".Update-module_footer__Q2TpEY9lvcnIYAZ_qrQn >> text=Update").click()

        # 6. 处理二次确认 Warning 弹窗并点击 OK
        ok_btn = page.get_by_role("button", name="OK")
        await ok_btn.wait_for(state="visible")
        await ok_btn.click()

        print("✔ 更新指令已成功发出！")
        return True

    except Exception as e:
        print(f"❌ 流程中断: {e}")
        print("正在尝试刷新并重新开始...")
        await page.reload()
        await asyncio.sleep(3)
        return await run_update_process(page)


async def main():
    async with async_playwright() as p:
        # 重点修改点：
        # 1. args 添加 --high-dpi-support=1 和 --force-device-scale-factor=1 解决缩放问题
        # 2. 启动时使用 maximized 模式
        browser = await p.chromium.launch(
            headless=False,
            args=['--start-maximized', '--high-dpi-support=1', '--force-device-scale-factor=1']
        )

        # 3. 重点：设置 no_viewport=True，这会让页面填充整个浏览器窗口，不再有奇怪的滚动条
        context = await browser.new_context(no_viewport=True)
        page = await context.new_page()

        await run_update_process(page)

        print("脚本已完成，浏览器将保持打开状态以便观察。")
        # 保持运行，不关闭浏览器
        while True:
            await asyncio.sleep(3600)


if __name__ == "__main__":
    if not os.path.exists(FILE_PATH):
        print(f"路径错误，文件不存在：{FILE_PATH}")
    else:
        asyncio.run(main())