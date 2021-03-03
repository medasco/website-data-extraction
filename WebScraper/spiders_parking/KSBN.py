
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver

import ctypes  # An included library with Python install.


class KSBNParkingSpider(AeroChartSpider):
    """ KSBN airport parking charts spider """
    name = 'KSBN'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        # self.url = 'http://flysbn.com/terminal/terminal-hours-map/'
        self.url = 'https://www.google.com'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)
        self.browser.get('http://flysbn.com/terminal/terminal-hours-map/')

        # Login
        ctypes.windll.user32.MessageBoxW(0, "Complete captcha images then click OK.", "Captcha Required", 0)

        link = self.browser.find_element_by_xpath('//*[@id="content"]/div/div[1]/div[2]/div/div/img').get_attribute('src')
        desc = link.rsplit('/', 1)[1].replace('SBN-', '').rsplit('.', 1)[0].replace('-', '_').upper()

        print('{} : {}'.format(desc, link))

        chart_item = ChartItem()

        chart_item['country'] = 'USA'
        chart_item['icao'] = self.country_name
        chart_item['link'] = link
        chart_item['file'] = self.country_name + '_' + desc
        chart_item['desc'] = desc
        chart_item['club'] = 'Parking'

        list_of_charts.append(chart_item)

        self.chart_mgr = KSBNParkingChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()



    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class KSBNParkingChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('KSBN')
