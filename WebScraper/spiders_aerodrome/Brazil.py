
import scrapy
import urllib
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver

import ctypes  # An included library with Python install.


class BrazilSpider(AeroChartSpider):
    """ Australia airport charts spider """
    name = 'Brazil'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name

        self.url = 'http://www.aisweb.aer.mil.br/?i=cartas&filtro=1&nova=1'

    def parse(self, response):
        """ Parsing callback function """

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        search = self.browser.find_element_by_xpath('//html/body/div[1]/div/div/div[2]/div/form/div/div[6]/div/input[2]')
        # print(search)
        search.click()

        # Navigate through each link and get pdf links
        pdf_links = []

        print('\nExtracting :', self.country_name)

        while True:

            # Wait for page to load and get html elements
            tableICAOs = self.browser.find_elements_by_xpath('//*[@id="datatable"]/tbody/tr/td[2]')
            tableLinks = self.browser.find_elements_by_xpath('//*[@id="datatable"]/tbody/tr/td[4]')
            tableDates = self.browser.find_elements_by_xpath('//*[@id="datatable"]/tbody/tr/td[5]')

            for icaoElement, linkElement, dateElement in list(zip(tableICAOs, tableLinks, tableDates)):
                linkElements = linkElement.find_elements_by_tag_name('a')

                if len(linkElements) > 0:
                    icao = icaoElement.text
                    date = dateElement.text
                    desc = linkElements[0].text
                    pdfLink = linkElements[0].get_attribute('href')
                    pdf_links.append([icao, desc, date, pdfLink])

                    print('\t   : {} : {} : {}'.format(icao, desc, pdfLink))


            next_button = self.browser.find_element_by_xpath('//*[@id="datatable_next"]')

            if 'disabled' not in next_button.get_attribute('class'):
                next_button.click()
                self.browser.wait(1)

                # Find button again because page is refreshed
                continue
            else:
                break

        self.browser.get('https://www.aisweb.aer.mil.br/index.cfm?i=publicacoes&p=aip')

        compEffDate = self.browser.find_element_by_xpath('//*[@id="amdt"]/div/div[2]/div/h3/strong').text.replace('AMDT ', '').replace('/', '')
        compLink = self.browser.find_element_by_xpath('//*[@id="amdt"]/div/div[2]/div/ul/li[2]/a').get_attribute('href')
        compDesc = self.browser.find_element_by_xpath('//*[@id="amdt"]/div/div[2]/div/ul/li[2]/a').text
        compICAO = 'All'
        pdf_links.append([compICAO, compDesc, compEffDate, compLink])

        print('\t   : {} : {} : {}'.format(compICAO, compDesc, compLink))

        # Prepare data for ChartPipeline
        list_of_charts = []

        for icao, desc, date, link in pdf_links:

            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['icao'] = icao
            chart_item['link'] = link
            chart_item['desc'] = desc
            chart_item['file'] = self.createFileName(icao, desc, date)
            chart_item['club'] = 'Default'

            list_of_charts.append(chart_item)

        print('\nExtraction completed [{0}] file(s).\n'.format(len(pdf_links)))

        self.chart_mgr = BrazilChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    @staticmethod
    def createFileName(icao, desc, date):
        newDesc = desc.replace('/', ' ').replace('-', ' ').replace('—', ' ').replace('_', ' ')
        while '  ' in newDesc:
            newDesc = newDesc.replace('  ', ' ')
        name = icao + '_' + newDesc.replace(' ', '_') + '_' + date.replace('.', '')
        return name

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class BrazilChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Brazil')
