
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver

import ctypes  # An included library with Python install.


class KBNAParkingSpider(AeroChartSpider):
    """ KBNA airport parking charts spider """
    name = 'KBNA'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://www.google.com'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)
        self.browser.get('https://www.flynashville.com/im/Pages/Landing.aspx')

        # Login
        ctypes.windll.user32.MessageBoxW(0, "Enter text you see in the Captcha image\n[Refresh to generate new image]\n\nDO NOT CLICK 'Submit'\nClick 'OK'\n\nIf there is no image captcha, click 'OK'", "Captcha Required", 0)
        self.click_enable(self.browser.find_element_by_xpath('/html/body/form/input[2]'))

        # Browsing
        link = self.browser.find_element_by_xpath('//*[@id="map_container"]/article/div[1]/ul/li[1]/a').get_attribute('href')
        file = link.rsplit('/', 1)[1].rsplit('.', 1)[0].replace('BNA', '').replace('%20', '_').upper()
        print(link, file)

        chart_item = ChartItem()

        chart_item['country'] = 'USA'
        chart_item['icao'] = self.country_name
        chart_item['link'] = link
        chart_item['file'] = self.country_name + '_' + file
        chart_item['desc'] = file
        chart_item['club'] = 'Parking'

        list_of_charts.append(chart_item)

        self.chart_mgr = KBNAParkingChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()
    
    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class KBNAParkingChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('KBNA')
