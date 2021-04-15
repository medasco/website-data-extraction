
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class RussiaSpider(AeroChartSpider):
    """ Russia airport charts spider """
    name = 'Russia'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'http://www.caiga.ru/common/AirInter/validaip/html/eng.htm'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # Switch frame to 'menu'
        self.browser.wait_until_located("XPATH", "//frame[@name='menu']", 3)
        self.browser.switch_to.frame("menu")

        ad_title = self.browser.find_elements_by_xpath("//*[@id='5025']/div/a")

        print('\nExtracting : ICAO(s)')

        for h in ad_title:
            link = h.get_attribute('href')
            icao = link.rsplit('/', 2)[1].upper()
            desc = h.get_attribute('title')
            filename = link.rsplit('/', 1)[1].split('.pdf')[0]
            file = '_'.join(filename.split('-')).upper()

            print('\t   :', icao + '_' + desc)

            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['icao'] = icao
            chart_item['link'] = link
            chart_item['file'] = file
            chart_item['desc'] = desc
            chart_item['club'] = 'Default'

            list_of_charts.append(chart_item)

        self.chart_mgr = RussiaChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class RussiaChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Russia')
