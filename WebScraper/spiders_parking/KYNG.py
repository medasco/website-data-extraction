
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class KYNGParkingSpider(AeroChartSpider):
    """ KYNG airport parking charts spider """
    name = 'KYNG'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://www.yngairport.com/'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        info = self.browser.find_element_by_xpath('//*[@id="menu-item-1496"]/a').get_attribute('href')
        self.browser.get(info)

        link = self.browser.find_element_by_xpath('//*[@id="post-999"]/div[2]/div[2]/div/div/div[2]/p[4]/a').get_attribute('href')
        desc = link.rsplit('/', 1)[1].rsplit('.', 1)[0]
        file = 'KYNG_' + desc.upper()

        print('{} : {} : {}'.format(desc, file, link))

        chart_item = ChartItem()

        chart_item['country'] = 'USA'
        chart_item['icao'] = self.country_name
        chart_item['link'] = link
        chart_item['file'] = file
        chart_item['desc'] = desc
        chart_item['club'] = 'Parking'

        list_of_charts.append(chart_item)

        self.chart_mgr = KYNGParkingChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class KYNGParkingChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('KYNG')
