
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class SingaporeSpider(AeroChartSpider):
    """ Singapore airport charts spider """
    name = 'Singapore'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://aim-sg.caas.gov.sg/eaip.html'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]

        list_of_charts = []
        total_charts = []
        grand_charts = []
        aip_related_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # Get eaip link
        eaip = self.browser.find_elements_by_xpath("//*[@id='content']/div/div[2]/ul/li[1]/a")[0].get_attribute('href')

        # Go to eaip
        self.browser.get(eaip)

        # Switch frame to 'eAISNavigationBase'
        self.browser.wait_until_located("XPATH", "//frame[@name='eAISNavigationBase']", 3)
        self.browser.switch_to.frame("eAISNavigationBase")

        # Switch frame to 'eAISNavigation'
        self.browser.wait_until_located("XPATH", "//frame[@name='eAISNavigation']", 3)
        self.browser.switch_to.frame("eAISNavigation")

        # Get effectivity date
        eff = self.browser.find_element_by_xpath("/html/body/div[2]/h2").text
        eff_date = eff.replace('Effective ', '').replace(' ', '')

        # get link to SUP Tab for later use
        sup_tab_link = self.browser.find_element_by_xpath("/html/body/div[1]/a[3]").get_attribute('href')


        ##
        ## AIP Section
        ##

        # Go to PART 3 - AERODROMES (AD)
        self.browser.wait_until_located("XPATH", "//*[@id='ADdetails']", 3)

        # Extract and Go to Aerodromes TOC via link (href)
        ad = self.browser.find_element_by_xpath("//*[@id='AD']").get_attribute('href')
        self.browser.get(ad)

        # Extracting Aerodrome and Related Charts links
        aip_charts = self.browser.find_elements_by_xpath("//*[@id='AD-0.6']/div[8]/div/h3/a")
        rel_charts = self.browser.find_elements_by_xpath("//*[@id='AD-0.6']/div[8]/div/div[last()]/h4/a")

        print(eff)
        print('\nExtracting :', self.country_name)

        for aip in aip_charts:
            ad = aip.get_attribute('href')
            ad_link = ad.replace('html', 'pdf').replace('eAIP/', '').replace('-en-GB', '')
            ad_icao = ad_link.rsplit('.', 1)[1]
            ad_desc = ad_link.split('#')[1].replace('-', '_').replace('.', '_')
            ad_file = ''.join([ad_desc, "_" + eff_date])
            cat = "AIP-AD"

            print('\t   : {} : {} : {} : {} : {} : {}'.format(ad_icao, ad_file, ad_desc, ad_link, cat, eff_date))
            total_charts.append([ad_icao, ad_link, ad_file, ad_desc, cat, eff_date])
            grand_charts.append(ad_file)

        print('\nDone listing [{0}] ICAO(s)...'.format(len(aip_charts)))
        print('Generating other related chart(s)...')

        for rel in rel_charts:
            rel_link = rel.get_attribute('href')
            rel_icao = rel_link.split('/AD-2.')[1].split('-')[0]
            aip_related_charts.append([rel_link, rel_icao])

        for ads, inn in aip_related_charts:
            self.browser.get(ads)
            add = ads.split('#')[1]
            order = self.browser.find_elements_by_id(add)

            if len(order) > 0:
                data = order[0]
                page = data.find_elements_by_tag_name('a')
                name = data.find_elements_by_tag_name('span')

                print('\nExtracting :', inn)

                for ad_page, ad_name in list(zip(page, name)):
                    prep = [ad_page.get_attribute('href'), ad_name.text]
                    if prep[1] != '':
                        rc_link = prep[0]
                        rc_desc = prep[1].replace(' - ', '_').replace(' ', '_').replace('(', '').replace(')', '').upper()
                        rc_file = ''.join([prep[0].split('/')[-1].split('.pdf')[0].replace('-', '_').replace('%20', '_').upper(), "_" + eff_date])
                        rc_icao = inn
                        cat = "AIP-AD"

                        print('\t   : {} : {} : {} : {} : {}:{}'.format(rc_icao, rc_file, rc_desc, rc_link, cat, eff_date))
                        total_charts.append([rc_icao, rc_link, rc_file, rc_desc, cat, eff_date])
                        grand_charts.append(rc_file)

                print('\t     Extracted [{0}] file(s)...'.format(len(page)))

        ##
        ## SUP Section
        ##
        self.browser.get(sup_tab_link)

        # Get elements
        sup_links = self.browser.find_elements_by_xpath('/html/body/div[2]/table/tbody/tr[@class="SupTable-Row"]/td[@class="SupTable-NRYear-td"]/a')
        sup_subject = self.browser.find_elements_by_xpath('/html/body/div[2]/table/tbody/tr/td[@class="SupTable-Subject-td"]')
        sup_validity_period = self.browser.find_elements_by_xpath('/html/body/div[2]/table/tbody/tr[@class="SupTable-Row"]/td[@class="SupTable-Period-td"]')

        # Check that total element in all categories match
        #   if a mismatch is found, spit out warning but proceed with parsing.
        #   length for subject is to be divided by two as SUP subject is captured on second element.
        if len(sup_links) != len(sup_subject) or \
            len(sup_links) != len(sup_validity_period):
            
            self.logger.warning("SINGAPORE SUP FILE ELEMENT COUNT DOES NOT MATCH!")
            self.logger.warning("    Trust Description/Publish Dates with caution!")

        # process all SUP element information
        for i in range (len(sup_links)):
            ad = sup_links[i].get_attribute('href')
            ad_icao = "SUP"
            ad_link = ad.replace('html','pdf').replace('eSUP/','').replace('-en-GB', '')
            ad_desc = sup_subject[i].get_attribute('innerText')
            ad_file = "SUP_" + sup_links[i].get_attribute('innerText').replace('.pdf', '') 
            validity_date = sup_validity_period[i].get_attribute('innerText')
            ad_cat = "SUP"

            print('\t   : {} : {} : {} : {} : {}: {}'.format(ad_icao, ad_link, ad_file, ad_desc, ad_cat, validity_date))
            total_charts.append([ad_icao, ad_link, ad_file, ad_desc, ad_cat, validity_date])
            grand_charts.append(ad_file)

        # DO NOT MOVE OUT, purposely positioned here to always be reinitalized to nothing before use
        # get all sup_link while still visible
        sup_link_captured = []      
        for x in range (len(sup_links)):
            sup_link_captured.append([sup_links[x].get_attribute('href'), sup_validity_period[x].get_attribute('innerText')])

        # enter all SUP link and check if there are additional attachments and process those
        for i in range (len(sup_links)):
            self.browser.get(sup_link_captured[i][0])
            sup_attachment = self.browser.find_elements_by_xpath('/html/body/div/div/div/a')

            counter = i + 1
            for attachment in sup_attachment:
                sup = attachment.get_attribute('href')
                sup_icao = "SUP"
                sup_link = sup.replace('html','pdf').replace('eSUP/','').replace('-en-GB', '')
                sup_desc = attachment.get_attribute('innerText').split('/')[-1].replace('.pdf', '')
                sup_file = "SUP_" + attachment.get_attribute('innerText').split('/')[-1].replace('.pdf', '')
                sup_eff_date = sup_link_captured[i][1]

                total_charts.append([sup_icao, sup_link, sup_file, sup_desc, "SUP", sup_eff_date])
                print ("Processing Effectivity Date:" + sup_link_captured[i][1] + " - Found Sup Attachment " + str(counter) + " " + sup_file)

        ##
        ## Process CSV 
        ##

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

        for chart in list_of_charts:
            # skip processing for SUP
            if 'SUP' in chart['icao']:
                pass
            else:
                if 'html' in chart['link']:
                    list_of_charts.remove(chart)

        for chart in list_of_charts:
             # skip processing for SUP
            if 'SUP' in chart['icao']:
                pass
            else:
                if chart['desc'] == 'NIL':
                    list_of_charts.remove(chart)

        print('\n Total of [{0}] ICAO(s).'.format(len(aip_charts)))
        print('\n Total of [{0}] SUP Charts'.format(len(sup_links)))
        print('Grand Total of  [{0}] PDF file(s).\n'.format(len(grand_charts)))

        self.chart_mgr = SingaporeChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class SingaporeChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Singapore')
