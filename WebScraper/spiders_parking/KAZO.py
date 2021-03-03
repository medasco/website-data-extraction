
import scrapy
import urllib.request
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class KAZOParkingSpider(AeroChartSpider):
    """ KAZO airport parking charts spider """
    name = 'KAZO'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'http://azoairport.com/'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        self.click_enable(self.browser.find_element_by_xpath('//*[@id="content"]/section/div[1]/div[3]/div/div/div[2]/a'))

        link = self.browser.find_element_by_xpath('//*[@id="image-map-pro-1751"]/div/div[10]/div/div/img').get_attribute('src')
        desc = link.rsplit('/', 1)[1].split('.')[0].replace('AZO', 'KAZO').upper()
        file = desc.rsplit('-', 2)[0].replace('-', '_')
        print('{} : {} : {}'.format(desc, file, link))

        chart_item = ChartItem()

        chart_item['country'] = 'USA'
        chart_item['icao'] = self.country_name
        chart_item['link'] = link
        chart_item['file'] = file
        chart_item['desc'] = desc
        chart_item['club'] = 'Parking'

        list_of_charts.append(chart_item)

        self.chart_mgr = KAZOParkingChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class KAZOParkingChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('KAZO')
