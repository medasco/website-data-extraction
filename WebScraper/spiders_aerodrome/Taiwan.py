
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver
import time


class TaiwanSpider(AeroChartSpider):
    """ Taiwan airentry_icao charts spider """
    name = 'Taiwan'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'http://eaip.caa.gov.tw/eaip/home.faces'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]

        list_of_charts = []
        total_charts = []
        grand_charts = []
        additionals = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)
        time.sleep(5)

        # Go to eAIP tab
        self.browser.find_element_by_xpath("//*[@id='j_id_e_j_id_f_menu']/table/tbody/tr[1]/td[2]").click()

        # Agree and Accept
        self.browser.find_element_by_xpath('//*[@id="j_id_n:j_id_z"]').click()

        # Go to eAIP link and Currently Effective Date
        aip = self.browser.find_element_by_xpath('//*[@id="j_id_n"]/div/table/tbody/tr[2]/td/div/table/tbody/tr[2]/td[1]/a')
        pub = aip.get_attribute('href')
        aip_eff_date = aip.text
        print('\nEffective Date: ', aip_eff_date)
        self.browser.get(pub)

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
        ## SUP Section
        ##

        # get into SUP page
        self.browser.get(sup_tab_link)

        print ("Processing Effectivity Date:" + aip_eff_date + " SUP Charts")

        # Get element details
        sup_links = self.browser.find_elements_by_xpath('/html/body/table/tbody/tr[@class="SupTable-Row"]/td[@class="SupTable-NRYear-td"]/a')
        sup_subject = self.browser.find_elements_by_xpath('/html/body/table/tbody/tr/td[@class="SupTable-Subject-td"]')
        sup_icaos = self.browser.find_elements_by_xpath('/html/body/table/tbody/tr[@class="SupTable-Row"]/td[@class="SupTable-Affect-td"]/a')
            
        # Check that total element in all categories match
        #   if a mismatch is found, spit out warning but proceed with parsing.
        #   length for subject is to be divided by two as SUP subject is captured on second element.
        if len(sup_links) != len(sup_subject):
            self.logger.warning("TAIWAN SUP FILE ELEMENT COUNT DOES NOT MATCH!")
            self.logger.warning("    Trust Description/Publish Dates with caution!")

        # process all SUP element inentry_descation
        # parse directly!
        for i in range (len(sup_links)):
            sup = sup_links[i].get_attribute('href')
            sup_icao = sup_icaos[i].get_attribute('innerText')
            sup_link = sup.replace('html','pdf').replace('eSUP/','')
            sup_desc = sup_subject[i].get_attribute('innerText')
            sup_file = "SUP_" + sup_icao + "_" + aip_eff_date
            sup_eff_date = aip_eff_date

            total_charts.append([sup_icao, sup_link, sup_file, sup_desc, "SUP", sup_eff_date])

        # DO NOT MOVE OUT, purposely positioned here to always be reinitalized to nothing before use
        # get all sup_link while still visible
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
        ## AIP - AD Section
        ## 

        # Go to PART 3 - AERODROMES (AD)
        self.browser.get(ad)

        # Extracting Aerodrome and Related Charts links
        icao_ad = self.browser.find_elements_by_xpath("//*[@id='AD-0.6']/div[2]/div/h3/a") 
        icao_ad_related = self.browser.find_elements_by_xpath("//*[@id='AD-0.6']/div/div/div[23]/h4/a") 

        # Aerodrome's PDF loop
        print('\nExtracting :', self.country_name)

        for entry in icao_ad:
            line = entry.get_attribute('href')
            entry_link = line.replace('html', 'pdf').replace('eAIP/', '')
            snap = entry_link.split('/')
            chop = snap[-1].split('.pdf#')
            entry_icao = chop[1].split('.')[1]
            entry_desc = chop[1]
            entry_filename = chop[0]

            entry_link = entry_link if entry_link[:2] == 'RC' else 'AD' + entry_link[2:-1]

            total_charts.append([entry_icao, entry_link, entry_filename, entry_desc, "AIP-AD", aip_eff_date])
            grand_charts.append(entry_filename)
            print('\t   :', entry_icao)

        print('\t     Generating other related chart(s)...')

        for bind in icao_ad_related:
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
                    stud = stud if stud[:2] == 'RC' else 'AD' + stud[2:-1]

                    total_charts.append([pier, loop, stud, mold, "AIP-AD", aip_eff_date])
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

        for chart in list_of_charts:
            if 'html' in chart['link']:
                list_of_charts.remove(chart)

        for chart in list_of_charts:
            if chart['desc'] == 'NIL':
                list_of_charts.remove(chart)

        print('\nTotal of [{0}] ICAO(s).'.format(len(icao_ad)))  # 18 ICAO
        print('Grand Total of  [{0}] PDF file(s).\n'.format(len(grand_charts)))  # 288 PDF files

        self.chart_mgr = TaiwanChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class TaiwanChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Taiwan')
