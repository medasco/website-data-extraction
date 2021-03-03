
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class EDFESupplementSpider(AeroChartSpider):
    """ EDFE airport supplementary charts spider """
    name = 'EDFE'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://egelsbach-airport.com/piloteninfo_aip.de.html'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        path = self.browser.find_elements_by_xpath('/html/body/div[2]/div[2]/div/table/tbody/tr[2]/td/table/tbody/tr/td[1]/a')

        for a in path:
            link = a.get_attribute('href')
            file = link.rsplit('/', 1)[1].split('.')[0]
            print('\t   : {} : {}'.format(file, link))

            chart_item = ChartItem()

            chart_item['country'] = 'Germany (ED)'
            chart_item['icao'] = self.country_name
            chart_item['link'] = link
            chart_item['file'] = self.country_name + '_' + file
            chart_item['desc'] = file
            chart_item['club'] = 'Supplementary'

            list_of_charts.append(chart_item)

        self.chart_mgr = EDFESupplementPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class EDFESupplementPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('EDFE')
