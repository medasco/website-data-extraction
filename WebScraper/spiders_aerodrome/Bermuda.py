import scrapy
from selenium.webdriver import ActionChains
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class BermudaSpider(AeroChartSpider):
    """ Bermuda airport charts spider """
    name = 'Bermuda'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://bermudaairport.com/'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # Go to AIP '//*[@id="end"]/div/p/a[1]'
        #self.click_enable(self.browser.find_element_by_xpath('//*[@id="end"]/div/p/a[1]'))

        # Go to GEN
        link = self.browser.find_elements_by_xpath('//*[@id="end"]/div/p/a[1]').get_attribute('href')
        tags = link.rsplit('/', 1)[1].split('.')[0].replace('%20', '_')
        icao = 'TXKF'
        file = tags.replace('-', '_')
        desc = tags.split('incl')[1]

        print('\t   : {} : {} : {} : {}'.format(icao, file, desc, link))

        chart_item = ChartItem()

        chart_item['country'] = self.country_name
        chart_item['icao'] = icao
        chart_item['link'] = link
        chart_item['desc'] = desc
        chart_item['file'] = file
        chart_item['club'] = 'Default'

        list_of_charts.append(chart_item)

        self.chart_mgr = BermudaChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()
        
    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)


class BermudaChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Bermuda')
