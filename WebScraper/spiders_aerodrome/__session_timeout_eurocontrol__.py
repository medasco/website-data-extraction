
import scrapy
from math import ceil
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver
from acm.downloader.utils import time_human
import time


class session_EuroControl(scrapy.Spider):
    """ Hong Kong airport charts spider """
    name = 'session_EuroControl'
    version = '1.0.0'

    def __init__(self):
        super(session_EuroControl, self).__init__()
        self.browser = ChromeDriver()
        self.club = self.name
        self.country_name = None
        self.chart_mgr = None

        self.data = None

    def start_requests(self):
        """ Set the main URL to be visited
            and start the request.
        """
        url = 'https://eadbasic.ead-it.com/cms-eadbasic/opencms/en/login/ead-basic'

        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """ Parsing callback function """

        username = 'psware8046'
        password = 'AMDB2099'

        pdf_desc = None
        pdf_links = None
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
        self.browser.wait_until_located('XPATH', "//button[@id='acceptTCButton']", 10).click()
        # Look for 'AIP Library' link and click it!
        self.browser.find_element_by_xpath("//*[@id='topForm:topMenu:j_idt17:3:j_idt18:j_idt28:j_idt29']").click()

        t1 = time.time()
        x = True
        while x:
            try:
                self.browser.find_element_by_xpath("//button[@id='mainForm:querySearch']").click()
                self.browser.wait(5)

                if (t1 - time.time()) >= 840:
                    self.browser.refresh()
                    t1 = time.time()

            except Exception as e:
                print(time_human(duration=int(time.time() - t1), fmt_short=False))
                x = False


    # def close(self, reason):
    #     # Quit the browser
    #     self.browser.quit()
    #     # Delete
    #     del self


class EuroControlChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        # self.print_chart_list()
        self.save_chart_list('EuroControl')

"""
class CountryCode_EuroControl:

    code = [('LA', 'Albania (LA)'),
            ('UD', 'Armenia (UD)'),
            ('LO', 'Austria (LO)'),
            ('UB', 'Azerbaijan (UB)'),
            ('UM', 'Belarus (UM)'),
            ('EB', 'Belgium (EB)'),
            ('LQ', 'Bosnia/Herzeg. (LQ)'),
            ('LB', 'Bulgaria (LB)'),
            ('LD', 'Croatia (LD)'),
            ('LC', 'Cyprus (LC)'),
            ('LK', 'Czech Republic (LK)'),
            ('EK', 'Denmark (EK)'),
            ('EE', 'Estonia (EE)'),
            ('XX', 'Faroe Islands (XX)'),
            ('EF', 'Finland (EF)'),
            ('LW', 'Former Yugoslav Rep. of Macedonia (LW)'),
            ('LF', 'France (LF)'),
            ('UG', 'Georgia (UG)'),
            ('ED', 'Germany (ED)'),
            ('LG', 'Greece (LG)'),
            ('BG', 'Greenland (BG)'),
            ('LH', 'Hungary (LH)'),
            ('BI', 'Iceland (BI)'),
            ('EI', 'Ireland (EI)'),
            ('LI', 'Italy (LI)'),
            ('OJ', 'Jordan (OJ)'),
            ('UA', 'Kazakhstan (UA)'),
            ('BK', 'Kosovo (BK)'),
            ('UC', 'Kyrgyzstan (UC)'),
            ('EV', 'Latvia (EV)'),
            ('EY', 'Lithuania (EY)'),
            ('LM', 'Malta (LM)'),
            ('LU', 'Moldova (LU)'),
            ('EH', 'Netherlands (EH)'),
            ('EN', 'Norway (EN)'),
            ('RP', 'Philippines (RP)'),
            ('EP', 'Poland (EP)'),
            ('LP', 'Portugal (LP)'),
            ('LR', 'Romania (LR)'),
            ('LY', 'Serbia and Montenegro (LY)'),
            ('LZ', 'Slovakia (LZ)'),
            ('LJ', 'Slovenia (LJ)'),
            ('LE', 'Spain (LE)'),
            ('ES', 'Sweden (ES)'),
            ('LS', 'Switzerland (LS)'),
            ('LT', 'Turkey (LT)'),
            ('UK', 'Ukraine (UK)'),
            ('EG', 'United Kingdom (EG)')
            ]
"""
