
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class KSATParkingSpider(AeroChartSpider):
    """ KSAT airport parking charts spider """
    name = 'KSAT'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'http://www.sanantonio.gov/SAT/At-the-Airport/Terminal-Maps'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        maps = self.browser.find_element_by_xpath('//*[@id="dnn_ctr1791_HtmlModule_lblContent"]/p[2]/a').get_attribute('href')

        link = maps.split('?')[0]
        desc = link.rsplit('/', 1)[1].rsplit('.', 1)[0].replace('%20', '_')
        file = 'KSAT_' + desc.upper()

        print('{} : {} : {}'.format(desc, file, link))

        chart_item = ChartItem()

        chart_item['country'] = 'USA'
        chart_item['icao'] = self.country_name
        chart_item['link'] = link
        chart_item['file'] = file
        chart_item['desc'] = desc
        chart_item['club'] = 'Parking'

        list_of_charts.append(chart_item)

        self.chart_mgr = KSATParkingChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class KSATParkingChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('KSAT')