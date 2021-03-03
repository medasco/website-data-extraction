
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class KBURParkingSpider(AeroChartSpider):
    """ KBUR airport parking charts spider """
    name = 'KBUR'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'http://hollywoodburbankairport.com/about-us/airport-facility-maps/'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        term_list = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # self.browser.wait_until_located("XPATH", "//*[@id='post-1665']/div", 3)
        frame = self.browser.find_element_by_tag_name('iframe')
        terms = frame.get_attribute('src')

        self.browser.get(terms)
        term_a = self.browser.find_element_by_xpath('//*[@id="terminalA"]/img').get_attribute('src')
        term_list.append(term_a)
        term_b = self.browser.find_element_by_xpath('//*[@id="terminalB"]/img').get_attribute('src')
        term_list.append(term_b)

        for term in term_list:
            link = term
            file = link.rsplit('/', 1)[1].rsplit('.', 1)[0]

            chart_item = ChartItem()

            chart_item['country'] = 'USA'
            chart_item['icao'] = self.country_name
            chart_item['link'] = link
            chart_item['file'] = self.country_name + '_' + file
            chart_item['desc'] = file
            chart_item['club'] = 'Parking'

            list_of_charts.append(chart_item)

        self.chart_mgr = KBURParkingChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class KBURParkingChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('KBUR')
