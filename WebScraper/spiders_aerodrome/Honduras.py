
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class HondurasSpider(AeroChartSpider):
    """ Honduras airport charts spider """
    name = 'Honduras'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'http://ahac.gob.hn/'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        total_charts = []
        grand_charts = []
        aip_related_charts = []
        eff_issues = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # close pop up
        self.browser.wait_until_located("XPATH", '//*[@id="elementor-popup-modal-4333"]/div/div[4]/i', 3)

        # go to EAIP
        eaip = self.browser.find_element_by_xpath('//*[@id="menu-item-209"]/a').get_attribute('href')
        self.browser.get(eaip)

        # get links for current and next issue
        current_issue = self.browser.find_element_by_xpath('/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[1]/a').get_attribute('href')
        eff_issues.append(current_issue)
        next_issue = self.browser.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/a').get_attribute('href')
        eff_issues.append(next_issue)
        
        for issue in eff_issues:

            # go to issue page
            self.browser.get(issue)
            # Switch frame to 'eAISNavigationBase'
            self.browser.wait_until_located("XPATH", "//frame[@name='eAISNavigationBase']", 1)
            self.browser.switch_to.frame("eAISNavigationBase")

            # Switch frame to 'eAISNavigation'
            self.browser.wait_until_located("XPATH", "//frame[@name='eAISNavigation']", 1)
            self.browser.switch_to.frame("eAISNavigation")

            # Go to PART 3 - AERODROMES (AD)
            self.browser.wait_until_located("XPATH", '//*[@id="ADdetails"]', 3)

            aip_charts = self.browser.find_elements_by_xpath("//*[@id='AD-2details']/div[@class='H3']/a[contains(@onclick, ', SHOW)')]")
            rel_charts = self.browser.find_elements_by_xpath("//div[contains(@id, 'AD-2.eAIP')]/div[24]/a")

            eff_date = self.browser.find_element_by_xpath('/html/body/h2').text.replace('Efectivo ', '').replace(' ', '_')

            print('\nGenerating AIP chart(s)')

            for aip in aip_charts:
                ad = aip.get_attribute('href')
                ad_icao = ad.rsplit('.', 1)[1]
                ad_link = ad.rsplit('.', 1)[0].replace('html/eAIP', 'pdf').replace('html', 'pdf')
                ad_desc = ad.split('ES')[1].replace('-AD-2', 'AD_2').replace('-es-', '')
                ad_file = ''.join([ad_desc, '_', eff_date])
                ad_eff = eff_date

                print('\t   : {} : {} : {} : {} :'.format(ad_icao, ad_file, ad_desc, ad_link, ad_eff))
                total_charts.append([ad_icao, ad_file, ad_desc, ad_link, ad_eff])
                grand_charts.append(ad_file)

            print('\nDone listing [{0}] ICAO(s)...'.format(len(aip_charts)))
            print('Generating other related chart(s)...')

            for rel in rel_charts:
                rel_link = rel.get_attribute('href')
                rel_icao = rel_link.split('#')[1].split('-')[0]
                aip_related_charts.append([rel_link, rel_icao])

            for ads, inn in aip_related_charts:
                self.browser.get(ads)
                order = self.browser.find_elements_by_xpath('//div[contains(@id, "2.24")]/table/tbody')

                if len(order) > 0:
                    data = order[0]
                    page = data.find_elements_by_tag_name('a')

                    print('\nExtracting :', inn)

                    for rc_page in page:
                        rc_link = rc_page.get_attribute('href')
                        rc_icao = inn
                        rc_desc = rc_link.rsplit('/', 1)[1].split('.')[1].replace('-', '_').replace('%20','_')
                        rc_file = ''.join([rc_desc, '_', eff_date])
                        rc_eff= eff_date

                        # print('\t   : {} : {} : {} : {} :'.format(rc_icao, rc_file, rc_desc, rc_link))
                        print('\t   :', rc_file)
                        total_charts.append([rc_icao, rc_file, rc_desc, rc_link, rc_eff])
                        grand_charts.append(rc_file)

                    print('\t     Extracted [{0}] file(s)...'.format(len(page)))

            for icao, file, desc, link, eff in total_charts:
                chart_item = ChartItem()

                chart_item['country'] = self.country_name
                chart_item['icao'] = icao
                chart_item['link'] = link
                chart_item['file'] = file
                chart_item['desc'] = desc
                chart_item['club'] = 'Default'
                chart_item['category'] = eff

                list_of_charts.append(chart_item)

        print('\nTotal of [{0}] ICAO(s).'.format(len(aip_charts)))
        print('Grand Total of  [{0}] PDF file(s).\n'.format(len(grand_charts)))

        self.chart_mgr = HondurasChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class HondurasChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Honduras')