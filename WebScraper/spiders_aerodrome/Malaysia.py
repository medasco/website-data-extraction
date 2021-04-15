
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver
from selenium.webdriver.common.action_chains import ActionChains


class MalaysiaSpider(AeroChartSpider):
    """ Hong Kong airport charts spider """
    name = 'Malaysia'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'http://aip.dca.gov.my/aip/eAIP/history-en-MS.html'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]

        list_of_charts = []
        total_charts = []
        grand_charts = []
        additionals = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # Currently Effective Issue
        pub = self.browser.find_element_by_xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/a")
        pub_date = pub.text
        print('\nEffective Date: ', pub_date)
        pub.click()
        self.browser.wait(5)

        # Switch frame to 'eAISNavigationBase'
        self.browser.wait_until_located("XPATH", "//frame[@name='eAISNavigationBase']", 3)
        self.browser.switch_to.frame("eAISNavigationBase")

        # Switch frame to 'eAISNavigation'
        self.browser.wait_until_located("XPATH", "//frame[@name='eAISNavigation']", 3)
        self.browser.switch_to.frame("eAISNavigation")

        # get link to SUP Tab for later use
        sup_tab_link = self.browser.find_element_by_xpath("/html/body/div[1]/a[3]").get_attribute('href')

        ##
        ## AIP-AD Section
        ##

        # Go to PART 3 - AERODROMES (AD)
        self.browser.wait_until_located("XPATH", "/html/body/div[6]", 3)

        # Extract and Go to Aerodromes TOC via link (href)
        ad = self.browser.find_element_by_xpath("/html/body/div[6]/a[2]").get_attribute('href')
        self.browser.get(ad)

        # Extracting Aerodrome Individual and Related Charts links
        origin = self.browser.find_elements_by_xpath("//*[@id='AD-0.6']/div[2]/div/h3/a")
        related = self.browser.find_elements_by_xpath("//*[@id='AD-0.6']/div/div/div[24]/h4/a")

        # Aerodrome's Individual Chart loop
        print('\nExtracting :', self.country_name)

        for h3 in origin:
            pdf = h3.get_attribute('href')
            olink = pdf.replace('/html/eAIP/', '/pdf/').replace('.html', '.pdf')
            osplit = olink.split('/')
            ochop = osplit[-1].split('.pdf#')
            oicao = ochop[1].split('.')[1]
            odesc = ochop[1]
            ofile = ochop[0]
            cat = "AIP-AD"


            total_charts.append([oicao, olink, ofile, odesc, cat, pub_date])
            grand_charts.append(ofile)
            print('\t   :', oicao)

        for h4 in related:
            rlink = h4.get_attribute('href')
            ricao = rlink.split('#')[1].split('-')[0]
            additionals.append([rlink, ricao])

        print('\t     Generating other related chart(s)...')

        for ads, inn in additionals:
            self.browser.get(ads)
            datas = self.browser.find_elements_by_xpath('//div[contains(@id, "2.24")]/table/tbody')

            if len(datas) > 0:
                data = datas[0]
                page = data.find_elements_by_tag_name('a')
                name = data.find_elements_by_tag_name('p')

                print('\nExtracting :', inn)

                for adpage, adname in list(zip(page, name)):
                    pep = [adpage.get_attribute('href'), adname.text, adpage.text]
                    adlink = pep[0]
                    addesc = pep[1].replace('-', '_')
                    adfile = pep[2].replace(' ', '_').replace('-', '_')
                    adicao = inn
                    cat = "AIP-AD"

                    total_charts.append([adicao, adlink, adfile, addesc, cat, pub_date])
                    grand_charts.append(adfile)
                    print('\t   :', adfile)

                print('\t     Extracted [{0}] file(s)...'.format(len(page)))

        ##
        ## SUP Section
        ##

        self.browser.get(sup_tab_link)

        # Get elements
        sup_links = self.browser.find_elements_by_xpath('/html/body/table/tbody/tr[@class="SupTable-Row"]/td[1]/a[1]')
        sup_links.extend(self.browser.find_elements_by_xpath('/html/body/table/tbody[1]/tr[9]/td[1]/span/a[1]'))     # specific due to inconsistency
        sup_pub_date = self.browser.find_element_by_xpath('/html/body/h2').text.replace('Published as of ','')

        # DO NOT MOVE OUT, purposely positioned here to always be reinitalized to nothing before use
        sup_link_captured = []     
        # process all SUP element information
        for link in sup_links:
            ad = link.get_attribute('href')
            ad_icao = "SUP"
            ad_link = ad.replace('html','pdf').replace('eSUP/','')
            ad_desc = "SUP_" + link.get_attribute('innerText')
            ad_file = "SUP_" + link.get_attribute('innerText').replace('.pdf', '') 
            ad_cat = "SUP"

            print("SUP ", ad_desc)
            total_charts.append([ad_icao, ad_link, ad_file, ad_desc, ad_cat, sup_pub_date])
            grand_charts.append(ad_file)

            # append SUP link for later use
            sup_link_captured.append(ad)

        # enter all SUP link and check if there are additional attachments and process those
        for sup_entry in sup_link_captured:
            self.browser.get(sup_entry)

            # look for tag name 'a' to find more links to downlo
            sup_attachment = self.browser.find_elements_by_tag_name('a')
            print('\nChecking for Additional Charts....')

            counter = 0
            for attachment in sup_attachment:
                sup = attachment.get_attribute('href')
                sup_icao = "SUP"
                sup_link = sup
                sup_desc = attachment.get_attribute('innerText').split('/')[-1].replace('.pdf', '')
                sup_file = "SUP_" + attachment.get_attribute('innerText').split('/')[-1].replace('.pdf', '')
                

                total_charts.append([sup_icao, sup_link, sup_file, sup_desc, "SUP", sup_pub_date])
                print('\t fetching additional charts: ' + sup_pub_date + " -"+ sup_icao + ": " + str(counter+1))

        for icao, link, file, desc, cat, eff_date in total_charts:
            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['icao'] = icao
            chart_item['link'] = link
            chart_item['file'] = file
            chart_item['desc'] = desc
            chart_item['club'] = cat
            chart_item['category'] = eff_date


            list_of_charts.append(chart_item)

        for chart in list_of_charts:
            if chart['desc'] == 'NIL':
                list_of_charts.remove(chart)

        # print('\nTotal of [{0}] ICAO(s).'.format(len(origin)))  # 39 ICAO
        print('Grand Total of  [{0}] PDF file(s).\n'.format(len(grand_charts)))  # 694 PDF files

        self.chart_mgr = MalaysiaChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class MalaysiaChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Malaysia')
