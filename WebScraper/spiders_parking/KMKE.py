
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class KMKEParkingSpider(AeroChartSpider):
    """ KMKE airport parking charts spider """
    name = 'KMKE'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://www.mitchellairport.com/airport-guide'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        link_list = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        guide = self.browser.find_element_by_xpath('/html/body/main/div[2]/div/div[3]/ul/li[2]/h3/a').get_attribute('href')
        self.browser.get(guide)

        link = self.browser.find_element_by_xpath('//*[@id="retail"]/img').get_attribute('src')
        name = link.rsplit('/', 1)[1]
        desc = name if '.gif' not in name else name.replace('.gif', '')
        file = 'KMKE_' + desc.replace('-', '_').upper()

        print('{} : {} : {}'.format(desc, file, link))

        chart_item = ChartItem()

        chart_item['country'] = 'USA'
        chart_item['icao'] = self.country_name
        chart_item['link'] = link
        chart_item['file'] = file
        chart_item['desc'] = desc
        chart_item['club'] = 'Parking'

        list_of_charts.append(chart_item)

        self.chart_mgr = KMKEParkingChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class KMKEParkingChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('KMKE')
