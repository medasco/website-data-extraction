
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ChromeOptions
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver
import pyautogui
import urllib
import urllib.request, urllib.parse, urllib.error
import urllib3
import ssl
import requests
import datetime
import shutil
import time
from acm.config import *


class JapanSpider(AeroChartSpider):
    """ Japan airport charts spider """
    name = 'Japan'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://aisjapan.mlit.go.jp/Login.do'

    def parse(self, response):
        """ Parsing callback function """

        username = 'psware8045'
        password = 'AMDB2095'

        total_charts = []
        origin_links = []
        cart_links = []
        other_charts = []
        list_of_charts = []
        aip_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)
        
        # Login
        self.browser.find_element_by_name("userID").send_keys(username)
        self.browser.find_element_by_name("password").send_keys(password)
        self.browser.find_element_by_xpath("//*[@name='button_submit1']").click()

        # Look for 'Log-out' button
        self.browser.find_element_by_xpath("//*[@name='menu-logout']")

        # Go to 'AIP' Link
        aip_page_link = self.browser.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table[4]/tbody/tr/td[2]/a[1]').get_attribute('href')
        self.browser.get(aip_page_link)

        # Go to Publication Date
        published_links = self.browser.find_elements_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/a')
                        
        # get aip links and effectivity dates to process while still in eAIP home page
        for aip in published_links:
            aip_captured_eff_date = aip.get_attribute('innerText')
            aip_captured_link = aip.get_attribute('href')

            aip_charts.append([aip_captured_eff_date, aip_captured_link])

        # start processing the aip links 
        for aip_eff_date, aip_ink in aip_charts:
            print ("Processing Effectivity Date:" + aip_eff_date)

            # DO NOT MOVE OUT, purposely positioned here to always be reinitalized to nothing before use
            total_links = []

            # enter aip page
            self.browser.get(aip_ink)

            # Switch frame to 'eAISNavigationBase'
            self.browser.switch_to.frame("eAISNavigationBase")

            # Switch frame to 'eAISNavigation'
            self.browser.switch_to.frame("eAISNavigation")

            # capture SUP tab and ad link for later use
            sup_tab_link = self.browser.find_element_by_xpath('/html/body/div[1]/a[3]').get_attribute('href')
            ad = self.browser.find_element_by_xpath("//*[@id='AD']").get_attribute('href')

            ##
            ## SUP 
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
                self.logger.warning("JAPAN SUP FILE ELEMENT COUNT DOES NOT MATCH!")
                self.logger.warning("    Trust Description/Publish Dates with caution!")

            # process all SUP element information
            # parse directly!
            for i in range (len(sup_links)):
                sup = sup_links[i].get_attribute('href')
                sup_icao = "SUP"
                sup_link = sup.replace('.html','.pdf').replace('eSUP/','eSUP/pdf/')
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
                    sup_link = sup
                    sup_desc = attachment.get_attribute('innerText').split('/')[-1].replace('.pdf', '')
                    sup_file = "SUP_" + attachment.get_attribute('innerText').split('/')[-1].replace('.pdf', '')
                    sup_eff_date = aip_eff_date

                    total_charts.append([sup_icao, sup_link, sup_file, sup_desc, "SUP", sup_eff_date])

            ##
            ## AIP-AD
            ##
            
            # Go to Part 3 - AERODROMES (AD)
            self.browser.get(ad)

            # Extracting Aerodrome Individual Charts links
            origin = self.browser.find_elements_by_xpath("//*[@id='AD-0.6']/div[2]/div/h3/a")
            additional = self.browser.find_elements_by_xpath('//*[@id="AD-0.6"]/div[2]/div/div[24]/h4/a')

            print('\nExtracting :', self.country_name)

            # Aerodrome's Individual Chart Links loop ****
            for con in origin:
                bond = con.get_attribute('href').replace('/JP', '/pdf/JP').replace('.html', '.pdf')
                origin_links.append(bond)
                total_links.append([bond, aip_eff_date, "AIP-AD"])
                print(bond)

            print('Total Individual Charts: {0} files\n'.format(len(origin_links)))

            # Aerodrome's Additional Charts Links loop
            for ins in additional:
                other_charts.append(ins.get_attribute('href'))

            # Aerodrome's Other Charts Loop ****
            for ads in other_charts:
                self.browser.get(ads)

                adds = self.browser.find_element_by_xpath("//div[contains(@id, '2.24')]")
                carts = adds.find_elements_by_tag_name('a')

                for links in carts:
                    link = links.get_attribute('href')
                    if link is not None:
                        cart_links.append(link)
                        total_links.append([link, aip_eff_date, "AIP-AD"])
                        print(link)

            print('Extracted: {0} files\n'.format(len(carts)))
            print('Total Additional Charts: {0} files\n'.format(len(cart_links)))

            # parsing for all AIP-AD that was already captured.
            for pdf, aip_eff_date, cat in total_links:
                path = pdf
                chop = pdf.rsplit('/')
                name = chop[-1] if '#' not in pdf else chop[-1].split('#')[0]
                data = name.split('.pdf')[0]
                body = data + '_' + chop[6]
                port = name.split('-')[3]
                total_charts.append([port, path, data, body, cat, aip_eff_date])

        for icao, link, file, desc, cat, eff_date in total_charts:
            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['icao'] = icao
            chart_item['link'] = link
            chart_item['file'] = file
            chart_item['desc'] = desc
            chart_item['club'] = cat
            chart_item['category'] = eff_date if not None else "N/A"

            list_of_charts.append(chart_item)

        #remove unnecessary entries
        for chart in list_of_charts:
            if '.html' in chart['link']:
                list_of_charts.remove(chart)

        for chart in list_of_charts:
            if chart['desc'] == 'NIL':
                list_of_charts.remove(chart)

        print('\nTotal of [{0}] ICAO(s).'.format(len(origin)))  # 127 ICAO

        self.chart_mgr = JapanChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self
        # pass


class JapanChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Japan')
