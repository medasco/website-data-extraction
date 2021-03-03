
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver
from selenium import webdriver


class MaldivesSpider(AeroChartSpider):
    """ Maldives airport charts spider """
    name = 'Maldives'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://www.macl.aero/corporate/services/operational/ans'

    def parse(self, response):

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []
        total_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # get aip page link
        aip_link = self.browser.find_element_by_xpath('//*[@id="bodyarea"]/div[8]/div/div/div/div[1]/a').get_attribute('href')

        # get aip supplements link
        sup = self.browser.find_element_by_link_text('AIP SUPPLEMENTS')
        self.browser.execute_script('arguments[0].click();', sup)

        sup_link = self.browser.find_element_by_xpath('//*[@id="tab-aipsuppliments"]/div[1]/div[1]/a').get_attribute('href')

        ##
        ## AIP-AD
        ##
        
        # enter aip page
        self.browser.get(aip_link)

        # Clicking element w/o clickable attribute
        adrome = self.browser.find_element_by_partial_link_text('Aerodrome')
        self.browser.execute_script('arguments[0].click();', adrome)

        # Get all charts under Aerodrome tab
        adds = self.browser.find_elements_by_xpath('//h6[contains(@id, "dataloadlist-")]')

        for ad in adds:
            adtext = ad.text

            if 'VRM' in adtext:
                self.browser.execute_script('arguments[0].click();', ad)
                self.browser.wait(3)
                name = self.browser.find_element_by_xpath('//*[@id="documentitle"]')
                link = self.browser.find_element_by_xpath('//*[@id="myframe"]').get_attribute('src')
                file = name.text
                desc = file.replace(' ', '_')
                icao = file[:4]
                cat = "AIP-AD"
                eff_date = "N/A"

                total_charts.append([icao, file, desc, link, cat, eff_date])
                print('\t   : {} : {} : {} : {} : {} : {}'.format(icao, file, desc, link, cat, eff_date))


        ## SUP section
        ##

        # enter sup page
        self.browser.get(sup_link)

        # Get all charts under Aerodrome tab
        adds = self.browser.find_elements_by_xpath('//tr[contains(@id, "dataloadlist-")]')
 
        for ad in adds:
            
            self.browser.execute_script('arguments[0].click();', ad)
            self.browser.wait(3)
    
            desc = self.browser.find_element_by_xpath('//*[@id="documentitle"]').text
            icao = "SUP"
            cat = "SUP"
            eff_date = ad.find_element_by_xpath('./td[2]/ul/h6').text

            print("SUP", eff_date)
            # this is done like this because there's a chance that there are multiple images
            sup_link = self.browser.find_elements_by_xpath('//*[@id="documentholder"]/p/img')
            name_counter = 1
            for links in sup_link:
                link = links.get_attribute('src')
                filename = "SUP_" + eff_date.replace('-', '_') + "__" + str(name_counter) + "_of_" + str(len(sup_link))
                name_counter += 1

                total_charts.append([icao, filename, desc, link, cat, eff_date])
                print('\t   : {} : {} : {} : {} : {} : {}'.format(icao, filename, desc, link, cat, eff_date))

        # start list processing
        for icao, filename, desc, link, cat, eff_date in total_charts:
            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['icao'] = icao
            chart_item['link'] = link
            chart_item['file'] = filename
            chart_item['desc'] = desc
            chart_item['club'] = cat
            chart_item['category'] = eff_date

            list_of_charts.append(chart_item)

        self.chart_mgr = MaldivesChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class MaldivesChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Maldives')
