
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class KPHXParkingSpider(AeroChartSpider):
    """ KPHX airport parking charts spider """
    name = 'KPHX'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://www.skyharbor.com/Maps'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        links_list = []
        term_list = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # Terminal 3
        self.browser.find_element_by_xpath('//*[@id="maps-directions"]/div/div[3]/div[2]').click()
        self.browser.wait(2)
        self.browser.find_element_by_xpath('//*[@id="maps-directions"]/div/div[3]/div[2]/div/div[2]/div[3]').click()
        self.browser.wait(2)
        term3 = self.browser.find_element_by_xpath('//*[@id="maps-directions"]/div/div[4]/div/img').get_attribute('src')
        term_list.append(term3)

        # Terminal 4
        self.browser.find_element_by_xpath('//*[@id="maps-directions"]/div/div[3]/div[3]').click()
        self.browser.wait(2)
        self.browser.find_element_by_xpath('//*[@id="maps-directions"]/div/div[3]/div[3]/div/div[2]/div[3]').click()
        self.browser.wait(2)
        term4 = self.browser.find_element_by_xpath('//*[@id="maps-directions"]/div/div[4]/div/img').get_attribute('src')
        term_list.append(term4)

        for term in term_list:
            link = term
            file = term.rsplit('/', 1)[1].split('.')[0].upper()

            print('\t   : {} : {}'.format(file, link))

            chart_item = ChartItem()

            chart_item['country'] = 'USA'
            chart_item['icao'] = self.country_name
            chart_item['link'] = link
            chart_item['file'] = self.country_name + '_' + file
            chart_item['desc'] = file
            chart_item['club'] = 'Parking'

            list_of_charts.append(chart_item)

        self.chart_mgr = KPHXParkingChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(5)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class KPHXParkingChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('KPHX')
