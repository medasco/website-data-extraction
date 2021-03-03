

import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class TunisiaSpider(AeroChartSpider):
    """ Tunisia airport charts spider """
    name = 'Tunisia'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'http://www.oaca.nat.tn/index.php?id=751'
        self.url = 'http://www.oaca.nat.tn/'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)
        
        # get into AERONAUTICAL INFORMATION SERVICE section
        aics_section = self.browser.find_element_by_xpath('//*[@id="oaca-02"]/a[2]').get_attribute('href')
        self.browser.get(aics_section)

        # get links to AIP and Supplemental for later use.
        aip_page = self.browser.find_element_by_xpath('//*[@id="menuAdx"]/div/ul/li[3]/ul/li[3]/a').get_attribute('href')
        aip_supp_page = self.browser.find_element_by_xpath('//*[@id="menuAdx"]/div/ul/li[4]/a').get_attribute('href')

        ##
        ## SUP Charts
        ##

        self.browser.get(aip_supp_page)

        # check if language is in English or not. Switch to english if not
        current_language_option = self.browser.find_element_by_xpath('//*[@id="oaca-15"]/a[1]')
        if current_language_option.text == "English":
            self.click_enable(current_language_option)
            
        # get supp element and description
        aip_supp_elements = self.browser.find_elements_by_xpath('//*[@id="c2839"]/p/span/a')
        aip_supp_description = self.browser.find_elements_by_xpath('//*[@id="c2839"]/p/span')

        # parse csv categories
        for i in range(len(aip_supp_elements)):
            link = aip_supp_elements[i].get_attribute('href')
            filename = link.rsplit('/')[-1].replace('.pdf', '') 
            ICAO = "SUP"
            eff_date = link.rsplit('/')[-1].rsplit('_')[-2]
            desc = aip_supp_description[i].text
            cat = "SUP"

            print('\t   : {} : {} : {} : {} : {} : {}'.format(ICAO, filename, desc, link, cat,  eff_date))
            chart_item_SUP = ChartItem()

            chart_item_SUP['country'] = self.country_name
            chart_item_SUP['icao'] = ICAO
            chart_item_SUP['link'] = link
            chart_item_SUP['file'] = filename
            chart_item_SUP['desc'] = desc
            chart_item_SUP['club'] = cat
            chart_item_SUP['category'] = eff_date

            list_of_charts.append(chart_item_SUP)

        ##
        ## AIP Charts
        ##

        self.browser.get(aip_page)

        ad = self.browser.find_elements_by_xpath("//td[@class='contenu_principale']/div")[3:14]  # 14 items

        print('\nExtracting : ICAO(s)')

        for i in ad:
            idLinks = i.get_attribute('id')
            driveLinks = self.browser.find_elements_by_id(idLinks)

            if len(driveLinks) > 0:
                driver = driveLinks[0]
                pdf_links = driver.find_elements_by_xpath("table/tbody/tr/td[3]/p/a")
                pdf_file = driver.find_elements_by_xpath("table/tbody/tr/td[4]/p/a")

                for adLink, adFile, adDesc in list(zip(pdf_links, pdf_file, pdf_links)):
                    tagged = adLink.get_attribute('href')
                    zipped = [tagged, adFile.text, adDesc.text]

                    if 'index.php?id=' not in tagged:

                        link = zipped[0]
                        file = zipped[1]
                        desc = zipped[2]
                        icao = link.rsplit('/', 2)[1]
                        cat = "AIP-AD"

                        print('\t   :', icao + '_' + desc)

                        chart_item = ChartItem()

                        chart_item['country'] = self.country_name
                        chart_item['icao'] = icao
                        chart_item['link'] = link
                        chart_item['file'] = file
                        chart_item['desc'] = desc
                        chart_item['club'] = cat
                        chart_item['category'] = "N/A"

                        list_of_charts.append(chart_item)

                    else:
                        print('\t     Extracting : {0} RELATED CHARTS'.format(adFile.text))

                        browser = ChromeDriver()
                        browser.get(tagged)
                        xpath = browser.find_elements_by_xpath("//table[@class='tableau_contenu']/tbody/tr/td[3]/p/a")

                        for path in xpath:
                            link = path.get_attribute('href')
                            icao = link.rsplit('/', 2)[1]
                            file = link.rsplit('/', 2)[2].split('.pdf')[0]
                            cat = "AIP-AD"

                            print('\t                :', file)

                            chart_item = ChartItem()

                            chart_item['country'] = self.country_name
                            chart_item['icao'] = icao
                            chart_item['link'] = link
                            chart_item['file'] = file
                            chart_item['desc'] = file
                            chart_item['category'] = "N/A"
                            chart_item['club'] = cat

                            list_of_charts.append(chart_item)

                        browser.quit()

                for chart in list_of_charts:
                    if chart['icao'] == 'AMDT_3_15':
                        chart['icao'] = 'DTTX'

        self.chart_mgr = TunisiaChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)


    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class TunisiaChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Tunisia')
