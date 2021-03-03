
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class KBHMParkingSpider(AeroChartSpider):
    """ KBHM airport parking charts spider """
    name = 'KBHM'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'http://www.flybirmingham.com/in-the-airport/airport-map/'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        maps_list = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        terminal_map = self.browser.find_elements_by_xpath('/html/body/div[1]/div[3]/div/div/a')

        for terminals in terminal_map:
            maps = terminals.get_attribute('href')
            maps_list.append(maps)

        for gate in maps_list:
            self.browser.get(gate)
            term = self.browser.find_element_by_xpath('/html/body/div/div[2]/div[1]/ul/li[2]/a')

            link = term.get_attribute('href')
            name = link.rsplit('/', 1)[1].rsplit('.', 1)[0]
            file = name.rsplit('-', 2)[1].replace('-', '_').upper()

            chart_item = ChartItem()

            chart_item['country'] = 'USA'
            chart_item['icao'] = self.country_name
            chart_item['link'] = link
            chart_item['file'] = self.country_name + '_' + file
            chart_item['desc'] = file
            chart_item['club'] = 'Parking'

            list_of_charts.append(chart_item)

        self.chart_mgr = KBHMParkingChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class KBHMParkingChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('KBHM')
