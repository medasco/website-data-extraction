import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver
from selenium import webdriver


class CostaRicaSpider(AeroChartSpider):
    """ Costa Rica airport charts spider """
    name = 'CostaRica'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        # self.browser = webdriver.PhantomJS() # without GUI
        self.country_name = 'Costa Rica'
        self.ICAOs = ['MROC', 'MRLB']

        self.url = 'http://www.dgac.go.cr/tecnicos-aeronauticos/aip-en-espanol-e-ingles/'

    def parse(self, response):
        # go to main url
        self.browser.get(response.url)
        # get pdf urls
        listOfPdfUrls = []  # list of pdf urls
        xpathsUrl = self.browser.find_elements_by_xpath('//a[@href]')
        for xpath in xpathsUrl:
            if str(xpath.get_attribute('href')).lower().split('.')[-1] == 'pdf':
                listOfPdfUrls.append(xpath.get_attribute('href'))

        list_of_charts = []
        for ICAO in self.ICAOs:
            for url in listOfPdfUrls:
                file = url.split('/')[-1].split('.pdf')[0]
                icao = ICAO
                desc = file

                chart_item = ChartItem()

                chart_item['country'] = self.country_name
                chart_item['icao'] = icao
                chart_item['link'] = url
                chart_item['file'] = file
                chart_item['desc'] = desc
                chart_item['club'] = 'Default'

                list_of_charts.append(chart_item)

        self.chart_mgr = CostaRicaChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class CostaRicaChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('CostaRica')
