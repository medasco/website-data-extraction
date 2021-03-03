
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class KSJCParkingSpider(AeroChartSpider):
    """ KSJC airport parking charts spider """
    name = 'KSJC'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://www.flysanjose.com/terminal-maps'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        terminal_list = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        terminal_A = self.browser.find_element_by_xpath('//*[@id="block-mainpagecontent"]/div/article/div/div[2]/div[1]/div/a')
        self.click_enable(terminal_A)
        print_version_A = self.browser.find_element_by_xpath('//*[@id="block-terminalamaplinks-2"]/div/div/p/a[1]')
        terminal_list.append(print_version_A.get_attribute('href'))

        terminal_B = self.browser.find_element_by_xpath('//*[@id="block-terminalamaplinks-2"]/div/div/p/a[2]')
        self.click_enable(terminal_B)
        print_version_B = self.browser.find_element_by_xpath('//*[@id="block-terminalbmaplinks-2"]/div/div/p/a[1]')
        terminal_list.append(print_version_B.get_attribute('href'))

        for terminal in terminal_list:

            link = terminal
            file = link.rsplit('/', 1)[1].split('.')[0].replace('%20', '_')
            desc = file.upper()

            chart_item = ChartItem()

            chart_item['country'] = 'USA'
            chart_item['icao'] = self.country_name
            chart_item['link'] = link
            chart_item['file'] = self.country_name + '_' + file
            chart_item['desc'] = desc
            chart_item['club'] = 'Parking'

            list_of_charts.append(chart_item)

        self.chart_mgr = KSJCParkingChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class KSJCParkingChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('KSJC')
