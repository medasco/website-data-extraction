import scrapy
from selenium.webdriver import ActionChains
from WebScraper.psw_spider import WebDataSpider
from WebScraper.items import DataItem
from WebScraper.web_drivers import ChromeDriver
from WebScraper.pipelines import DataPipeline
from selenium.webdriver.common.keys import Keys
from wsm.config import DOCX_PATH


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

        list_of_data = []
        pages = []
        links = []
        infos = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        this_page = self.browser.find_element_by_xpath('//div[@class="custom-pagination"]/a[1]').get_attribute('href')
        last_page = self.browser.find_element_by_xpath('//div[@class="custom-pagination"]/a[3]').get_attribute('href')
        next_page = int(this_page.rsplit('/', 2)[1])

        for pagination in range(int(last_page.rsplit('/', 2)[1])):
            next_page = str(pagination + 1)
            for page in pages:
                self.browser.get(page)
                streamers = self.browser.find_elements_by_xpath('//*[@id="custom-cat-content-area"]/div/div/a')
                for streamer in streamers:
                    links.append(streamer.get_attribute('href'))
            
            self.browser.get(self.url + 'page/' + next_page)

        for link in links:
            self.browser.get(streamer.get_attribute('href'))
            streamers_infos = self.browser.find_elements_by_xpath('//div[@class="streamers-info-section info-section-top clearfix"]')

            for streamers_info in streamers_infos:
                name = streamers_info.find_element_by_xpath('//div[1]/span[@class="streamers-info-value"]').text
                age = streamers_info.find_element_by_xpath('//div[2]/span[@class="streamers-info-value"]').text
                birthday = streamers_info.find_element_by_xpath('//div[3]/span[@class="streamers-info-value"]').text
                nationality = streamers_info.find_element_by_xpath('//div[4]/span[@class="streamers-info-value"]').text
                hometown = streamers_info.find_element_by_xpath('//div[5]/span[@class="streamers-info-value"]').text
                ethnicity = streamers_info.find_element_by_xpath('//div[6]/span[@class="streamers-info-value"]').text
                streams = streamers_info.find_element_by_xpath('//div[7]/span[@class="streamers-info-value"]').text
                formerteams = streamers_info.find_element_by_xpath('//div[8]/span[@class="streamers-info-value"]').text

                data_item = DataItem()

                data_item['name'] = name
                data_item['age'] = age
                data_item['birthday'] = birthday
                data_item['nationality'] = nationality
                data_item['hometown'] = hometown
                data_item['ethnicity'] = ethnicity
                data_item['streams'] = streams
                data_item['formerteams'] = formerteams

                list_of_data.append(data_item)

        self.data_mgr = TwitchPipeline(list_of_data)
        self.data_mgr.process_data()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)


class TwitchPipeline(DataPipeline):

    def process_data(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_data_list()
        self.save_data_list('Twitch')
