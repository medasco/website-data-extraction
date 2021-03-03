# import scrapy
# from selenium.webdriver import ActionChains
from WebScraper.psw_spider import WebDataSpider
# from WebScraper.items import WebItem
# from WebScraper.web_drivers import ChromeDriver
# from WebScraper.pipelines import DataPipeline
# from selenium.webdriver.common.keys import Keys
# from docx import Document
# from wsm.config import DOCX_PATH
# from itertools import product


class TwitchSpider(WebDataSpider):
    """ Twitch's streamers spider """
    name = 'twitch'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.spider_name = self.name
        self.url = 'https://toptwitchstreamers.com/streamers/'

    def parse(self, response):
        """ Parsing callback function """

        # list_of_data = []
        # streamer_links = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)
        streamers = self.browser.find_elements_by_xpath('//*[@id="custom-cat-content-area"]/div/div/a')

        for streamer in streamers[:1]:
            self.browser.get(streamer.get_attribute('href'))

            infos = self.browser.find_elements_by_xpath('//div[@class="streamers-info-section info-section-top clearfix"]/div')
            for info in infos:
                info.find_elements_by_tag_name('span')


        # for streamer_link in streamer_links:
        #     self.browser.get(streamer_link)
        #     infos = self.browser.find_elements_by_xpath('//div[@class="streamers-info-section info-section-top clearfix"]/div')


    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)
