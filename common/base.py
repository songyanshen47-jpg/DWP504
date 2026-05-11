from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # 点击元素
    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    # 获取所有元素
    def find_elements(self, locator):
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    # 获取激活的元素
    def find_element(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))