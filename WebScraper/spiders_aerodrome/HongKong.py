
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class HongKongSpider(AeroChartSpider):
    """ Hong Kong airport charts spider """
    name = 'HongKong'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = 'Hong Kong'
        self.url = 'https://www.ais.gov.hk/'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]

        baseURL = 'https://www.ais.gov.hk/'
        list_of_charts = []
        total_charts = []
        eff_issues = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # By ticking this box to agree
        self.browser.find_element_by_xpath('//*[@id="agreeTerms"]').click()
        self.browser.wait(3)

        # Click Continue
        self.browser.find_element_by_xpath('//*[@id="terms"]/div[2]/button').click()
        self.browser.wait(3)

        # AIP Supplements
        sup = self.browser.find_element_by_xpath('//*[@id="SUP"]').click()
        supplements = self.browser.find_elements_by_xpath('//*[@id="AIP"]/div[5]') #'/div/div[1]/table/tbody/tr/td[2]/a

        if supplements:
            supcharts = supplements[0]
            scharts = supcharts.find_elements_by_tag_name('a')

            for schart in scharts :
                onclick = schart.get_attribute('onclick')
                onsplit = onclick.split(',')[0].split('(')[1].replace("'", '')
                slink = ''.join([baseURL, onsplit])
                sdesc = slink.split('hk/')[1].replace('/', '_').replace('.pdf', '')
                sfile = slink.rsplit('/', 1)[1].replace('.pdf', '')
                sicao = 'VHHH'

                # print('\t   : {} : {} : {} : {}'.format(sicao, sfile, sdesc, slink))
                total_charts.append([sicao, sfile, sdesc, slink, ''])

        # Aerodromes (AD)
        #eaip = self.browser.find_element_by_xpath('//*[@id="info"]/div[2]/ul/li[1]/span/a').get_attribute('href')
        # Get AD Charts

        self.browser.get(response.url)

        # By ticking this box to agree
        self.browser.find_element_by_xpath('//*[@id="agreeTerms"]').click()
        self.browser.wait(3)

        # Click Continue
        self.browser.find_element_by_xpath('//*[@id="terms"]/div[2]/button').click()
        self.browser.wait(3)

        pub_date = self.browser.find_element_by_xpath('//*[@id="amdtPub"]').text.replace('-', '')

        eaipLoc = "eaip_" + pub_date + "/VH-history-en-US.html"
        eaip = response.url + eaipLoc
        browser = ChromeDriver()
        browser.get(eaip)

        # Currently Effective Issue
        current_issue = browser.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/a').get_attribute('href')
        eff_issues.append(current_issue)
        next_issues = browser.find_elements_by_xpath('/html/body/table/tbody/tr[4]/td/table/tbody/tr/td/a')
        for issue in next_issues:
            eff_issues.append(issue.get_attribute('href'))
        
        for issue in eff_issues:

            browser.get(issue)

            browser.wait(3)

            # Switch frame to 'eAISNavigation'
            browser.wait_until_located("XPATH", "//frame[@name='eAISNavigation']", 3)
            browser.switch_to.frame("eAISNavigation")

            # Effectivity date
            eff_date = browser.find_element_by_xpath('/html/body/h2').text.replace('Effective ', '').replace(' ', '')

            # Aerodromes
            adrome = browser.find_element_by_xpath('//*[@id="i52175"]')
            adrome.click()

            ad = adrome.get_attribute('href')
            adlink = ''.join([ad.rsplit('-en-', 1)[0].replace('html/eAIP', 'pdf'), '.pdf'])
            addesc = adrome.text.upper()
            adfile = ad.rsplit('-en-', 1)[0].rsplit('/', 1)[1].replace('VH-', '')  + '_' + eff_date
            adicao = ad.rsplit('-en-', 1)[0].rsplit('/', 1)[1].replace('VH-', '').split('-')[-1]
            adeff = eff_date

            print('\t   : {} : {} : {} : {}'.format(adicao, adfile, addesc, adlink))
            total_charts.append([adicao, adfile, addesc, adlink, adeff])

            related = browser.find_element_by_xpath('//*[@id="i49703"]').get_attribute('href')

            browser.get(related)
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            td3 = browser.find_elements_by_xpath('//*[@id="i1227320"]/tbody/tr/td[3]/span/div/div/a')
            td1 = browser.find_elements_by_xpath('//*[@id="i1227320"]/tbody/tr/td[1]')
            td2 = browser.find_elements_by_xpath('//*[@id="i1227320"]/tbody/tr/td[2]')

            for tlink, tfile, tdesc in list(zip(td3, td2, td1)):
                rlink = tlink.get_attribute('href')
                rchop = rlink.split('VH-')[1].replace('AD-', 'AD ').replace('.pdf', '')
                rfile = rchop + '_' + eff_date if tfile.text == '' else tfile.text + '_' + eff_date
                rdesc = rchop if tdesc.text == '' else tdesc.text
                ricao = 'VHHH'
                reff = eff_date

                print('\t   : {} : {} : {} : {}'.format(ricao, rfile, rdesc, rlink))
                total_charts.append([ricao, rfile, rdesc, rlink, reff])

        for icao, file, desc, link, eff in total_charts:

            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['desc'] = desc
            chart_item['link'] = link
            chart_item['icao'] = icao
            chart_item['file'] = file
            chart_item['club'] = 'Default'
            chart_item['category'] = eff

            list_of_charts.append(chart_item)

        # Process extracted ChartItem list
        self.chart_mgr = HongKongChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class HongKongChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Hong Kong')
