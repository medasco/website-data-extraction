
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class KDFWParkingSpider(AeroChartSpider):
    """ KDFW airport parking charts spider """
    name = 'KDFW'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://www.dfwairport.com/map/'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        boarding = self.browser.find_elements_by_xpath('//*[@id="r2"]/table/tbody/tr[2]/td[1]/table/tbody/tr[1]/td/table/tbody/tr/td/img')

        for gate in boarding:
            link = gate.get_attribute('src')
            name = gate.get_attribute('alt')
            file = name.upper() if '.jpg' not in name else name.replace('.jpg', '').upper()

            chart_item = ChartItem()

            chart_item['country'] = 'USA'
            chart_item['icao'] = self.country_name
            chart_item['link'] = link
            chart_item['file'] = self.country_name + '_' + file
            chart_item['desc'] = file

            chart_item['club'] = 'Parking'

            list_of_charts.append(chart_item)

        self.chart_mgr = KDFWParkingChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class KDFWParkingChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('KDFW')
