
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class EgyptSpider(AeroChartSpider):
    """ Egypt airport charts spider """
    name = 'Egypt'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'http://www.nansceg.net/ais.html'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        pdf_link = self.browser.find_element_by_xpath("//tbody/tr/td/p[8]/a")
        pdf_desc = self.browser.find_element_by_xpath("//tbody/tr/td/p[8]/span")

        link = pdf_link.get_attribute('href')
        desc = pdf_desc.text
        file = link.rsplit('/', 1)[1].split('.pdf')[0].upper()

        chart_item = ChartItem()

        chart_item['country'] = self.country_name
        chart_item['icao'] = 'All'
        chart_item['link'] = link
        chart_item['desc'] = desc
        chart_item['file'] = file
        chart_item['club'] = 'Default'

        list_of_charts.append(chart_item)

        self.chart_mgr = EgyptChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class EgyptChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Egypt')
