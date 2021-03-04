import scrapy
from selenium.webdriver import ActionChains
from WebScraper.psw_spider import WebDataSpider
from WebScraper.items import DataItem
from WebScraper.web_drivers import ChromeDriver
from selenium.webdriver.common.keys import Keys
from docx import Document
from wsm.config import DOCX_PATH
from itertools import product


class CreateFBPageSpider(WebDataSpider):
    """ CreateFBPage airport charts spider """
    name = 'createfbpage'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://www.facebook.com'

    def parse(self, response):
        """ Parsing callback function """

        username = 'betauser2@gmail.com'
        password = 'pwuser2'

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # Login
        self.browser.find_element_by_name("email").send_keys(username)
        self.browser.find_element_by_name("pass").send_keys(password)
        self.browser.find_element_by_name("login").click()
        self.browser.wait(5)

        # Go to Pages
        tab_pages = self.browser.find_element_by_xpath('//div[@class="buofh1pr"]/div[1]/ul/li[3]/div/a').get_attribute('href')
        self.browser.get(tab_pages)
        self.browser.wait_until_located("XPATH", '//div[@class="cxgpxx05"]/a', 3)

        # Go to Create New Page
        create_new_page = self.browser.find_element_by_xpath('//div[@class="cxgpxx05"]/a').get_attribute('href')
        self.browser.get(create_new_page)
        self.browser.wait(3)

        # Click Category search box
        self.click_enable(self.browser.find_element_by_xpath('//div[@role="presentation"]'))
        self.browser.wait_until_located('XPATH', '//*[@id="jsc_c_i"]', 3)

        # Fill up search box and scrape suggested items
        combinations = []

        vow1 = ['a','e','i','o','u']
        con1 = ['b','c','d','f','g','h','j','k','l','m','n','p','q','r','s','t','v','w','x','y','z']
        
        vv_com = [''.join(t) for t in product(vow1, vow1)]
        vc_com = [''.join(t) for t in product(vow1, con1)]
        cv_com = [''.join(t) for t in product(con1, vow1)]
        cc_com = [''.join(t) for t in product(con1, con1)]

        for vv in vv_com:
            combinations.append(vv)
        for vc in vc_com:
            combinations.append(vc)
        for cv in cv_com:
            combinations.append(cv)
        for cc in cc_com:
            combinations.append(cc)

        # print(combinations)
        # print(len(combinations))

        aux_list = []
        for two_letter in combinations:
            print('\nCombinations of : "{}"'.format(two_letter.upper()))
            self.browser.find_element_by_xpath('//*[@id="jsc_c_i"]').send_keys(two_letter)
            self.browser.wait(3)

            option_div = self.browser.find_elements_by_xpath('//li[@role="option"]/div/div/div/div/div/div/span')
            self.browser.wait(3)
            for od in option_div:
                if od.text is not None:
                    print('\t\t: {}'.format(od.text))
                    aux_list.append(od.text)
            
            print('\t\t-------- {} items --------\n'.format(len(option_div)))

            self.browser.find_element_by_xpath('//*[@id="jsc_c_i"]').send_keys(Keys.BACKSPACE)
            self.browser.wait(3)

            span_item = self.browser.find_elements_by_xpath('//li[@role="option"]/div/div/div/div/div/div/span')
            self.browser.wait(3)
            
            for item in span_item:
                if item.text is not None:
                    print('\t\t: {}'.format(item.text))
                    aux_list.append(item.text)

            print('\t\t-------- {} items --------\n'.format(len(span_item)))

            self.browser.find_element_by_xpath('//*[@id="jsc_c_i"]').send_keys(Keys.BACKSPACE)
            self.browser.wait(3)

            empty_sbox = self.browser.find_elements_by_xpath('//li[@role="option"]/div/div/div/div/div/div/span')
            self.browser.wait(3)
            
            for sbox in empty_sbox:
                if sbox.text is not None:
                    print('\t\t: {}'.format(sbox.text))
                    aux_list.append(sbox.text)

            print('\t\t-------- {} items --------\n'.format(len(empty_sbox)))
        
        set_category = []
        for aux in aux_list:
            if aux not in set_category:
                set_category.append(aux)
        
        sorted_category = sorted(set_category)
        print(sorted_category)
        print('-------- {} items --------\n'.format(len(sorted_category)))

        doc = Document()
        for category in sorted_category:
            doc.add_paragraph(category)
            docx = DOCX_PATH + 'category.docx'
            doc.save(docx)

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)
