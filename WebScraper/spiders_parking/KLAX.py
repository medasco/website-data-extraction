
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class KLAXParkingSpider(AeroChartSpider):
    """ KLAX airport parking charts spider """
    name = 'KLAX'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://www.google.com/'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        list_of_trmnls = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)
        self.browser.get('https://www.flylax.com/')

        self.click_enable(self.browser.find_element_by_xpath('//*[@id="tab_default_1"]/div/div[3]/a'))

        lax = self.browser.find_elements_by_xpath('//*[@id="tab-1"]/div/div[2]/div/a')

        for gate in lax:
            gate_link = gate.get_attribute('href')
            name = gate_link.rsplit('/', 1)[1].split('.')[0].upper()
            list_of_trmnls.append([name, gate_link])

            print('{} :\t{}'.format(name, gate_link))

        for file, term in list_of_trmnls:
            self.browser.get(term)
            link = self.browser.find_element_by_xpath('//*[@id="wrap"]/div[2]/div/div[3]/div[2]/div/div/div[2]/div[3]/div/p/a').get_attribute('href')

            print('{}'.format(link))

            chart_item = ChartItem()

            chart_item['country'] = 'USA'
            chart_item['icao'] = self.country_name
            chart_item['link'] = link
            chart_item['file'] = self.country_name + '_' + file
            chart_item['desc'] = file
            chart_item['club'] = 'Parking'

            list_of_charts.append(chart_item)

        self.chart_mgr = KLAXParkingChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class KLAXParkingChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('KLAX')