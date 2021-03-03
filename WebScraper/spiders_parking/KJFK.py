
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class KJFKParkingSpider(AeroChartSpider):
    """ KJFK airport parking charts spider """
    name = 'KJFK'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://www.jfkairport.com/at-airport/airport-maps'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        option_list = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # Extract /select[@id='ddlTerminal']/option for dropdown items
        option_values = self.browser.find_elements_by_xpath('//*[@id="ddlTerminal"]/option')

        # Extract "value" attribute of each dropdown item
        for option in option_values:
            locator = "//select[@id='ddlTerminal']"
            value = option.get_attribute('value')

            # Select dropdown item and get the links
            self.browser.select_dropdown_option(locator, value)
            link = self.browser.find_element_by_xpath('//*[@id="dwnload"]/a').get_attribute('href')
            desc = link.rsplit('/', 1)[1].split('.')[0].replace('-','_').upper()
            file = ''.join([self.country_name, '_', desc]) if 'JFK' not in desc \
                    else ''.join([self.country_name, '_', desc.replace('JFK_', '')])

            print('\t   : {} : {} : {}'.format(file, desc, link))

            chart_item = ChartItem()

            chart_item['country'] = 'USA'
            chart_item['icao'] = self.country_name
            chart_item['link'] = link
            chart_item['file'] = file
            chart_item['desc'] = desc
            chart_item['club'] = 'Parking'

            list_of_charts.append(chart_item)

        self.chart_mgr = KJFKParkingChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class KJFKParkingChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('KJFK')
