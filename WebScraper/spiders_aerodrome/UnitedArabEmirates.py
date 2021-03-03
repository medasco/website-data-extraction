

import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class UnitedArabEmiratesSpider(AeroChartSpider):
    """ Hong Kong airport charts spider """
    name = 'UAE'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://www.google.com'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        total_charts = []
        grand_charts = []
        other_charts = []
        information_charts = []
        aip_related_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)
        self.browser.get('https://www.gcaa.gov.ae/aip/current/UAE_AIP.html')
        self.browser.wait(2)

        self.browser.wait_until_located("XPATH", '/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[1]/a', 3)
        pub = self.browser.find_element_by_xpath('/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[1]/a')
        eff_text = self.browser.find_element_by_xpath('/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]').text
        eff_date = eff_text.replace('-', '').replace(' ', '').replace('\n', '')
        print('\nEffective Date:', eff_date)
        self.click_enable(pub)

        # Switch frame to 'eAISNavigationBase'
        self.browser.wait_until_located("XPATH", "//frame[@name='eAISNavigationBase']", 3)
        self.browser.switch_to.frame("eAISNavigationBase")

        # Switch frame to 'eAISNavigation'
        self.browser.wait_until_located("XPATH", "//frame[@name='eAISNavigation']", 3)
        self.browser.switch_to.frame("eAISNavigation")

        # Go to PART 3 - AERODROMES (AD)
        self.browser.wait_until_located("XPATH", "//*[@id='AD']", 3)

        # Extracting Aerodrome and Related Charts links
        aip_charts = self.browser.find_elements_by_xpath('//*[@id="AD-2details"]/div[@class="Hx"]/a[2]')

        # Aerodrome's PDF loop
        print('\nExtracting : ICAO(s)')

        for aip in aip_charts:
            ad = aip.get_attribute('href')
            ad_icao = ad.rsplit('.', 1)[1]
            ad_link = ad.replace('html/eAIP', 'pdf').replace('-en-GB.html', '.pdf')
            ad_desc = ad_link.rsplit('#', 1)[1].replace('-', '_').replace('.', '_')
            ad_file = ''.join([ad_desc, '_', eff_date])

            print('\t   : {} : {} : {} : {}'.format(ad_icao, ad_file, ad_desc, ad_link))
            other_charts.append([ad_icao, ad])
            total_charts.append([ad_icao, ad_file, ad_desc, ad_link])
            grand_charts.append(ad_file)

        print('\t     Done listing [{0}] ICAO(s)...'.format(len(aip_charts)))
        print('\t     Extracting other related chart(s)...')

        for ad_icao, other in other_charts:
            self.browser.get(other)
            others = self.browser.find_elements_by_xpath('//div[contains(@id, "2.24")]')

            if len(others) > 0:
                data = others[0]
                page = data.find_elements_by_tag_name('a')

                print('\nExtracting :', ad_icao)

                for otc in page:
                    rc_link = otc.get_attribute('href')
                    rc_desc = rc_link.rsplit('/', 1)[1].replace('-', '_').replace('.pdf', '')
                    rc_file = ''.join([rc_desc, '_', eff_date])
                    rc_icao = ad_icao

                    print('\t   : {} : {} : {} : {}'.format(rc_icao, rc_file, rc_desc, rc_link))
                    total_charts.append([rc_icao, rc_file, rc_desc, rc_link])
                    grand_charts.append(rc_file)

                print('\t     Extracted [{0}] file(s)...'.format(len(page)))

        for icao, file, desc, link in total_charts:
            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['icao'] = icao
            chart_item['link'] = link
            chart_item['file'] = file
            chart_item['desc'] = desc
            chart_item['club'] = 'Default'
            chart_item['category'] = eff_date


            list_of_charts.append(chart_item)

        print('\nTotal of [{0}] ICAO(s).'.format(len(aip_charts)))
        print('Grand Total of  [{0}] PDF file(s).\n'.format(len(grand_charts)))

        self.chart_mgr = UnitedArabEmiratesChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class UnitedArabEmiratesChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('UnitedArabEmirates')
