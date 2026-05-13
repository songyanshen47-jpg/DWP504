import time
import re
from csv import excel
from multiprocessing import context

from playwright.sync_api import expect, sync_playwright


def gpio_standby_NC():
   with sync_playwright() as p:
        #1.初始化流量器
       browser = p.chromium.launch(headless=False,slow_mo=800)
       context = browser.new_context()
       page = context.new_page()
       print("GPIO自动化测试准备开始")

       try:
         #导航到目标页面首页
         page.goto("http://192.168.66.123/#/Home")
         expect(page).to_have_url("http://192.168.66.123/#/Home")
         print("成功进入首页")

         page.locator("div").filter(has_text=re.compile(r"^Settings$")).click()
         expect(page).to_have_url(re.compile(r".*/Settings/.*"))
         print("成功进入setting页面")

         page.locator("div").filter(has_text=re.compile(r"^GPIO$")).first.click()
         expect(page).to_have_url(re.compile(".*/GPIO"))
         print("成功进入GPIO设置")

         Standby_NC_btn = page.locator("div").filter(has_text=re.compile(r"^Standby \(NC\)$"))
         Standby_NC_btn.click()
         expect(Standby_NC_btn).to_have_class(re.compile(r".*selected.*"))
         print("已选择Standby NC")

         page.locator("div").filter(has_text=re.compile(r"^Home$")).click()
         expect(page).to_have_url(re.compile(".*/Home"))
         print("已经回到首页")
         power_container = page.locator("div[class*='Home-module_part-content']").filter(has_text="Power")
         expect(power_container).to_contain_text("Power")
         expect(power_container).to_contain_text("Standby")
         print("GPIO_NC测试成功")
         page.locator("div").filter(has_text=re.compile(r"^Settings$")).click()
         expect(page).to_have_url(re.compile(r".*/Settings/.*"))
         print("成功进入setting页面")
         page.locator("div").filter(has_text=re.compile(r"^GPIO$")).first.click()
         expect(page).to_have_url(re.compile(".*/GPIO"))
         print("成功进入GPIO设置")
         Standby_NC_btn = page.locator("div").filter(has_text=re.compile(r"^Off$")).first
         Standby_NC_btn.click()
         expect(Standby_NC_btn).to_have_class(re.compile(r".*selected.*"))
         print("已选择Off")
         page.locator("div").filter(has_text=re.compile(r"^Home$")).click()
         expect(page).to_have_url(re.compile(".*/Home"))
         print("已经回到首页")
         power_container_new = page.locator("div[class*='Home-module_part-content']").filter(has_text="Power")
         power_container_new.click()
         expect(power_container_new).to_contain_text("On")
         print("OFF测试成功")

       except Exception as e:
          print(f"\n❌ 测试失败: {e}")
          # 报错时自动截图保留证据
          page.screenshot(path="security_error.png")
          raise e

       finally:
          time.sleep(2)  # 留点时间看一眼最后的结果
          browser.close()

if __name__ == "__main__":
    gpio_standby_NC()