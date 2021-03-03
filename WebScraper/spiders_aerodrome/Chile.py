
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver
import time


class ChileSpider(AeroChartSpider):
    """ Chile airport charts spider """
    name = 'Chile'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name

        self.url = 'https://www.aipchile.gob.cl/aip/vol1/seccion/ad'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        supp_links = []
        total_charts = []
        grand_charts = []

        t = time.time()

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # Get AIP Supplements
        sup_charts = self.browser.find_element_by_xpath('//*[@id="tabnav3"]/div[5]/div/div/div/a').get_attribute('href')
        aip_charts = self.browser.find_elements_by_xpath("//*[@id='cat2']/li/a")
        ad2_charts = self.browser.find_elements_by_xpath('//*[@id="cat3"]/li/a')

        print('\nExtracting :', self.country_name)

        for aip in aip_charts:
            ad_link = aip.get_attribute('href')
            ad_desc = aip.get_attribute('title').replace('Bajar archivo ', '').replace(' ','_')[2:].replace('2.0-1', 'AD')
            ad_icao = ad_link.rsplit('/', 1)[1].rsplit('%20', 1)[1].split('.')[0]
            ad_file = ad_link.rsplit('/', 1)[1].replace('%20', '_').replace('.pdf', '')[2:].replace('2.0-1', 'AD')

            print('\t   : {} : {} : {} : {}'.format(ad_icao, ad_file, ad_desc, ad_link))
            total_charts.append([ad_icao, ad_file, ad_desc, ad_link])
            grand_charts.append(ad_file)

        print('Done listing [{0}] ICAO(s)...'.format(len(aip_charts)))
        print('\nGenerating AD 2a chart(s)')

        # Process AD 2a links
        for ad2 in ad2_charts:
            ad2_link = ad2.get_attribute('href')
            ad2_desc = 'AD_' + ad2.get_attribute('title').split('AD ')[1].replace(' ', '_')
            ad2_icao = ad2.get_attribute('title')[-4:]
            ad2_file = ad2_desc

            total_charts.append([ad2_icao, ad2_file, ad2_desc, ad2_link])
            grand_charts.append(ad2_file)

        print('Done generating AD 2a chart(s)\n')
        print('Generating supplementary chart(s)...')

        self.browser.get(sup_charts)
        sup_page = self.browser.find_elements_by_xpath('//*[@id="cat0"]/li/a')

        for sup in sup_page:
            sup_link = sup.get_attribute('href')
            sup_desc = sup_link.rsplit('/', 1)[1].split('.')[0].replace('%20', '_').upper()
            sup_file = sup_desc
            sup_icao = sup_file[:15]

            print('\t   : {} : {} : {} : {}'.format(sup_icao, sup_file, sup_desc, sup_link))
            total_charts.append([sup_icao, sup_file, sup_desc, sup_link])
            grand_charts.append(ad_file)

        for icao, file, desc, link in total_charts:

            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['icao'] = icao
            chart_item['link'] = link
            chart_item['file'] = file
            chart_item['desc'] = desc
            chart_item['club'] = 'Default'

            list_of_charts.append(chart_item)

        print('\nTotal of [{0}] ICAO(s).'.format(len(aip_charts)))
        print('Grand Total of  [{0}] PDF file(s).\n'.format(len(grand_charts)))

        self.chart_mgr = ChileChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

        t = time.time() - t
        print('\nExtraction_time = {0:.3f} sec'.format(t))

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class ChileChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Chile')
