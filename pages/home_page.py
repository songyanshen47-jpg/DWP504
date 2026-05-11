from selenium.webdriver.common.by import By
from common.base import BasePage

class HomePage(BasePage):
    # 定位器
    TAB_ITEMS = (By.CSS_SELECTOR, '[class*="index-module_tabbar-item"]')
    ACTIVE_TAB = (By.CSS_SELECTOR, '[class*="index-module_tabbar-item"].active')

    # 动作：点击第 N 个底部 tab
    def click_tab_by_index(self, index):
        tabs = self.find_elements(self.TAB_ITEMS)
        tabs[index].click()

    # 动作：判断当前激活 tab 是否存在
    def is_tab_active(self):
        return self.find_element(self.ACTIVE_TAB) is not None