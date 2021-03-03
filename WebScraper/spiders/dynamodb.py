import scrapy
from selenium.webdriver import ActionChains
from WebScraper.psw_spider import WebDataSpider
from WebScraper.items import WebItem
from WebScraper.web_drivers import ChromeDriver
from selenium.webdriver.common.keys import Keys
from docx import Document
from wsm.config import DOCX_PATH
from itertools import product


class dynamoDBSpider(WebDataSpider):
    """ dynamoDB airport charts spider """
    name = 'dynamodb'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://www.facebook.com'

    def parse(self, response):
        """ Parsing callback function """

        username = 'betauser2@gmail.com'
        password = 'pwuser2'

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # Login
        self.browser.find_element_by_name("email").send_keys(username)
        self.browser.find_element_by_name("pass").send_keys(password)
        self.browser.find_element_by_name("login").click()
        self.browser.wait(5)

        # Go to Pages
        

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)
