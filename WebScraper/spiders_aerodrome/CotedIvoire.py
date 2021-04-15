
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class CotedIvoireSpider(AeroChartSpider):
    """ CotedIvoire airport charts spider """
    name = "CotedIvoire"
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = "Cote d'Ivoire"

        self.url = 'https://ais.asecna.aero/en/ad/ad2.htm'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        total_charts = []
        aerodromes = []

        base_url = 'https://ais.asecna.aero/'

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        icoast = self.browser.find_element_by_xpath('//*[@id="margin1"]/ul/li[8]/img')
        icoast.click()

        achart = self.browser.find_element_by_xpath('//*[@id="margin1"]/ul/li[8]/ul[1]')
        adrome = achart.find_elements_by_tag_name('a')

        for adchart in adrome:
            acharts = adchart.get_attribute('onclick')
            atlas = adchart.get_attribute('href')

            if acharts is not None:
                aerodromes.append(acharts)

            if 'abidjan.htm' in atlas:
                aerodromes.append(atlas)

        for adlink in aerodromes:

            if '../../' and 'DIAP' in adlink:
                pdlinks = base_url + adlink.split(',')[0].split('../../')[1].replace("'", '')
                total_charts.append(pdlinks)

            elif '.htm' in adlink:
                self.browser.get(adlink)
                tbody = self.browser.find_element_by_xpath('//*[@id="marge"]/table/tbody')
                image = tbody.find_elements_by_tag_name('a')

                for img in image:
                    imlink = img.get_attribute('onclick')
                    imlinks = base_url + imlink.split(',')[0].split('../../../')[1].replace("'", '')
                    total_charts.append(imlinks)


        for chartLinks in total_charts:

            link = chartLinks
            file = link.rsplit('/', 1)[1].replace('.pdf', '')
            desc = file.replace('-', '_').upper()
            icao = 'DIAP'
            category = link.split('/')[4].upper()

            print('\t   : {} : {} : {} : {} : {}'.format(icao, file, desc, category, link))

            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['category'] = category
            chart_item['icao'] = icao
            chart_item['link'] = link
            chart_item['file'] = file
            chart_item['desc'] = desc
            chart_item['club'] = 'Default'

            list_of_charts.append(chart_item)

        self.chart_mgr = CotedIvoireChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class CotedIvoireChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list("Coted d'Ivoire")
