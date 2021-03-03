
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class KOAKParkingSpider(AeroChartSpider):
    """ KOAK airport parking charts spider """
    name = 'KOAK'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'http://www.oaklandairport.com/maps-directions/airport-terminal-map/'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        terminal = self.browser.find_element_by_xpath('/html/body/div[1]/div[1]/div[4]/div/div[1]/p[2]/a')

        link = terminal.get_attribute('href')
        name = link.rsplit('/', 1)[1].split('.')[0]
        file = name.replace('OAK_', '')

        chart_item = ChartItem()

        chart_item['country'] = 'USA'
        chart_item['icao'] = self.country_name
        chart_item['link'] = link
        chart_item['file'] = self.country_name + '_' + file
        chart_item['desc'] = file
        chart_item['club'] = 'Parking'

        list_of_charts.append(chart_item)

        self.chart_mgr = KOAKParkingChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class KOAKParkingChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('KOAK')