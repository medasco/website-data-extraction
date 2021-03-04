
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as ec
from time import sleep
from wsm.config import SPIDERS_PATH, PROJECT_PATH, CSV_PATH, REF_PATH, DOWNLOAD_PATH


class ChromeDriver(webdriver.Chrome):

    def __init__(self, country="Default"):
        options = webdriver.ChromeOptions()
        prefs = {"download.default_directory": DOWNLOAD_PATH + country}
        # options.set_headless(headless=True)
        options.add_experimental_option("prefs", prefs)
        
        # 'Allow Notifications' Popup Window: Pass the argument 1 to allow and 2 to block
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2
        })

        # options.add_argument("--start-maximized")
        options.add_argument("--window-position=545,0")
        options.add_argument("window-size=1380,1080")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        chromedriver = os.path.abspath(''.join([os.curdir, '/Webscraper/driver/chromedriver.exe']))
        # chromedriver = os.path.abspath(os.getcwd() + "\\AerodromeChartScraper\\driver\\chromedriver.exe") #SPIDERS_PATH + ".\\driver\\chromedriver.exe"
        # print("\n=========================== {} ===========================".format(chromedriver))
        super().__init__(executable_path=chromedriver, chrome_options=options)

    def wait(self, seconds):
        sleep(seconds)

    def wait_until_located(self, selector_type, value: str, timeout: int):
        """ Explicitly wait until an element is located """
        element = None
        if selector_type == 'XPATH':
            element = WebDriverWait(self, timeout).until(ec.presence_of_element_located((By.XPATH, value)))
        elif selector_type == 'CSS':
            element = WebDriverWait(self, timeout).until(ec.presence_of_element_located((By.CSS_SELECTOR, value)))
        else:
            print("Specify a valid parameter!")

        return element

    def select_dropdown_option(self, select_locator, option_value):
        """
        Selects the option in the drop-down
            required params:
            @select_locator == XPATH location of dropdown
            @option_value == the value of the option
        """

        select = Select(self.find_element_by_xpath(select_locator))
        select.select_by_value(option_value)
        self.wait(5)

        # dropdown = self.find_element_by_xpath(select_locator)
        # for option in dropdown.find_elements_by_tag_name('option'):
        #     if option.get_attribute('value') == option_value:
        #         option.click()
        #         break


class FirefoxDriver(webdriver.Firefox):

    def __init__(self, country="Default"):
        options = webdriver.FirefoxOptions()
        options.headless = True
        firefox = os.path.abspath(os.getcwd() + "\\AerodromeChartScraper\\driver\\geckodriver.exe") #SPIDERS_PATH + ".\\driver\\geckodriver.exe"
        super().__init__(executable_path=firefox, firefox_options=options)

    def wait(self, seconds):
        sleep(seconds)

    def wait_until_located(self, selector_type, value: str, timeout: int):
        """ Explicitly wait until an element is located """
        element = None
        if selector_type == 'XPATH':
            element = WebDriverWait(self, timeout).until(ec.presence_of_element_located((By.XPATH, value)))
        elif selector_type == 'CSS':
            element = WebDriverWait(self, timeout).until(ec.presence_of_element_located((By.CSS_SELECTOR, value)))
        else:
            print("Specify a valid parameter!")

        return element

    def select_dropdown_option(self, select_locator, option_value):
        """
        Selects the option in the drop-down
            required params:
            @select_locator == XPATH location of dropdown
            @option_value == the value of the option
        """

        select = Select(self.find_element_by_xpath(select_locator))
        select.select_by_value(option_value)
        self.wait(5)

        # dropdown = self.find_element_by_xpath(select_locator)
        # for option in dropdown.find_elements_by_tag_name('option'):
        #     if option.get_attribute('value') == option_value:
        #         option.click()
        #         break


class PhantomJSDriver(webdriver.PhantomJS):

    def __init__(self, country="Default"):
        phantomjs = os.path.abspath(os.getcwd() + "\\AerodromeChartScraper\\driver\\phantomjs.exe") #SPIDERS_PATH + ".\\driver\\phantomjs.exe"
        super().__init__(executable_path=phantomjs)

    def wait(self, seconds):
        sleep(seconds)

    def wait_until_located(self, selector_type, value: str, timeout: int):
        """ Explicitly wait until an element is located """
        element = None
        if selector_type == 'XPATH':
            element = WebDriverWait(self, timeout).until(ec.presence_of_element_located((By.XPATH, value)))
        elif selector_type == 'CSS':
            element = WebDriverWait(self, timeout).until(ec.presence_of_element_located((By.CSS_SELECTOR, value)))
        else:
            print("Specify a valid parameter!")

        return element

    def select_dropdown_option(self, select_locator, option_value):
        """
        Selects the option in the drop-down
            required params:
            @select_locator == XPATH location of dropdown
            @option_value == the value of the option
        """

        select = Select(self.find_element_by_xpath(select_locator))
        select.select_by_value(option_value)
        self.wait(5)

        # dropdown = self.find_element_by_xpath(select_locator)
        # for option in dropdown.find_elements_by_tag_name('option'):
        #     if option.get_attribute('value') == option_value:
        #         option.click()
        #         break