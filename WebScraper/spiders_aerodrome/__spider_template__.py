
import scrapy
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class NameOfSpider(scrapy.Spider):
    """ Hong Kong airport charts spider """
    name = 'NameOfSpider'
    version = '1.0.0'

    def __init__(self):
        super(NameOfSpider, self).__init__()
        self.browser = ChromeDriver()
        self.country_name = self.name
        self.chart_mgr = None

    def start_requests(self):
        """ Set the main URL to be visited
            and start the request.
        """
        url = 'http://www.main.url.of.the.charts'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """ Parsing callback function """

        pdf_desc = None
        pdf_links = None
        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class NameOfSpiderChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('NameOfSpider')
