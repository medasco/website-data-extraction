
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class AustraliaSpider(AeroChartSpider):
    """ Australia airport charts spider """
    name = 'Australia'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://www.airservicesaustralia.com/aip/current/dap/AeroProcChartsTOC.htm'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        pub = self.browser.find_element_by_xpath('//*[@id="Titles"]/p[1]')
        pub_date = pub.text.split('to ')[1].split(' ')[0].upper()
        print('\nEffective until :', pub_date)

        # pdf_icao = self.browser.find_elements_by_xpath('//*[@id="MainSection"]/h3')
        pdf_main = self.browser.find_elements_by_xpath('//*[@id="MainSection"]/table/tbody/tr/td/a')
        pdf_date = self.browser.find_elements_by_xpath('//*[@id="MainSection"]/table/tbody/tr/td[3]')

        print('\nExtracting :')

        otherFiles = []

        for paths, dates, descs in list(zip(pdf_main, pdf_date, pdf_main)):
            tagged = paths.get_attribute('href')
            zipped = [tagged, dates.text, descs.text] if tagged != '' else [None, dates.text, descs.text]

            if tagged is not None:

                link = zipped[0]
                date = ''.join(zipped[1].split(' '))
                desc = zipped[2]
                file = link.split('/')[-1].split('.')[0].split('_')[0]
                icao = 'Y' + file[:3].upper()

                otherFiles.append(file)

                # print('\t   : {} : {} : {} : {} : {}'.format(icao, file, date, desc, link))

                chart_item = ChartItem()

                chart_item['country'] = self.country_name
                chart_item['icao'] = icao
                chart_item['link'] = link
                chart_item['desc'] = desc
                chart_item['file'] = file + '_' + date
                chart_item['club'] = 'Default'

                list_of_charts.append(chart_item)

        print('\nTotal of  [{0}] Extracted Chart(s)...\n'.format(len(otherFiles)))

        self.chart_mgr = AustraliaChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class AustraliaChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Australia')
