
import scrapy
import time
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class ArgentinaSpider(AeroChartSpider):
    """ Argentina aiport charts spider """
    name = 'Argentina'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'http://ais.anac.gov.ar/aip'

    def parse(self, response):
        """ Parsing callback function """
        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # Wait for the page to load: default (only for satic pages)
        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        total_charts = []

        # Traverse the page and find the 'Ad' link and click it!
        self.click_enable(self.browser.find_element_by_xpath('//*[@id="ad"]/a'))
        self.scroll_down_window_height()

        adrome = self.browser.find_elements_by_xpath('//*[@id="datatable"]/tbody/tr')

        for ad in adrome:
            adtags = ad.find_elements_by_tag_name('a')
            addesc = ad.text
            adlink = adtags[0].get_attribute('href')
            adfile = addesc.split(' - ')[0].replace(' Aeródromos', '').replace('-', '_')
            adicao = adfile[:6].replace('_A', '')

            print('\t   : {} : {} : {} : {}'.format(adicao, adfile, addesc, adlink))
            total_charts.append([adicao, adfile, addesc, adlink])

        # Traverse the page and find the 'Vol-3' link and click it!
        self.click_enable(self.browser.find_element_by_xpath('//*[@id="mapri"]/a'))
        self.scroll_down_window_height()

        volume = self.browser.find_elements_by_xpath('//*[@id="datatable"]/tbody/tr')

        for vol in volume:
            voltags = vol.find_elements_by_tag_name('a')
            voldesc = vol.text
            vollink = voltags[0].get_attribute('href')
            volfile = voldesc.split(' - ')[0]
            volicao = volfile.replace('Vol-3 ', '')

            print('\t   : {} : {} : {} : {}'.format(volicao, volfile, voldesc, vollink))
            total_charts.append([volicao, volfile, voldesc, vollink])

        # Traverse back to the top of the page and click the home logo; can be made into a method (TODO)
        self.browser.execute_script("window.scrollTo(0, 0);")
        self.browser.wait(2)

        self.click_enable(self.browser.find_element_by_xpath('//*[@href="./"]'))
        self.scroll_down_window_height()

        # Traverse the page and find the "SUP" link and click it
        self.click_enable(self.browser.find_element_by_xpath('//*[@href="/sup"]'))
        self.scroll_down_window_height()


        supplement = self.browser.find_elements_by_xpath('//*[@id="datatable"]/tbody/tr')

        for sup in supplement:
            suptags = sup.find_elements_by_tag_name('a')
            supdesc = sup.text
            suplink = suptags[0].get_attribute('href')
            supicao = supdesc.split('(')[1].split(')')[0]
            supfile = supicao + ' SUP'
            

            print('\t   : {} : {} : {} : {}'.format(supicao, supfile, supdesc, suplink))
            total_charts.append([supicao, supfile, supdesc, suplink])

        for icao, file, desc, link in total_charts:

            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['icao'] = icao
            chart_item['link'] = link
            chart_item['file'] = file
            chart_item['desc'] = desc
            chart_item['club'] = 'Default'

            list_of_charts.append(chart_item)

        # Process extracted ChartItem list
        self.chart_mgr = ArgentinaChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def scroll_down_window_height(self):
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.browser.wait(2)

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class ArgentinaChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Argentina')
