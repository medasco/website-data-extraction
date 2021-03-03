
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver
import time


class SaudiArabiaSpider(AeroChartSpider):
    """ Saudi Arabia airport charts spider """
    name = 'SaudiArabia'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        # self.country_name = self.name
        self.country_name = 'Saudi Arabia'

        # Work-around for non-response when directly accessing homepage from usual process
        
        # self.url = 'https://www.sans.com.sa/English/AIMs/'
        self.url = 'https://www.google.com/'

    def parse(self, response):
        """ Parsing callback function """

        # Initialize lists
        list_of_charts = []         # list for all charts
        total_charts = []           # list for aip charts processed
        grand_charts = []           # list for all files

        additionals = []            # list for aip additional
        pre_process_list = []       # list for un-sorted preprocess
        aip_to_process = []         # list for aip that still needs to be processed

        sup_charts = []             # list of SUP main Links
        aip_charts = []             # list of AIP main Links

        # Prepare credentials
        username = 'mwkpsw'
        password = 'Performance@2095'

        # Start the selenium Chrome driver
        # Work-around for non-response when directly accessing homepage from usual process
        self.browser.get('https://www.sans.com.sa/English/AIMs/')

        # Login
        self.browser.find_element_by_xpath("//*[@placeholder='User Name']").send_keys(username)
        self.browser.find_element_by_xpath("//*[@placeholder='Password']").send_keys(password)
        self.browser.find_element_by_xpath("//*[@type='submit']").click()

        # Go to eAIP link
        eaip = self.browser.find_element_by_xpath('//*[@id="zz7_RootAspMenu"]/li[2]/a').get_attribute('href')
        self.browser.get(eaip)
        self.browser.switch_to.frame("eAISContent")

        
        # Get all Currently EFfective and Next Issues Link
        pre_process_list = self.browser.find_elements_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/a')
        pre_process_list.extend(self.browser.find_elements_by_xpath('/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[1]/a'))

        # split the captured links from SUP and AIPs.
        # this is so we can process them separately later.
        for items in pre_process_list:
            if "SUP" in items.get_attribute('href'):
                sup_charts.append(items)
            else:
                aip_to_process.append(items)

        ##
        ## SUP Section
        ##
        
        for sup in sup_charts:
            # get effectivity date from link text
            sup_eff_date = sup.get_attribute('innerText')
            sup_link = sup.get_attribute('href')

            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['icao'] = "SUP"
            chart_item['link'] = sup_link
            chart_item['file'] = sup_link.split('/')[-1].replace('.pdf','')
            chart_item['desc'] = "Saudi Arabia SUP_" + sup_eff_date
            chart_item['club'] = "SUP"
            chart_item['category'] = sup_eff_date

            print(chart_item['desc'])
            list_of_charts.append(chart_item)
            grand_charts.append(chart_item['file'])

        ##
        ## AIP Section
        ##

        # get aip links and effectivity dates to process while still in eAIP home page
        for aip in aip_to_process:
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

            # capture SUP tab and ad link for later use
            sup_tab_link = self.browser.find_element_by_xpath('/html/body/div[1]/a[3]').get_attribute('href')
            ad = self.browser.find_element_by_xpath("//*[@id='AD']").get_attribute('href')
            
            ##
            ## SUP Section (SUP Tab inside eAIP)
            ##

            # get into SUP page
            self.browser.get(sup_tab_link)

            print ("Processing Effectivity Date:" + aip_eff_date + " SUP Charts")

            # Get element details
            sup_links = self.browser.find_elements_by_xpath('/html/body/table/tbody/tr[@class="SupTable-Row"]/td[@class="SupTable-NRYear-td"]/a')
            sup_subject = self.browser.find_elements_by_xpath('/html/body/table/tbody/tr/td[@class="SupTable-Subject-td"]')
               
            # Check that total element in all categories match
            #   if a mismatch is found, spit out warning but proceed with parsing.
            #   length for subject is to be divided by two as SUP subject is captured on second element.
            if len(sup_links) != len(sup_subject):
                self.logger.warning("SAUDI ARABIA SUP FILE ELEMENT COUNT DOES NOT MATCH!")
                self.logger.warning("    Trust Description/Publish Dates with caution!")

            # process all SUP element information
            # parse directly!
            for i in range (len(sup_links)):
                sup = sup_links[i].get_attribute('href')
                sup_icao = "SUP"
                sup_link = sup.replace('html','pdf').replace('eSUP/','')
                sup_desc = sup_subject[i].get_attribute('innerText')
                sup_file = "SUP_" + sup_subject[i].get_attribute('innerText').replace('.html', '') 
                sup_eff_date = aip_eff_date

                total_charts.append([sup_icao, sup_link, sup_file, sup_desc, "SUP", sup_eff_date])

            # DO NOT MOVE OUT, purposely positioned here to always be reinitalized to nothing before use
            # get all sup_link
            sup_link_captured = []      
            for link in sup_links:
                sup_link_captured.append(link.get_attribute('href'))

            # enter all SUP link and check if there are additional attachments and process those
            for i in range (len(sup_links)):
                self.browser.get(sup_link_captured[i])
                sup_attachment = self.browser.find_elements_by_xpath('/html/body/div/div/div/a')

                print ("Processing Effectivity Date:" + aip_eff_date + " - Found Sup Attachment " + str(i+1))

                for attachment in sup_attachment:
                    sup = attachment.get_attribute('href')
                    sup_icao = "SUP"
                    sup_link = sup.replace('html','pdf').replace('eSUP/','')
                    sup_desc = attachment.get_attribute('innerText').split('/')[-1].replace('.pdf', '')
                    sup_file = "SUP_" + attachment.get_attribute('innerText').split('/')[-1].replace('.pdf', '')
                    sup_eff_date = aip_eff_date

                    total_charts.append([sup_icao, sup_link, sup_file, sup_desc, "SUP", sup_eff_date])

            ##
            ## AIP-AD Section
            ##

            # Go to PART 3 - AERODROMES (AD)
            self.browser.get(ad)

            # Extracting Aerodrome and Related Charts links
            genes = self.browser.find_elements_by_xpath("//*[@id='AD-0.6']/div[2]/div/h3/a")
            stock = self.browser.find_elements_by_xpath("//*[@id='AD-0.6']/div/div/div[23]/h4/a")

            # Aerodrome's PDF loop
            print('\nExtracting :', self.country_name)

            for ring in genes:
                line = ring.get_attribute('href')
                bond = line.replace('html', 'pdf').replace('eAIP/', '')
                snap = bond.split('/')
                chop = snap[-1].split('.pdf#')
                port = chop[1].split('.')[1]
                form = chop[1]
                case = chop[0]
                cat = "AIP-AD"
                total_charts.append([port, bond, case, form, cat, aip_eff_date])
                grand_charts.append(case)
                print('\t   :', port)

            print('\t     Generating other related chart(s)...')

            for bind in stock:
                hold = bind.get_attribute('href')
                dock = hold.split('#')[1].split('-')[0]
                additionals.append([hold, dock])

            for ads, ins in additionals:
                self.browser.get(ads)
                order = self.browser.find_elements_by_xpath('//div[contains(@id, "2.24")]/table/tbody')

                if len(order) > 0:
                    data = order[0]
                    page = data.find_elements_by_tag_name('a')
                    name = data.find_elements_by_tag_name('p')

                    print('\nExtracting :', ins)

                    for leaf, term in list(zip(page, name)):
                        dash = [leaf.get_attribute('href'), term.text, leaf.text]
                        loop = dash[0]
                        mold = dash[1].replace('-', '_')
                        stud = dash[2].replace(' ', '_').replace('-', '_')
                        pier = ins
                        cat = "AIP-AD"
                        total_charts.append([pier, loop, stud, mold, cat, aip_eff_date])
                        grand_charts.append(stud)
                        print('\t   :', stud)

                    print('\t     Extracted [{0}] file(s)...'.format(len(page)))

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

        # remove unnecessary item
        for chart in list_of_charts:
            if 'html' in chart['link']:
                list_of_charts.remove(chart)

        for chart in list_of_charts:
            if chart['desc'] == 'NIL':
                list_of_charts.remove(chart)

        print('\nTotal of [{0}] ICAO(s).'.format(len(genes)))
        print('Total of [{0}] SUPs'.format(len(sup_charts)))
        print('Grand Total of  [{0}] PDF file(s).\n'.format(len(grand_charts)))
        #
        self.chart_mgr = SaudiArabiaChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        # self.browser.wait(2)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class SaudiArabiaChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('SaudiArabia')
