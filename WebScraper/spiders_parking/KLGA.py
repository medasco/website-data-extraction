
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class KLGAParkingSpider(AeroChartSpider):
    """ KLGA airport parking charts spider """
    name = 'KLGA'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'http://laguardiaairport.com/at-airport/airport-maps'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        option_list = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # get downloadable pdf path
        term = self.browser.find_element_by_xpath('//*[@id="dwnload"]/a').get_attribute('href')
        path = term.rsplit('/', 1)[0]

        # get each terminal pdf name
        option = self.browser.find_elements_by_xpath('//*[@id="ddlTerminal"]/option')

        for value in option:
            ovalue = value.get_attribute('value')
            option_list.append(ovalue)

        # construct the link
        for terminal in option_list:
            link = path + '/' + terminal + '.pdf'
            print(link)

            file = terminal.replace('lga-', '').replace('-', '_').upper()

            chart_item = ChartItem()

            chart_item['country'] = 'USA'
            chart_item['icao'] = self.country_name
            chart_item['link'] = link
            chart_item['file'] = self.country_name + '_' + file
            chart_item['desc'] = file
            chart_item['club'] = 'Parking'

            list_of_charts.append(chart_item)

        self.chart_mgr = KLGAParkingChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class KLGAParkingChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('KLGA')