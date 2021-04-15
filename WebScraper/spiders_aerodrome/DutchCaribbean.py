
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver
from selenium import webdriver


class DutchCaribbeanSpider(AeroChartSpider):
    """ DutchCaribbean airport charts spider """
    name = 'DutchCaribbean'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'http://dc-ansp.org/'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        publications = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # Going AIS
        ais = self.browser.find_element_by_xpath('//*[@id="menu-item-2009"]/a').get_attribute('href')
        self.browser.get(ais)

        # Click 'I Agree'
        agree = self.browser.find_element_by_xpath('/html/body/div[6]/div[2]/div[2]/div/a').get_attribute('href')
        self.browser.get(agree)

        # Going Publications tab then SUP
        aip_supp = self.browser.find_element_by_xpath('//*[@id="menu-item-2371"]/a').get_attribute('href')

        # Going Publications tab then EAIP
        eaip = self.browser.find_element_by_xpath('//*[@id="menu-item-2367"]/a').get_attribute('href')
        self.browser.get(eaip)

        # Switch frame to 'CoverBody'
        self.browser.wait_until_located("XPATH", "//frame[@name='CoverBody']", 3)
        self.browser.switch_to.frame("CoverBody")

        # Get AIP Current Issue and AIP Next Issue appending it in Publications List
        aip = self.browser.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/h2/table/tbody/tr/td[1]/a').get_attribute('href')
        publications.append(aip)
        aip_next = self.browser.find_element_by_xpath('/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[1]/a').get_attribute('href')
        publications.append(aip_next)

        for issue in publications:

            # Getting each issue's link
            self.browser.get(issue)

            # Switch frame to 'eAISNavigationBase'
            self.browser.wait_until_located("XPATH", "//frame[@name='eAISNavigationBase']", 3)
            self.browser.switch_to.frame("eAISNavigationBase")

            # Switch frame to 'eAISNavigation'
            self.browser.wait_until_located("XPATH", "//frame[@name='eAISNavigation']", 3)
            self.browser.switch_to.frame("eAISNavigation")

            # Getting the Publication Date
            eff = self.browser.find_element_by_xpath('/html/body/h2')
            eff_date = eff.text
            eff_date = eff_date.replace('Effective ', '').replace(' ', '_')
            print('\n', eff_date)

            # Go to PART 3 - AERODROMES (AD)
            self.browser.wait_until_located("XPATH", "//*[@id='AD_2details']", 3)

            # Extracting Aerodrome Individual and Related Charts links
            origin = self.browser.find_elements_by_xpath("//*[@id='AD_2_01details']/div[@class='Hx']")

            # Aerodrome's Individual Chart Links loop
            print('\nExtracting :', self.country_name)

            href_charts = []
            html_charts = []
            total_charts = []
            grand_charts = []

            for aero in origin:
                page = aero.find_elements_by_tag_name('a')

                for ad in page:
                    href = ad.get_attribute('href')
                    href_charts.append(href)

            for bind in href_charts:
                self.browser.get(bind)
                order = self.browser.find_element_by_xpath('//*[@id="IncludeFileBottom"]').get_attribute('src')
                html_charts.append(order)

            for dock in html_charts:
                olink = dock.replace('_BChart', '').replace('html', 'pdf')
                oicao = dock.split('2.1')[1][:4]
                ofile = olink.rsplit('/', 1)[1].replace('.pdf', '') + '_' + eff_date
                odesc = ofile.replace('.', '_')
                total_charts.append([oicao, olink, ofile, odesc])
                grand_charts.append(ofile)

                self.browser.get(dock)
                adicao = oicao
                dash = self.browser.find_elements_by_xpath('/html/body/table[1]/tbody/tr/td[2]/a[2]')

                print('\nExtracting :', adicao)
                print('\t   :', olink)
                print('\t     Generating other related chart(s)...')

                for leaf in dash:
                    adlink = leaf.get_attribute('href')
                    adtext = leaf.text
                    adfile = adtext.replace('.pdf', '') + '_' + eff_date
                    addesc = adfile.replace(' ', '_')
                    total_charts.append([adicao, adlink, adfile, addesc])
                    grand_charts.append(adfile)
                    print('\t   :', adlink)

            for icao, link, file, desc in total_charts:

                chart_item = ChartItem()

                chart_item['country'] = 'Aruba' if icao =='TNCA' else 'Curacao' if icao =='TNCC' else 'St. Martin' if icao =='TNCM' else self.country_name
                chart_item['icao'] = icao
                chart_item['link'] = link
                chart_item['file'] = file
                chart_item['desc'] = desc
                chart_item['club'] = 'Default'
                chart_item['category'] = eff_date

                list_of_charts.append(chart_item)

            print('\nTotal of [{0}] ICAO(s).'.format(len(origin)))
            print('Grand Total of  [{0}] PDF file(s).\n'.format(len(grand_charts)))

            supp_links = []
            browser = ChromeDriver()
            browser.get(aip_supp)

            slide = browser.find_element_by_xpath('//*[@id="supplements"]/div/div/div')
            supLinks = slide.find_elements_by_tag_name('a')

            for sup in supLinks:
                suplink = sup.get_attribute('href')
                supfile = sup.text.replace(' - ', '_').replace(' _ ', '_').replace('- ', '_')
                supdesc = supfile.split('_')[0].upper() if '-ATS' not in supfile else supfile.split('-ATS')[0].upper()
                supicao = 'TNC' + supfile.split('TNC')[1][:1] if 'TNC' in supfile else 'SUPP'

                supp_links.append([suplink, supfile, supicao, supdesc])
                print('    : {} : {} : {} : {}'.format(supicao, supdesc, supfile, suplink))

            for link, file, icao, desc in supp_links:

                chart_item = ChartItem()

                chart_item['country'] = 'Aruba' if icao=='TNCA' else 'Curacao' if icao=='TNCC' else 'St. Martin' if icao=='TNCM' else self.country_name
                chart_item['icao'] = icao
                chart_item['link'] = link
                chart_item['file'] = file
                chart_item['desc'] = desc
                chart_item['club'] = 'Default'

                list_of_charts.append(chart_item)

        self.chart_mgr = DutchCaribbeanChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class DutchCaribbeanChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('DutchCaribbean')
