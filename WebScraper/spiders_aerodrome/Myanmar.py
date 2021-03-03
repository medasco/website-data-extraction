
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class MyanmarSpider(AeroChartSpider):
    """ Myanmar airport charts spider """
    name = 'Myanmar'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'http://www.ais.gov.mm/eAIP/history-en-GB.html'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]

        grand_charts = []
        total_charts = []
        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        pub = self.browser.find_element_by_xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/a")
        pub_date = pub.text.replace(' ', '')
        print('\nEffective Date: ', pub_date)
        pub.click()
        self.browser.wait(1)

        # Switch frame to 'eAISNavigationBase'
        self.browser.wait_until_located("XPATH", "//frame[@name='eAISNavigationBase']", 3)
        self.browser.switch_to.frame("eAISNavigationBase")

        # Switch frame to 'eAISNavigation'
        self.browser.wait_until_located("XPATH", "//frame[@name='eAISNavigation']", 3)
        self.browser.switch_to.frame("eAISNavigation")

        # Go to PART 3 - AERODROMES (AD)
        self.browser.wait_until_located("XPATH", "//*[@id='ADdetails']", 3)

        # Extract and Go to Aerodromes TOC via link (href)
        ad = self.browser.find_element_by_xpath("//*[@id='AD']").get_attribute('href')
        self.browser.get(ad)

        origin = self.browser.find_elements_by_xpath("//*[@id='AD-0.6']/div[2]/div/h3/a")

        print('\nExtracting :', self.country_name)

        # Aerodrome's Individual Chart loop
        for h3 in origin:
            pdf = h3.get_attribute('href')
            link3 = pdf.replace('/html/eAIP/', '/pdf/').replace('-en-GB.html', '.pdf')
            split = link3.split('/')
            file3 = link3.rsplit('/', 1)[1].split('.pdf')[0]
            icao3 = file3.split('2.')[1].split('-')[0]
            desc3 = split[6].split('.pdf#')[0].replace('-', '_') + '_' + split[4].replace('-Non-AIRAC', '').replace('-', '')

            # h3_new = '/pdf/'.join([pdf.rsplit('/html/eAIP/', 1)[0], pdf.rsplit('/html/eAIP/', 1)[1]])
            # link = ''.join([h3_new.rsplit('-en-GB', 1)[0], '.pdf'])
            # split = link.rsplit('/eAIP/', 1)[1].split('/pdf/')
            # desc = '_'.join([split[0].split('-Non-AIRAC')[0], split[1]]).split('.pdf')[0]

            print('\t   :', icao3)

            total_charts.append([icao3, link3, file3, desc3])
            grand_charts.append(file3)

        # Aerodrome's Additional Charts loop
        additional = []
        related = self.browser.find_elements_by_xpath("//*[@id='AD-0.6']/div[2]/div/div[last()]/h4/a")

        for h4 in related:
            additional.append(h4.get_attribute('href'))

        print('\t     Extracting other related chart(s)...')

        for ad in additional:
            # browser = ChromeDriver()
            # currentLink = ad.get_attribute('href')
            # browser.get(currentLink)
            # divId = currentLink.split('#')[1]
            self.browser.get(ad)
            divId = ad.split('#')[1]
            divElements = self.browser.find_elements_by_id(divId)

            print('\nExtracting :', divId)

            if len(divElements) > 0:
                divElement = divElements[0]
                pdf_link = divElement.find_elements_by_tag_name("a")
                pdf_desc = divElement.find_elements_by_tag_name("span")
                # pdf_links = browser.find_elements_by_xpath("//body/div[2]/div[last()]/div/div/a")
                # pdf_descs = browser.find_elements_by_xpath("//body/div[2]/div[last()]/div/span")

                for linkElement, descElement in list(zip(pdf_link, pdf_desc)):

                    link4 = linkElement.get_attribute('href')
                    icao4 = link4.rsplit('/', 2)[1]
                    file4 = '_'.join(link4.rsplit('/', 2)[2].split('-')).split('.pdf')[0]
                    desc4 = descElement.text

                    print('\t   :', icao4 + '_' + desc4)

                    total_charts.append([icao4, link4, file4, desc4])
                    grand_charts.append(file4)

                print('\t     Extraction completed [{0}] file(s)...'.format(len(pdf_link)))

            # browser.quit()

        for icao, link, file, desc in total_charts:

            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['icao'] = icao
            chart_item['link'] = link
            chart_item['file'] = file
            chart_item['desc'] = desc
            chart_item['club'] = 'Default'

            list_of_charts.append(chart_item)

        print('\nTotal of [{0}] ICAO(s).'.format(len(origin)))  # 33 ICAO
        print('Grand Total of  [{0}] PDF file(s).\n'.format(len(grand_charts)))  # 121 PDF files

        self.chart_mgr = MyanmarChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class MyanmarChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Myanmar')
