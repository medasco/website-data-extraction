
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class SIRLSupplementSpider(AeroChartSpider):
    """ Ireland supplementary charts spider """
    name = 'SIRL'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://www.iaa.ie/commercial-aviation/aeronautical-information-management-1/iaip'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        iaip = self.browser.find_element_by_xpath('//*[@id="Body_TA62696B2010_Col01"]/div/div/p[2]/a').get_attribute('href')
        self.browser.get(iaip)

        self.click_enable(self.browser.find_element_by_xpath('/html/body/div/table/tbody/tr[2]/td[1]/h6/a'))
        self.browser.switch_to.frame("Left")

        supp = self.browser.find_element_by_xpath('/html/body/div/h5[3]/a').get_attribute('href')
        self.browser.get(supp)

        supp_charts = self.browser.find_elements_by_xpath('/html/body/div/table/tbody/tr/td/h6/span/a')
        supp_subjct = self.browser.find_elements_by_xpath('/html/body/div/table/tbody/tr/td[3]/h4/span')
        supp_sction = self.browser.find_elements_by_xpath('/html/body/div/table/tbody/tr/td[4]/h4/span')
        for h6, h4,td in list(zip(supp_charts, supp_subjct, supp_sction)):
            link = h6.get_attribute('href')
            desc = h4.text.replace('\n', ' ')
            icao = td.text.split(' ')[0] if 'EI' in td.text else 'SUPP'
            file = link.rsplit('/', 1)[1].split('.')[0]
            print('\t   : {} : {} : {} : {}'.format(icao, file, desc, link))

            chart_item = ChartItem()

            chart_item['country'] = 'Finland (EF)'
            chart_item['icao'] = self.country_name
            chart_item['link'] = link
            chart_item['file'] = self.country_name + '_' + file
            chart_item['desc'] = file
            chart_item['club'] = 'Supplementary'

            list_of_charts.append(chart_item)

        self.chart_mgr = SIRLSupplementPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class SIRLSupplementPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('SIRL')
