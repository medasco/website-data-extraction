import scrapy
from math import ceil
from selenium.webdriver import ActionChains
from WebScraper.web_spider import WebDataSpider
from WebScraper.items import DataItem
from WebScraper.pipelines import DataPipeline
from WebScraper.web_drivers import ChromeDriver
from selenium.webdriver.common.keys import Keys


class DuvalSpider(WebDataSpider):
    """ Duval County Clerk of Courts """
    name = 'duval'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://core.duvalclerk.com/'

    def parse(self, response):
        """ Parsing callback function """

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # Click Public Access
        self.browser.find_element_by_xpath('//input[@value="Public access"]').click()
        
        # Click blank area
        self.browser.find_element_by_xpath('//body').click()
        self.browser.wait_until_located('XPATH', '//td[@class="caseSearchFieldInput"]/select/option', 5)

        # Select Case Year
        year = '2020'
        self.browser.find_element_by_xpath('//*[@id="ContentPlaceHolder1_WebTab1"]/div/div[3]/div/table[2]/tbody/tr[3]/td[1]/input').send_keys(year)

        # Select Case Type (Eviction)
        self.browser.find_element_by_xpath('//td[@class="caseSearchFieldInput"]/select/option[98]').click()
        self.browser.wait_until_located('XPATH', '//td[@class="caseSearchFooter"]/input[@type="button"]', 3)

        # Click Begin Search
        self.browser.find_element_by_xpath('//*[@id="ContentPlaceHolder1_WebTab1"]/div/div[3]/div/table[2]/tbody/tr[8]/td/input').click()
        self.browser.wait_until_located('XPATH', '//div[@class="searchResultsControl_Bottom"]/div[@class="searchResultsControl_Jumper"]', 5)

        # Get current page and total actual pages
        page_number = int(self.browser.find_element_by_xpath('//div[@class="searchResultsControl_Page"]/input').get_attribute('value'))
        # total_pages = int(self.browser.find_element_by_xpath('//div[@class="searchResultsControl_Page"]/span').text)

        # Get searched results
        for page_number in range(1, 2):
            getCaseTab = self.browser.find_elements_by_xpath('//*[@id="ContentPlaceHolder1_WebTab1"]/div/div[4]/div/table/tbody')

            element_num = 4 # start on case element's div[4]
            element_tab = 3 # start on case element's span[3]

            case_fields = []
            if len(getCaseTab) > 0:
                open_case = getCaseTab[0]
                case_type = open_case.find_elements_by_xpath('//div[@class="searchResultItem_CaseType"]')
                case_status = open_case.find_elements_by_xpath('//div[@class="searchResultItem_CaseStatus"]')
                case_division = open_case.find_elements_by_xpath('//div[@class="searchResultItem_Division"]')
            
                for c_type, c_status, c_division in list(zip(case_type, case_status, case_division))[:2]:
                    outer_fields = [c_type.text, c_status.text, c_division.text]

                    # Open each searched case
                    self.click_enable(c_type)
                    
                    # Extract all important details
                    element_num += 1
                    content = str('//div[@class="igtab_THContentHolder"]/div['+ str(element_num) +']')

                    # Extract Case Numbers
                    case_number = self.browser.find_element_by_xpath(content + '/div/h1/span').text
                    department = self.browser.find_element_by_xpath(content + '/div/div[1]/table/tbody/tr[1]/td[2]').text
                    fileddate = self.browser.find_element_by_xpath(content + '/div/div[1]/table/tbody/tr[2]/td[4]').text.split(' ')[0]

                    # Extract Party Type (Plaintiff)
                    plaintiff = self.browser.find_element_by_xpath(content + '/div/div[2]/div/table/tbody/tr/td[2]').text.strip('\n/')
                    plt_name = self.browser.find_element_by_xpath(content + '/div/div[2]/div/table/tbody/tr/td[1]').text
                    plt_address = self.browser.find_element_by_xpath(content + '/div/div[2]/div/table/tbody/tr/td[3]').text.replace('\n', ', ')

                    # Extract Party Type (Defendant)
                    defendant = self.browser.find_element_by_xpath(content + '/div/div[2]/div/table/tbody[2]/tr/td[2]').text.strip('\n/')
                    def_name = self.browser.find_element_by_xpath(content + '/div/div[2]/div/table/tbody[2]/tr/td[1]').text
                    def_address = self.browser.find_element_by_xpath(content + '/div/div[2]/div/table/tbody[2]/tr/td[3]').text.replace('\n', ', ')

                    # Extract Attorney
                    # attorney = self.browser.find_element_by_xpath(content + '/div/div[3]/div/thead/tr/td').text
                    # att_name = self.browser.find_element_by_xpath(content + '/div/div[3]/div/table/tbody/tr/td[1]').text.replace('\n', ', ')
                    # att_address = self.browser.find_element_by_xpath(content + '/div/div[3]/div/table/tbody/tr/td[2]').text.replace('\n', ', ')

                    dispositiondate = fileddate
                    county = 'Duval'

                    # Extend case_fields list
                    outer_fields.insert(0, case_number)
                    outer_fields.extend([fileddate, dispositiondate, county, department, [plaintiff, plt_name, plt_address], [defendant, def_name, def_address]])
                    # outer_fields.extend([fileddate, dispositiondate, county, department, [plaintiff, plt_name, plt_address], [defendant, def_name, def_address], [attorney, att_name, att_address]])
                    case_fields.append(outer_fields)
  
                    # Close current searched case tab
                    element_tab += 1
                    self.browser.find_element_by_xpath('//*[@id="ContentPlaceHolder1_WebTab1"]/span/span[2]/span/span['+ str(element_tab) +']/img').click()
                
            for cf in case_fields:
                print("Case Number      : {}".format(cf[0]))
                print("Case Type        : {}".format(cf[1]))
                print("Case Status      : {}".format(cf[2]))
                print("File Date        : {}".format(cf[4]))
                print("Disposition Date : {}".format(cf[5]))
                print("County           : {}".format(cf[6]))
                print("Court Agency     : {}".format(cf[7]))
                print("Party Type       : {}".format(cf[8]))
                print("Party Type       : {}".format(cf[9]))
                # print("Attorney         : {}".format(cf[10]))
                print('\n')

            """ A case_fields should contain
            [casenumber, casetype, casestatus, casedivision, fileddate, dispositiondate, county, courtagency,
            [def_name, def_fulladdress, def_state, def_city, def_zipcode],
            [att_name, att_fulladdress, att_state, att_city, att_zipcode],
            [plt_name, plt_fulladdress, plt_state, plt_city, plt_zipcode]]"""

            # Go to next page
            self.browser.find_element_by_xpath('//div[@class="searchResultsControl_Page"]/input').clear()
            self.browser.find_element_by_xpath('//div[@class="searchResultsControl_Page"]/input').send_keys(str(page_number + 1))
            self.browser.find_element_by_xpath('//div[@class="searchResultsControl_Page"]/input').send_keys(Keys.ENTER)
            self.browser.wait(3)

        
        # web_item = DataItem()

        # web_item['country'] = self.country_name
        # web_item['icao'] = icao
        # web_item['link'] = link
        # web_item['desc'] = desc
        # web_item['file'] = file
        # web_item['club'] = 'Default'

        # list_of_charts.append(web_item)

        # self.chart_mgr = DuvalDataPipeline(list_of_charts)
        # self.chart_mgr.process_charts()
        
    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)

    def hover_element(self, element):
        hover = ActionChains(self.browser).move_to_element(element)
        hover.perform()

class DuvalDataPipeline(DataPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_data_list()
        self.save_data_list('Duval')
