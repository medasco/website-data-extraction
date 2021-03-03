
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class KRSWParkingSpider(AeroChartSpider):
    """ KRSW airport parking charts spider """
    name = 'KRSW'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://flylcpa.com/shoppinginfo/'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        content = self.browser.find_element_by_xpath('//*[@class="row main-content"]/div/p/img')
        link = content.get_attribute('src')
        desc = content.get_attribute('title').split(' and ')[0].upper()
        file = link.rsplit('/', 1)[1].split('.')[0].upper()

        print('{} : {} : {}'.format(file, desc, link))

        chart_item = ChartItem()

        chart_item['country'] = 'USA'
        chart_item['icao'] = self.country_name
        chart_item['link'] = link
        chart_item['file'] = self.country_name + '_' + file
        chart_item['desc'] = desc
        chart_item['club'] = 'Parking'

        list_of_charts.append(chart_item)

        self.chart_mgr = KRSWParkingChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class KRSWParkingChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('KRSW')