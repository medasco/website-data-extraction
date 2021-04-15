
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class SouthAfricaSpider(AeroChartSpider):
    """ South Africa airport charts spider """
    name = 'SouthAfrica'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = 'South Africa'
        self.url = 'http://www.caa.co.za/Pages/Aeronautical%20Information/Aeronautical-charts.aspx'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        additionals = []
        total_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        print('\nExtracting :', self.country_name)

        # ICAO Loop
        for page in range(1, 3):

            print('\nScanning   : AIP page {} of 2'.format(page))

            aero = self.browser.find_elements_by_xpath("//*[@id='onetidDoclibViewTbl0']/tbody/tr/td[1]/a")
            ad_icao = self.browser.find_elements_by_xpath("//*[@id='onetidDoclibViewTbl0']/tbody/tr/td[2]/div[1]/a[1]")

            for adzip, icaozip in list(zip(aero, ad_icao)):  # 54 items
                adrome = adzip.get_attribute('href')
                name = icaozip.text.replace(' ', '').replace('(', '-').replace(')', '')
                adicao = name.replace('–', '-').split('-')[1]

                zipped = ([adrome, adicao])
                additionals.append(zipped)

                print('\t   :', adicao)

            if page != 2:
                next = self.browser.find_element_by_xpath('//*[@id="bottomPagingCellWPQ3"]/table/tbody/tr/td[2]/a')
                next.click()
                self.browser.wait(3)

        # PDF Loop
        print('\t     Extracting other additional chart(s)...')

        for achart, aicao in additionals:
            self.browser.get(achart)
            ad_link = self.browser.find_elements_by_xpath("//*[@id='onetidDoclibViewTbl0']/tbody/tr/td[2]/div[1]/a")

            print('\nExtracting :', aicao)

            for links in ad_link:
                link = links.get_attribute('href')
                desc = links.text
                file = desc

                total_charts.append(file)
                print('\t   :', desc)

                chart_item = ChartItem()

                chart_item['country'] = self.country_name
                chart_item['icao'] = aicao
                chart_item['link'] = link
                chart_item['file'] = file
                chart_item['desc'] = desc
                chart_item['club'] = 'Default'

                list_of_charts.append(chart_item)

            print('\t     Extraction completed [{0}] file(s).'.format(len(ad_link)))

        print('\nTotal of [{0}] ICAO(s).'.format(len(additionals)))  # 54 ICAO
        print('Grand Total of  [{0}] PDF file(s).\n'.format(len(total_charts)))  # 337 PDF files

        self.chart_mgr = SouthAfricaChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class SouthAfricaChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('South Africa')
