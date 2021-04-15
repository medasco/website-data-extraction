

import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class DominicanRepublicSpider(AeroChartSpider):
    """ Dominican Republic airport charts spider """
    name = 'DominicanRepublic'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = 'Dominican Republic'
        self.url = 'https://www.google.com'#'https://aip.idac.gob.do/' 

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        port_list = []
        total_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)
        self.browser.get('https://aip.idac.gob.do/')
        self.browser.wait(3)

        # click upper tab for Aeronautical Publications
        self.click_enable(self.browser.find_element_by_xpath('//*[@id="navbarResponsive"]/ul/li[2]/a'))

        # click sidebar's AIP
        self.click_enable(self.browser.find_element_by_xpath('//*[@id="sidebar-container"]/ul/a[1]/div'))

        # click AIP sub-item Aerodromes (AD)
        self.click_enable(self.browser.find_element_by_xpath('//*[@id="submenu1"]/a[3]'))

        # click content "Aeronautical Chart Relative to the Aerodrome"
        self.click_enable(self.browser.find_element_by_xpath('//*[@id="content-right"]/div/a[3]'))

        # get necessary airport charts in a list
        airports = self.browser.find_elements_by_xpath('//*[@id="ad2"]/a')
        for ads in airports:
            port_list.append(ads.get_attribute('href'))

        print('\nExtracting :', self.country_name)

        for port in port_list:
            self.browser.get(port)
            port_icao = port.rsplit('/', 1)[1].replace(' ','').replace('AdData', '').upper()
            ad_datas = self.browser.find_element_by_xpath('//*[@id="content-right"]/div/a[1]')
            self.click_enable(ad_datas)
            aero_datas = self.browser.find_elements_by_xpath('//*[@id="ad0"]/a')

            print('Aerodrome Charts : ', port_icao)

            for aerodata in aero_datas:
                aerolink = aerodata.get_attribute('href')
                aeroicao = port_icao
                aerofile = aerolink.rsplit('/', 1)[1].replace('.pdf', '').upper()
                aerodesc = aerofile

                print('\t   : {} : {} : {} : {}'.format(aeroicao, aerofile, aerodesc, aerolink))
                total_charts.append([aeroicao, aerofile, aerodesc, aerolink])

            aeroChart = self.browser.find_element_by_xpath('//*[@id="ad3"]/a[1]').get_attribute('href')
            self.browser.get(aeroChart)
            adCharts = self.browser.find_elements_by_xpath('//*[@id="sid0"]/a')

            print('Relative Charts : ', port_icao)

            for adchart in adCharts:
                adlink = adchart.get_attribute('href')
                adicao = port_icao
                adfile = adlink.rsplit('/', 1)[1].replace('.pdf', '').upper()
                addesc = adfile

                print('\t   : {} : {} : {} : {}'.format(adicao, adfile, addesc, adlink))
                total_charts.append([adicao, adfile, addesc, adlink])

        for icao, file, desc, link in total_charts:
            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['icao'] = icao
            chart_item['link'] = link
            chart_item['file'] = file
            chart_item['desc'] = desc
            chart_item['club'] = 'Default'

            list_of_charts.append(chart_item)

        for chart in list_of_charts:
            if 'html' in chart['link']:
                list_of_charts.remove(chart)

        for chart in list_of_charts:
            if chart['file'] == '':
                list_of_charts.remove(chart)

        self.chart_mgr = DominicanRepublicChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class DominicanRepublicChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Dominican Republic')
