
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class IsraelSpider(AeroChartSpider):
    """ Israel airport charts spider """
    name = 'Israel'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'http://en.caa.gov.il/index.php?option=com_content&view=article&id=409&Itemid=273'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        total_charts = []
        aero_list = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        self.browser.wait_until_located('XPATH', '//*[@id="jsn-footer"]', 10)

        # Go to Aerodromes
        aero = self.browser.find_elements_by_xpath('//li[@class="parent active item273 order6 last current"]/ul/li')

        for ad in aero:

            drome = ad.find_elements_by_tag_name('a')

            if len(drome) > 0:
                tabLink = drome[0].get_attribute('href')
                tabName = drome[0].text.rsplit(' ')[-1]
                aero_list.append([tabName, tabLink])
                print('{} : {}'.format(tabName, tabLink))

        for icao, href in aero_list:
            self.browser.get(href)
            pdfCharts = self.browser.find_elements_by_xpath('//*[@id="jsn-mainbody"]/table[2]')

            print('\nExtracting :', icao)

            for tag in pdfCharts:
                chartLinks = tag.find_elements_by_tag_name('a')

                for pot in chartLinks:
                    links = pot.get_attribute('href')
                    files = pot.text.replace('/O', '').replace('/0', '')
                    descs = files.replace('AD ', 'AD_')

                    if files != '':
                        print('{} : {} : {} : {}'.format(icao, descs, files, links))
                        total_charts.append([icao, descs, files, links])

        for icao, desc, file, link in total_charts:

            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['icao'] = icao
            chart_item['link'] = link
            chart_item['file'] = file
            chart_item['desc'] = desc
            chart_item['club'] = 'Default'

            list_of_charts.append(chart_item)

        self.chart_mgr = IsraelChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class IsraelChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Israel')
