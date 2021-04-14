
import logging
import scrapy
import requests.exceptions as re
import selenium.common.exceptions as e
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from WebScraper.web_drivers import ChromeDriver


configure_logging(install_root_handler=False)
logging.basicConfig(
    filename='spider.txt',
    format='[%(name)s] %(levelname)s: %(message)s',
    level=logging.INFO,
    filemode='w'
)

webLogger = logging.getLogger('webSpiderLog')


class WebDataSpider(scrapy.Spider):

    name = 'WebSpider'

    def __init__(self):

        super().__init__()
        self.browser = ChromeDriver()
        self.spider_name = None
        self.chart_mgr = None
        self.url = None

    def start_requests(self):
        """ Start the request.
        """
        if self.spider_name is None:
            alpha_tag = 'EuroControl' # due to self.spider_name of EuroControl was set to None
        else:
            alpha_tag = self.spider_name

        tag = '{0} : {1} : {2}'.format(alpha3[alpha_tag], 'Start Request', self.url)
        webLogger.info(tag)

        yield scrapy.Request(url=self.url, callback=self.scrape)

    def scrape(self, response):

        try:
            self.parse(response)
            msg = '{0} : {1} : {2}'.format(alpha3[self.spider_name], 'Parsing OK', response.url)
            webLogger.info(msg)

        except e.NoSuchElementException as inst:
            msg = inst.msg.split(': ')[1:3]
            msg = '{0} : {1}'.format(msg[0], msg[1].split('\n')[0])

            msg = '{0} : {1}'.format(alpha3[self.spider_name], msg)
            webLogger.error(msg)

            # Close the spider
            self.close_spider(msg)

    def close_spider(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


alpha3 = {
        'createfbpage': 'createfbpage',  # Greenmamastore (scraping jobs)
        'amazon': 'amazon',  # Greenmamastore (scraping jobs)
        'duval': 'duval',  # LoveClientsInc (scraping jobs)
        'twitch': 'twitch',
        'streamers': 'streamers',
        'mattress': 'mattress'
}
