
import os
import scrapy
from selenium.webdriver import ActionChains
from WebScraper.psw_spider import WebDataSpider
from WebScraper.items import DataItem
from WebScraper.web_drivers import ChromeDriver
from WebScraper.pipelines import DataPipeline
from selenium.webdriver.common.keys import Keys
from wsm.config import DOCX_PATH, SAVING_PATH


class TwitchSpider(WebDataSpider):
    """ Twitch's streamers spider """
    name = 'twitch'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        
        self.spider_name = self.name
        self.data_mgr = None
        self.url = 'https://toptwitchstreamers.com/streamers/'

    def parse(self, response):
        """ Parsing callback function """

        list_of_data = []
        info_list = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        self.browser.execute_script("window.scrollTo(document.body.scrollWidth, 0);")
        self.browser.wait(3)
        
        page_nums = self.browser.find_element_by_xpath('//div[@class="custom-pagination"]/a[3]').get_attribute('href')
        last_page = page_nums.rsplit('/', 2)
        pages = []

        info_list = []
        for pagination in range(0, int(last_page[1])):
            next_page = str(pagination + 1)
            make_page = '/'.join([last_page[0], next_page])
            pages.append(make_page)

        # Page creation from the last page available 
        for page in pages[:1]:  # TODO manipulate pages if Exception Timeout
            current_page = page.split('page/')[1].replace('/', '')
            
            # Get pages
            self.browser.get(page)
            self.browser.wait(2)

            # Get each streamer's link on each page
            streamers = self.browser.find_elements_by_xpath('//*[@id="custom-cat-content-area"]/div/div/a')
            for streamer in streamers[:1]:
                
                # Get streamer's details
                data_item = DataItem()
                browser = ChromeDriver()
                browser.get(streamer.get_attribute('href'))
                browser.wait(2)

                # Streamer's twitch headers section
                header_labels = browser.find_elements_by_xpath('//div[@class="dataTable"]/div[@class="dataRow"]/div[1]')
                header_values = browser.find_elements_by_xpath('//div[@class="dataTable"]/div[@class="dataRow"]/div[2]')
                browser.wait(2)

                alias = browser.find_element_by_xpath('//div[@class="streamers-name"]/h1').text

                print(f"\n:::::::::::::::::::::: Currently parsing page {current_page}: Extracting {alias}'s details ::::::::::::::::::::::\n")

                data_item['Page'] = current_page
                data_item['Alias'] = alias

                for header_label, header_value in list(zip(header_labels, header_values)):
                    if header_label:
                        print(alias, header_label.text, header_value.text)
                        if header_label.text == 'Twitch Status':
                            data_item['TwitchStatus'] = header_value.text

                        elif header_label.text == 'Twitch Followers':
                            data_item['TwitchFollowers'] = header_value.text

                        elif header_label.text == 'Twitch Channel Views':
                            data_item['TwitchChannelViews'] = header_value.text
            
                # Streamer's details section
                infos = browser.find_elements_by_xpath('//div[@class="streamers-info-section info-section-top clearfix"]')
                browser.wait(2)

                values_list = []
                if len(infos) > 0:
                    info = infos[0]

                    info_keys = info.find_elements_by_xpath('//div/span[@class="streamers-info-key"]')
                    info_values = info.find_elements_by_xpath('//div/span[@class="streamers-info-value"]')
                    self.browser.wait(2)

                    for info_key, info_value in list(zip(info_keys, info_values)):
                        if info_key:
                            print(alias, info_key.text, info_value.text)
                            if info_key.text == 'Name':
                                data_item['Name'] = info_value.text

                            elif info_key.text == 'Age':
                                data_item['Age'] = info_value.text

                            elif info_key.text == 'Birthday':
                                data_item['Birthday'] = info_value.text

                            elif info_key.text == 'Nationality':    
                                data_item['Nationality'] = info_value.text

                            elif info_key.text == 'Hometown':
                                data_item['Hometown'] = info_value.text

                            elif info_key.text == 'Ethnicity':
                                data_item['Ethnicity'] = info_value.text

                            elif info_key.text == 'Streams':
                                data_item['Streams'] = info_value.text

                            elif info_key.text == 'Former Teams':
                                data_item['FormerTeams'] = info_value.text

                            elif info_key.text == 'Team':
                                data_item['Team'] = info_value.text

                # Streamer's info section
                streamers_id = browser.find_element_by_xpath('//*[@id="main-content"]/div/article').get_attribute('id')
                sections = browser.find_elements_by_xpath('//*[@id= '+'"'+ str(streamers_id) +'"'+ ']/div/div[1]/div/div[6]')
                browser.wait(2)

                for section in sections:
                    block = section.get_attribute('class')
                    
                    if 'accomp_list' in block:
                        accomplishments = []
                        label = section.find_element_by_tag_name('h4')
                        values = section.find_elements_by_xpath('//ul/li/span')
                        print('test')
                        for value in values:
                            accomplishments.append(value.text)
                        data_item['Accomplishments'] = accomplishments
                        print([alias, label.text, data_item['Accomplishments']])

                    elif 'quote_list' in block:
                        label = section.find_element_by_tag_name('h4')
                        value = section.find_element_by_tag_name('p')
                        data_item['Quotes'] = value.text
                        print([alias, label.text, data_item['Quotes']])

                    elif 'sources_list' in block:
                        sources = []
                        label = section.find_element_by_tag_name('h4')
                        source = section.find_elements_by_tag_name('a')
                        for value, href in list(zip(values, source)):
                            link = href.get_attribute('href')
                            sources.append([value.text, link])
                        data_item['Sources'] = sources
                        print([alias, label.text, data_item['Sources']])
                    
                    elif block == 'streamers-info-section':
                        label = section.find_element_by_tag_name('h4')
                        values = section.find_elements_by_xpath('div[@class="streamers-more-value"]')
                        for value in values:
                            print([alias, label.text, value.text])
                            if label.text == 'FAMILY':
                                data_item['Family'] = value.text

                            elif label.text == 'NAME ORIGINS':
                                data_item['NameOrigins'] = value.text
                            
                            elif label.text == 'PROFESSIONAL GAMING':
                                data_item['ProfessionalGaming'] = value.text

                            elif label.text == 'STREAMING HOURS':
                                data_item['StreamingHours'] = value.text

                            elif label.text == 'REALTIONSHIPS':
                                data_item['Relationships'] = value.text

                            elif label.text == 'INCOME':
                                data_item['Income'] = value.text

                            elif label.text == 'OTHER INTERESTS':
                                data_item['OtherInterests'] = value.text

                            elif label.text == 'INTERESTING FACTS':
                                data_item['InterestingFacts'] = value.text

                            elif label.text == 'ADVICE FOR STREAMERS':
                                data_item['AdviceForStreamers'] = value.text

                list_of_data.append(data_item)
                browser.close()

            self.data_mgr = TwitchPipeline(list_of_data)
            # self.data_mgr.save_data_list('streamers')

        self.data_mgr.print_data_list()

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

    def print_data_list(self):
        """ Prints the chart list """
        print('\n{0}'.format(self.webDataFrame))

    def save_data_list(self, file_name):
        """ Write and saves the chart list to CSV file """
        x = file_name + '.csv'
        f = SAVING_PATH + x

        if not os.path.isfile(f):
            print('\nSaving data into a CSV file [{0}]...'.format(x))
            self.webDataFrame.to_csv(f, encoding='utf-8', index=False)
        else:
            print('\nAppending data into an existing CSV file [{0}]...'.format(x))
            self.webDataFrame.to_csv(f, mode='a', encoding='utf-8', index=False, header=False)
            # self.webDataFrame.drop_duplicates()

        print('Finished writing the webiste data list file: {0}\n'.format(os.path.abspath(f)))
