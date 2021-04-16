
import os
import json
import scrapy
from selenium.webdriver import ActionChains
from WebScraper.web_spider import WebDataSpider
from WebScraper.items import DataItem
from WebScraper.web_drivers import ChromeDriver
from WebScraper.pipelines import DataPipeline
from selenium.webdriver.common.keys import Keys
from wsm.config import DOCX_PATH, SAVING_PATH


class MattressSpider(WebDataSpider):
    """ Mattress's streamers spider """
    name = 'mattress'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        
        self.spider_name = self.name
        self.data_mgr = None
        self.url = 'https://au.mattress.zone/'

    def parse(self, response):
        """ Parsing callback function """

        mattress_list = []
        mattress_links = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        links = self.browser.find_elements_by_xpath('//*[@id="gatsby-focus-wrapper"]/div/main/div[2]/div/form/div[1]/div/div/label/div/div/a')
        for link in links:
            mattress_links.append(link.get_attribute('href'))

        for mattress in mattress_links[:2]:
            self.browser.get(mattress)
            name = mattress.split('/')[-1].replace('-', '_').title()

            mattress_dict = {}
            labels = self.browser.find_elements_by_xpath('//*[@class="table compare-table mb-5"]/tbody/tr/td[@class="label"]')
            datas = self.browser.find_elements_by_xpath('//*[@class="table compare-table mb-5"]/tbody/tr/td[@class="data"]')

            for label, data in list(zip(labels, datas)):
                data_text = data.text

                if label.text == 'Trial Period':
                    data_icon = data.find_element_by_tag_name('svg').get_attribute('data-icon')
                    data_text = 'Available' if data_icon == 'check' else 'None'
                    print(f'"{label.text}": "{data_text}"')

                elif label.text == 'One Firmness Fits All?':
                    data_icon = data.find_element_by_tag_name('svg').get_attribute('data-icon')
                    data_text = 'Available' if data_icon == 'check' else 'None'
                    print(f'"{label.text}": "{data_text}"')

                elif label.text == 'Adjustable Firmness':
                    data_icon = data.find_element_by_tag_name('svg').get_attribute('data-icon')
                    data_text = 'Available' if data_icon == 'check' else 'None'
                    print(f'"{label.text}": "{data_text}"')

                elif label.text == 'Half-Half Firmness':
                    data_icon = data.find_element_by_tag_name('svg').get_attribute('data-icon')
                    data_text = 'Available' if data_icon == 'check' else 'None'
                    print(f'"{label.text}": "{data_text}"')

                elif label.text == 'Selectable Firmness':
                    data_icon = data.find_element_by_tag_name('svg').get_attribute('data-icon')
                    data_text = 'Available' if data_icon == 'check' else 'None'
                    print(f'"{label.text}": "{data_text}"')

                elif label.text == 'Flippable / Reversible Firmness':
                    data_icon = data.find_element_by_tag_name('svg').get_attribute('data-icon')
                    data_text = 'Available' if data_icon == 'check' else 'None'
                    print(f'"{label.text}": "{data_text}"')

                elif label.text == 'Side Sleepers':
                    data_icon = data.find_element_by_tag_name('svg').get_attribute('data-icon')
                    data_text = 'Available' if data_icon == 'check' else 'None'
                    print(f'"{label.text}": "{data_text}"')

                elif label.text == 'Back Sleepers':
                    data_icon = data.find_element_by_tag_name('svg').get_attribute('data-icon')
                    data_text = 'Available' if data_icon == 'check' else 'None'
                    print(f'"{label.text}": "{data_text}"')

                else:
                    pass
            #     mattress_dict.update({label.text: data_text})
            # mattress_list.append({name: mattress_dict})
            
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(mattress_list, f, ensure_ascii=False, indent=4)
    
    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)

