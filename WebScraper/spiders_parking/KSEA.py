
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class KSEAParkingSpider(AeroChartSpider):
    """ KSEA airport parking charts spider """
    name = 'KSEA'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://www.portseattle.org/sea-tac'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        term_links = []
        gates_list = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        maps = self.browser.find_elements_by_xpath('//a[contains(@class, "static menu-item")]')

        for terminal in maps:

            href = terminal.get_attribute('href')

            if 'Concourse-' in str(href) or '-Satellite' in str(href):
                # print(href)
                term_links.append(href)

        for course in term_links:
            self.browser.get(course)
            concourse = self.browser.find_elements_by_xpath('//a[contains(@href, "printable.pdf")]')

            for gates in concourse[:1]:
                link = gates.get_attribute('href')
                file = link.rsplit('/', 1)[1].split('_printable')[0].upper()
                # print('{} :\t{}'.format(file, link))

                chart_item = ChartItem()

                chart_item['country'] = 'USA'
                chart_item['icao'] = self.country_name
                chart_item['link'] = link
                chart_item['file'] = self.country_name + '_' + file
                chart_item['desc'] = file
                chart_item['club'] = 'Parking'

                list_of_charts.append(chart_item)

        self.chart_mgr = KSEAParkingChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class KSEAParkingChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('KSEA')
