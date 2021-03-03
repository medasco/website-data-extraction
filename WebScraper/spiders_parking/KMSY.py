
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class KMSYParkingSpider(AeroChartSpider):
    """ KMSY airport parking charts spider """
    name = 'KMSY'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'http://www.flymsy.com/terminals'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        term_list = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        maps = self.browser.find_elements_by_xpath('//*[@id="content"]/table/tbody/tr/td[2]/table/tbody/tr/td/table/tbody/tr[3]/td/table/tbody/tr')
        for concs in maps:
            term = concs.find_element_by_tag_name('a').get_attribute('href')
            if 'Concourse' in term:
                term_list.append(term)

        for item in term_list:
            self.browser.get(item)
            conc = self.browser.find_elements_by_tag_name('img')

            for tags in conc:
                link = tags.get_attribute('src')

                if 'concourse' in link:
                    file = link.rsplit('/', 1)[1].rsplit('.', 1)[0].replace('-', '_').upper()
                    print(file, link)

                    chart_item = ChartItem()

                    chart_item['country'] = 'USA'
                    chart_item['icao'] = self.country_name
                    chart_item['link'] = link
                    chart_item['file'] = self.country_name + '_' + file
                    chart_item['desc'] = file
                    chart_item['club'] = 'Parking'

                    list_of_charts.append(chart_item)

        self.chart_mgr = KMSYParkingChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class KMSYParkingChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('KMSY')
