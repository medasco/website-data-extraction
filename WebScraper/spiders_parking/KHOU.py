
import scrapy
import urllib.request
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class KHOUParkingSpider(AeroChartSpider):
    """ KHOU airport parking charts spider """
    name = 'KHOU'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'http://www.fly2houston.com/hou/maps/'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        term = self.browser.find_elements_by_xpath('//*[@id="info"]/div[2]/div/a')

        for item in term:
            starter = item.get_attribute('href')
            request = urllib.request.urlopen(starter)
            link = request.geturl()
            # print(link)

            if 'l2' in str(link):
                file = link.rsplit('/', 1)[1].rsplit('.', 1)[0].replace('-', '_').upper()
                print('{} : {}'.format(file, link))

                chart_item = ChartItem()

                chart_item['country'] = 'USA'
                chart_item['icao'] = self.country_name
                chart_item['link'] = link
                chart_item['file'] = self.country_name + '_' + file
                chart_item['desc'] = file
                chart_item['club'] = 'Parking'

                list_of_charts.append(chart_item)

        self.chart_mgr = KHOUParkingChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class KHOUParkingChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('KHOU')
