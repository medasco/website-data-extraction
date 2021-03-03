
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver

import ctypes  # An included library with Python install.


class IndonesiaSpider(AeroChartSpider):
    """ Australia airport charts spider """
    name = 'Indonesia'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://aimindonesia.dephub.go.id/signin.php'
        self.icao = []
        # self.desc = []
        # self.link = []

    def parse(self, response):
        """ Parsing callback function """

        baseUri = 'https://aimindonesia.dephub.go.id/'
        username = 'ed.chaput@psware.com'
        password = 'AMDB2095'

        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        path_list = []

        # Login
        ctypes.windll.user32.MessageBoxW(0, "Enter the security code then click OK\n!!! DO NOT CLICK SIGN IN !!!", "Captcha Required", 0)
        self.browser.find_element_by_id("email").send_keys(username)
        self.browser.find_element_by_id("password").send_keys(password)
        self.browser.select_dropdown_option("//*[@id='txtLang']", "en")
        self.browser.find_element_by_id("btnSubmit").click()

        self.browser.wait_until_located('XPATH', "/html/body/div[2]/aside[1]/section/ul/li[4]/ul/li[2]/a", 30)

        sideBar = self.browser.find_elements_by_xpath('/html/body/div[2]/aside[1]/section/ul/li[4]/ul/li[1]/ul/li/a')

        for tab in sideBar:
            tabs = tab.get_attribute('href')
            path_list.append(tabs)

        # Going vol123 html
        self.browser.get(path_list[1])

        # Go Vol II link
        v2 = self.browser.find_element_by_xpath('//*[@id="main-content"]/div/div/div/div[2]/table/tbody/tr[3]/td[2]/a').get_attribute('href')
        self.browser.get(v2)

        # Go AD 2
        ad = self.browser.find_element_by_xpath('//*[@id="main-content"]/div/div/div/div[2]/table/tbody/tr[4]/td[2]/a').get_attribute('href')
        self.browser.get(ad)

        self.browser.wait_until_located('XPATH', '//*[@id="main-content"]//table', 30)
        self.browser.wait(1)

        icaoTD2 = self.browser.find_elements_by_xpath('//*[@id="main-content"]//table//td[2]')
        icaoTD4 = self.browser.find_elements_by_xpath('//*[@id="main-content"]//table//td[4]')

        icaoNames = []
        icaoURLs = []

        print('\nExtracting :', self.country_name)

        for icao, url in list(zip(icaoTD2, icaoTD4)):
            link = url.find_elements_by_tag_name("a")

            if len(link) > 0:
                icaoNames.append(icao.text)
                href = link[0].get_attribute('href')
                icaoURLs.append(href)

        pdf_links = []
        for icao, url in list(zip(icaoNames, icaoURLs)):

            self.browser.get(url)
            self.browser.wait_until_located('XPATH', '//*[@id="tab_1"]/iframe', 30)

            pdfLink = self.browser.find_element_by_xpath('//*[@id="tab_1"]/iframe').get_attribute("src")
            pdf_links.append([icao, "AIP", pdfLink])

            print('\nExtracting :', icao)

            self.browser.find_element_by_xpath('//*[@id="main-content"]/div/div/div/div[2]/div/div/div/ul/li[2]/a').click()
            self.browser.wait_until_located('XPATH', '//*[@id="tab_2"]/script', 30)
            additionalLinks = self.browser.find_elements_by_xpath('//*[@id="tab_2"]/table//td[2]')

            for additionalLink in additionalLinks:
                chartLink = additionalLink.find_elements_by_tag_name("a")
                if len(chartLink) > 0:
                    temp = chartLink[0].get_attribute('onclick')
                    links = temp.split(",")[1].strip().split("'")
                    path = links[1].split('/')[-1].rsplit('.', 1)[0]  # added by medasco for Terminal printouts

                    print('\t   :', path)

                    for link in links:
                        if "pdf" in link:
                            pdfLink = baseUri + link
                            pdf_links.append([icao, chartLink[0].text, pdfLink])

            print('\t     Extraction completed [{0}] file(s)...'.format(len(additionalLinks)))

        for icao, desc, link in pdf_links:

            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['icao'] = icao
            chart_item['link'] = link
            chart_item['desc'] = desc
            chart_item['file'] = link.split('/')[-1].rsplit('.', 1)[0].replace('%20', '_')
            chart_item['club'] = 'Default'

            list_of_charts.append(chart_item)

        print('\nTotal of [{0}] ICAO(s).'.format(len(icaoNames)))  # 25 ICAO
        print('Grand Total of [{0}] PDF file(s).\n'.format(len(pdf_links)))  # 347 PDF files

        # Go AIP Supplements
        self.browser.get(path_list[5])  # entire AIP supplements acquisition added by medasco

        supHtml_list = []

        sup_html = self.browser.find_elements_by_xpath('//*[@id="main-content"]/div/div/div/div[2]/table/tbody/tr/td[3]/a')

        for supHtml in sup_html:
            supHtmls = supHtml.get_attribute('href')
            supHtml_list.append(supHtmls)

        for path in supHtml_list:
            self.browser.get(path)
            suplink = self.browser.find_element_by_xpath('//*[@id="main-content"]/div/div/div/div[2]/iframe').get_attribute('src')
            supdesc = self.browser.find_element_by_xpath('//*[@id="main-content"]/div/div/div/div[1]/a[3]').text

            if 'index.php?' not in suplink:
                supfile = suplink.rsplit('/', 1)[1].replace('%20', '_').replace('.pdf', '').upper()
                supicao = 'WIII' if 'SOEKARNO' in supdesc else 'SUPP'

                chart_item = ChartItem()

                chart_item['country'] = self.country_name
                chart_item['icao'] = supicao
                chart_item['link'] = suplink
                chart_item['desc'] = supdesc
                chart_item['file'] = supfile
                chart_item['club'] = 'Default'

                print('\t   : {} : {} : {} : {}'.format(supicao, supfile, supdesc, suplink))

                list_of_charts.append(chart_item)

        print('\nTotal of [{0}] SUPP(s).'.format(len(supHtml_list)))
        print('Grand Total of [{0}] PDF file(s).\n'.format(len(pdf_links) + len(supHtml_list)))

        self.chart_mgr = IndonesiaChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class IndonesiaChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Indonesia')
