
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class KoreaSpider(AeroChartSpider):
    """ South Korea airport charts spider """
    name = 'Korea'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = "South Korea"
        self.url = 'http://ais.casa.go.kr/'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        aip_charts = []
        total_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        self.browser.wait_until_located("XPATH", "//frame[@name='mainFrame']", 3)
        self.browser.switch_to.frame("mainFrame")

        # Get into AIP General location
        aip_general_link = self.browser.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/a[1]').get_attribute('href')
        self.browser.get(aip_general_link)

        # Get address of aip_AD and aip_SUP for later use
        eaip_link = self.browser.find_element_by_xpath('/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[3]/table/tbody/tr/td/table[1]/tbody/tr/td[2]/a').get_attribute('href')
        aip_AD_link = self.browser.find_element_by_xpath('/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[1]/table/tbody/tr[4]/td/a').get_attribute('href')
        aip_SUP_link = self.browser.find_element_by_xpath('/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[1]/table/tbody/tr[6]/td/a').get_attribute('href')

        ##
        ## AIP_SUPP section
        ##

        # get into SUPP location
        self.browser.get(aip_SUP_link)        

        # capture supp elements
        sup_element = self.browser.find_elements_by_xpath('/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[3]/' +
                                                         'table/tbody/tr/td/table[2]/tbody/tr[2]/td[2]/table/tbody' +
                                                          '/tr/td/table/tbody/tr[@bgcolor="#FFFFFF"]/td[1]/a')
        sup_eff_dates = self.browser.find_elements_by_xpath('/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[3]/' + 
                                                          'table/tbody/tr/td/table[2]/tbody/tr[2]/td[2]/table/tbody' +
                                                            '/tr/td/table/tbody/tr[@bgcolor="#FFFFFF"]/td[2]')
        download_button = self.browser.find_elements_by_xpath('/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[3]/' +
                                                            'table/tbody/tr/td/table[2]/tbody/tr[2]/td[2]/table/tbody' +
                                                            '/tr/td/table/tbody/tr[@bgcolor="#FFFFFF"]/td[3]/a')

        # process captured supp elements
        for i in range (len(sup_element)):
            link = download_button[i].get_attribute('href')
            desc = sup_element[i].get_attribute('innerText')

            chart_item = ChartItem()
            chart_item['country'] = self.country_name
            chart_item['icao'] = desc.split(None,4)[3].split('_')[0]
            chart_item['link'] = link
            chart_item['desc'] = desc
            chart_item['file'] = "SUP_" + desc.split(None,4)[2] + "_" + desc.split(None,4)[3].split('_')[0]
            chart_item['club'] = "SUP"
            chart_item['category'] = sup_eff_dates[i].get_attribute('innerText')

            print(chart_item['file'])
            list_of_charts.append(chart_item)

        ##
        ## AIP_AD section (GENERAL)
        ##

        # get into AD location
        self.browser.get(aip_AD_link)

        #Get links for each AD
        ad_links = self.browser.find_elements_by_xpath("/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[3]/table/" +
                                                       "tbody/tr/td/table[2]/tbody/tr[2]/td[2]/table/tbody/tr/td/" +
                                                       "table/tbody/tr/td[2]/a")

        temp_list = []
        for i in ad_links:
            temp_list.append(i.get_attribute('href'))

        for i in temp_list:
            
            self.browser.get(i)
            self.browser.wait(5)
            pdf_links = self.browser.find_elements_by_xpath("/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[3]/" +
                                                            "table/tbody/tr/td/table[2]/tbody/tr[2]/td[2]/table/" +
                                                            "tbody/tr/td/table/tbody/tr/td/a")
                                                            
            for (idx, a_tag) in enumerate(pdf_links):
                if idx % 2 == 0:
                    split_length = len(pdf_links[idx + 1].text.split(' '))

                    chart_item = ChartItem()
                    chart_item['country'] = self.country_name
                    chart_item['icao'] = pdf_links[idx + 1].text.split(' ')[0] if split_length > 1 else \
                        pdf_links[idx + 1].text.split('-')[0]
                    chart_item['link'] = a_tag.get_attribute('href')
                    chart_item['desc'] = pdf_links[idx + 1].text.split('.pdf')[0]
                    chart_item['file'] = pdf_links[idx + 1].text.replace(' ', '_').split('(0)')[0].split('(1)')[0].split('.pdf')[0]
                    chart_item['club'] = 'AD-AIP'
                    chart_item['category'] = "AIP"

                    print(chart_item['file'])
                    list_of_charts.append(chart_item)

         ##
        ## AIP_AD section (eAIP)
        ##

        # get into e-aip link
        self.browser.get(eaip_link)

        # Get all Currently EFfective and Next Issues Link
        pre_process_list = []
        pre_process_list = self.browser.find_elements_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/a')
        pre_process_list.extend(self.browser.find_elements_by_xpath('/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[1]/a'))

        # get aip links and effectivity dates to process while still in eAIP home page
        for aip in pre_process_list:
            aip_captured_eff_date = aip.get_attribute('innerText')
            aip_captured_link = aip.get_attribute('href')

            aip_charts.append([aip_captured_eff_date, aip_captured_link])

        # start processing aip!
        for aip_eff_date, aip_ink in aip_charts:

            # get into aip page
            self.browser.get(aip_ink)

            # Switch frame to 'eAISNavigationBase'
            self.browser.wait_until_located("XPATH", "//frame[@name='eAISNavigationBase']", 3)
            self.browser.switch_to.frame("eAISNavigationBase")

            # Switch frame to 'eAISNavigation'
            self.browser.wait_until_located("XPATH", "//frame[@name='eAISNavigation']", 3)
            self.browser.switch_to.frame("eAISNavigation")          

            # Go to PART 3 - AERODROMES (AD)
            ad = self.browser.find_element_by_xpath("//*[@id='AD']").get_attribute('href')
            self.browser.get(ad)

            # Extracting Aerodrome and Related Charts links
            ad_icao_link = self.browser.find_elements_by_xpath("//*[@id='6Lm7VJUIfG']/div[2]/div/h3/a")
  

            # Aerodrome's PDF loop
            print('\nExtracting :', self.country_name)

            additional_checking = []
            for entry in ad_icao_link:
                additional_checking.append(entry.get_attribute('href')) # collecting the link for additional checking
                line = entry.get_attribute('href')

                link_icao = line.split('.')[-1]
                link_suffix = "/{}/{}-TEXT.pdf".format(link_icao,link_icao)
                link_prefix = line.replace('html','pdf').replace('eAIP/','AD/').rsplit('/',1)[0]
                link = link_prefix + link_suffix

                filename = link_suffix.replace('.pdf', '').split('/')[-1] + "_" + line.split('/')[5]
                desc = link_icao + "_" + line.split('/')[5] + "_" + line.split('/')[7]
                cat = "AD_eAIP"
                eff_date = cat + "_"+ aip_eff_date

                total_charts.append([link_icao, link, filename, desc, cat, eff_date])
                print('\t   :', link_icao)

            
            # check if there's anymore additional charts to fetch
            for additionals in additional_checking:
                # enter icao html page
                self.browser.get(additionals)

                # look for tag name 'a' to find more links to downlo
                add_links = self.browser.find_elements_by_tag_name('a')
                print('\Checking for Additional Charts....')

                counter = 0
                for entry in add_links:
                    link = entry.get_attribute('href')
                    icao = link.split('/')[8]
                    desc = icao + "_" + link.split('/')[-1].replace('.pdf','').replace('%20',"_")
                    filename = icao + "_" + link.split('/')[5] + link.split('/')[8]
                    cat = "AD_eAIP"
                    eff_date = cat + "_"+ aip_eff_date

                    total_charts.append([icao, link, filename, desc, cat, eff_date])
                    print('\t fetching additional charts: ' + aip_eff_date + " -"+ icao + ": " + str(counter+1))
                

        for icao, link, file, desc, cat, eff_date in total_charts:
            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['icao'] = icao
            chart_item['link'] = link
            chart_item['file'] = file
            chart_item['desc'] = desc
            chart_item['club'] = cat
            chart_item['category'] = eff_date

            list_of_charts.append(chart_item)

        self.chart_mgr = KoreaChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()   

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class KoreaChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('South Korea')
