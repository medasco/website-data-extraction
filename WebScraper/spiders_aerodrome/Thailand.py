if __name__ == "__main__":
    pass
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class  ThailandSpider(AeroChartSpider):
    """ Thailand airport charts spider """
    name = 'Thailand'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://ais.caat.or.th'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []     # for pipe-lining
        grand_charts = []       # for summary  GRAND TOTAL
        total_charts = []
        aip_related_charts = []
        eff_issues = []

        ##
        ## Landing Page
        ##

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # Check I agree checkbox in landing page
        self.click_enable(self.browser.find_element_by_xpath('//*[@id="0"]/div/div[2]/div/label'))

        # click Submit button in landing page
        self.browser.find_element_by_xpath('//*[@id="term-btn"]').click()
        
        # Get AIP SUP and eAIP link from landing page for later use.
        aip_supp = self.browser.find_element_by_xpath('//*[@id="navbarSupportedContent"]/ul[2]/li[2]/a').get_attribute('href')
        eaip = self.browser.find_element_by_xpath('//*[@id="navbarSupportedContent"]/ul[1]/li[1]/a').get_attribute('href')

        ##
        ## SUPP Charts 
        ##

        # Enter aip_supp page
        self.browser.get(aip_supp)

        # get elements for relevant information of all supplement charts
        supplement_links = self.browser.find_elements_by_xpath('//*[@id="myTable"]/tbody/tr/td[3]/a')
        suplement_details = self.browser.find_elements_by_xpath('//*[@id="myTable"]/tbody/tr/td[4]')
        suplement_pub_date = self.browser.find_elements_by_xpath('//*[@id="myTable"]/tbody/tr/td[5]')

        # Check that total element in all categories match
        #   if a mismatch is found, spit out warning but proceed with parsing.
        if len(supplement_links) != len(suplement_details) or \
            len(supplement_links) != len(suplement_pub_date):
            
            self.logger.warning("THAILAND SUP FILE ELEMENT COUNT DOES NOT MATCH!")
            self.logger.warning("    Trust Description/Publish Dates with caution!")

        print('\nExtracting SUP for :', self.country_name)

        # iterate through list of supplement charts
        for i in range (len(supplement_links)):
            ad = supplement_links[i].get_attribute('href')
            ad_icao = "SUP"
            ad_link = ad
            ad_desc = suplement_details[i].get_attribute('innerText')
            ad_file = ad.rsplit('/', 4)[4].replace('.pdf', '') 
            pub_date = suplement_pub_date[i].get_attribute('innerText')
            cat = "SUP"

            print('\t   : {} : {} : {} : {} : {}'.format(ad_icao, ad_file, ad_desc, ad_link, cat, pub_date))
            total_charts.append([ad_icao, ad_file, ad_desc, ad_link, cat, pub_date])
            grand_charts.append(ad_file)

        print('\nDone listing [{0}] SUP(s)...'.format(len(supplement_links)))
        print('Moving to AIP(s)...')
        
        ##
        ## AIP Charts
        ##

        # Enter eaip page
        self.browser.get(eaip)
          
        # All effective issues to capture.
        #   Include here all path of effective charts.
        effective_issue_position = [
            '/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/a',    # current
            '/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[1]/a',    # next
            ]
        
        # get the links of effective issues
        for issue_links in effective_issue_position:
            eff_issues.append(self.browser.find_element_by_xpath(issue_links).get_attribute('href'))

        print(eff_issues)
        # start fetching!
        for issues in eff_issues:

            # enter issue page
            self.browser.get(issues)

            self.browser.wait(3)

            # Switch frame to 'eAISNavigationBase'
            self.browser.wait_until_located("XPATH", "//frame[@name='eAISNavigationBase']", 3)
            self.browser.switch_to.frame("eAISNavigationBase")

            # Switch frame to 'eAISNavigation'
            self.browser.wait_until_located("XPATH", "//frame[@name='eAISNavigation']", 3)
            self.browser.switch_to.frame("eAISNavigation")

            # Getting the Effectivity Date
            eff = self.browser.find_element_by_xpath('/html/body/h2')
            eff_date = ''.join([eff.text.replace('Effective', '').replace(' ', '')])
            print('\n', eff_date)

            # Go to PART 3 - AERODROMES (AD)
            self.browser.wait_until_located("XPATH", "//*[@id='AD']", 3)

            aip_charts = self.browser.find_elements_by_xpath("//*[@id='AD-2details']/div[@class='Hx']/a[contains(@onclick, ', SHOW)')]")
            rel_charts = self.browser.find_elements_by_xpath("//*[@id='AD-2details']/div[@class='level']/div[24]/a[contains(@onclick, ', SHOW)')]")
        
            print('\nExtracting AIP for :', self.country_name)

            for aip in aip_charts:
                ad = aip.get_attribute('href')
                ad_icao = ad.rsplit('.', 1)[1]
                ad_link = ad.rsplit('.', 1)[0].replace('html/eAIP', 'pdf').replace('html', 'pdf')
                ad_desc = ad_link.rsplit('/', 1)[1].rsplit('.', 1)[0]
                ad_file = ''.join([ad_desc.replace('VT-AD-2.','AD_2_'), eff_date])
                cat = "AIP-AD"

                print('\t   : {} : {} : {} : {} : {} : {}'.format(ad_icao, ad_file, ad_desc, ad_link, cat, eff_date))
                total_charts.append([ad_icao, ad_file, ad_desc, ad_link, cat, eff_date])
                grand_charts.append(ad_file)

            print('\nDone listing [{0}] ICAO(s)...'.format(len(aip_charts)))
            print('Generating AIP related chart(s)...')

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
                    name = data.find_elements_by_tag_name('p')

                    print('\nExtracting :', inn)

                    for ad_page, ad_name in list(zip(page, name)):
                        prep = [ad_page.get_attribute('href'), ad_name.text, ad_page.text]
                        rc_link = prep[0]
                        rc_desc = prep[1].replace('-', '_')
                        rc_file = ''.join([prep[2].replace(' ', '_').replace('-', '_'), eff_date])
                        rc_icao = inn
                        cat = "AIP-AD"

                        print('\t   :', rc_file)
                        total_charts.append([rc_icao, rc_file, rc_desc, rc_link, cat, eff_date])
                        grand_charts.append(rc_file)

                    print('\t     Extracted [{0}] file(s)...'.format(len(page)))


        ##
        ## Prepare CSV File for all
        ##

        for icao, file, desc, link, cat,  eff_pub_dates in total_charts:
            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['icao'] = icao
            chart_item['link'] = link
            chart_item['file'] = file
            chart_item['desc'] = desc
            chart_item['club'] = cat
            chart_item['category'] = eff_pub_dates

            list_of_charts.append(chart_item)


        # Summary
        print('\nTotal of [{0}] ICAO(s).'.format(len(aip_charts)))
        print('\nTotal of [{0}] SUP Charts.'.format(len(supplement_links)))
        print('Grand Total of  [{0}] PDF file(s).\n'.format(len(grand_charts)))

        self.chart_mgr = ThailandChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class ThailandChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Thailand')