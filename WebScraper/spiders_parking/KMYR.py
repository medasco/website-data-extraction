
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class KMYRParkingSpider(AeroChartSpider):
    """ KMYR airport parking charts spider """
    name = 'KMYR'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://www.flymyrtlebeach.com/airport-services/airport-map/'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)
        images = self.browser.find_elements_by_xpath('//*[@id="mapplic-id1513"]/div[1]/div[2]/div/img[1]')

        for image in images:
            link = image.get_attribute('src')
            desc = link.rsplit('/', 1)[1].rsplit('.', 1)[0].replace('-mini', '').upper()
            file = ''.join([self.country_name, '_', desc])

            print('\t   : {} : {} : {}'.format(file, desc, link))

            chart_item = ChartItem()

            chart_item['country'] = 'USA'
            chart_item['icao'] = self.country_name
            chart_item['link'] = link
            chart_item['file'] = file
            chart_item['desc'] = desc
            chart_item['club'] = 'Parking'

            list_of_charts.append(chart_item)

        self.chart_mgr = KMYRParkingChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class KMYRParkingChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('KMYR')
