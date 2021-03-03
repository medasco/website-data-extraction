

import scrapy
from math import ceil
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver
from acm.downloader.utils import time_human
import time
import urllib.request, urllib.parse, urllib.error
import ssl
import datetime
import pandas
from acm.config import *


class UnitedStatesSpider(AeroChartSpider):
    """ United States airport charts spider """
    name = 'USA'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://www.faa.gov/air_traffic/flight_info/aeronav/digital_products/dtpp/'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]

        total_charts = []
        list_of_charts = []
        total_links = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)
        zip_folders = self.browser.find_elements_by_xpath('//*[@class="striped"]')

        for zips in zip_folders:
            zip_files = zips.find_elements_by_tag_name('a')

            for pdf in zip_files:
                links = pdf.get_attribute('href')
                total_links.append(links)

        click_link = self.browser.find_element_by_link_text('Chart Supplements').get_attribute('href')
        self.browser.get(click_link)
        sup_folders = self.browser.find_elements_by_xpath('//*[@title="Chart Supplements"]')

        for sups in sup_folders[:1]:
            sup_files = sups.find_elements_by_tag_name('a')

            for pdf in sup_files:
                paths = pdf.get_attribute('href')
                total_links.append(paths)

        for loop in total_links:
            name = loop.split('/')[-1].replace('.zip', '')
            keep = name.replace('.zip', '')

            # Get effectivity date from file name and format it to mm-dd-yy
            eff_date = name.split('_')[1]
            eff_date = "20" + eff_date if len(eff_date) == 6 else eff_date
            eff_date = pandas.to_datetime(eff_date, format='%Y%m%d').strftime('%m-%d-%Y')

            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['icao'] = name.split('_20')[1][:4] if 'DCS' in name else keep.replace('DCS', 'SUP')
            chart_item['link'] = loop
            chart_item['file'] = name.split('_20')[0] if 'DCS' in name else keep.replace('DCS', 'SUP')
            chart_item['desc'] = keep
            chart_item['club'] = 'Default'
            chart_item['category'] = eff_date

            list_of_charts.append(chart_item)

        self.chart_mgr = UnitedStatesChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

        print('\nDirect Downloading :', self.country_name)

        download_path = DOWNLOAD_PATH + 'USA\\Construction_DL\\'

        if not os.path.exists(download_path):
            os.makedirs(download_path)

        # click_link = self.browser.find_element_by_link_text('Aeronautical Data').get_attribute('href')
        # self.browser.get(click_link)
        # self.browser.find_element_by_link_text('Airport Construction Notices').click()
        self.click_enable(self.browser.find_element_by_link_text('Aeronautical Data'))
        self.click_enable(self.browser.find_element_by_link_text('Airport Construction Notices'))
        self.browser.wait_until_located("XPATH", "//div[@id='contentDiv']/ul/li/span", 5)
        content = self.browser.find_elements_by_xpath('//a[@target="blank"]')

        for cons in content:
            url = cons.get_attribute('href')
            date = datetime.datetime.now().strftime('%m%d%Y')
            file = 'K' + url.split('/')[-1].replace('.pdf', '').upper() + '_con' + '_' + date + '.pdf'
            print(file)

            # Direct Downloading
            retry_count = 0

            while retry_count < 2:
                try:
                    f = urllib.request.urlopen(url, timeout=4)
                    data = f.read()
                    with open(str(download_path + file), 'wb') as code:
                        code.write(data)
                        print('Downloaded:', file)
                    retry_count = 2

                except ssl.socket_error as e:
                    print(e)
                    print('Timeout(1):', file)

                    # Redirecting Download after first timeout
                    print('\tRetrying...:', file)
                    retry_count += 1

                except (urllib.error.HTTPError, urllib.error.URLError) as e:
                    print(e)
                    retry_count = 2

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class UnitedStatesChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('UnitedStates')
