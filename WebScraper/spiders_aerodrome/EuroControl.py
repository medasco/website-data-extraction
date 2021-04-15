
import scrapy
import re
from math import ceil
from AerodromeChartScraper.psw_spider import AeroChartSpider, pswLogger
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver
from acm.downloader.utils import time_human
import time
import csv
import os


class EuroControl(AeroChartSpider):
    """ Euro Control airport charts spider """
    name = 'EuroControl'
    version = '1.0.0'

    def __init__(self, country=None, countries=None):
        super().__init__()
        self.club = self.name
        self.country_name = None
        self.data = None
        self.requestedCountry = country if country is not None else None
        self.requestedCountries = countries.split(',') if countries is not None else None
        pattern = "(?<=[A-Za-z][A-Za-z]_[A-Za-z][A-Za-z]_\d_)[A-Za-z]{4}(?=_)"
        self.regex = re.compile(pattern)

        self.url = 'https://eadbasic.ead-it.com/cms-eadbasic/opencms/en/login/ead-basic'

    def parse(self, response):
        """ Parsing callback function """
        username = 'psware2020'
        password = 'AMDB2099'
        #username = 'psware8046'
        #password = 'AMDB2099'

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # Login
        self.browser.find_element_by_name("j_username").send_keys(username)
        self.browser.find_element_by_name("j_password").send_keys(password)
        self.browser.find_element_by_xpath("//input[@class='loginButton']").click()
        # Accept Terms and Conditions
        element = self.browser.wait_until_located('XPATH', "//*[@id='acceptTCButton']", 30)
        element.click()
        self.browser.wait(2)
        if element.is_displayed():
            element.click()

        # Look for 'AIP Library' link and click it!
        self.browser.wait_until_located('XPATH', "//*[@id='topForm:topMenu:j_idt17:3:j_idt18:j_idt28:j_idt29']", 30).click()

        # Get all the countries into a list
        country_element = self.browser.find_elements_by_xpath("//select[@id='mainForm:selectAuthorityCode_input']/option")
        country_list = [] 
        for ce in country_element:
            if self.requestedCountries is not None:
                for requestedCountry in self.requestedCountries:
                    if requestedCountry in ce.text:
                        country_list.append((ce.get_attribute('value'), ce.text, requestedCountry))
                        break
            elif self.requestedCountry is not None:
                if self.requestedCountry in ce.text:
                    country_list.append((ce.get_attribute('value'), ce.text, self.requestedCountry))
                    break
            else:
                country_list.append((ce.get_attribute('value'), ce.text))

        # Log in time
        in_time = time.time()

        self.scan_chart_types(self.browser, country_list, list_of_charts, [('Charts', 'AD'), ('SUP', ''), ('AIP', 'AD')]) # 

        print('\nTotal session time:', time_human(time.time() - in_time))

    def create_chart_item(self, list_of_charts, links, descs, country_name, aipType, eff_date):

        for i, l in enumerate(links):
            chart_item = ChartItem()
            chart_item['club'] = 'EuroControl'
            chart_item['country'] = country_name
            chart_item['link'] = l.get_attribute('href')
            chart_item['file'] = l.text.split('.pdf')[0].replace(' ', '') + '_' + eff_date[i].text
            chart_item['desc'] = descs[i].text

            match = self.regex.search(chart_item['file'])
            
            if match is not None:
                chart_item['icao'] = match.group(0)
                code = chart_item['icao'][0:2]
                countryFromCode = CountryCode_EuroControl().findCountryByICAO(chart_item['icao'])
                if countryFromCode is not None:
                    chart_item['country'] = countryFromCode
            elif aipType == 'Charts':
                try:
                    chart_item['icao'] = chart_item['desc'].split(' ')[2]
                except IndexError as e:
                    print(e)
                    chart_item['icao'] = chart_item['desc'].split(' ')[1]
            elif aipType == 'SUP':
            	#chart_item['icao'] = 'SUP'
                for icao in CountryCode_EuroControl().findActiveIcaosByCountry(country_name):
                    if chart_item['desc'].find(icao) != -1:
                        chart_item['icao'] = icao
                        break
                    else:
                        chart_item['icao'] = 'SUP'
            elif chart_item['desc'].startswith('AD 2'):
                try:
                    chart_item['icao'] = chart_item['desc'].split(' ')[2]
                except IndexError as e:
                    print(e)
                    chart_item['icao'] = chart_item['desc'].split(' ')[1]
            else:
                chart_item['icao'] = '_textCharts_'

            # Append created ChartItem
            list_of_charts.append(chart_item)

    def scan_chart_types(self, browser, country_list, list_of_charts, aip):

        # Country Loop
        for country in country_list[:]:

            value = country[0]
            pswLogger.info(country[1])

            if value == 'BK':
                # Kosovo only have GEN charts
                continue
            else:

                for typeAIP, aipPart in aip:

                    if typeAIP == 'Charts':
                        print('\n\nGathering links for EuroControl :: Charts-AD')

                    if typeAIP == 'AIP':
                        print('\nGathering links for EuroControl :: AIP-AD')

                    if typeAIP == 'SUP':
                        print('\nGathering links for EuroControl :: SUP')

                    country_time = time.time()

                    # Locate the 'Authority Code' dropdown
                    auth_code_dd = "//select[@id='mainForm:selectAuthorityCode_input']"
                    
                    if self.requestedCountry is not None or self.requestedCountries is not None:
                        idx = CountryCode_EuroControl().findIndexByCountry(country[2])
                    else:
                        idx = country_list.index(country)
                    print('\n\tSelecting: {0} :: index {1}'.format(country[1], idx))

                    browser.execute_script("window.scrollTo(0, 0);")
                    
                    # Select the needed 'Authority Code'
                    browser.select_dropdown_option(auth_code_dd, value)
                    browser.wait(1)

                    # Select the necessary descriptive options for the search [Civil, EN, Charts, AD]
                    browser.select_dropdown_option("//select[@id='mainForm:selectAuthorityType_input']", 'C')
                    browser.select_dropdown_option("//select[@id='mainForm:selectLanguage_input']", 'EN')
                    if(typeAIP == 'SUP'):
                        try:
                            browser.select_dropdown_option("//select[@id='mainForm:selectAipType_input']", typeAIP)
                        except:
                            continue
                    else:
                        browser.select_dropdown_option("//select[@id='mainForm:selectAipType_input']", typeAIP)

                    if(aipPart != ''):
                    	browser.select_dropdown_option("//select[@id='mainForm:selectAipPart_input']", aipPart)

                    # Click 'Search' button
                    browser.find_element_by_xpath("//button[@id='mainForm:querySearch']").click()
                    browser.wait(1)

                    # Wait for the paginator element to load
                    browser.wait_until_located('XPATH', "//*[@id='mainForm:searchResults_paginator_bottom']", 10)
                    browser.wait(1)

                    # Get the total pages
                    result_count = float(browser.wait_until_located('XPATH', "//span[@id='mainForm:resultCount']", 5).text)
                    print('\tSearch result:', result_count)
                    # Maximum results per page: 15
                    max_results_per_page = 15.0
                    # Calculate the total number of pages
                    page_count = int(ceil(result_count / max_results_per_page))

                    # Always START at the first page
                    browser.wait_until_located('XPATH', "//span[contains(@class, 'ui-paginator-first')]", 10)
                    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    browser.find_element_by_xpath("//span[contains(@class, 'ui-paginator-first')]").click()
                    print('\tGoing to the first page!')
                    browser.wait(1)
                    browser.wait_until_located('XPATH', "//span[contains(@class, 'ui-paginator-page') and text()='1']", 10)
                    browser.wait(1)

                    country_name = CountryCode_EuroControl().code[idx][1]

                    # Scan Loop
                    for page in range(1, page_count + 1):

                        # Wait for the active paginator element to load
                        browser.wait_until_located('XPATH', "//span[contains(@class, 'ui-state-active')]", 5)

                        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                        print('\tScanning: page {}'.format(page))

                        # Capture all links displayed
                        pdf_links = browser.find_elements_by_xpath("//*[@id='mainForm:searchResults_data']/tr/td[@class='uibs-ais-column-m']/a")
                        pdf_desc = browser.find_elements_by_xpath("//*[@id='mainForm:searchResults_data']/tr/td[@class='uibs-ais-column-l']")
                        eff_date = browser.find_elements_by_xpath("//*[@id='mainForm:searchResults_data']/tr/td[1]")
                        # print(eff_date.text)

                        self.create_chart_item(list_of_charts, pdf_links, pdf_desc, country_name, typeAIP, eff_date)

                        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        print('\t\t Page: {} Done!'.format(page))

                        # Go to the next page
                        browser.wait_until_located('XPATH', "//span[contains(@class, 'ui-paginator-next')]", 10)
                        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        self.browser.find_element_by_xpath("//span[contains(@class, 'ui-paginator-next')]").click()
                        self.browser.wait(5)

                    # Refresh the browser
                    print('  Time elapsed for {0} : {1}'.format(country[1], time_human(time.time() - country_time)))
                    print('  Refreshing browser!')
                    browser.refresh()

                    # Process extracted ChartItem list
                    self.chart_mgr = EuroControlChartPipeline(list_of_charts)
                    self.chart_mgr.save_chart_list("-".join([country_name, typeAIP]))
                    list_of_charts.clear()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class EuroControlChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        # self.print_chart_list()
        self.save_chart_list('EuroControl')


class CountryCode_EuroControl:

    def findCountryByICAO(self, icao):
        code = icao[0:2]
        for x in self.code:
            if code in x[0]:
                return x[1]
        return None

    def findIndexByCountry(self, country_name):
        index = -1
        for x in self.code:
            index += 1
            if country_name in x[1]:
                return index

    def findActiveIcaosByCountry(self, country_name):
        referenceFile = os.getcwd() + "/../../reference/Euro.csv"
        list_of_icaos = []
        with open(referenceFile) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                    continue
                else:
                    if row[3] == country_name and row[4] == "Active":
                        list_of_icaos.append(row[2])
                    line_count += 1
            print(f'Processed {line_count} lines.')
        return list_of_icaos

    code = [('LA', 'Albania'),  # 0
            ('UD', 'Armenia'),  # 1
            ('LO', 'Austria'),  # 2
            ('UB', 'Azerbaijan'),  # 3
            ('EB', 'Belgium'),  # 4
            ('LQ', 'Bosnia'),  # 5
            ('LB', 'Bulgaria'),  # 6
            ('LD', 'Croatia'),  # 7
            ('LC', 'Cyprus'),  # 8
            ('LK', 'Czech Republic'),  # 9
            ('EK', 'Denmark'),  # 10
            ('EE', 'Estonia'),  # 11
            ('XX', 'Faroe Islands'),  # 12
            ('EF', 'Finland'),  # 13
            ('LW', 'Macedonia'),  # 14
            ('LF', 'France'),  # 15
            ('UG', 'Georgia'),  # 16
            ('ED', 'Germany'),  # 17
            ('LG', 'Greece'),  # 18
            ('BG', 'Greenland'),  # 19
            ('LH', 'Hungary'),  # 20
            ('BI', 'Iceland'),  # 21
            ('EI', 'Ireland'),  # 22
            ('LI', 'Italy'),  # 23
            ('BK', 'Kosovo'),  # 24
            ('EV', 'Latvia'),  # 25
            ('EY', 'Lithuania'),  # 26
            ('LM', 'Malta'),  # 27
            ('LU', 'Moldova'),  # 28
            ('EH', 'Netherlands'),  # 29
            ('EN', 'Norway'),  # 30
            ('RP', 'Philippines'),  # 31
            ('EP', 'Poland'),  # 32
            ('LP', 'Portugal'),  # 33
            ('LR', 'Romania'),  # 34
            ('LY', 'Serbia Montenegro'),  # 35
            ('LZ', 'Slovakia'),  # 36
            ('LJ', 'Slovenia'),  # 37
            ('LE', 'Spain'),  # 38
            ('ES', 'Sweden'),  # 39
            ('LS', 'Switzerland'),  # 40
            ('LT', 'Turkey'),  # 41
            ('UK', 'Ukraine'),  # 42
            ('EG', 'United Kingdom'), # 43
            ('EL', 'Luxembourg'),
            ('UM', 'Belarus'),
            ('OJ', 'Jordan')
            ]
