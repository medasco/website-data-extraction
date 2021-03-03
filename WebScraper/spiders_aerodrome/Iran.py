
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver
from selenium.common.exceptions import NoSuchElementException 
import time


class IranSpider(AeroChartSpider):
    """ Iran airport charts spider """
    name = 'Iran'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://www.google.com/' # this is only for Iran due to unable to reach direct website front page
        # self.url = 'https://ais.airport.ir/47'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]

        list_of_charts = []
        total_charts = []
        sub_folder_pages = []
        sub_folders = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # bypass website's safety feature, go to home page
        self.browser.get('https://ais.airport.ir')

        # go to AIP link from drop-down
        aip_link = self.browser.find_element_by_xpath('/html/body/div[2]/header/nav/div/div[1]/ul/li[2]/div/ul/li[2]/a').get_attribute('href')
        self.browser.get(aip_link)

        # before entering AD 2, capture SUP link while still visible.
        sup_link = self.browser.find_element_by_xpath('/html/body/div[2]/div/div/div/div/div/div/section/div/div/div/div[2]/ \
                                                        div[2]/div/div[2]/div[2]/div/div/div[1]/div/table/tbody/tr[3]/td[1]/a[2]').get_attribute('href')

        # get effectivity date
        eff_date = self.browser.find_element_by_xpath('/html/body/div[2]/div/div/div/div/div/div/section/div/div/div/div[2]/div[1]/h3/span').text
        eff_date = eff_date.split(' ',2)[2].replace(' )', '')
        
        ##
        ## AIP-AD Section
        ##  

        # click your way into into AD 2 page
        self.click_enable(self.browser.find_element_by_link_text('AIP'))
        self.click_enable(self.browser.find_element_by_link_text('AD'))
        self.click_enable(self.browser.find_element_by_link_text('AD 2'))

        # get every page element from drop-down list for AIP-AD
        drop_down = self.browser.find_element_by_xpath('//ul[@class="dropdown-menu lfr-menu-list direction-down"]')
        pages = drop_down.find_elements_by_tag_name('a')

        print('\nExtracting AIP-AD:', self.country_name)

        # capture and append every page link
        for page in pages:
            sub_folder_pages.append(page.get_attribute('href'))

        # process every page links to capture pdf names and links
        for sub_folder_page in sub_folder_pages:
            self.browser.get(sub_folder_page)
            ad2_chart = self.browser.find_element_by_xpath('//tbody[@class="table-data"]')

            chart_links = ad2_chart.find_elements_by_xpath('//tr/td[1]/a[1]')
            chart_names = ad2_chart.find_elements_by_tag_name('strong')

            for pdf_link, pdf_name in list(zip(chart_links, chart_names)):

                pdf_links = pdf_link.get_attribute('href')
                pdf_names = pdf_name.text
                sub_folders.append([pdf_names, pdf_links, "AIP-AD"])

        ##
        ## SUP Section
        ##

        # enter sup page from previously captured link
        self.browser.get(sup_link)

        sup_chart = self.browser.find_element_by_xpath('//tbody[@class="table-data"]')

        sup_chart_links = sup_chart.find_elements_by_xpath('//tr/td[1]/a[1]')
        sup_chart_names = sup_chart.find_elements_by_tag_name('strong')

        for pdf_link, pdf_name in list(zip(sup_chart_links, sup_chart_names)):

            pdf_links = pdf_link.get_attribute('href')
            pdf_names = pdf_name.text
            sub_folders.append([pdf_names, pdf_links, "SUP"])


        ##
        ## Process everything
        ##

        # process every pdf names and links for parsing
        for docu_name, docu_link, docu_type in sub_folders:
            self.browser.get(docu_link)
            total_documents = self.browser.find_element_by_xpath('//div[@class="lfr-asset-icon lfr-asset-items last"]')
            no_of_documents = total_documents.text.split(' ')[0]

            # if listed document is less than or equal to 10
            #  start processing immediately
            if int(no_of_documents) <= 10:
                print('\t   : {} : {} : {}Documents'.format(docu_name, no_of_documents, docu_type))
                actual_extracted_adc = []

                aerodromes = self.browser.find_elements_by_tag_name('img')

                for ad_chart in aerodromes:
                    ad_charts = ad_chart.get_attribute('src')
                    ad_link = ad_charts.split('&document')[0].replace('.PDF', '.pdf')

                    if '.pdf' in ad_link:
                        ad_file = ad_link.split('.pdf')[0].rsplit('/', 1)[1].replace('+', '_').replace('-', '_').replace('++', '_').upper()
                        ad_desc = ad_file
                        print('\t   : {} : {} : {} : {} : {}'.format(ad_desc, ad_file, ad_link, docu_type, eff_date))
                        total_charts.append([docu_name, ad_desc, ad_file, ad_link, docu_type])
                        actual_extracted_adc.append(ad_link)

                print('\t     Extracted [{0}] file(s)...\n'.format(len(actual_extracted_adc)))

            # otherwise, a drop down of pages will be 'present' so capture all page links first.
            else:
                print('\t   : {} : {} : {} Documents'.format(docu_name, no_of_documents, docu_type))
                sub_docu_pages = []
                actual_extracted_doc = []

                docu_drop_down = self.browser.find_element_by_xpath('//ul[@class="dropdown-menu lfr-menu-list direction-down"]')
                document_pages = docu_drop_down.find_elements_by_tag_name('a')

                for docu_page in document_pages:
                    sub_docu_pages.append(docu_page.get_attribute('href'))

                for sub_docu_page in sub_docu_pages:
                    self.browser.get(sub_docu_page)
                    sub_docu_charts = self.browser.find_elements_by_tag_name('img')

                    for sub_chart in sub_docu_charts:
                        sub_charts = sub_chart.get_attribute('src')
                        sub_link = sub_charts.split('&document')[0].replace('.PDF', '.pdf')

                        if '.pdf' in sub_link:
                            sub_file = sub_link.split('.pdf')[0].rsplit('/', 1)[1].replace('+', '_').replace('-', '_').replace('++', '_').upper()
                            sub_desc = sub_file
                            print('\t   : {} : {} : {} : {} : {}'.format(sub_desc, sub_file, sub_link, docu_type, eff_date))
                            total_charts.append([docu_name, sub_desc, sub_file, sub_link, docu_type])
                            actual_extracted_doc.append(sub_link)

                print('\t     Extracted [{0}] file(s)...\n'.format(len(actual_extracted_doc)))

        
        # produce list for csv processing
        for icao, desc, file, link, cat in total_charts:
            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['icao'] = icao
            chart_item['link'] = link
            chart_item['file'] = file
            chart_item['desc'] = desc
            chart_item['club'] = cat
            chart_item['category'] = eff_date

            list_of_charts.append(chart_item)

        self.chart_mgr = IranChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        # self.browser.wait(2)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class IranChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Iran')
