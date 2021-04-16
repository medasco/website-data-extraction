import scrapy
from selenium.webdriver import ActionChains
from WebScraper.web_spider import WebDataSpider
from WebScraper.items import DataItem
from WebScraper.web_drivers import ChromeDriver
from WebScraper.pipelines import DataPipeline
from selenium.webdriver.common.keys import Keys
from docx import Document
from wsm.config import DOCX_PATH
from itertools import product


class AmazonSpider(WebDataSpider):
    """ Amazon Categories spider """
    name = 'amazon'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.spider_name = self.name
        self.url = 'https://www.amazon.com/'

    def parse(self, response):
        """ Parsing callback function """

        list_of_data = []
        subcategories_list = []
        categories_list = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # Go to Amazon Fresh
        self.browser.find_element_by_xpath('//*[@id="twotabsearchtextbox"]').send_keys('Amazon Fresh')
        self.browser.find_element_by_xpath('//*[@id="twotabsearchtextbox"]').send_keys(Keys.ENTER)
        self.browser.wait_until_located('XPATH', '//*[@id="nav-main"]/div[1]/div/div/div[3]/span[1]', 2)

        # Select 'Close'
        self.browser.find_element_by_xpath('//*[@id="nav-main"]/div[1]/div/div/div[3]/span[1]').click()
        self.browser.wait_until_located('XPATH', '//*[@id="nav-subnav"]/a[12]', 2)

        # Get Categories
        self.browser.execute_script("window.scrollTo(document.body.scrollWidth, 0);")
        categories = self.browser.find_elements_by_xpath('//div[@id="nav-subnav"]/a')

        print("\nParsing Amazon's Categories and Sub-Categories...")

        for category_name in categories[3:]:
            
            self.hover_element(category_name)
            print('\t: {}'.format((category_name.text).upper()))

            # Get Subcategories
            sub_category_links = self.browser.find_elements_by_xpath('//li[@class="generic-subnav-flyout-item"]/a')
            sub_category_names = self.browser.find_elements_by_xpath('//li[@class="generic-subnav-flyout-item"]/a/div[@class="generic-subnav-flyout-title"]')
            
            for sub_name, sub_link in list(zip(sub_category_names, sub_category_links)):
                if sub_name.text != '':
                    print('\t  : {}'.format(sub_name.text))
                    subcategories_list.append([category_name.text, sub_name.text, sub_link.get_attribute('href')])
            
            print()

        print("Extraction and Assembling of Collected Data Fields...")

        # Get Sub-subcategories
        for categoryName,subCategoryName, subLink in subcategories_list:
            print('\t: {} CATEGORY'.format(categoryName.upper()))

            self.browser.get(subLink)
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.browser.wait(5)

            print('\t  : {} SUBCATEGORY'.format(subCategoryName.upper()))
            
            sub_subcategory_names = self.browser.find_elements_by_xpath('//div[@class="a-column a-span12"]/h2[@class="a-size-large"]/span')

            for subSubCategoryName in sub_subcategory_names:
                print('\t    : {}'.format(subSubCategoryName.text))
                categories_list.append([categoryName, subCategoryName, subSubCategoryName.text])

            print()

        for category, subcategory, subsubcategory in categories_list:
                    
            web_item = DataItem()

            web_item['spider'] = self.spider_name
            web_item['category'] = category
            web_item['subcategory'] = subcategory
            web_item['subsubcategory'] = subsubcategory

            list_of_data.append(web_item)

        self.browser.quit()
        
        self.chart_mgr = AmazonDataPipeline(list_of_data)
        self.chart_mgr.process_charts()
    
    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)

    def hover_element(self, element):
        hover = ActionChains(self.browser).move_to_element(element)
        hover.perform()
        self.browser.wait(2)


class AmazonDataPipeline(DataPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted WebItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_data_list()
        self.save_data_list('Amazon')
 