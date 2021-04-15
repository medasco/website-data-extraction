
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver
from selenium.webdriver.common.action_chains import ActionChains
import time

import ctypes  # An included library with Python install

# need the following for csv reading
import csv
from pathlib import Path
import os



class VietnamSpider(AeroChartSpider):
    """ Vietnam airport charts spider """
    name = 'Vietnam'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://vnaic.vn/index.php?option=com_content&view=category&id=53%3Aaip&layout=blog&Itemid=92&lang=en'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]

        list_of_charts = []
        supp_links = []
        total_charts = []
        grand_charts = []
        aip_related_charts = []

        t = time.time()

        # Login
        username = 'psware'
        password = 'vnaic2013'

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # Get AIP Supplements link
        aip_supp = self.browser.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/div/div/div[1]/div[1]/div/ul/li[2]/a').get_attribute('href')

        # Get eAIP link
        eaip = self.browser.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/div/div/div[2]/div/div/div[3]/ul/li[2]/a').get_attribute('href')

        ##
        ## AIP-AD
        ##

        self.browser.get(eaip)

        self.browser.find_element_by_id('user').send_keys(username)
        self.browser.find_element_by_id('pass').send_keys(password)
        self.browser.find_element_by_name('submit').click()

        self.browser.wait_until_located('XPATH', '/html/body/table/tbody/tr/td[2]/div/a', 10)
        english = self.browser.find_element_by_xpath('/html/body/table/tbody/tr/td[2]/div/a').get_attribute('href')
        self.browser.get(english)

        eff = self.browser.find_element_by_xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/a")
        eff_date = ''.join(['_', eff.text.replace(' ', '')])
        
        eff.click()
        self.browser.wait(1)

        # Switch frame to 'eAISNavigationBase'
        self.browser.wait_until_located("XPATH", "//frame[@name='eAISNavigationBase']", 3)
        self.browser.switch_to.frame("eAISNavigationBase")

        # Switch frame to 'eAISNavigation'
        self.browser.wait_until_located("XPATH", "//frame[@name='eAISNavigation']", 3)
        self.browser.switch_to.frame("eAISNavigation")

        # Go to PART 3 - AERODROMES (AD)
        self.browser.wait_until_located("XPATH", '//*[@id="ADdetails"]', 3)

        # # Extract and Go to Aerodromes TOC via link (href)
        # ad = self.browser.find_element_by_xpath('//*[@id="ADdetails"]/a[1]').get_attribute('href')
        # self.browser.get(ad)

        aip_charts = self.browser.find_elements_by_xpath("//*[@id='AD-2details']/div[@class='Hx']/a[contains(@onclick, ', SHOW)')]")
        rel_charts = self.browser.find_elements_by_xpath("//*[@id='AD-2details']/div[@class='level']/div[24]/a[contains(@onclick, ', SHOW)')]")
        
        print('\nExtracting :', self.country_name)

        for aip in aip_charts:
            ad = aip.get_attribute('href')
            ad_link = ad.replace('/html/eAIP/', '/pdf/').replace('-en-GB.html', '.pdf')
            ad_desc = ad.rsplit('#', 1)[1]
            ad_icao = ad_desc.split('.')[1]
            ad_file = ''.join([ad_desc.replace('-', '_').replace('.', '_'), eff_date])

            print('\t   : {} : {} : {} : {}'.format(ad_icao, ad_file, ad_desc, ad_link))
            total_charts.append([ad_icao, ad_file, ad_desc, ad_link])
            grand_charts.append(ad_file)

        print('\nDone listing [{0}] ICAO(s)...'.format(len(aip_charts)))
        print('Generating other related chart(s)...')

        for rel in rel_charts:
            rel_link = rel.get_attribute('href')
            rel_icao = rel_link.split('#')[1].split('-')[0]
            aip_related_charts.append([rel_link, rel_icao])

        for ads, tag in aip_related_charts:
            self.browser.get(ads)
            order = self.browser.find_elements_by_xpath('//div[contains(@id, "2.24")]/div')

            if len(order) > 0:
                data = order[0]
                page = data.find_elements_by_xpath("//div[@class='Figure']/div/a")
                name = data.find_elements_by_xpath("//div[@class='Figure']/span/span/span/span")

                print('\nExtracting :', tag)


            for ad_page, ad_name in list(zip(page, name)):

                rc_link = ad_page.get_attribute('href')
                rc_desc = ad_name.text.upper()
                rc_file = ''.join([rc_link.rsplit('/', 1)[1].split('.pdf')[0].replace('-', '_').upper(), eff_date])
                rc_icao = tag

                print('\t   :', rc_file)
                total_charts.append([rc_icao, rc_file, rc_desc, rc_link])
                grand_charts.append(rc_file)

            print('\t     Extraction completed [{0}] file(s)...'.format(len(page)))

        for icao, file, desc, link in total_charts:

            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['icao'] = icao
            chart_item['link'] = link
            chart_item['file'] = file
            chart_item['desc'] = desc
            chart_item['club'] = "AIP-AD"
            chart_item['category'] = "N/A"


            list_of_charts.append(chart_item)

        print('\nTotal of [{0}] ICAO(s).'.format(len(aip_charts)))
        print('Grand Total of  [{0}] PDF file(s).\n'.format(len(grand_charts)))

        #
        # AIP SUP section
        #

        #### this part is for csv reading

        # get file base path for relative path finding of reference file
        base_path = Path(__file__).parent

        # get reference file location.
        #  relative path from manual location
        file_location = (base_path / "..\..\\reference\Airport Names List.csv").resolve()
        if not os.path.isfile(file_location):
                #  relative path from ACM
                file_location = (base_path / "..\..\..\\reference\Airport Names List.csv").resolve()
                if not os.path.isfile(file_location):
                        self.logger.warning("REFERENCE FILE OF AIRPORT NAMES NOT FOUND!")
        
        # open Airport Names List.csv from reference folder to fetch airport name icao code
        with open(file_location, 'r') as ref_file:
                csv_content = csv.reader(ref_file)
                amdb_codes = []
                for row in csv_content:
                        if self.country_name in row:
                                amdb_codes.append([row[0], row[3]])     # row 0 if icao, row 3 is name

        
        ## continue fetching sup

        browser = ChromeDriver()
        browser.get(aip_supp)

        # fetch all sup page link. extension is due to inconsistency in element hierarchy
        sup_page = browser.find_elements_by_xpath('/html/body/div/div[2]/div/div/div/div/div[2]/div/div/table[1]/tbody/tr/td[1]/em/a')
        sup_page.extend(browser.find_elements_by_xpath('/html/body/div/div[2]/div/div/div/div/div[2]/div/div/table[1]/tbody/tr/td[1]/a'))

        sup_name = browser.find_elements_by_xpath('/html/body/div/div[2]/div/div/div/div/div[2]/div/div/table[1]/tbody/tr/td[2]/p/em')
        sup_name.extend(browser.find_elements_by_xpath('/html/body/div/div[2]/div/div/div/div/div[2]/div/div/table[1]/tbody/tr/td[2]/em'))

        for sup_link, sup_title in list(zip(sup_page, sup_name)):
            sc_link = sup_link.get_attribute('href')
            sc_desc = sup_title.text
            sc_file = ''.join([sup_link.text, eff_date])

            supp_links.append([sc_link, sc_file, sc_desc])
            print('    : {} : {} : {}'.format(sc_file, sc_desc, sc_link))

        for link, file, desc in supp_links:

            chart_item = ChartItem()

            # if description has the word " AT ", then this means that airport name is followed by it.
            # If it is the case, then convert it to the airport ICAO code previously read. Otherwise, just have it as SUP  
            if " AT " in desc:
                    icao = desc.rsplit(' AT ', 2)[-1]                                  # get the string after the word " AT "   
                    airport_name = icao.split(" AERODROME")[0].split(" INTERNATIONAL")[0]  # remove the specified words so only airport name reamains
                    icao_code_converted  = 'SUP'      # pre-emptively set icao to "SUP", it will be overwritten when a match is found.                              
                    print(airport_name)
                    for icao_code, icao_name in amdb_codes: # loop through read amdb_codes from csv
                            if airport_name in icao_name:   # if airport name is found, then overwrite the SUP to corresponding icao code.
                                    icao_code_converted = icao_code                        
            else:   
                    icao_code_converted = 'SUP'

            chart_item['icao'] = icao_code_converted
            chart_item['country'] = self.country_name
            chart_item['link'] = link
            chart_item['file'] = file
            chart_item['desc'] = desc
            chart_item['club'] = 'SUP'
            chart_item['category'] = "N/A"

            list_of_charts.append(chart_item)

        self.chart_mgr = VietnamChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

        t = time.time() - t
        print('\nExtraction_time = {0}s'.format(t))

        

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class VietnamChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Vietnam')