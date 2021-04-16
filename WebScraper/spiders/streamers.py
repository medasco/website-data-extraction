
import os
import scrapy
from selenium.webdriver import ActionChains
from WebScraper.web_spider import WebDataSpider
from WebScraper.items import DataItem
from WebScraper.web_drivers import ChromeDriver
from WebScraper.pipelines import DataPipeline
from selenium.webdriver.common.keys import Keys
from wsm.config import DOCX_PATH, SAVING_PATH


class StreamersSpider(WebDataSpider):
    """ Streamers' spider """
    name = 'streamers'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        
        self.spider_name = self.name
        self.data_mgr = None
        self.url = 'https://toptwitchstreamers.com/streamers/'

    def parse(self, response):
        """ Parsing callback function """

        list_of_data = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.browser.wait(3)

        total_page = self.browser.find_element_by_xpath('//div[@class="custom-pagination"]/a[3]').get_attribute('href')
        last_page = total_page.rsplit('/', 2)
        print(last_page)
