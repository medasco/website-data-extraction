
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class IndiaSpider(AeroChartSpider):
    """ India airport charts spider """
    name = 'India'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://aim-india.aai.aero/'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        supp_links = []
        supp_pages = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # Get AIP Supplements link (subject of change in xpath)
        aip_supp = self.browser.find_element_by_link_text('AIP Supplements').get_attribute('href')
        supp_pages.append(aip_supp)

        # Go eAIP
        eaip = self.browser.find_element_by_xpath('//*[@id="block-system-main-menu"]/ul/li[2]/a').get_attribute('href')
        self.browser.get(eaip)

        # Switch frame to 'eAISNavigationBase'
        self.browser.wait_until_located("XPATH", "//frame[@name='eAISNavigationBase']", 3)
        self.browser.switch_to.frame("eAISNavigationBase")

        # Switch frame to 'eAISNavigation'
        self.browser.wait_until_located("XPATH", "//frame[@name='eAISNavigation']", 3)
        self.browser.switch_to.frame("eAISNavigation")

        # Getting the Publication Date
        pub = self.browser.find_element_by_xpath('/html/body/h2')
        pub_date = pub.text
        print('\n', pub_date)

        # Go to PART 3 - AERODROMES (AD)
        self.browser.wait_until_located("XPATH", "//*[@id='AERODROMESdetails']", 3)

        # Extract Aerodromes
        individual = self.browser.find_elements_by_xpath("//*[@id='AERODROMESdetails']/div[@class='Hx']/a[contains(@onclick, 'showHide')]")
        eaip_links = []
        related_charts = []

        # Aerodrome's Individual Chart Links loop
        print('\nExtracting :', self.country_name)

        for con in individual:  # Promulgated Version if any
            date = pub_date.replace('Effective', '').replace(' ', '_')
            path = con.get_attribute('href')
            adlink = path.replace('IN-', '').replace('-en-GB', '').replace('.html', '.pdf').replace('/eAIP', '/pdf/eAIP')
            adicao = adlink.rsplit('/', 1)[-1].split('.')[1].replace('1', '')
            adfile = adlink.rsplit('/', 1)[-1].replace('.pdf', '').replace('%20', '')
            addesc = adfile + '_EFF:' + date
            related_charts.append(path)

            print('\t   : {} : {} : {} : {}'.format(adicao, adfile, addesc, adlink))

            eaip_links.append([adicao, adfile, addesc, adlink])

        # Aerodrome's Related Chart Links loop
        for rel in related_charts:
            self.browser.get(rel)
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.browser.wait(1)

            # to pass '#document'
            iframe = self.browser.find_elements_by_tag_name('iframe')[1]
            self.browser.switch_to_frame(iframe)
            tags = self.browser.find_elements_by_xpath('/html/body/table[1]/tbody/tr/td[2]/a[2]')

            for tag in tags:
                tagLink = tag.get_attribute('href')
                tagName = tagLink.rsplit('/', 1)[1].replace('%20', '')
                tagIcao = tagName[:4] if '_' not in tagName else tagName.rsplit('_', 1)[1][:4].upper()
                tagFile = tagName.replace('.pdf', '')
                tagDesc = tagFile.replace('-', '_')

                if tagIcao == 'VADO':
                    tagIcao = 'VABO'

                if (tagIcao == '33.P') | (tagIcao == 'LVPT') | (tagIcao == 'ILSC'):
                    tagIcao = 'VIDP'

                print('\t   : {} : {} : {} : {}'.format(tagIcao, tagFile, tagDesc, tagLink))

                eaip_links.append([tagIcao, tagFile, tagDesc, tagLink])

        # Get AIP Supplements
        browser = ChromeDriver()
        browser.get(aip_supp)

        pages = browser.find_elements_by_xpath("//*[@id='block-system-main']/div/div[3]/ul/li/a")

        for page in pages:  # Actual webpages minus one
            supp_pages.append(page.get_attribute('href')) if 'next' in page.text else None

        print('\n\t   : AIP Supplements :', self.country_name)

        # Get links and effectivity dates on every page
        for sup in supp_pages:

            print('\t   : {}'.format(sup))

            browser.get(sup)
            tbody = browser.find_elements_by_xpath('//*[@id="block-system-main"]/div/div[2]/div/table/tbody')

            if len(tbody) > 0:
                body = tbody[0]
                supLinks = body.find_elements_by_tag_name('a')

                for suppLink in supLinks:
                    suplink = suppLink.get_attribute('href')
                    suptitle = suppLink.text.replace('\n', '-')
                    supdesc = suppLink.text.replace('\n', '-')
                    supname = suptitle.rsplit(' ', 1)[-1]
                    supfile = suplink.rsplit('/', 1)[1].split('.')[0]
                    supicao = supname.replace('(', '').replace(')', '') if '(V' in supname else 'SUPP'

                    print('\t   : {} : {} : {} : {}'.format(supicao, supfile, supdesc, suplink))

                    eaip_links.append([supicao, supfile, supdesc, suplink])

        for icao, file, desc, link in eaip_links:
            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['icao'] = icao
            chart_item['link'] = link
            chart_item['file'] = file
            chart_item['desc'] = desc
            chart_item['club'] = 'Default'

            list_of_charts.append(chart_item)

        self.chart_mgr = IndiaChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class IndiaChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('India')
