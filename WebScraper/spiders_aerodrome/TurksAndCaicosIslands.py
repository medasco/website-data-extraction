
import scrapy
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class TurksAndCaicosIslands(scrapy.Spider):
    """ Turks and Caicos Islands charts spider """
    name = 'TurksAndCaicosIslands'
    version = '1.0.0'

    def __init__(self):
        super(TurksAndCaicosIslands, self).__init__()
        self.browser = ChromeDriver()
        self.country_name = self.name
        self.chart_mgr = None

    def start_requests(self):
        """ Set the main URL to be visited
            and start the request.
        """
        url = 'http://tciairports.com/tci-aip/'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        total_charts = []
        grand_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # get the link to the AIP Ammendment chart
        aip_element = self.browser.find_element_by_xpath('//*[@id="Content"]/div/div/div/div[1]/div/div/div[2]/figure/figcaption/code/a')

        # there's only one link to download for now (july 21, 2020)
        ad = aip_element.get_attribute('href')
        ad_icao = "MBPV"    # hard-coded to the only ICAO PSW uses in this country.
        ad_link = ad
        ad_desc = "Turks and Caicos " + aip_element.get_attribute('innerText')
        ad_file = ad.rsplit('/')[9].replace('.pdf', '') 
        eff_date = ad.rsplit('-')[-3] + ad.rsplit('-')[-2] + ad.rsplit('-')[-1][:-4]

        print('\t   : {} : {} : {} : {} : {}'.format(ad_icao, ad_file, ad_desc, ad_link, eff_date))
        total_charts.append([ad_icao, ad_file, ad_desc, ad_link, eff_date])
        grand_charts.append(ad_file)

        for icao, file, desc, link, eff_pub_dates in total_charts:
            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['icao'] = icao
            chart_item['link'] = link
            chart_item['file'] = file
            chart_item['desc'] = desc
            chart_item['club'] = "AIP-AD'"
            chart_item['category'] = eff_pub_dates

            list_of_charts.append(chart_item)

        # Summary
        print('\nTotal of [{0}] ICAO(s).'.format("1 generic"))
        print('Grand Total of  [{0}] PDF file(s).\n'.format(len(grand_charts)))

        self.chart_mgr = TurksAndCaicosIslandsChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class TurksAndCaicosIslandsChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('TurksAndCaicosIslands')
